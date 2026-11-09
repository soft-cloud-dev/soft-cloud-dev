#!/usr/bin/env python3
"""Shared internationalization, YAML parsing, and document structure utilities for SoftCloud."""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore[import-untyped]
except ImportError:
    yaml = None


# ---------------------------------------------------------------------------
# Cryptographic & Atomic File Helpers
# ---------------------------------------------------------------------------


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def sha256_json(obj: Any) -> str:
    canonical = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return sha256_text(canonical)


def sha256_file(path: Path) -> str:
    with path.open("rb") as f:
        if hasattr(hashlib, "file_digest"):
            return hashlib.file_digest(f, "sha256").hexdigest()
        h = hashlib.sha256()
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
        return h.hexdigest()


def atomic_write_bytes(target: Path, data: bytes) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path_str = tempfile.mkstemp(
        dir=str(target.parent),
        prefix=f".tmp.{target.name}.",
    )
    tmp_path = Path(tmp_path_str)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.chmod(tmp_path, 0o644)
        os.replace(tmp_path, target)
    except Exception:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)
        raise


def atomic_write_text(target: Path, text: str) -> None:
    atomic_write_bytes(target, text.encode("utf-8"))


def atomic_write_json(target: Path, obj: Any) -> None:
    content = json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    atomic_write_bytes(target, content.encode("utf-8"))


# ---------------------------------------------------------------------------
# YAML Loader & Dumper (PyYAML with Standard-Library Recursive Fallback)
# ---------------------------------------------------------------------------


def _parse_yaml_scalar(raw: str) -> Any:
    val = raw.strip()
    if not val or val in ("null", "~"):
        return None
    if val == "true":
        return True
    if val == "false":
        return False
    if val == "[]":
        return []
    if val == "{}":
        return {}
    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
        if val.startswith('"'):
            try:
                return json.loads(val)
            except Exception:
                return val[1:-1]
        return val[1:-1].replace("''", "'")
    if re.match(r"^-?\d+$", val):
        return int(val)
    if re.match(r"^-?\d+\.\d+$", val):
        return float(val)
    return val


def _fallback_parse_yaml_lines(lines: list[tuple[int, str]], start: int, base_indent: int) -> tuple[Any, int]:
    """Parse indented YAML block mappings, sequences, and folded/literal scalars."""
    if start >= len(lines):
        return {}, start

    first_indent, first_text = lines[start]
    if first_indent < base_indent:
        return {}, start

    # Sequence block
    if first_text.startswith("- ") or first_text == "-":
        items: list[Any] = []
        idx = start
        seq_indent = first_indent
        while idx < len(lines):
            ind, txt = lines[idx]
            if ind < seq_indent:
                break
            if ind > seq_indent or not (txt.startswith("- ") or txt == "-"):
                break
            after_dash = txt[2:].strip() if txt.startswith("- ") else ""
            idx += 1
            if not after_dash:
                if idx < len(lines) and lines[idx][0] > seq_indent:
                    child, idx = _fallback_parse_yaml_lines(lines, idx, lines[idx][0])
                    items.append(child)
                else:
                    items.append(None)
            elif ":" in after_dash and not (after_dash.startswith('"') or after_dash.startswith("'")):
                # Inline mapping inside list item: e.g. `- file: README.md`
                k_part, v_part = after_dash.split(":", 1)
                item_dict: dict[str, Any] = {}
                key = _parse_yaml_scalar(k_part)
                v_clean = v_part.strip()
                if v_clean:
                    item_dict[str(key)] = _parse_yaml_scalar(v_clean)
                else:
                    if idx < len(lines) and lines[idx][0] > seq_indent:
                        sub_val, idx = _fallback_parse_yaml_lines(lines, idx, lines[idx][0])
                        item_dict[str(key)] = sub_val
                    else:
                        item_dict[str(key)] = None
                # Check if additional mapping keys follow at greater indentation
                if idx < len(lines) and lines[idx][0] > seq_indent and not lines[idx][1].startswith("-"):
                    extra_map, idx = _fallback_parse_yaml_lines(lines, idx, lines[idx][0])
                    if isinstance(extra_map, dict):
                        item_dict.update(extra_map)
                items.append(item_dict)
            else:
                items.append(_parse_yaml_scalar(after_dash))
        return items, idx

    # Mapping block
    mapping: dict[str, Any] = {}
    idx = start
    map_indent = first_indent
    while idx < len(lines):
        ind, txt = lines[idx]
        if ind < map_indent:
            break
        if ind > map_indent:
            break
        if txt.startswith("- ") or txt == "-":
            break
        if ":" not in txt:
            idx += 1
            continue
        k_part, v_part = txt.split(":", 1)
        key = str(_parse_yaml_scalar(k_part))
        v_clean = v_part.strip()
        idx += 1
        if v_clean in (">-", ">", "|", "|-"):
            folded = v_clean.startswith(">")
            block_parts: list[str] = []
            if idx < len(lines) and lines[idx][0] > map_indent:
                scalar_indent = lines[idx][0]
                while idx < len(lines) and lines[idx][0] >= scalar_indent:
                    block_parts.append(lines[idx][1])
                    idx += 1
            mapping[key] = (" ".join(block_parts) if folded else "\n".join(block_parts)).strip()
        elif v_clean == "":
            if idx < len(lines) and lines[idx][0] > map_indent:
                child, idx = _fallback_parse_yaml_lines(lines, idx, lines[idx][0])
                mapping[key] = child
            else:
                mapping[key] = None
        else:
            mapping[key] = _parse_yaml_scalar(v_clean)
    return mapping, idx


