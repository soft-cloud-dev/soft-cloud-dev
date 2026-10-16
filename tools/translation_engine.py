"""
translation_engine.py
---------------------
Pure (network-free) building blocks for translation updates:

* protect/restore: extract content that must never reach the model, translate the
  remainder, reconstruct, and verify every placeholder survived exactly once.
* section/cell reconciliation: decide, per section, whether to keep the existing
  localized text, translate it, or report a conflict (English changed *and* a human
  edited the same localized section). Human edits are never overwritten silently.
* dependency fingerprints for included files.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Callable

from i18n_utils import sha256_file, sha256_json

TOKEN_FMT = "\u27e6SC{n}\u27e7"
TOKEN_RE = re.compile(r"\u27e6SC(\d+)\u27e7")

FENCE_RE = re.compile(r"^(\s*)(`{3,}|~{3,})(.*)$")
DIRECTIVE_INFO_RE = re.compile(r"^\{([\w:.-]+)\}")
# Directives whose bodies are code/data/execution input, never prose.
PROTECTED_DIRECTIVES = frozenset(
    {
        "code-cell", "code-block", "code", "sourcecode", "literalinclude", "include",
        "anywidget", "math", "mermaid", "raw", "csv-table", "list-table-data",
    }
)
OPTION_LINE_RE = re.compile(r"^\s*:[\w-]+:(?:\s.*)?$")
DISPLAY_MATH_RE = re.compile(r"\$\$.+?\$\$", re.DOTALL)
INLINE_CODE_RE = re.compile(r"(`+)(?!`)(.+?)(?<!`)\1(?!`)")
INLINE_MATH_RE = re.compile(r"(?<![\\$\w])\$(?![\s$])([^$\n]+?)(?<![\s\\])\$(?![\w$])")
LINK_TARGET_RE = re.compile(r"(\]\()([^)\s]+)((?:\s+[^)]*)?\))")
AUTOLINK_RE = re.compile(r"<(?:https?://|mailto:)[^>\s]+>")
INCLUDE_RE = re.compile(
    r"^\s*(?:`{3,}|:{3,}|~{3,})\s*\{(?:include|literalinclude)\}\s+(\S+)", re.MULTILINE
)


class ProtectionError(ValueError):
    """Raised when a translated text lost, duplicated, or invented a placeholder."""


def protect_markdown(text: str) -> tuple[str, list[str]]:
    """Replace protected spans with opaque tokens. Returns (masked_text, originals)."""
    originals: list[str] = []

    def stash(original: str) -> str:
        originals.append(original)
        return TOKEN_FMT.format(n=len(originals) - 1)

    lines = text.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    while i < len(lines):
        raw = lines[i].rstrip("\r\n")
        m = FENCE_RE.match(raw)
        if m:
            fence, info = m.group(2), m.group(3).strip()
            dm = DIRECTIVE_INFO_RE.match(info)
            if dm is None or dm.group(1) in PROTECTED_DIRECTIVES:
                close_re = re.compile(r"^\s*" + re.escape(fence[0]) + "{" + str(len(fence)) + r",}\s*$")
                j = i + 1
                while j < len(lines) and not close_re.match(lines[j].rstrip("\r\n")):
                    j += 1
                end = min(j + 1, len(lines))
                block = "".join(lines[i:end])
                body = block.rstrip("\r\n")
                out.append(stash(body) + block[len(body):])
                i = end
                continue
            # Prose-bearing directive (note, admonition...): keep scanning inside it.
            out.append(lines[i])
            i += 1
            continue
        if OPTION_LINE_RE.match(raw):
            out.append(stash(raw) + lines[i][len(raw):])
            i += 1
            continue
        out.append(lines[i])
        i += 1

    masked = "".join(out)
    masked = DISPLAY_MATH_RE.sub(lambda mm: stash(mm.group(0)), masked)
    masked = INLINE_CODE_RE.sub(lambda mm: stash(mm.group(0)), masked)
    masked = INLINE_MATH_RE.sub(lambda mm: stash(mm.group(0)), masked)
    masked = AUTOLINK_RE.sub(lambda mm: stash(mm.group(0)), masked)
    masked = LINK_TARGET_RE.sub(lambda mm: mm.group(1) + stash(mm.group(2)) + mm.group(3), masked)
    return masked, originals


def restore_markdown(translated: str, originals: list[str]) -> str:
    """Reinsert protected spans; every token must appear exactly once."""
    found = [int(n) for n in TOKEN_RE.findall(translated)]
    expected = list(range(len(originals)))
    if sorted(found) != expected:
        missing = sorted(set(expected) - set(found))
        extra = sorted({n for n in found if n not in set(expected) or found.count(n) > 1})
        raise ProtectionError(f"placeholder mismatch (missing={missing[:5]}, unexpected/duplicated={extra[:5]})")
    return TOKEN_RE.sub(lambda mm: originals[int(mm.group(1))], translated)


def translate_protected(
    text: str,
    translate_fn: Callable[[str], str],
    max_attempts: int = 3,
) -> str:
    """Mask protected content, translate only the remainder, rebuild, and verify."""
    if not text.strip():
        return text
    masked, originals = protect_markdown(text)
    if not originals and not masked.strip():
        return text
    last: Exception | None = None
    for _ in range(max_attempts):
        try:
            return restore_markdown(translate_fn(masked), originals)
        except ProtectionError as exc:
            last = exc
    raise ProtectionError(f"model did not preserve protected content after {max_attempts} attempts: {last}")


# --------------------------------------------------------------------------- reconciliation


def decide_sections(
    en_items: list[dict[str, str]],
    loc_items: list[dict[str, str]],
    old_records: list[dict[str, Any]],
    force_all: bool = False,
) -> tuple[list[dict[str, Any]], list[str], list[int]]:
    """
    Decide per English item: keep the localized text or translate it.

    en_items/loc_items: dicts with heading, content, sha256.
    old_records: previous provenance section records (source_heading, source_sha256, translated_sha256),
    aligned positionally with loc_items. Returns (decisions, conflicts, preserved_edit_positions).
    Raises ValueError when the structure cannot be mapped confidently.
    """
    if len(old_records) != len(loc_items):
        raise ValueError("localized structure does not match recorded provenance")

    unused = set(range(len(old_records)))
    decisions: list[dict[str, Any]] = []
    conflicts: list[str] = []
    preserved: list[int] = []

    def edited(pos: int) -> bool:
        return old_records[pos].get("translated_sha256") != loc_items[pos]["sha256"]

    for en_pos, en in enumerate(en_items):
        match = None
        if not force_all:
            match = next(
                (p for p in sorted(unused) if old_records[p].get("source_sha256") == en["sha256"]), None
            )
        if match is not None:
            unused.discard(match)
            if edited(match):
                preserved.append(match)
            decisions.append({"action": "keep", "content": loc_items[match]["content"]})
            continue
        same_heading = [p for p in sorted(unused) if old_records[p].get("source_heading") == en["heading"]]
        if len(same_heading) == 1:
            pos = same_heading[0]
            unused.discard(pos)
            if edited(pos):
                conflicts.append(
                    f"section {en['heading']!r}: English changed and the localized section was edited"
                )
                decisions.append({"action": "conflict", "content": en["content"]})
            else:
                decisions.append({"action": "translate", "content": en["content"]})
            continue
        decisions.append({"action": "translate", "content": en["content"]})
    return decisions, conflicts, preserved


# --------------------------------------------------------------------------- dependencies


def document_dependencies(root: Path, rel_doc: str) -> dict[str, str]:
    """Return {relative_path: sha256} for files a Markdown document includes."""
    path = root / rel_doc
    if path.suffix != ".md" or not path.is_file():
        return {}
    deps: dict[str, str] = {}
    root_resolved = root.resolve()
    for target in INCLUDE_RE.findall(path.read_text(encoding="utf-8")):
        dep = (path.parent / target).resolve()
        try:
            rel = dep.relative_to(root_resolved).as_posix()
        except ValueError:
            continue  # never follow includes outside the repository
        if dep.is_file():
            deps[rel] = sha256_file(dep)
    return dict(sorted(deps.items()))


def dependency_fingerprint(root: Path, rel_doc: str) -> str:
    return sha256_json(document_dependencies(root, rel_doc))
