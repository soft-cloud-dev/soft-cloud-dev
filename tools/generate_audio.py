#!/usr/bin/env python3
"""Build-time AI audio narration generator and validator for SoftCloud Documentation.

Implements:
- Document extraction into an ordered intermediate representation with stable IDs and hashes
- AI code explanation generation and content-addressed caching via Gemini API
- Narration transcript assembly divided by logical sections and paragraph boundaries
- Speech synthesis via Gemini 3.8 Flash TTS (`gemini-3.8-flash-tts`) and MP3 transcoding
- Strict fail-closed validation of credentials, models, rate limits, checksums, and manifests
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore[import-untyped]
except ImportError:
    yaml = None

try:
    import mistune  # type: ignore[import-untyped]
except ImportError:
    mistune = None


# ---------------------------------------------------------------------------
# Configuration & Constants
# ---------------------------------------------------------------------------

SCHEMA_VERSION = "1.0.0"
DEFAULT_LOCALE = "en"
DEFAULT_TEXT_MODEL = "gemini-3.8-flash"
DEFAULT_TTS_MODEL = "gemini-3.8-flash-tts"
DEFAULT_VOICE_NAME = "Kore"
DEFAULT_SAMPLE_RATE = 24000
DEFAULT_MP3_BITRATE = "64k"
DEFAULT_MAX_CHUNK_CHARS = 1800
GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta"

LOCALE_SPOKEN_LANGUAGES: dict[str, str] = {
    "en": "English",
    "pl": "Polish (język polski)",
    "de": "German (Deutsch)",
    "es": "Spanish (español)",
    "fr": "French (français)",
}

CODE_SUMMARY_SYSTEM_PROMPT = (
    "You are a technical documentation narrator for the Software Cloud platform. "
    "Provide a concise, technically accurate spoken explanation of the provided code block "
    "suitable for audio narration. Describe:\n"
    "1. Purpose and functionality.\n"
    "2. Significant inputs, outputs and dependencies.\n"
    "3. Important operations and implementation decisions.\n"
    "4. Material side effects, limitations or risks.\n"
    "Rules:\n"
    "- Do NOT invent behavior unsupported by the code.\n"
    "- Do NOT read the code character-by-character or line-by-line.\n"
    "- Write in clear, natural spoken prose without Markdown formatting, bullet points, or code fences."
)


def build_code_summary_system_prompt(locale: str = DEFAULT_LOCALE) -> str:
    norm = (locale or DEFAULT_LOCALE).strip().lower()
    if norm == "en":
        return CODE_SUMMARY_SYSTEM_PROMPT
    lang_label = LOCALE_SPOKEN_LANGUAGES.get(norm, norm)
    return (
        f"{CODE_SUMMARY_SYSTEM_PROMPT}\n"
        f"- Write the entire spoken explanation in {lang_label} matching document locale '{norm}'."
    )


class NarrationError(Exception):
    """Raised when any fail-closed narration requirement or validation fails."""


@dataclass(frozen=True)
class NarrationConfig:
    schema_version: str = SCHEMA_VERSION
    locale: str = DEFAULT_LOCALE
    text_model: str = DEFAULT_TEXT_MODEL
    text_temperature: float = 0.0
    text_system_prompt: str = CODE_SUMMARY_SYSTEM_PROMPT
    tts_model: str = DEFAULT_TTS_MODEL
    voice_name: str = DEFAULT_VOICE_NAME
    audio_format: str = "mp3"
    sample_rate: int = DEFAULT_SAMPLE_RATE
    mp3_bitrate: str = DEFAULT_MP3_BITRATE
    max_chunk_chars: int = DEFAULT_MAX_CHUNK_CHARS

    def text_config_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "locale": self.locale,
            "text_model": self.text_model,
            "text_temperature": self.text_temperature,
            "text_system_prompt": self.text_system_prompt,
        }

    def tts_config_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "locale": self.locale,
            "tts_model": self.tts_model,
            "voice_name": self.voice_name,
            "audio_format": self.audio_format,
            "sample_rate": self.sample_rate,
            "mp3_bitrate": self.mp3_bitrate,
        }

    def full_config_dict(self) -> dict[str, Any]:
        return {
            **self.text_config_dict(),
            **self.tts_config_dict(),
            "max_chunk_chars": self.max_chunk_chars,
        }

    def text_config_hash(self) -> str:
        return sha256_json(self.text_config_dict())

    def tts_config_hash(self) -> str:
        return sha256_json(self.tts_config_dict())

    def config_hash(self) -> str:
        return sha256_json(self.full_config_dict())


# ---------------------------------------------------------------------------
# Cryptographic & Utility Helpers
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


def atomic_write_json(target: Path, obj: Any) -> None:
    content = json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    atomic_write_bytes(target, content.encode("utf-8"))


def slugify_anchor(heading_text: str) -> str:
    cleaned = re.sub(r"[`*_~\[\]()]", "", heading_text).strip().lower()
    # Transliterate common Latin characters that NFKD does not decompose to ASCII
    translit_map = str.maketrans(
        {
            "ł": "l",
            "ß": "ss",
            "œ": "oe",
            "æ": "ae",
            "ø": "o",
            "đ": "d",
        }
    )
    cleaned = cleaned.translate(translit_map)
    normalized = unicodedata.normalize("NFKD", cleaned).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", normalized).strip("-")
    return slug or "section"


def logical_rel_path(rel_path: str) -> str:
    """Strip leading i18n/<locale>/ prefix from a localized source path."""
    norm = Path(rel_path).as_posix().lstrip("./")
    m = re.match(r"^i18n/[a-zA-Z0-9_-]+/(.+)$", norm)
    if m:
        return m.group(1)
    return norm


def page_id_from_path(rel_path: str) -> str:
    logical = logical_rel_path(rel_path)
    p = Path(logical)
    stem_parts = list(p.parent.parts) + [p.stem]
    cleaned = [p for p in stem_parts if p and p != "."]
    return "-".join(cleaned).lower()


# ---------------------------------------------------------------------------
# Minimal YAML Loader Fallback (when PyYAML is absent in bare system python)
# ---------------------------------------------------------------------------


def load_yaml_file(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if yaml is not None:
        loaded = yaml.safe_load(text)
        if not isinstance(loaded, dict):
            raise NarrationError(f"Expected YAML mapping in {path}")
        return loaded
    # Fallback parser for myst.yml toc extraction
    files: list[dict[str, Any]] = []
    for match in re.finditer(r"^\s*-\s*file:\s*(\S+)\s*$", text, re.M):
        files.append({"file": match.group(1)})
    return {"version": 1, "project": {"toc": files}}


# ---------------------------------------------------------------------------
# 3.1. Document Extraction & Intermediate Representation
# ---------------------------------------------------------------------------


@dataclass
class ExtractedElement:
    element_id: str
    kind: str  # heading, paragraph, list, table, directive, code_block, cell_code, cell_output
    section_anchor: str
    section_title: str
    text: str  # For verbatim elements: clean spoken text; for code_block: raw code
    source_hash: str
    language: str = ""
    heading_level: int = 0
    directive_name: str = ""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "element_id": self.element_id,
            "kind": self.kind,
            "section_anchor": self.section_anchor,
            "section_title": self.section_title,
            "text": self.text,
            "source_hash": self.source_hash,
        }
        if self.language:
            d["language"] = self.language
        if self.heading_level:
            d["heading_level"] = self.heading_level
        if self.directive_name:
            d["directive_name"] = self.directive_name
        return d


@dataclass
class ExtractedDocument:
    locale: str
    page_id: str
    logical_source_path: str
    source_path: str
    source_file_sha256: str
    page_source_hash: str
    elements: list[ExtractedElement]

    def to_dict(self) -> dict[str, Any]:
        return {
            "locale": self.locale,
            "page_id": self.page_id,
            "logical_source_path": self.logical_source_path,
            "source_path": self.source_path,
            "source_file_sha256": self.source_file_sha256,
            "page_source_hash": self.page_source_hash,
            "elements": [e.to_dict() for e in self.elements],
        }


def clean_inline_markdown(text: str) -> str:
    """Preserve original textual content and inline code identifiers while stripping structural Markdown."""
    # Remove HTML comments
    s = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    # Replace image syntax ![alt](url) -> alt
    s = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", s)
    # Replace hyperlinks [label](url) -> label (handling nested bold/code inside label)
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
    # Replace MyST roles {role}`content` -> content
    s = re.sub(r"\{[a-zA-Z0-9_-]+\}`([^`]+)`", r"\1", s)
    # Preserve inline code content without backticks
    s = re.sub(r"`([^`]+)`", r"\1", s)
    # Strip bold/italic markers (**text**, __text__, *text*, _text_)
    s = re.sub(r"\*\*([^*]+)\*\*", r"\1", s)
    s = re.sub(r"__([^_]+)__", r"\1", s)
    s = re.sub(r"(?<!\w)\*([^*]+)\*(?!\w)", r"\1", s)
    s = re.sub(r"(?<!\w)_([^_]+)_(?!\w)", r"\1", s)
    # Collapse whitespace
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\s*\n\s*", " ", s)
    return s.strip()


def render_inline_ast_children(children: list[dict[str, Any]]) -> str:
    """Extract verbatim text from mistune AST inline nodes."""
    parts: list[str] = []
    for node in children:
        ntype = node.get("type", "")
        if ntype == "text":
            parts.append(node.get("raw", ""))
        elif ntype == "codespan":
            parts.append(node.get("raw", ""))
        elif ntype in ("strong", "emphasis", "link", "image"):
            parts.append(render_inline_ast_children(node.get("children", [])))
        elif ntype in ("softbreak", "linebreak"):
            parts.append(" ")
        elif "children" in node:
            parts.append(render_inline_ast_children(node["children"]))
        elif "raw" in node:
            parts.append(clean_inline_markdown(node["raw"]))
    joined = "".join(parts)
    return clean_inline_markdown(joined)


def parse_markdown_table_lines(lines: list[str]) -> str:
    """Read textual contents of a Markdown table in logical row/column order."""
    rows: list[list[str]] = []
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        inner = stripped.strip("|")
        cells = [c.strip() for c in inner.split("|")]
        # Check if separator row (e.g. --- | :--- | ---:)
        if all(re.match(r"^:?-{2,}:?$", c) for c in cells if c):
            continue
        cleaned_cells = [clean_inline_markdown(c) for c in cells]
        rows.append(cleaned_cells)

    if not rows:
        return ""
    headers = rows[0]
    body = rows[1:]
    narration_parts: list[str] = []
    if not body:
        return ". ".join(c for c in headers if c)
    for row in body:
        row_items: list[str] = []
        for idx, cell in enumerate(row):
            if not cell:
                continue
            header = headers[idx] if idx < len(headers) and headers[idx] else ""
            if header:
                row_items.append(f"{header}: {cell}")
            else:
                row_items.append(cell)
        if row_items:
            row_str = "; ".join(row_items)
            if not row_str.endswith((".", "!", "?")):
                row_str += "."
            narration_parts.append(row_str)
    return " ".join(narration_parts)


def extract_markdown_blocks(markdown_text: str) -> list[dict[str, Any]]:
    """Parse MyST Markdown into an ordered list of structural block dictionaries.

    Uses mistune AST when available (with table plugin) and handles MyST directives,
    tables, lists, headings, paragraphs, and fenced code blocks accurately.
    """
    # Strip YAML frontmatter
    front_match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", markdown_text, re.S)
    body = markdown_text[front_match.end() :] if front_match else markdown_text

    lines = body.splitlines()
    n = len(lines)
    i = 0
    raw_blocks: list[dict[str, Any]] = []

    while i < n:
        line = lines[i]
        stripped = line.strip()

        # Skip empty lines and thematic breaks (---, ***, ___)
        if not stripped or re.match(r"^(?:-{3,}|\*{3,}|_{3,})$", stripped):
            i += 1
            continue

        # Fenced block or MyST directive (``` or :::)
        fence_match = re.match(r"^(\s*)(`{3,}|:{3,})\s*(.*)$", line)
        if fence_match:
            indent, fence_chars, info = fence_match.groups()
            fence_char = fence_chars[0]
            fence_len = len(fence_chars)
            info_stripped = info.strip()
            i += 1
            block_lines: list[str] = []
            while i < n:
                close_match = re.match(
                    rf"^\s*{re.escape(fence_char)}{{{fence_len},}}\s*$", lines[i]
                )
                if close_match:
                    i += 1
                    break
                block_lines.append(lines[i])
                i += 1

            # Check if MyST directive: e.g. ```{note} or :::{admonition} Title
            dir_match = re.match(r"^\{([a-zA-Z0-9_-]+)\}\s*(.*)$", info_stripped)
            if dir_match or fence_char == ":":
                dir_name = dir_match.group(1).lower() if dir_match else info_stripped.split()[0].lower() if info_stripped else "directive"
                dir_arg = dir_match.group(2).strip() if dir_match else ""
                # Strip directive option lines (:option: value) at start of block
                content_start = 0
                while content_start < len(block_lines) and re.match(
                    r"^\s*:[a-zA-Z0-9_-]+:\s*.*$", block_lines[content_start]
                ):
                    content_start += 1
                inner_content = "\n".join(block_lines[content_start:]).strip()
                if dir_name in ("code-block", "code", "code-cell", "sourcecode"):
                    lang = dir_arg or "python"
                    raw_blocks.append(
                        {
                            "kind": "code_block",
                            "language": lang,
                            "text": inner_content,
                        }
                    )
                elif dir_name in ("toctree", "anywidget", "audio-player"):
                    # Non-narratable structural or player directives
                    continue
                else:
                    # Narrate relevant rendered content inside directive
                    sub_blocks = extract_markdown_blocks(inner_content)
                    spoken_parts: list[str] = []
                    if dir_arg:
                        spoken_parts.append(clean_inline_markdown(dir_arg))
                    for sb in sub_blocks:
                        if sb["kind"] != "code_block" and sb.get("text"):
                            spoken_parts.append(sb["text"])
                    combined = ". ".join(p.rstrip(".") for p in spoken_parts if p)
                    if combined:
                        if not combined.endswith((".", "!", "?")):
                            combined += "."
                        raw_blocks.append(
                            {
                                "kind": "directive",
                                "directive_name": dir_name,
                                "text": combined,
                            }
                        )
            else:
                # Standard fenced code block
                lang = info_stripped.split()[0] if info_stripped else "text"
                raw_blocks.append(
                    {
                        "kind": "code_block",
                        "language": lang,
                        "text": "\n".join(block_lines),
                    }
                )
            continue

        # ATX Heading (# Heading)
        heading_match = re.match(r"^(#{1,6})\s+(.+?)\s*#*$", stripped)
        if heading_match:
            level = len(heading_match.group(1))
            raw_title = heading_match.group(2)
            cleaned_title = clean_inline_markdown(raw_title)
            raw_blocks.append(
                {
                    "kind": "heading",
                    "heading_level": level,
                    "text": cleaned_title,
                }
            )
            i += 1
            continue

        # Table block (starts with |)
        if stripped.startswith("|"):
            table_lines: list[str] = []
            while i < n and lines[i].strip().startswith("|"):
                table_lines.append(lines[i])
                i += 1
            table_text = parse_markdown_table_lines(table_lines)
            if table_text:
                raw_blocks.append(
                    {
                        "kind": "table",
                        "text": table_text,
                    }
                )
            continue

        # List block (unordered -, *, + or ordered 1., 2.)
        list_match = re.match(r"^(\s*)(?:[-*+]|\d+[.)])\s+(.*)$", line)
        if list_match:
            items: list[str] = []
            while i < n:
                curr_line = lines[i]
                curr_stripped = curr_line.strip()
                if not curr_stripped:
                    # Look ahead to see if list continues after blank line
                    if i + 1 < n and re.match(r"^\s*(?:[-*+]|\d+[.)])\s+", lines[i + 1]):
                        i += 1
                        continue
                    break
                item_m = re.match(r"^\s*(?:[-*+]|\d+[.)])\s+(.*)$", curr_line)
                if item_m:
                    items.append(item_m.group(1).strip())
                    i += 1
                elif items and (curr_line.startswith("  ") or curr_line.startswith("\t")):
                    items[-1] += " " + curr_stripped
                    i += 1
                else:
                    break
            cleaned_items: list[str] = []
            for item in items:
                c_item = clean_inline_markdown(item)
                if c_item:
                    if not c_item.endswith((".", "!", "?", ":", ";")):
                        c_item += "."
                    cleaned_items.append(c_item)
            if cleaned_items:
                raw_blocks.append(
                    {
                        "kind": "list",
                        "text": " ".join(cleaned_items),
                    }
                )
            continue

        # Paragraph (accumulate until blank line or structural block start)
        para_lines: list[str] = []
        while i < n:
            curr = lines[i]
            curr_s = curr.strip()
            if (
                not curr_s
                or re.match(r"^(?:-{3,}|\*{3,}|_{3,})$", curr_s)
                or re.match(r"^(\s*)(`{3,}|:{3,})", curr)
                or re.match(r"^#{1,6}\s+", curr_s)
                or curr_s.startswith("|")
                or re.match(r"^\s*(?:[-*+]|\d+[.)])\s+", curr)
            ):
                break
            para_lines.append(curr_s)
            i += 1

        if para_lines:
            joined_para = " ".join(para_lines)
            if mistune is not None:
                md_ast = mistune.create_markdown(renderer="ast")
                ast_nodes = md_ast(joined_para)
                para_text = ""
                for node in ast_nodes:
                    if "children" in node:
                        para_text += render_inline_ast_children(node["children"]) + " "
                para_text = para_text.strip() or clean_inline_markdown(joined_para)
            else:
                para_text = clean_inline_markdown(joined_para)
            if para_text:
                raw_blocks.append(
                    {
                        "kind": "paragraph",
                        "text": para_text,
                    }
                )

    return raw_blocks


def extract_document(
    source_path: Path,
    root: Path,
    locale: str = DEFAULT_LOCALE,
) -> ExtractedDocument:
    """Extract a MyST Markdown or Jupyter Notebook file into an ordered ExtractedDocument."""
    norm_locale = (locale or DEFAULT_LOCALE).strip().lower()
    rel_path = source_path.resolve().relative_to(root.resolve()).as_posix()
    logical_path = logical_rel_path(rel_path)
    page_id = page_id_from_path(rel_path)
    raw_bytes = source_path.read_bytes()
    file_sha256 = sha256_bytes(raw_bytes)
    text_content = raw_bytes.decode("utf-8")

    raw_blocks: list[dict[str, Any]] = []
    if source_path.suffix == ".md":
        raw_blocks = extract_markdown_blocks(text_content)
    elif source_path.suffix == ".ipynb":
        nb = json.loads(text_content)
        for cell in nb.get("cells", []):
            ctype = cell.get("cell_type")
            source_str = "".join(cell.get("source", []))
            if not source_str.strip():
                continue
            if ctype == "markdown":
                raw_blocks.extend(extract_markdown_blocks(source_str))
            elif ctype == "code":
                raw_blocks.append(
                    {
                        "kind": "code_block",
                        "language": "python",
                        "text": source_str.strip(),
                    }
                )
    else:
        raise NarrationError(f"Unsupported document extension: {source_path}")

    elements: list[ExtractedElement] = []
    current_anchor = "top"
    current_title = "Introduction"
    anchor_counts: dict[str, int] = {}

    for idx, blk in enumerate(raw_blocks, start=1):
        kind = blk["kind"]
        text = blk["text"]
        lang = blk.get("language", "")
        level = blk.get("heading_level", 0)
        dir_name = blk.get("directive_name", "")

        if kind == "heading":
            base_anchor = slugify_anchor(text)
            count = anchor_counts.get(base_anchor, 0)
            anchor_counts[base_anchor] = count + 1
            current_anchor = base_anchor if count == 0 else f"{base_anchor}-{count}"
            current_title = text

        element_id = f"el-{idx:04d}-{kind}"
        element_hash = sha256_json(
            {
                "kind": kind,
                "text": text,
                "language": lang,
                "heading_level": level,
                "directive_name": dir_name,
            }
        )
        elements.append(
            ExtractedElement(
                element_id=element_id,
                kind=kind,
                section_anchor=current_anchor,
                section_title=current_title,
                text=text,
                source_hash=element_hash,
                language=lang,
                heading_level=level,
                directive_name=dir_name,
            )
        )

    if not elements:
        raise NarrationError(f"Document extraction yielded zero elements for {rel_path}")

    page_source_hash = sha256_json(
        {
            "locale": norm_locale,
            "source_path": rel_path,
            "elements": [
                {
                    "element_id": e.element_id,
                    "kind": e.kind,
                    "section_anchor": e.section_anchor,
                    "text": e.text,
                    "source_hash": e.source_hash,
                    "language": e.language,
                    "heading_level": e.heading_level,
                    "directive_name": e.directive_name,
                }
                for e in elements
            ],
        }
    )

    return ExtractedDocument(
        locale=norm_locale,
        page_id=page_id,
        logical_source_path=logical_path,
        source_path=rel_path,
        source_file_sha256=file_sha256,
        page_source_hash=page_source_hash,
        elements=elements,
    )


# ---------------------------------------------------------------------------
# Gemini REST API Client (Standard Library HTTP with Bounded Exponential Backoff)
# ---------------------------------------------------------------------------


class GeminiClient:
    """Standard-library HTTPS client for Gemini text generation and TTS synthesis."""

    def __init__(
        self,
        api_key: str,
        api_base: str = GEMINI_API_BASE,
        max_retries: int = 4,
        base_delay: float = 1.5,
        timeout: float = 90.0,
    ) -> None:
        self.api_key = api_key.strip()
        self.api_base = api_base.rstrip("/")
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.timeout = timeout
        self._verified_models: set[str] = set()

    @staticmethod
    def validate_api_key_format(api_key: str | None) -> str:
        if not api_key or not api_key.strip():
            raise NarrationError(
                "Missing or empty GEMINI_API_KEY credential. "
                "Provide a valid GEMINI_API_KEY or run with --offline when all artifacts are already cached and valid."
            )
        cleaned = api_key.strip()
        if len(cleaned) < 16 or any(c.isspace() for c in cleaned):
            raise NarrationError("Malformed GEMINI_API_KEY credential.")
        return cleaned

    def _request_json(
        self,
        method: str,
        endpoint: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = f"{self.api_base}/{endpoint.lstrip('/')}"
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key,
        }
        body = json.dumps(payload).encode("utf-8") if payload is not None else None

        for attempt in range(self.max_retries + 1):
            req = urllib.request.Request(url, data=body, headers=headers, method=method)
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    raw = resp.read().decode("utf-8")
                    data = json.loads(raw)
                    if not isinstance(data, dict):
                        raise NarrationError(f"Malformed JSON response from {endpoint}")
                    return data
            except urllib.error.HTTPError as exc:
                status = exc.code
                err_body = ""
                try:
                    err_body = exc.read().decode("utf-8", errors="replace")
                except Exception:
                    pass

                # Rate limit / quota / temporary capacity (429, 503)
                if status in (429, 503):
                    if attempt >= self.max_retries:
                        raise NarrationError(
                            f"Gemini API rate-limit or capacity exhaustion (HTTP {status}) after "
                            f"{self.max_retries} retries on {endpoint}: {err_body[:300]}"
                        ) from exc
                    retry_after = exc.headers.get("Retry-After") if exc.headers else None
                    delay = self.base_delay * (2**attempt)
                    if retry_after:
                        try:
                            delay = max(delay, float(retry_after))
                        except ValueError:
                            pass
                    time.sleep(min(delay, 30.0))
                    continue

                if status in (401, 403):
                    raise NarrationError(
                        f"Gemini API authentication or permission error (HTTP {status}) on {endpoint}: {err_body[:300]}"
                    ) from exc

                if status == 404:
                    raise NarrationError(
                        f"Gemini API model or endpoint unavailable (HTTP 404) on {endpoint}: {err_body[:300]}"
                    ) from exc

                raise NarrationError(
                    f"Gemini API error (HTTP {status}) on {endpoint}: {err_body[:300]}"
                ) from exc
            except urllib.error.URLError as exc:
                if attempt >= self.max_retries:
                    raise NarrationError(
                        f"Network failure communicating with Gemini API ({endpoint}) after "
                        f"{self.max_retries} retries: {exc}"
                    ) from exc
                time.sleep(self.base_delay * (2**attempt))

        raise NarrationError(f"Exhausted retries for {endpoint}")

    def verify_model_available(self, model_id: str) -> dict[str, Any]:
        """Verify that the configured model exists and supports generateContent."""
        if model_id in self._verified_models:
            return {"name": f"models/{model_id}"}
        info = self._request_json("GET", f"models/{model_id}")
        methods = info.get("supportedGenerationMethods", [])
        if methods and "generateContent" not in methods:
            raise NarrationError(
                f"Configured model '{model_id}' does not support 'generateContent' "
                f"(supported: {methods})."
            )
        self._verified_models.add(model_id)
        return info

    def generate_code_summary(self, code: str, language: str, config: NarrationConfig) -> str:
        """Generate a concise spoken technical explanation for a code block in the target locale."""
        self.verify_model_available(config.text_model)
        spoken_lang = LOCALE_SPOKEN_LANGUAGES.get(config.locale, config.locale)
        prompt = (
            f"Documentation Locale: {config.locale} ({spoken_lang})\n"
            f"Programming Language: {language or 'text'}\n\n"
            f"Code Block:\n{code}\n\n"
            f"Provide the spoken narration explanation for this code block in {spoken_lang}:"
        )
        payload: dict[str, Any] = {
            "systemInstruction": {
                "parts": [{"text": config.text_system_prompt}],
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}],
                }
            ],
            "generationConfig": {
                "temperature": config.text_temperature,
            },
        }
        resp = self._request_json(
            "POST",
            f"models/{config.text_model}:generateContent",
            payload,
        )
        try:
            candidates = resp["candidates"]
            parts = candidates[0]["content"]["parts"]
            text = "".join(p.get("text", "") for p in parts).strip()
        except (KeyError, IndexError, TypeError) as exc:
            raise NarrationError(
                f"Malformed text generation response from '{config.text_model}': {resp}"
            ) from exc

        cleaned = clean_inline_markdown(text)
        if not cleaned:
            raise NarrationError(
                f"Model '{config.text_model}' returned an empty code explanation."
            )
        return cleaned

    def synthesize_speech(self, text: str, config: NarrationConfig) -> tuple[bytes, str]:
        """Synthesize spoken audio using the configured Gemini TTS model.

        Returns (raw_audio_bytes, mime_type).
        """
        self.verify_model_available(config.tts_model)
        payload: dict[str, Any] = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": text,
                        }
                    ]
                }
            ],
            "generationConfig": {
                "responseModalities": ["AUDIO"],
                "speechConfig": {
                    "voiceConfig": {
                        "prebuiltVoiceConfig": {
                            "voiceName": config.voice_name,
                        }
                    }
                },
            },
        }
        resp = self._request_json(
            "POST",
            f"models/{config.tts_model}:generateContent",
            payload,
        )
        try:
            candidates = resp["candidates"]
            parts = candidates[0]["content"]["parts"]
            inline_data = None
            for part in parts:
                if "inlineData" in part:
                    inline_data = part["inlineData"]
                    break
            if not inline_data or "data" not in inline_data:
                raise KeyError("Missing inlineData.data in TTS response")
            b64_data = inline_data["data"]
            mime_type = inline_data.get("mimeType", "audio/L16;rate=24000")
            audio_bytes = base64.b64decode(b64_data)
        except Exception as exc:
            raise NarrationError(
                f"Model '{config.tts_model}' did not return valid audio inlineData: {exc}"
            ) from exc

        if not audio_bytes:
            raise NarrationError(f"Model '{config.tts_model}' returned empty audio bytes.")
        return audio_bytes, mime_type


# ---------------------------------------------------------------------------
# 3.2. Code Explanation Cache & Validation
# ---------------------------------------------------------------------------


def summary_cache_path(
    page_audio_dir: Path,
    element_source_hash: str,
    locale: str = DEFAULT_LOCALE,
) -> Path:
    norm_locale = (locale or DEFAULT_LOCALE).strip().lower()
    cache_key = sha256_json({"locale": norm_locale, "source_hash": element_source_hash})
    return page_audio_dir / "summaries" / f"{norm_locale}-{cache_key[:16]}.json"


def validate_code_summary_entry(
    entry: Any,
    expected_source_hash: str,
    config: NarrationConfig,
) -> bool:
    if not isinstance(entry, dict):
        return False
    required_keys = {
        "schema_version",
        "locale",
        "source_hash",
        "model",
        "text_config_hash",
        "generation_config",
        "transcript",
        "transcript_sha256",
    }
    if not required_keys.issubset(entry.keys()):
        return False
    if entry.get("schema_version") != config.schema_version:
        return False
    if entry.get("locale") != config.locale:
        return False
    if entry.get("source_hash") != expected_source_hash:
        return False
    if entry.get("model") != config.text_model:
        return False
    if entry.get("text_config_hash") != config.text_config_hash():
        return False
    if entry.get("generation_config") != config.text_config_dict():
        return False
    transcript = entry.get("transcript")
    if not isinstance(transcript, str) or not transcript.strip():
        return False
    if entry.get("transcript_sha256") != sha256_text(transcript):
        return False
    return True


def resolve_code_summaries(
    doc: ExtractedDocument,
    page_audio_dir: Path,
    config: NarrationConfig,
    client: GeminiClient | None,
) -> dict[str, dict[str, Any]]:
    """Validate cached code summaries or generate missing/invalid ones via Gemini."""
    summaries_by_element_id: dict[str, dict[str, Any]] = {}

    for el in doc.elements:
        if el.kind != "code_block":
            continue
        cache_file = summary_cache_path(page_audio_dir, el.source_hash, config.locale)
        if cache_file.is_file():
            try:
                cached = json.loads(cache_file.read_text(encoding="utf-8"))
                if validate_code_summary_entry(cached, el.source_hash, config):
                    summaries_by_element_id[el.element_id] = cached
                    continue
            except Exception:
                pass  # Treat malformed cache entry as a cache miss

        # Cache miss or invalid cached summary
        if client is None:
            raise NarrationError(
                f"Code summary missing or invalid for element {el.element_id} "
                f"(locale={config.locale}, hash={el.source_hash[:12]}) in {doc.source_path}, "
                "and generation is unavailable (offline mode)."
            )

        summary_text = client.generate_code_summary(el.text, el.language, config)
        transcript_hash = sha256_text(summary_text)
        entry = {
            "schema_version": config.schema_version,
            "locale": config.locale,
            "element_id": el.element_id,
            "language": el.language,
            "source_hash": el.source_hash,
            "model": config.text_model,
            "text_config_hash": config.text_config_hash(),
            "generation_config": config.text_config_dict(),
            "transcript": summary_text,
            "transcript_sha256": transcript_hash,
        }
        if not validate_code_summary_entry(entry, el.source_hash, config):
            raise NarrationError(f"Generated code summary failed self-validation for {el.element_id}")
        atomic_write_json(cache_file, entry)
        summaries_by_element_id[el.element_id] = entry

    return summaries_by_element_id


# ---------------------------------------------------------------------------
# 3.3. Narration Assembly & Chunking
# ---------------------------------------------------------------------------


@dataclass
class NarrationSegment:
    element_id: str
    kind: str
    is_ai_summary: bool
    source_hash: str
    spoken_text: str
    code_summary_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "element_id": self.element_id,
            "kind": self.kind,
            "is_ai_summary": self.is_ai_summary,
            "source_hash": self.source_hash,
            "spoken_text": self.spoken_text,
        }
        if self.code_summary_hash:
            d["code_summary_hash"] = self.code_summary_hash
        return d


@dataclass
class NarrationChunk:
    chunk_id: str
    chunk_index: int
    section_anchor: str
    section_title: str
    element_ids: list[str]
    segments: list[NarrationSegment]
    text: str
    text_sha256: str
    chunk_hash: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "chunk_index": self.chunk_index,
            "section_anchor": self.section_anchor,
            "section_title": self.section_title,
            "element_ids": self.element_ids,
            "segments": [s.to_dict() for s in self.segments],
            "text": self.text,
            "text_sha256": self.text_sha256,
            "chunk_hash": self.chunk_hash,
        }


def assemble_narration_transcript(
    doc: ExtractedDocument,
    code_summaries: dict[str, dict[str, Any]],
    config: NarrationConfig,
) -> dict[str, Any]:
    """Assemble verbatim content and code explanations into ordered sections and chunks."""
    # Group elements by section transitions (headings start a new logical section)
    sections: list[dict[str, Any]] = []
    for el in doc.elements:
        if el.kind == "heading" or not sections:
            sections.append(
                {
                    "section_anchor": el.section_anchor,
                    "section_title": el.section_title,
                    "elements": [el],
                }
            )
        else:
            sections[-1]["elements"].append(el)

    chunks: list[NarrationChunk] = []
    chunk_idx = 0

    for sec in sections:
        sec_anchor = sec["section_anchor"]
        sec_title = sec["section_title"]
        sec_elements: list[ExtractedElement] = sec["elements"]

        current_segments: list[NarrationSegment] = []
        current_char_len = 0

        def flush_chunk() -> None:
            nonlocal chunk_idx, current_segments, current_char_len
            if not current_segments:
                return
            chunk_idx += 1
            chunk_id = f"chunk-{chunk_idx:03d}"
            spoken_parts: list[str] = []
            for seg in current_segments:
                t = seg.spoken_text.strip()
                if t and not t.endswith((".", "!", "?", ":", ";")):
                    t += "."
                if t:
                    spoken_parts.append(t)
            full_text = "\n\n".join(spoken_parts)
            text_sha256 = sha256_text(full_text)
            chunk_hash = sha256_json(
                {
                    "locale": config.locale,
                    "text_sha256": text_sha256,
                    "tts_config_hash": config.tts_config_hash(),
                    "element_ids": [s.element_id for s in current_segments],
                    "segment_hashes": [
                        s.code_summary_hash if s.is_ai_summary else s.source_hash
                        for s in current_segments
                    ],
                }
            )
            chunks.append(
                NarrationChunk(
                    chunk_id=chunk_id,
                    chunk_index=chunk_idx,
                    section_anchor=sec_anchor,
                    section_title=sec_title,
                    element_ids=[s.element_id for s in current_segments],
                    segments=list(current_segments),
                    text=full_text,
                    text_sha256=text_sha256,
                    chunk_hash=chunk_hash,
                )
            )
            current_segments = []
            current_char_len = 0

        for el in sec_elements:
            if el.kind == "code_block":
                summary_entry = code_summaries.get(el.element_id)
                if not summary_entry:
                    raise NarrationError(f"Missing code summary for element {el.element_id}")
                spoken = summary_entry["transcript"]
                seg = NarrationSegment(
                    element_id=el.element_id,
                    kind=el.kind,
                    is_ai_summary=True,
                    source_hash=el.source_hash,
                    spoken_text=spoken,
                    code_summary_hash=summary_entry["transcript_sha256"],
                )
            else:
                seg = NarrationSegment(
                    element_id=el.element_id,
                    kind=el.kind,
                    is_ai_summary=False,
                    source_hash=el.source_hash,
                    spoken_text=el.text,
                )

            seg_len = len(seg.spoken_text)
            # Divide long sections at element/paragraph boundaries without omitting or reordering
            if (
                current_segments
                and current_char_len + seg_len > config.max_chunk_chars
                and not (len(current_segments) == 1 and current_segments[0].kind == "heading")
            ):
                flush_chunk()

            current_segments.append(seg)
            current_char_len += seg_len

        flush_chunk()

    # Verify chunking did not omit, duplicate, or reorder elements
    expected_ids = [e.element_id for e in doc.elements]
    assembled_ids = [eid for c in chunks for eid in c.element_ids]
    if assembled_ids != expected_ids:
        raise NarrationError(
            f"Chunking element order mismatch in {doc.source_path}: "
            f"expected {expected_ids}, got {assembled_ids}"
        )

    code_summary_hashes = {
        eid: entry["transcript_sha256"] for eid, entry in sorted(code_summaries.items())
    }

    transcript_payload = {
        "schema_version": config.schema_version,
        "locale": config.locale,
        "page_id": doc.page_id,
        "logical_source_path": doc.logical_source_path,
        "source_path": doc.source_path,
        "source_file_sha256": doc.source_file_sha256,
        "page_source_hash": doc.page_source_hash,
        "config_hash": config.config_hash(),
        "narration_config": config.full_config_dict(),
        "element_ids": expected_ids,
        "elements": [e.to_dict() for e in doc.elements],
        "code_summary_hashes": code_summary_hashes,
        "chunks": [c.to_dict() for c in chunks],
    }
    transcript_payload["transcript_sha256"] = sha256_json(transcript_payload)
    return transcript_payload


def validate_transcript_file(
    transcript_path: Path,
    doc: ExtractedDocument,
    code_summaries: dict[str, dict[str, Any]],
    config: NarrationConfig,
) -> dict[str, Any] | None:
    if not transcript_path.is_file():
        return None
    try:
        stored = json.loads(transcript_path.read_text(encoding="utf-8"))
        expected = assemble_narration_transcript(doc, code_summaries, config)
        if stored == expected:
            return stored
    except Exception:
        return None
    return None


# ---------------------------------------------------------------------------
# 3.4. Speech Synthesis, Audio Transcoding & MP3 Validation
# ---------------------------------------------------------------------------


def pcm_l16_to_wav(pcm_data: bytes, sample_rate: int = DEFAULT_SAMPLE_RATE, channels: int = 1) -> bytes:
    """Wrap raw 16-bit little-endian signed PCM bytes in a standard RIFF WAVE header."""
    bits_per_sample = 16
    block_align = channels * (bits_per_sample // 8)
    byte_rate = sample_rate * block_align
    data_size = len(pcm_data)
    chunk_size = 36 + data_size
    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF",
        chunk_size,
        b"WAVE",
        b"fmt ",
        16,
        1,  # PCM format
        channels,
        sample_rate,
        byte_rate,
        block_align,
        bits_per_sample,
        b"data",
        data_size,
    )
    return header + pcm_data


def transcode_to_mp3(
    raw_audio: bytes,
    mime_type: str,
    sample_rate: int,
    bitrate: str,
) -> bytes:
    """Convert Gemini TTS audio output (PCM L16, WAV, or MP3) into deterministic MP3 bytes."""
    mime_lower = mime_type.lower()
    if "mpeg" in mime_lower or "mp3" in mime_lower:
        return raw_audio

    ffmpeg_bin = shutil.which("ffmpeg")
    if not ffmpeg_bin:
        raise NarrationError("ffmpeg is required to transcode Gemini TTS audio into MP3.")

    # Parse sample rate from mime_type if present (e.g., audio/L16;codec=pcm;rate=24000)
    rate_match = re.search(r"rate=(\d+)", mime_lower)
    effective_rate = int(rate_match.group(1)) if rate_match else sample_rate

    if raw_audio.startswith(b"RIFF") and raw_audio[8:12] == b"WAVE":
        wav_input = raw_audio
    else:
        wav_input = pcm_l16_to_wav(raw_audio, sample_rate=effective_rate)

    cmd = [
        ffmpeg_bin,
        "-hide_banner",
        "-loglevel",
        "error",
        "-f",
        "wav",
        "-i",
        "pipe:0",
        "-vn",
        "-ar",
        str(sample_rate),
        "-ac",
        "1",
        "-codec:a",
        "libmp3lame",
        "-b:a",
        bitrate,
        "-write_xing",
        "1",
        "-id3v2_version",
        "0",
        "-map_metadata",
        "-1",
        "-f",
        "mp3",
        "pipe:1",
    ]
    proc = subprocess.run(cmd, input=wav_input, capture_output=True, check=False)
    if proc.returncode != 0 or not proc.stdout:
        err_msg = proc.stderr.decode("utf-8", errors="replace")
        raise NarrationError(f"ffmpeg MP3 transcoding failed: {err_msg}")
    return proc.stdout


def probe_mp3_file(path: Path) -> float:
    """Validate that path is a readable, well-formed MP3 file with positive duration."""
    if not path.is_file():
        raise NarrationError(f"Audio file does not exist: {path}")
    data = path.read_bytes()
    if len(data) < 256:
        raise NarrationError(f"Audio file is too small ({len(data)} bytes): {path}")

    # Verify MP3 sync word (0xFFE or ID3 header)
    has_id3 = data[:3] == b"ID3"
    has_sync = len(data) >= 2 and data[0] == 0xFF and (data[1] & 0xE0) == 0xE0
    if not (has_id3 or has_sync):
        raise NarrationError(f"Invalid MP3 header signature in {path}")

    ffprobe_bin = shutil.which("ffprobe")
    if ffprobe_bin:
        cmd = [
            ffprobe_bin,
            "-v",
            "error",
            "-select_streams",
            "a:0",
            "-show_entries",
            "stream=codec_name,duration:format=duration",
            "-of",
            "json",
            str(path),
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if proc.returncode != 0:
            raise NarrationError(f"ffprobe failed on {path}: {proc.stderr}")
        try:
            probe_data = json.loads(proc.stdout)
            streams = probe_data.get("streams", [])
            if not streams or streams[0].get("codec_name") != "mp3":
                raise NarrationError(f"Expected MP3 codec in {path}, got {streams}")
            dur_str = streams[0].get("duration") or probe_data.get("format", {}).get("duration")
            duration = float(dur_str) if dur_str is not None else 0.0
        except (ValueError, KeyError, TypeError) as exc:
            raise NarrationError(f"Failed to parse ffprobe duration for {path}: {exc}") from exc
        if duration <= 0.05:
            raise NarrationError(f"Non-positive audio duration ({duration}s) in {path}")
        return round(duration, 3)

    # Pure-Python MP3 frame duration fallback when ffprobe is absent
    # At 64 kbps (8000 bytes/sec), estimate duration from file size
    estimated_duration = len(data) / 8000.0
    if estimated_duration <= 0.05:
        raise NarrationError(f"Estimated MP3 duration too short ({estimated_duration}s) in {path}")
    return round(estimated_duration, 3)


def validate_chunk_artifact(
    manifest_chunk: dict[str, Any],
    expected_chunk: dict[str, Any],
    page_audio_dir: Path,
    config: NarrationConfig,
) -> bool:
    """Verify a cached TTS chunk against all locale, source, config, checksum, format, and duration rules."""
    if not isinstance(manifest_chunk, dict):
        return False
    required = {
        "locale",
        "chunk_id",
        "chunk_index",
        "section_anchor",
        "section_title",
        "element_ids",
        "text_sha256",
        "chunk_hash",
        "model",
        "voice",
        "audio_format",
        "tts_config_hash",
        "audio_file",
        "audio_sha256",
        "duration_seconds",
        "size_bytes",
    }
    if not required.issubset(manifest_chunk.keys()):
        return False
    if manifest_chunk.get("locale") != config.locale:
        return False
    if manifest_chunk.get("chunk_id") != expected_chunk["chunk_id"]:
        return False
    if manifest_chunk.get("chunk_index") != expected_chunk["chunk_index"]:
        return False
    if manifest_chunk.get("section_anchor") != expected_chunk["section_anchor"]:
        return False
    if manifest_chunk.get("section_title") != expected_chunk["section_title"]:
        return False
    if manifest_chunk.get("element_ids") != expected_chunk["element_ids"]:
        return False
    if manifest_chunk.get("text_sha256") != expected_chunk["text_sha256"]:
        return False
    if manifest_chunk.get("chunk_hash") != expected_chunk["chunk_hash"]:
        return False
    if manifest_chunk.get("model") != config.tts_model:
        return False
    if manifest_chunk.get("voice") != config.voice_name:
        return False
    if manifest_chunk.get("audio_format") != config.audio_format:
        return False
    if manifest_chunk.get("tts_config_hash") != config.tts_config_hash():
        return False

    audio_rel = manifest_chunk.get("audio_file")
    if not isinstance(audio_rel, str) or not audio_rel.endswith(".mp3"):
        return False
    audio_path = page_audio_dir / audio_rel
    if not audio_path.is_file():
        return False

    try:
        actual_sha = sha256_file(audio_path)
        if actual_sha != manifest_chunk.get("audio_sha256"):
            return False
        actual_size = audio_path.stat().st_size
        if actual_size != manifest_chunk.get("size_bytes"):
            return False
        duration = probe_mp3_file(audio_path)
        rec_duration = float(manifest_chunk.get("duration_seconds", 0.0))
        if rec_duration <= 0.05 or abs(duration - rec_duration) > 0.5:
            return False
    except Exception:
        return False

    return True


# ---------------------------------------------------------------------------
# Page Processing Pipeline (Generate + Validate)
# ---------------------------------------------------------------------------


def process_page(
    source_path: Path,
    root: Path,
    audio_root: Path,
    config: NarrationConfig,
    client: GeminiClient | None,
    check_only: bool = False,
    offline_mode: bool = False,
) -> dict[str, Any]:
    """Process and validate a single documentation page for a specific locale."""
    doc = extract_document(source_path, root, locale=config.locale)
    page_audio_dir = audio_root / doc.page_id
    transcript_path = page_audio_dir / "transcript.json"
    manifest_path = page_audio_dir / "manifest.json"
    no_api = check_only or offline_mode or (client is None)

    # 1. Resolve and validate code summaries
    code_summaries = resolve_code_summaries(
        doc=doc,
        page_audio_dir=page_audio_dir,
        config=config,
        client=None if no_api else client,
    )

    # 2. Assemble expected narration transcript and check existing transcript
    expected_transcript = assemble_narration_transcript(doc, code_summaries, config)
    valid_transcript = validate_transcript_file(transcript_path, doc, code_summaries, config)
    if valid_transcript is None:
        if check_only:
            raise NarrationError(
                f"Transcript missing or stale for {doc.source_path} (locale={config.locale}) at {transcript_path}"
            )
        if offline_mode:
            # In offline mode, allow refreshing transcript metadata only if an existing
            # transcript matches the exact locale, page_source_hash, and chunks
            if not transcript_path.is_file():
                raise NarrationError(
                    f"Transcript missing for {doc.source_path} (locale={config.locale}) at {transcript_path} in offline mode"
                )
            try:
                old_t = json.loads(transcript_path.read_text(encoding="utf-8"))
            except Exception as exc:
                raise NarrationError(
                    f"Malformed transcript at {transcript_path} in offline mode"
                ) from exc
            if (
                old_t.get("locale") != expected_transcript["locale"]
                or old_t.get("page_source_hash") != expected_transcript["page_source_hash"]
                or old_t.get("config_hash") != expected_transcript["config_hash"]
                or old_t.get("chunks") != expected_transcript["chunks"]
            ):
                raise NarrationError(
                    f"Source content or narration config changed for {doc.source_path} (locale={config.locale}); "
                    "cannot regenerate transcript in offline mode."
                )
        atomic_write_json(transcript_path, expected_transcript)
        valid_transcript = expected_transcript

    # 3. Load existing manifest if available to reuse valid audio chunks
    existing_chunks_by_hash: dict[str, dict[str, Any]] = {}
    if manifest_path.is_file():
        try:
            old_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if isinstance(old_manifest, dict) and old_manifest.get("locale") == config.locale:
                for ch in old_manifest.get("chunks", []):
                    if isinstance(ch, dict) and "chunk_hash" in ch:
                        existing_chunks_by_hash[ch["chunk_hash"]] = ch
        except Exception:
            pass

    # 4. Validate or synthesize TTS audio chunks
    manifest_chunks: list[dict[str, Any]] = []
    expected_audio_files: set[str] = set()

    for ch in valid_transcript["chunks"]:
        chunk_hash = ch["chunk_hash"]
        expected_filename = f"{ch['chunk_id']}-{chunk_hash[:12]}.mp3"
        expected_audio_files.add(expected_filename)
        audio_path = page_audio_dir / expected_filename

        cached_entry = existing_chunks_by_hash.get(chunk_hash)
        if (
            cached_entry is not None
            and cached_entry.get("audio_file") == expected_filename
            and validate_chunk_artifact(cached_entry, ch, page_audio_dir, config)
        ):
            manifest_chunks.append(cached_entry)
            continue

        # Cache miss or invalid audio artifact
        if no_api or client is None:
            raise NarrationError(
                f"TTS audio artifact missing or invalid for {doc.source_path} (locale={config.locale}) "
                f"chunk {ch['chunk_id']} ({expected_filename}), and synthesis is unavailable."
            )

        raw_audio, mime_type = client.synthesize_speech(ch["text"], config)
        mp3_bytes = transcode_to_mp3(
            raw_audio=raw_audio,
            mime_type=mime_type,
            sample_rate=config.sample_rate,
            bitrate=config.mp3_bitrate,
        )
        atomic_write_bytes(audio_path, mp3_bytes)
        duration = probe_mp3_file(audio_path)
        audio_sha = sha256_file(audio_path)

        new_entry = {
            "locale": config.locale,
            "chunk_id": ch["chunk_id"],
            "chunk_index": ch["chunk_index"],
            "section_anchor": ch["section_anchor"],
            "section_title": ch["section_title"],
            "element_ids": ch["element_ids"],
            "text_sha256": ch["text_sha256"],
            "chunk_hash": chunk_hash,
            "model": config.tts_model,
            "voice": config.voice_name,
            "audio_format": config.audio_format,
            "tts_config_hash": config.tts_config_hash(),
            "audio_file": expected_filename,
            "audio_sha256": audio_sha,
            "duration_seconds": duration,
            "size_bytes": len(mp3_bytes),
        }
        if not validate_chunk_artifact(new_entry, ch, page_audio_dir, config):
            raise NarrationError(
                f"Synthesized audio chunk failed post-generation validation: {audio_path}"
            )
        manifest_chunks.append(new_entry)

    # 5. Assemble and validate complete page manifest
    total_duration = round(sum(c["duration_seconds"] for c in manifest_chunks), 3)
    expected_manifest: dict[str, Any] = {
        "schema_version": config.schema_version,
        "status": "complete",
        "locale": config.locale,
        "page_id": doc.page_id,
        "logical_source_path": doc.logical_source_path,
        "source_path": doc.source_path,
        "source_file_sha256": doc.source_file_sha256,
        "page_source_hash": doc.page_source_hash,
        "config_hash": config.config_hash(),
        "narration_config": config.full_config_dict(),
        "transcript_file": "transcript.json",
        "transcript_sha256": valid_transcript["transcript_sha256"],
        "total_chunks": len(manifest_chunks),
        "total_duration_seconds": total_duration,
        "chunks": manifest_chunks,
    }
    expected_manifest["manifest_sha256"] = sha256_json(expected_manifest)

    manifest_matches = False
    if manifest_path.is_file():
        try:
            current_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if current_manifest == expected_manifest:
                manifest_matches = True
        except Exception:
            manifest_matches = False

    if not manifest_matches:
        if check_only:
            raise NarrationError(
                f"Manifest missing, stale, or mismatched for {doc.source_path} (locale={config.locale}) at {manifest_path}"
            )
        atomic_write_json(manifest_path, expected_manifest)

    # Clean up stale .mp3 files in page_audio_dir when not in check_only mode
    if not check_only and page_audio_dir.is_dir():
        for mp3_file in page_audio_dir.glob("*.mp3"):
            if mp3_file.name not in expected_audio_files:
                mp3_file.unlink(missing_ok=True)

    return expected_manifest


def resolve_locale_page_path(root: Path, page_rel: str, locale: str = DEFAULT_LOCALE) -> Path:
    """Resolve a page path for the requested locale (e.g. 'introduction.md' + 'pl' -> 'i18n/pl/introduction.md')."""
    norm_locale = (locale or DEFAULT_LOCALE).strip().lower()
    direct = (root / page_rel).resolve()
    if norm_locale == DEFAULT_LOCALE:
        return direct
    if page_rel.startswith(f"i18n/{norm_locale}/"):
        return direct
    localized = (root / "i18n" / norm_locale / page_rel).resolve()
    return localized


def default_audio_root_for_locale(root: Path, audio_dir_arg: str, locale: str = DEFAULT_LOCALE) -> Path:
    """Resolve the audio root directory for a locale ('audio' for en, 'audio/<locale>' for non-en)."""
    norm_locale = (locale or DEFAULT_LOCALE).strip().lower()
    base = (root / audio_dir_arg).resolve()
    if norm_locale == DEFAULT_LOCALE:
        return base
    # If the user already passed e.g. --audio-dir audio/pl, do not double-append
    if base.name.lower() == norm_locale:
        return base
    return (base / norm_locale).resolve()


def discover_enabled_pages(
    root: Path,
    requested_pages: list[str] | None = None,
    include_notebooks: bool = False,
    locale: str = DEFAULT_LOCALE,
) -> list[Path]:
    """Discover enabled documentation pages from myst.yml or explicit CLI arguments for a given locale."""
    norm_locale = (locale or DEFAULT_LOCALE).strip().lower()
    if requested_pages:
        pages: list[Path] = []
        for p_str in requested_pages:
            p = resolve_locale_page_path(root, p_str, norm_locale)
            if not p.is_file():
                raise NarrationError(f"Requested page does not exist for locale '{norm_locale}': {p_str} ({p})")
            pages.append(p)
        return pages

    myst_path = root / "myst.yml"
    if not myst_path.is_file():
        raise NarrationError(f"Missing myst.yml in {root}")
    config = load_yaml_file(myst_path)
    toc = config.get("project", {}).get("toc", [])
    discovered: list[Path] = []

    def walk(entries: list[Any]) -> None:
        for entry in entries:
            if isinstance(entry, dict):
                if "file" in entry:
                    fpath = resolve_locale_page_path(root, entry["file"], norm_locale)
                    if fpath.is_file() and (
                        fpath.suffix == ".md" or (include_notebooks and fpath.suffix == ".ipynb")
                    ):
                        discovered.append(fpath)
                if "children" in entry and isinstance(entry["children"], list):
                    walk(entry["children"])

    walk(toc)
    return discovered


def load_api_key_from_env_or_dotenv(root: Path) -> str | None:
    env_val = os.environ.get("GEMINI_API_KEY")
    if env_val:
        return env_val
    dotenv_path = root / ".env"
    if dotenv_path.is_file():
        for raw_line in dotenv_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k = k.strip()
            if k.startswith("export "):
                k = k[len("export ") :].strip()
            if k == "GEMINI_API_KEY":
                return v.strip().strip("'").strip('"')
    return None


def _sync_and_verify_target_dir(
    src_dir: Path,
    dst_dir: Path,
    manifest: dict[str, Any],
) -> None:
    dst_dir.mkdir(parents=True, exist_ok=True)
    required_files = ["manifest.json", manifest["transcript_file"]] + [
        ch["audio_file"] for ch in manifest["chunks"]
    ]
    for fname in required_files:
        src_file = src_dir / fname
        dst_file = dst_dir / fname
        if not src_file.is_file():
            raise NarrationError(f"Missing source audio artifact before publish: {src_file}")
        if not dst_file.is_file() or sha256_file(dst_file) != sha256_file(src_file):
            atomic_write_bytes(dst_file, src_file.read_bytes())

    pub_manifest_path = dst_dir / "manifest.json"
    pub_transcript_path = dst_dir / manifest["transcript_file"]
    if not pub_manifest_path.is_file() or not pub_transcript_path.is_file():
        raise NarrationError(f"Published manifest or transcript missing in {dst_dir}")

    pub_manifest = json.loads(pub_manifest_path.read_text(encoding="utf-8"))
    if pub_manifest != manifest:
        raise NarrationError(f"Published manifest mismatch in {pub_manifest_path}")
    if pub_manifest.get("locale") != manifest.get("locale"):
        raise NarrationError(f"Published manifest locale mismatch in {pub_manifest_path}")
    if sha256_file(pub_transcript_path) != manifest["transcript_sha256"] and (
        json.loads(pub_transcript_path.read_text(encoding="utf-8")).get("transcript_sha256")
        != manifest["transcript_sha256"]
    ):
        raise NarrationError(f"Published transcript checksum mismatch in {pub_transcript_path}")

    for ch in manifest["chunks"]:
        pub_mp3 = dst_dir / ch["audio_file"]
        if not pub_mp3.is_file():
            raise NarrationError(f"Published audio chunk missing: {pub_mp3}")
        if sha256_file(pub_mp3) != ch["audio_sha256"]:
            raise NarrationError(f"Published audio chunk SHA-256 mismatch: {pub_mp3}")


def publish_and_verify_build_assets(
    build_html_dir: Path,
    audio_root: Path,
    manifests: list[dict[str, Any]],
    config: NarrationConfig,
) -> None:
    """Ensure all validated audio assets, manifests, and transcripts exist in the built HTML directory."""
    if not build_html_dir.is_dir():
        raise NarrationError(f"Built HTML directory does not exist: {build_html_dir}")

    for manifest in manifests:
        page_id = manifest["page_id"]
        locale = manifest.get("locale", config.locale)
        src_dir = audio_root / page_id

        if locale == DEFAULT_LOCALE or build_html_dir.name.lower() == locale:
            target_dirs = [build_html_dir / "audio" / page_id]
        else:
            # Combined root _build/html: publish to both _build/html/<locale>/audio/<page_id>
            # and _build/html/audio/<locale>/<page_id> so both route prefixes resolve identically
            target_dirs = [
                build_html_dir / locale / "audio" / page_id,
                build_html_dir / "audio" / locale / page_id,
            ]

        for dst_dir in target_dirs:
            _sync_and_verify_target_dir(src_dir, dst_dir, manifest)


def _discover_enabled_locale_codes(root: Path) -> list[str]:
    locales_yml = root / "i18n" / "locales.yml"
    if not locales_yml.is_file():
        return [DEFAULT_LOCALE]
    try:
        tools_dir = str((root / "tools").resolve())
        if tools_dir not in sys.path:
            sys.path.insert(0, tools_dir)
        from i18n_utils import get_enabled_locales, load_locales_config

        cfg = load_locales_config(root)
        return list(get_enabled_locales(cfg).keys())
    except Exception:
        return [DEFAULT_LOCALE]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build-time AI audio narration generator and validator for SoftCloud."
    )
    parser.add_argument(
        "--page",
        action="append",
        dest="pages",
        help="Relative path to a documentation page to process (may be specified multiple times).",
    )
    parser.add_argument(
        "--locale",
        default=os.environ.get("SOFTCLOUD_LOCALE", DEFAULT_LOCALE),
        help=f"Documentation locale code to process (default: {DEFAULT_LOCALE}).",
    )
    parser.add_argument(
        "--all-locales",
        action="store_true",
        help="Process all enabled locales defined in i18n/locales.yml.",
    )
    parser.add_argument(
        "--include-notebooks",
        action="store_true",
        help="Include .ipynb notebooks from myst.yml TOC when --page is not specified.",
    )
    parser.add_argument(
        "--audio-dir",
        default="audio",
        help="Root directory for generated audio assets, transcripts, and manifests (default: audio).",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Explicitly run in pre-approved offline mode; requires all artifacts to exist and pass validation.",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Verify completeness, checksums, formats, and source hashes without writing or calling APIs.",
    )
    parser.add_argument(
        "--verify-build-dir",
        default="",
        help="Verify and sync published static audio assets inside the built HTML directory (e.g. _build/html).",
    )
    parser.add_argument(
        "--text-model",
        default=os.environ.get("SOFTCLOUD_TEXT_MODEL", DEFAULT_TEXT_MODEL),
        help=f"Gemini text model for code explanations (default: {DEFAULT_TEXT_MODEL}).",
    )
    parser.add_argument(
        "--tts-model",
        default=os.environ.get("SOFTCLOUD_TTS_MODEL", DEFAULT_TTS_MODEL),
        help=f"Gemini TTS model for speech synthesis (default: {DEFAULT_TTS_MODEL}).",
    )
    parser.add_argument(
        "--voice",
        default=os.environ.get("SOFTCLOUD_TTS_VOICE", DEFAULT_VOICE_NAME),
        help=f"Prebuilt voice name for TTS synthesis (default: {DEFAULT_VOICE_NAME}).",
    )
    args = parser.parse_args(argv)

    root = Path.cwd().resolve()

    offline_env = os.environ.get("SOFTCLOUD_AUDIO_OFFLINE", "")
    if offline_env and offline_env not in ("0", "1"):
        print(
            f"[ERROR] Invalid SOFTCLOUD_AUDIO_OFFLINE value: {offline_env!r} (expected '0' or '1')",
            file=sys.stderr,
        )
        return 1
    is_offline = args.offline or (offline_env == "1")

    target_locales = (
        _discover_enabled_locale_codes(root)
        if args.all_locales
        else [args.locale.strip().lower()]
    )

    try:
        client: GeminiClient | None = None
        if not args.check_only and not is_offline:
            raw_key = load_api_key_from_env_or_dotenv(root)
            if raw_key:
                api_key = GeminiClient.validate_api_key_format(raw_key)
                client = GeminiClient(api_key=api_key)

        for loc in target_locales:
            audio_root = default_audio_root_for_locale(root, args.audio_dir, loc)
            config = NarrationConfig(
                locale=loc,
                text_model=args.text_model,
                text_system_prompt=build_code_summary_system_prompt(loc),
                tts_model=args.tts_model,
                voice_name=args.voice,
            )

            pages = discover_enabled_pages(
                root=root,
                requested_pages=args.pages,
                include_notebooks=args.include_notebooks,
                locale=loc,
            )
            if not pages:
                raise NarrationError(f"No enabled documentation pages found to process for locale '{loc}'.")

            manifests: list[dict[str, Any]] = []
            for page_path in pages:
                rel = page_path.relative_to(root).as_posix()
                manifest = process_page(
                    source_path=page_path,
                    root=root,
                    audio_root=audio_root,
                    config=config,
                    client=client,
                    check_only=args.check_only,
                    offline_mode=is_offline,
                )
                manifests.append(manifest)
                mode_label = (
                    "Verified"
                    if (args.check_only or is_offline)
                    else "Generated/Validated"
                )
                audio_rel_dir = audio_root.relative_to(root).as_posix()
                print(
                    f"{mode_label} narration [{loc}] for {rel} -> "
                    f"{audio_rel_dir}/{manifest['page_id']}/ "
                    f"({manifest['total_chunks']} chunks, {manifest['total_duration_seconds']:.2f}s)"
                )

            if args.verify_build_dir:
                build_dir = (root / args.verify_build_dir).resolve()
                publish_and_verify_build_assets(
                    build_html_dir=build_dir,
                    audio_root=audio_root,
                    manifests=manifests,
                    config=config,
                )
                print(
                    f"Verified published static audio assets [{loc}] in {build_dir.relative_to(root)} "
                    f"for {len(manifests)} page(s)"
                )

    except NarrationError as exc:
        print(f"[NARRATION FAILURE] {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"[UNEXPECTED NARRATION ERROR] {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