def load_yaml_text(text: str) -> Any:
    if yaml is not None:
        return yaml.safe_load(text)
    cleaned_lines: list[tuple[int, str]] = []
    for raw_line in text.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        # Strip end-of-line comments outside quotes
        stripped = raw_line.lstrip(" ")
        indent = len(raw_line) - len(stripped)
        cleaned_lines.append((indent, stripped.rstrip()))
    if not cleaned_lines:
        return {}
    parsed, _ = _fallback_parse_yaml_lines(cleaned_lines, 0, cleaned_lines[0][0])
    return parsed


def load_yaml_file(path: Path) -> dict[str, Any]:
    data = load_yaml_text(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected YAML mapping in {path}")
    return data


def _dump_yaml_value(val: Any, indent: int = 0) -> list[str]:
    prefix = " " * indent
    if isinstance(val, dict):
        if not val:
            return [f"{prefix}{{}}"]
        out: list[str] = []
        for k, v in val.items():
            key_str = str(k)
            if isinstance(v, dict) and v:
                out.append(f"{prefix}{key_str}:")
                out.extend(_dump_yaml_value(v, indent + 2))
            elif isinstance(v, list) and v:
                out.append(f"{prefix}{key_str}:")
                out.extend(_dump_yaml_value(v, indent + 2))
            else:
                scalar = _format_yaml_scalar(v)
                out.append(f"{prefix}{key_str}: {scalar}")
        return out
    if isinstance(val, list):
        if not val:
            return [f"{prefix}[]"]
        out = []
        for item in val:
            if isinstance(item, dict) and item:
                keys = list(item.keys())
                first_k = keys[0]
                first_v = item[first_k]
                if isinstance(first_v, (dict, list)) and first_v:
                    out.append(f"{prefix}- {first_k}:")
                    out.extend(_dump_yaml_value(first_v, indent + 4))
                else:
                    out.append(f"{prefix}- {first_k}: {_format_yaml_scalar(first_v)}")
                for rest_k in keys[1:]:
                    rest_v = item[rest_k]
                    if isinstance(rest_v, (dict, list)) and rest_v:
                        out.append(f"{prefix}  {rest_k}:")
                        out.extend(_dump_yaml_value(rest_v, indent + 4))
                    else:
                        out.append(f"{prefix}  {rest_k}: {_format_yaml_scalar(rest_v)}")
            else:
                out.append(f"{prefix}- {_format_yaml_scalar(item)}")
        return out
    return [f"{prefix}{_format_yaml_scalar(val)}"]


def _format_yaml_scalar(val: Any) -> str:
    if val is None:
        return "null"
    if val is True:
        return "true"
    if val is False:
        return "false"
    if isinstance(val, (int, float)):
        return str(val)
    if isinstance(val, list) and not val:
        return "[]"
    if isinstance(val, dict) and not val:
        return "{}"
    s = str(val)
    if (
        not s
        or any(c in s for c in (":", "#", "{", "}", "[", "]", "\n", '"', "'", "&", "*", "?", "|", ">", "!"))
        or s != s.strip()
        or s.lower() in ("true", "false", "null", "yes", "no")
    ):
        return json.dumps(s, ensure_ascii=False)
    return s


def dump_yaml_text(data: Any) -> str:
    if yaml is not None:
        return yaml.safe_dump(data, sort_keys=False, allow_unicode=True)
    return "\n".join(_dump_yaml_value(data, 0)) + "\n"


# ---------------------------------------------------------------------------
# Locale & Route Helpers
# ---------------------------------------------------------------------------

DEFAULT_LOCALE_FLAGS: dict[str, str] = {
    "en": "🇬🇧",
    "pl": "🇵🇱",
    "de": "🇩🇪",
    "es": "🇪🇸",
    "fr": "🇫🇷",
}

SEARCH_LABELS: dict[str, str] = {
    "en": "Search",
    "pl": "Szukaj",
    "de": "Suchen",
    "es": "Buscar",
    "fr": "Rechercher",
}

SWITCHER_UI_KEYS: frozenset[str] = frozenset(
    {
        "language_label",
        "language_menu_label",
        "fallback_notice",
        "fallback_action",
        "unavailable_badge",
        "search_placeholder",
    }
)


def discover_toc_files(toc: list[dict[str, Any]]) -> list[str]:
    """Recursively collect file entries from a MyST project.toc structure."""
    files: list[str] = []
    for item in toc:
        if not isinstance(item, dict):
            continue
        f = item.get("file")
        if isinstance(f, str) and f.strip():
            files.append(f.strip())
        children = item.get("children")
        if isinstance(children, list):
            files.extend(discover_toc_files(children))
    return files


def load_locales_config(root: Path) -> dict[str, Any]:
    locales_path = root / "i18n" / "locales.yml"
    if not locales_path.is_file():
        raise FileNotFoundError(f"Missing locales configuration: {locales_path}")
    return load_yaml_file(locales_path)


def load_glossary(root: Path) -> dict[str, Any]:
    glossary_path = root / "i18n" / "glossary.yml"
    if not glossary_path.is_file():
        raise FileNotFoundError(f"Missing glossary configuration: {glossary_path}")
    return load_yaml_file(glossary_path)


def get_enabled_locales(locales_cfg: dict[str, Any]) -> dict[str, dict[str, Any]]:
    locales = locales_cfg.get("locales", {})
    if not isinstance(locales, dict):
        raise ValueError("i18n/locales.yml 'locales' must be a mapping")
    return {
        code: info
        for code, info in locales.items()
        if isinstance(info, dict) and info.get("enabled", True)
    }


def page_slug_from_rel_path(rel_path: str) -> str:
    """Map a repository source path (e.g. 'README.md', 'projects/linux.md') to its route slug."""
    norm = Path(rel_path).as_posix().lstrip("./")
    if norm.lower() in ("readme.md", "index.md"):
        return ""
    p = Path(norm)
    stem = p.stem
    parent = p.parent.as_posix()
    if parent in ("", "."):
        return stem
    return f"{parent}/{stem}"


def route_url_for_page(prefix: str, slug: str, base_url: str = "") -> str:
    """Build the site-relative route path for a locale prefix and page slug."""
    clean_base = base_url.rstrip("/")
    clean_prefix = ("/" + prefix.strip("/")) if prefix.strip("/") else ""
    if not slug:
        path = f"{clean_base}{clean_prefix}/"
    else:
        path = f"{clean_base}{clean_prefix}/{slug.strip('/')}"
    return path if path.startswith("/") else f"/{path}"


def canonical_url_for_page(domain: str, prefix: str, slug: str) -> str:
    clean_domain = domain.rstrip("/")
    route = route_url_for_page(prefix, slug, base_url="")
    return f"{clean_domain}{route}"


# ---------------------------------------------------------------------------
# Code Block, Directive, Math, Inline Code, Link, and Notebook Integrity Extraction
# ---------------------------------------------------------------------------

CODE_DIRECTIVE_NAMES = frozenset({"code-block", "code", "code-cell", "sourcecode"})
MATH_DIRECTIVE_NAMES = frozenset({"math", "amsmath"})
LOCALIZED_BODY_DIRECTIVES = frozenset({"anywidget"})


def _strip_frontmatter_with_offset(markdown_text: str) -> tuple[str, str, int]:
    """Return (frontmatter_slice, body_slice, body_start_offset) from original markdown_text."""
    front_match = re.match(r"\A(---\r?\n.*?\r?\n---(?:\r?\n|\Z))", markdown_text, re.S)
    if front_match:
        return front_match.group(1), markdown_text[front_match.end() :], front_match.end()
    return "", markdown_text, 0


def _split_directive_options(inner_slice: str) -> tuple[dict[str, str], str]:
    """Split MyST directive options (`:key: val` or `--- ... ---`) from the directive body slice."""
    options: dict[str, str] = {}
    if not inner_slice:
        return options, ""

    # Check YAML-style option block at top of directive
    yaml_opt_match = re.match(r"\A([ \t]*---\r?\n(.*?)\r?\n[ \t]*---(?:\r?\n|\Z))", inner_slice, re.S)
    if yaml_opt_match:
        raw_opts = yaml_opt_match.group(2)
        for line in raw_opts.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                options[k.strip()] = v.strip()
        return options, inner_slice[yaml_opt_match.end() :]

    # Check `:key: value` option lines at top of directive
    lines = inner_slice.splitlines(keepends=True)
    consumed = 0
    for line in lines:
        opt_match = re.match(r"^[ \t]*:([a-zA-Z0-9_.-]+):[ \t]*(.*?)\r?\n?$", line)
        if opt_match:
            options[opt_match.group(1)] = opt_match.group(2).strip()
            consumed += len(line)
        else:
            break
    return options, inner_slice[consumed:]


def _parse_myst_document_slice(body_slice: str) -> dict[str, Any]:
    """Recursively parse a MyST Markdown slice using exact source offsets.

    Supports backtick (```), tilde (~~~), and colon (:::) fences, as well as nested
    container directives (e.g. code blocks or math inside `:::{note}` or ````{dropdown}`).
    """
    lines = body_slice.splitlines(keepends=True)
    n = len(lines)
    offsets: list[int] = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))

    code_blocks: list[dict[str, str]] = []
    math_blocks: list[str] = []
    directives: list[dict[str, Any]] = []
    prose_slices: list[str] = []

    i = 0
    prose_start_line = 0

    while i < n:
        line = lines[i]
        fence_match = re.match(r"^([ \t]*)(`{3,}|~{3,}|:{3,})[ \t]*(.*?)[ \t]*\r?\n?$", line)
        if fence_match:
            _, fence_chars, info_stripped = fence_match.groups()
            fence_char = fence_chars[0]
            fence_len = len(fence_chars)

            # Per CommonMark/MyST spec, backtick fence info strings cannot contain backticks
            if fence_char == "`" and "`" in info_stripped:
                i += 1
                continue

            # Flush preceding prose slice
            if i > prose_start_line:
                prose_slices.append(body_slice[offsets[prose_start_line] : offsets[i]])

            # Locate matching closing fence, accounting for nested same-character colon fences
            j = i + 1
            colon_nesting = 0
            close_line_idx = n
            while j < n:
                cand = lines[j]
                if fence_char == ":":
                    # Check if cand opens a nested colon directive of >= fence_len
                    open_colon = re.match(r"^[ \t]*(:{3,})[ \t]*(\{[a-zA-Z0-9_-]+\}|[a-zA-Z0-9_-]+)", cand)
                    if open_colon and len(open_colon.group(1)) == fence_len:
                        colon_nesting += 1
                        j += 1
                        continue
                close_match = re.match(
                    rf"^[ \t]*{re.escape(fence_char)}{{{fence_len},}}[ \t]*\r?\n?$",
                    cand,
                )
                if close_match:
                    if fence_char == ":" and colon_nesting > 0:
                        colon_nesting -= 1
                        j += 1
                        continue
                    close_line_idx = j
                    break
                j += 1

            raw_inner = body_slice[offsets[i + 1] : offsets[close_line_idx]]
            if raw_inner.endswith("\r\n"):
                exact_inner = raw_inner[:-2]
            elif raw_inner.endswith("\n"):
                exact_inner = raw_inner[:-1]
            else:
                exact_inner = raw_inner

            dir_match = re.match(r"^\{([a-zA-Z0-9_-]+)\}[ \t]*(.*)$", info_stripped)
            colon_dir_match = (
                re.match(r"^([a-zA-Z0-9_-]+)[ \t]*(.*)$", info_stripped)
                if (fence_char == ":" and not dir_match)
                else None
            )

            if dir_match or colon_dir_match or fence_char == ":":
                if dir_match:
                    dir_name = dir_match.group(1).lower()
                    dir_arg = dir_match.group(2).strip()
                elif colon_dir_match:
                    dir_name = colon_dir_match.group(1).lower()
                    dir_arg = colon_dir_match.group(2).strip()
                else:
                    dir_name = "directive"
                    dir_arg = info_stripped

                dir_options, dir_body = _split_directive_options(raw_inner)
                directives.append(
                    {
                        "name": dir_name,
                        "argument": dir_arg,
                        "options": sorted(dir_options.keys()),
                    }
                )

                if dir_name in CODE_DIRECTIVE_NAMES:
                    code_blocks.append(
                        {
                            "info": info_stripped,
                            "content": exact_inner,
                        }
                    )
                elif dir_name in MATH_DIRECTIVE_NAMES:
                    math_blocks.append(dir_body.strip())
                elif dir_name in LOCALIZED_BODY_DIRECTIVES:
                    pass
                else:
                    # Container / admonition directive: recursively parse inner body!
                    nested = _parse_myst_document_slice(dir_body)
                    code_blocks.extend(nested["code_blocks"])
                    math_blocks.extend(nested["math_blocks"])
                    directives.extend(nested["directives"])
                    prose_slices.extend(nested["prose_slices"])
            else:
                # Standard backtick or tilde fenced code block
                code_blocks.append(
                    {
                        "info": info_stripped,
                        "content": exact_inner,
                    }
                )

            i = close_line_idx + 1
            prose_start_line = i
            continue

        i += 1

    if prose_start_line < n:
        prose_slices.append(body_slice[offsets[prose_start_line] : offsets[n]])

    return {
        "code_blocks": code_blocks,
        "math_blocks": math_blocks,
        "directives": directives,
        "prose_slices": prose_slices,
    }


