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
        return hashlib.file_digest(f, "sha256").hexdigest()


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
# Code Block, Directive, Link, and Notebook Integrity Extraction
# ---------------------------------------------------------------------------


def extract_fenced_code_blocks_from_markdown(markdown_text: str) -> list[dict[str, str]]:
    """Extract all code fenced blocks and executable code directives from Markdown byte-for-byte."""
    front_match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", markdown_text, re.S)
    body = markdown_text[front_match.end() :] if front_match else markdown_text
    lines = body.splitlines()
    n = len(lines)
    i = 0
    blocks: list[dict[str, str]] = []

    while i < n:
        line = lines[i]
        fence_match = re.match(r"^(\s*)(`{3,}|:{3,})\s*(.*)$", line)
        if fence_match:
            _, fence_chars, info = fence_match.groups()
            fence_char = fence_chars[0]
            fence_len = len(fence_chars)
            info_stripped = info.strip()
            i += 1
            block_lines: list[str] = []
            while i < n:
                if re.match(rf"^\s*{re.escape(fence_char)}{{{fence_len},}}\s*$", lines[i]):
                    i += 1
                    break
                block_lines.append(lines[i])
                i += 1

            dir_match = re.match(r"^\{([a-zA-Z0-9_-]+)\}\s*(.*)$", info_stripped)
            if dir_match or fence_char == ":":
                dir_name = (
                    dir_match.group(1).lower()
                    if dir_match
                    else (info_stripped.split()[0].lower() if info_stripped else "directive")
                )
                if dir_name in ("code-block", "code", "code-cell", "sourcecode"):
                    blocks.append(
                        {
                            "info": info_stripped,
                            "content": "\n".join(block_lines),
                        }
                    )
            else:
                blocks.append(
                    {
                        "info": info_stripped,
                        "content": "\n".join(block_lines),
                    }
                )
            continue
        i += 1

    return blocks


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


def extract_markdown_links(markdown_text: str) -> list[str]:
    """Extract all markdown link targets outside fenced code blocks."""
    front_match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", markdown_text, re.S)
    body = markdown_text[front_match.end() :] if front_match else markdown_text
    lines = body.splitlines()
    n = len(lines)
    i = 0
    non_code_lines: list[str] = []
    while i < n:
        line = lines[i]
        fence_match = re.match(r"^(\s*)(`{3,})\s*(.*)$", line)
        if fence_match:
            fence_len = len(fence_match.group(2))
            i += 1
            while i < n and not re.match(rf"^\s*`{{{fence_len},}}\s*$", lines[i]):
                i += 1
            i += 1
            continue
        non_code_lines.append(line)
        i += 1
    prose = "\n".join(non_code_lines)
    targets = [m.group(2).strip() for m in re.finditer(r"(!?\[[^\]]*\])\(([^)]+)\)", prose)]
    return targets


def split_markdown_sections(markdown_text: str) -> tuple[str, list[dict[str, str]]]:
    """Split a Markdown document into (frontmatter_block, list of sections) for section-level provenance."""
    front_match = re.match(r"\A(---\r?\n.*?\r?\n---(?:\r?\n|\Z))", markdown_text, re.S)
    frontmatter = front_match.group(1) if front_match else ""
    body = markdown_text[front_match.end() :] if front_match else markdown_text

    lines = body.splitlines(keepends=True)
    sections: list[dict[str, str]] = []
    curr_heading = "__preamble__"
    curr_lines: list[str] = []
    in_fence = False
    fence_char = ""
    fence_len = 0

    for line in lines:
        if not in_fence:
            fm = re.match(r"^(\s*)(`{3,}|:{3,})", line)
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
            if re.match(rf"^\s*{re.escape(fence_char)}{{{fence_len},}}\s*$", line):
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