def extract_fenced_code_blocks_from_markdown(markdown_text: str) -> list[dict[str, str]]:
    """Extract all code fenced blocks (```, ~~~, :::) and executable code directives byte-for-byte,
    including code blocks nested inside MyST admonitions and container directives."""
    _, body, _ = _strip_frontmatter_with_offset(markdown_text)
    parsed = _parse_myst_document_slice(body)
    return parsed["code_blocks"]


def _extract_inline_protected_from_prose(prose_slices: list[str]) -> dict[str, list[str]]:
    """Extract display math, inline math, inline code spans, and link targets from non-code prose."""
    display_math: list[str] = []
    inline_math: list[str] = []
    inline_code: list[str] = []
    links: list[str] = []

    for chunk in prose_slices:
        # 1. Extract display math $$ ... $$ before scanning inline code/math
        def _collect_display_math(m: re.Match[str]) -> str:
            display_math.append(m.group(1).strip())
            return " "

        without_display_math = re.sub(r"\$\$(.+?)\$\$", _collect_display_math, chunk, flags=re.S)

        # 2. Extract {math}`...` roles before generic inline code
        def _collect_math_role(m: re.Match[str]) -> str:
            inline_math.append(m.group(2).strip())
            return " "

        without_math_role = re.sub(
            r"\{math\}(`+)(.+?)\1",
            _collect_math_role,
            without_display_math,
            flags=re.S,
        )

        # 3. Extract inline code spans `...` (so $ or []() inside inline code are ignored by math/link scanners)
        def _collect_inline_code(m: re.Match[str]) -> str:
            inline_code.append(m.group(2))
            return " "

        without_inline_code = re.sub(
            r"(`+)([^`]+?)\1",
            _collect_inline_code,
            without_math_role,
        )

        # 4. Extract inline math $...$ (excluding escaped \$)
        for m in re.finditer(r"(?<!\\)\$(?!\s)([^\$\n]+?)(?<!\s|\\)\$", without_inline_code):
            inline_math.append(m.group(1).strip())

        # 5. Extract Markdown link and image targets
        for m in re.finditer(r"(!?\[[^\]]*\])\(([^)]+)\)", without_inline_code):
            links.append(m.group(2).strip())

    return {
        "display_math": display_math,
        "inline_math": inline_math,
        "inline_code": inline_code,
        "links": links,
    }


def extract_math_expressions(markdown_text: str) -> list[str]:
    """Extract all MyST mathematical expressions (directive math, $$...$$, {math}`...`, and $...$)."""
    _, body, _ = _strip_frontmatter_with_offset(markdown_text)
    parsed = _parse_myst_document_slice(body)
    inline_res = _extract_inline_protected_from_prose(parsed["prose_slices"])
    return parsed["math_blocks"] + inline_res["display_math"] + inline_res["inline_math"]


def extract_inline_code_spans(markdown_text: str) -> list[str]:
    """Extract all inline code spans (`...`) outside fenced code and math blocks."""
    _, body, _ = _strip_frontmatter_with_offset(markdown_text)
    parsed = _parse_myst_document_slice(body)
    inline_res = _extract_inline_protected_from_prose(parsed["prose_slices"])
    return inline_res["inline_code"]


def extract_myst_directives(markdown_text: str) -> list[dict[str, Any]]:
    """Extract all MyST directives (name, argument, option keys) across all nesting levels."""
    _, body, _ = _strip_frontmatter_with_offset(markdown_text)
    parsed = _parse_myst_document_slice(body)
    return parsed["directives"]


def extract_markdown_links(markdown_text: str) -> list[str]:
    """Extract all markdown link targets outside fenced code blocks."""
    _, body, _ = _strip_frontmatter_with_offset(markdown_text)
    parsed = _parse_myst_document_slice(body)
    inline_res = _extract_inline_protected_from_prose(parsed["prose_slices"])
    return inline_res["links"]


def extract_code_fingerprint(path: Path) -> dict[str, Any]:
    """Return a deterministic structure of code blocks / cells & metadata for byte-for-byte verification."""
    raw = path.read_text(encoding="utf-8")
    if path.suffix == ".md":
        blocks = extract_fenced_code_blocks_from_markdown(raw)
        return {
            "kind": "markdown",
            "count": len(blocks),
            "blocks": blocks,
            "sha256": sha256_json(blocks),
        }
    if path.suffix == ".ipynb":
        nb = json.loads(raw)
        code_cells = []
        for idx, cell in enumerate(nb.get("cells", [])):
            if cell.get("cell_type") == "code":
                code_cells.append(
                    {
                        "cell_index": idx,
                        "source": "".join(cell.get("source", [])),
                        "metadata": cell.get("metadata", {}),
                    }
                )
        nb_metadata = nb.get("metadata", {})
        payload = {
            "code_cells": code_cells,
            "metadata": nb_metadata,
            "nbformat": nb.get("nbformat"),
            "nbformat_minor": nb.get("nbformat_minor"),
        }
        return {
            "kind": "notebook",
            "count": len(code_cells),
            "payload": payload,
            "sha256": sha256_json(payload),
        }
    raise ValueError(f"Unsupported document type for code fingerprint: {path}")


def split_markdown_sections(markdown_text: str) -> tuple[str, list[dict[str, str]]]:
    """Split a Markdown document into (frontmatter_block, list of sections) for section-level provenance."""
    frontmatter, body, _ = _strip_frontmatter_with_offset(markdown_text)

    lines = body.splitlines(keepends=True)
    sections: list[dict[str, str]] = []
    curr_heading = "__preamble__"
    curr_lines: list[str] = []
    in_fence = False
    fence_char = ""
    fence_len = 0

    for line in lines:
        if not in_fence:
            fm = re.match(r"^([ \t]*)(`{3,}|~{3,}|:{3,})", line)
            if fm:
                in_fence = True
                fence_char = fm.group(2)[0]
                fence_len = len(fm.group(2))
                curr_lines.append(line)
                continue
            hm = re.match(r"^(#{1,6})\s+(.+?)\s*$", line.strip())
            if hm:
                if curr_lines:
                    content = "".join(curr_lines)
                    sections.append(
                        {
                            "heading": curr_heading,
                            "content": content,
                            "sha256": sha256_text(content.strip()),
                        }
                    )
                curr_heading = hm.group(2).strip()
                curr_lines = [line]
                continue
        else:
            if re.match(rf"^[ \t]*{re.escape(fence_char)}{{{fence_len},}}[ \t]*\r?\n?$", line):
                in_fence = False
        curr_lines.append(line)

    if curr_lines:
        content = "".join(curr_lines)
        sections.append(
            {
                "heading": curr_heading,
                "content": content,
                "sha256": sha256_text(content.strip()),
            }
        )

    return frontmatter, sections
