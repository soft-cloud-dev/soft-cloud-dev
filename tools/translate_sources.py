#!/usr/bin/env python3
"""
translate_sources.py
--------------------
Translation preparation and provenance verification workflow for SoftCloud multilingual docs.

Supports two distinct workflows per the Multilingual Implementation Memorandum:
1. Translation preparation (`--prepare` / `--sync-provenance`):
   - Uses Gemini (`gemini-2.5-flash`) with `i18n/glossary.yml` (`domain_terms` and `invariant_terms`)
     to draft or incrementally update only changed sections while preserving unchanged reviewed
     sections, code blocks (` ``` `, `~~~`, `:::`, and nested directives), executable notebook
     cells, notebook metadata, mathematical expressions, inline code spans, directives, and links
     byte-for-byte.
   - Handles both Markdown (`.md`) and Jupyter Notebook (`.ipynb`) documents, translating notebook
     Markdown cells separately from executable code cells.
   - Records source hashes, section-level hashes, code fingerprints, and per-document revision
     state in `i18n/<locale>/provenance.json`.
2. Publication verification (`--check-only`):
   - Strictly verifies that all translated documents exist, match their recorded `source_sha256`,
     `section_hashes`, and `translated_sha256` in `i18n/<locale>/provenance.json`, have
     `revision_state == "approved"`, and preserve all code blocks, math expressions, inline code,
     directives, links, and notebook code cells/metadata byte-for-byte against the authoritative
     English source.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from i18n_utils import (
    atomic_write_json,
    atomic_write_text,
    extract_code_fingerprint,
    extract_fenced_code_blocks_from_markdown,
    extract_inline_code_spans,
    extract_markdown_links,
    extract_math_expressions,
    extract_myst_directives,
    get_enabled_locales,
    load_glossary,
    load_locales_config,
    load_yaml_file,
    sha256_file,
    sha256_json,
    sha256_text,
    split_markdown_sections,
)
from translation_engine import (
    decide_sections,
    dependency_fingerprint,
    translate_protected,
)

PROVENANCE_SCHEMA_VERSION = "1.0"
DEFAULT_TRANSLATION_MODEL = "gemini-2.5-flash"
PRESERVATION_RULES_VERSION = "2"
# Revision states: "draft" = bot-generated; "reviewed" = explicitly accepted via
# --accept-reviewed; "approved" is legacy. Human approval proper is the reviewed merge.
ACCEPTED_REVISION_STATES = ("approved", "reviewed")


def translation_policy_fingerprint(root: Path) -> str:
    """Fingerprint of everything except content/glossary that shapes a translation:
    model, policy version, prompt skeleton, and preservation rules."""
    cfg = load_locales_config(root)
    t = (cfg.get("localization") or {}).get("translation") or {}
    return sha256_json(
        {
            "model": t.get("model", DEFAULT_TRANSLATION_MODEL),
            "policy_version": t.get("policy_version", 1),
            "prompt": sha256_text(build_translation_prompt("{S}", "{L}", "{N}", {})),
            "rules": PRESERVATION_RULES_VERSION,
        }
    )


def current_source_commit(root: Path) -> str | None:
    """Originating English commit, for traceability only (never used for freshness)."""
    import subprocess

    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=True, timeout=10
        )
        return out.stdout.strip() or None
    except Exception:
        return None



def discover_source_documents(root: Path) -> list[str]:
    """Return ordered list of relative document paths from authoritative myst.yml."""
    myst_cfg = load_yaml_file(root / "myst.yml")
    toc = myst_cfg.get("project", {}).get("toc", [])
    docs: list[str] = []

    def walk(entries: list[dict[str, Any]]) -> None:
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            if "file" in entry and isinstance(entry["file"], str):
                docs.append(entry["file"])
            if "children" in entry and isinstance(entry["children"], list):
                walk(entry["children"])

    walk(toc)
    return docs


def compute_document_section_hashes(path: Path) -> list[dict[str, str]]:
    """Compute section-level hashes for a Markdown or Notebook document."""
    raw = path.read_text(encoding="utf-8")
    if path.suffix == ".md":
        frontmatter, sections = split_markdown_sections(raw)
        result: list[dict[str, str]] = []
        if frontmatter:
            result.append(
                {
                    "index": "frontmatter",
                    "heading": "__frontmatter__",
                    "sha256": sha256_text(frontmatter.strip()),
                }
            )
        for idx, sec in enumerate(sections):
            result.append(
                {
                    "index": str(idx),
                    "heading": sec["heading"],
                    "sha256": sec["sha256"],
                }
            )
        return result
    if path.suffix == ".ipynb":
        nb = json.loads(raw)
        result = []
        for idx, cell in enumerate(nb.get("cells", [])):
            cell_src = "".join(cell.get("source", []))
            result.append(
                {
                    "index": f"cell-{idx}",
                    "heading": f"{cell.get('cell_type', 'unknown')}-{idx}",
                    "sha256": sha256_text(cell_src),
                }
            )
        return result
    raise ValueError(f"Unsupported document suffix: {path}")


def verify_markdown_protected_constructs(
    en_text: str,
    loc_text: str,
    locale: str,
    doc_label: str,
) -> list[str]:
    """Verify that protected MyST constructs (math, inline code, directives, links, section count) match."""
    errors: list[str] = []

    en_math = extract_math_expressions(en_text)
    loc_math = extract_math_expressions(loc_text)
    if en_math != loc_math:
        errors.append(
            f"[{locale}] Mathematical expressions altered in {doc_label}: "
            f"expected {en_math}, got {loc_math}"
        )

    en_inline = extract_inline_code_spans(en_text)
    loc_inline = extract_inline_code_spans(loc_text)
    if en_inline != loc_inline:
        errors.append(
            f"[{locale}] Inline code spans altered in {doc_label}: "
            f"expected {en_inline}, got {loc_inline}"
        )

    en_dirs = extract_myst_directives(en_text)
    loc_dirs = extract_myst_directives(loc_text)
    if en_dirs != loc_dirs:
        errors.append(
            f"[{locale}] MyST directives or attributes altered in {doc_label}: "
            f"expected {en_dirs}, got {loc_dirs}"
        )

    en_links = extract_markdown_links(en_text)
    loc_links = extract_markdown_links(loc_text)
    if en_links != loc_links:
        errors.append(
            f"[{locale}] Markdown link targets altered in {doc_label}: "
            f"expected {en_links}, got {loc_links}"
        )

    _, en_secs = split_markdown_sections(en_text)
    _, loc_secs = split_markdown_sections(loc_text)
    if len(en_secs) != len(loc_secs):
        errors.append(
            f"[{locale}] Markdown section count mismatch in {doc_label}: "
            f"expected {len(en_secs)}, got {len(loc_secs)}"
        )

    return errors


def verify_document_preservation(en_path: Path, loc_path: Path, locale: str) -> list[str]:
    """Verify code blocks, math, inline code, directives, links, and notebook cells/metadata."""
    errors: list[str] = []
    en_fp = extract_code_fingerprint(en_path)
    loc_fp = extract_code_fingerprint(loc_path)

    if en_fp["sha256"] != loc_fp["sha256"]:
        errors.append(
            f"[{locale}] Code/notebook fingerprint mismatch in {loc_path.name}: "
            f"expected {en_fp['sha256'][:12]} ({en_fp['count']} blocks), "
            f"got {loc_fp['sha256'][:12]} ({loc_fp['count']} blocks)"
        )

    if en_path.suffix == ".md":
        en_text = en_path.read_text(encoding="utf-8")
        loc_text = loc_path.read_text(encoding="utf-8")
        errors.extend(verify_markdown_protected_constructs(en_text, loc_text, locale, loc_path.name))
    elif en_path.suffix == ".ipynb":
        en_nb = json.loads(en_path.read_text(encoding="utf-8"))
        loc_nb = json.loads(loc_path.read_text(encoding="utf-8"))
        en_cells = en_nb.get("cells", [])
        loc_cells = loc_nb.get("cells", [])
        if len(en_cells) != len(loc_cells):
            errors.append(
                f"[{locale}] Notebook cell count mismatch in {loc_path.name}: "
                f"expected {len(en_cells)}, got {len(loc_cells)}"
            )
        for idx, (ec, lc) in enumerate(zip(en_cells, loc_cells)):
            if ec.get("cell_type") != lc.get("cell_type"):
                errors.append(
                    f"[{locale}] Notebook cell {idx} type mismatch in {loc_path.name}: "
                    f"expected {ec.get('cell_type')}, got {lc.get('cell_type')}"
                )
            elif ec.get("cell_type") == "markdown":
                ec_text = "".join(ec.get("source", []))
                lc_text = "".join(lc.get("source", []))
                if extract_fenced_code_blocks_from_markdown(ec_text) != extract_fenced_code_blocks_from_markdown(lc_text):
                    errors.append(
                        f"[{locale}] Embedded code block mismatch in {loc_path.name} markdown cell {idx}"
                    )
                errors.extend(
                    verify_markdown_protected_constructs(
                        ec_text, lc_text, locale, f"{loc_path.name}#cell-{idx}"
                    )
                )
    return errors


def build_provenance_manifest(
    root: Path,
    locale: str,
    docs: list[str],
    revision_state: str = "approved",
    per_doc_revision_states: dict[str, str] | None = None,
    record_docs: set[str] | None = None,
    old_manifest: dict[str, Any] | None = None,
    extra_by_doc: dict[str, dict[str, Any]] | None = None,
    progressive: bool = False,
) -> dict[str, Any]:
    """Build deterministic provenance.json structure for a target locale.

    When ``record_docs`` is given, only those documents get fresh records; every other
    document's existing record is carried over verbatim (never refreshed against the
    current English), as are records for pages no longer published.
    """
    locales_cfg = load_locales_config(root)
    locales_map = get_enabled_locales(locales_cfg)
    if locale not in locales_map:
        raise ValueError(f"Unknown or disabled locale: {locale}")
    locale_info = locales_map[locale]
    loc_root = root / str(locale_info.get("source_dir", f"i18n/{locale}"))
    glossary = load_glossary(root)
    glossary_sha = sha256_json(glossary)
    policy_sha = translation_policy_fingerprint(root)
    source_commit = current_source_commit(root)
    old_docs: dict[str, Any] = (
        old_manifest.get("documents", {}) if isinstance(old_manifest, dict) else {}
    )
    old_locale_glossary = (old_manifest or {}).get("glossary_sha256")
    translation_model = str(
        ((locales_cfg.get("localization") or {}).get("translation") or {}).get("model", DEFAULT_TRANSLATION_MODEL)
    )

    documents_meta: dict[str, Any] = {}
    for rel_doc in docs:
        if record_docs is not None and rel_doc not in record_docs:
            old_entry = old_docs.get(rel_doc)
            if isinstance(old_entry, dict):
                documents_meta[rel_doc] = old_entry
            continue
        en_path = root / rel_doc
        loc_path = loc_root / rel_doc
        if not en_path.is_file():
            raise FileNotFoundError(f"Missing authoritative source document: {en_path}")
        if not loc_path.is_file():
            if progressive or rel_doc.startswith("components/"):
                old_entry = old_docs.get(rel_doc)
                if isinstance(old_entry, dict):
                    documents_meta[rel_doc] = old_entry
                continue
            raise FileNotFoundError(f"Missing localized document for '{locale}': {loc_path}")

        preservation_errors = verify_document_preservation(en_path, loc_path, locale)
        if preservation_errors:
            raise ValueError("\n".join(preservation_errors))

        en_fp = extract_code_fingerprint(en_path)
        loc_fp = extract_code_fingerprint(loc_path)
        en_sec_hashes = compute_document_section_hashes(en_path)
        loc_sec_hashes = compute_document_section_hashes(loc_path)

        section_records = []
        for en_sec, loc_sec in zip(en_sec_hashes, loc_sec_hashes):
            section_records.append(
                {
                    "index": en_sec["index"],
                    "source_heading": en_sec["heading"],
                    "translated_heading": loc_sec["heading"],
                    "source_sha256": en_sec["sha256"],
                    "translated_sha256": loc_sec["sha256"],
                }
            )

        doc_rev_state = (
            per_doc_revision_states.get(rel_doc, revision_state)
            if per_doc_revision_states
            else revision_state
        )

        entry: dict[str, Any] = {
            "source_path": rel_doc,
            "localized_path": loc_path.relative_to(root).as_posix(),
            "source_sha256": sha256_file(en_path),
            "translated_sha256": sha256_file(loc_path),
            "dependency_sha256": dependency_fingerprint(root, rel_doc),
            "glossary_sha256": glossary_sha,
            "policy_sha256": policy_sha,
            "translation_model": translation_model,
            "code_fingerprint_sha256": en_fp["sha256"],
            "localized_code_fingerprint_sha256": loc_fp["sha256"],
            "code_block_count": en_fp["count"],
            "revision_state": doc_rev_state,
            "sections": section_records,
        }
        if source_commit:
            entry["source_commit"] = source_commit
        entry.update((extra_by_doc or {}).get(rel_doc, {}))
        documents_meta[rel_doc] = entry

    for rel_doc, old_entry in old_docs.items():
        if rel_doc not in documents_meta and rel_doc not in docs and isinstance(old_entry, dict):
            documents_meta[rel_doc] = old_entry  # unpublished page: removal is a separate, reviewed step

    if record_docs is None or not old_manifest:
        locale_glossary = glossary_sha
    else:
        effective = [
            e.get("glossary_sha256", old_locale_glossary)
            for d, e in documents_meta.items()
            if d in docs
        ]
        locale_glossary = glossary_sha if all(g == glossary_sha for g in effective) else old_locale_glossary

    manifest: dict[str, Any] = {
        "schema_version": PROVENANCE_SCHEMA_VERSION,
        "locale": locale,
        "source_locale": str(locales_cfg.get("default_locale", "en")),
        "glossary_sha256": locale_glossary,
        "documents": documents_meta,
    }
    manifest["provenance_sha256"] = sha256_json(manifest)
    return manifest


def check_locale_provenance(root: Path, locale: str, docs: list[str], progressive: bool = False) -> list[str]:
    """Validate translation files, code preservation, and provenance.json for a target locale."""
    errors: list[str] = []
    locales_cfg = load_locales_config(root)
    locales_map = get_enabled_locales(locales_cfg)
    if locale not in locales_map:
        return [f"Unknown locale: {locale}"]
    locale_info = locales_map[locale]
    loc_root = root / str(locale_info.get("source_dir", f"i18n/{locale}"))
    prov_path = loc_root / "provenance.json"

    if not prov_path.is_file():
        return [f"[{locale}] Missing translation provenance file: {prov_path.relative_to(root)}"]

    try:
        prov = json.loads(prov_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"[{locale}] Invalid JSON in {prov_path.relative_to(root)}: {exc}"]

    if prov.get("schema_version") != PROVENANCE_SCHEMA_VERSION:
        errors.append(f"[{locale}] Unsupported provenance schema_version: {prov.get('schema_version')}")
    if prov.get("locale") != locale:
        errors.append(f"[{locale}] Provenance locale mismatch: {prov.get('locale')}")

    expected_copy = dict(prov)
    recorded_digest = expected_copy.pop("provenance_sha256", None)
    if recorded_digest != sha256_json(expected_copy):
        errors.append(f"[{locale}] provenance_sha256 integrity mismatch in {prov_path.relative_to(root)}")

    glossary_sha = sha256_json(load_glossary(root))
    if prov.get("glossary_sha256") != glossary_sha:
        errors.append(f"[{locale}] Stale glossary_sha256 in {prov_path.relative_to(root)}")

    prov_docs = prov.get("documents", {})
    for rel_doc in docs:
        en_path = root / rel_doc
        loc_path = loc_root / rel_doc
        if not loc_path.is_file():
            if not progressive and not rel_doc.startswith("components/"):
                errors.append(f"[{locale}] Missing translated document: {loc_path.relative_to(root)}")
            continue

        errors.extend(verify_document_preservation(en_path, loc_path, locale))

        doc_entry = prov_docs.get(rel_doc)
        if not isinstance(doc_entry, dict):
            errors.append(f"[{locale}] Missing provenance entry for document '{rel_doc}'")
            continue

        if doc_entry.get("revision_state") not in ACCEPTED_REVISION_STATES:
            errors.append(
                f"[{locale}] Document '{rel_doc}' has revision_state={doc_entry.get('revision_state')!r} "
                f"(expected one of {list(ACCEPTED_REVISION_STATES)})"
            )

        actual_en_sha = sha256_file(en_path)
        if doc_entry.get("source_sha256") != actual_en_sha:
            errors.append(
                f"[{locale}] Stale translation for '{rel_doc}': source_sha256 in provenance "
                f"({str(doc_entry.get('source_sha256'))[:12]}) != authoritative English ({actual_en_sha[:12]})"
            )

        actual_loc_sha = sha256_file(loc_path)
        if doc_entry.get("translated_sha256") != actual_loc_sha:
            errors.append(
                f"[{locale}] Unrecorded edit in '{rel_doc}': translated_sha256 in provenance "
                f"({str(doc_entry.get('translated_sha256'))[:12]}) != file on disk ({actual_loc_sha[:12]})"
            )

        en_fp = extract_code_fingerprint(en_path)
        if doc_entry.get("code_fingerprint_sha256") != en_fp["sha256"]:
            errors.append(f"[{locale}] Code fingerprint hash mismatch in provenance for '{rel_doc}'")

        en_secs = compute_document_section_hashes(en_path)
        loc_secs = compute_document_section_hashes(loc_path)
        recorded_secs = doc_entry.get("sections", [])
        if len(recorded_secs) != len(en_secs):
            errors.append(
                f"[{locale}] Section provenance count mismatch for '{rel_doc}': "
                f"recorded {len(recorded_secs)}, expected {len(en_secs)}"
            )
        else:
            for r_sec, e_sec, l_sec in zip(recorded_secs, en_secs, loc_secs):
                if r_sec.get("source_sha256") != e_sec["sha256"]:
                    errors.append(
                        f"[{locale}] Stale section '{e_sec['heading']}' in '{rel_doc}' "
                        "(English section changed since translation)"
                    )
                if r_sec.get("translated_sha256") != l_sec["sha256"]:
                    errors.append(
                        f"[{locale}] Unsynced translated section '{l_sec['heading']}' in '{rel_doc}'"
                    )

    return errors


def extract_glossary_term_map(glossary: dict[str, Any], target_locale: str) -> dict[str, str]:
    """Extract English-to-target-locale preferred domain terminology from `i18n/glossary.yml`."""
    entries: list[dict[str, Any]] = []
    domain_terms = glossary.get("domain_terms")
    if isinstance(domain_terms, dict):
        for val in domain_terms.values():
            if isinstance(val, dict):
                entries.append(val)
    elif isinstance(domain_terms, list):
        for val in domain_terms:
            if isinstance(val, dict):
                entries.append(val)

    legacy_terms = glossary.get("terms")
    if isinstance(legacy_terms, list):
        for val in legacy_terms:
            if isinstance(val, dict):
                entries.append(val)

    term_map: dict[str, str] = {}
    for entry in entries:
        en_term = entry.get("en")
        if isinstance(en_term, str) and en_term.strip():
            target_term = entry.get(target_locale, en_term)
            if isinstance(target_term, str) and target_term.strip():
                term_map[en_term] = target_term
    return term_map


def build_translation_prompt(
    section_text: str,
    target_locale: str,
    language_name: str,
    glossary: dict[str, Any],
) -> str:
    """Build the Gemini translation prompt incorporating invariant terms and `domain_terms`."""
    invariants = ", ".join(str(x) for x in glossary.get("invariant_terms", []))
    term_map = extract_glossary_term_map(glossary, target_locale)
    return (
        f"Translate the following MyST Markdown section from English into {language_name} ({target_locale}).\n"
        "STRICT RULES:\n"
        "1. Preserve ALL fenced code blocks (```, ~~~, :::), inline code spans, URLs, link targets, and MyST directive names/attributes byte-for-byte.\n"
        "2. Preserve mathematical expressions ($...$, $$...$$, {math}) byte-for-byte.\n"
        f"3. Keep these technical identifiers untranslated: {invariants}\n"
        f"4. Preferred domain terminology in {language_name}: {json.dumps(term_map, ensure_ascii=False)}\n"
        "5. Output ONLY the translated Markdown text without wrapping it in outer code fences.\n"
        "6. Tokens of the form \u27e6SC<number>\u27e7 are opaque placeholders for protected content: copy each one "
        "exactly once, in place; never translate, merge, reorder, duplicate or drop them.\n\n"
        f"SOURCE SECTION:\n{section_text}"
    )


class FatalTranslationError(RuntimeError):
    """Invalid credentials, unsupported model/configuration: do not retry, stop the run."""


class TransientTranslationError(RuntimeError):
    """Retries for a transient provider failure were exhausted."""


def _post_json(url: str, payload: dict[str, Any], api_key: str, max_attempts: int = 4) -> dict[str, Any]:
    """POST with bounded retries; honours Retry-After; fails fast on non-retryable errors."""
    import time

    if not api_key:
        raise FatalTranslationError("GEMINI_API_KEY is required to generate translations")
    delay = 2.0
    last: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        req = urllib.request.Request(
            url=url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
            method="POST",
        )
        wait = delay
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code in (400, 401, 403, 404):
                raise FatalTranslationError(f"Gemini rejected the request (HTTP {exc.code})") from exc
            if not (exc.code in (408, 429) or exc.code >= 500):
                raise FatalTranslationError(f"Unexpected HTTP {exc.code} from Gemini") from exc
            retry_after = exc.headers.get("Retry-After") if exc.headers else None
            if retry_after and retry_after.strip().isdigit():
                wait = min(float(retry_after), 120.0)
            last = exc
        except (urllib.error.URLError, TimeoutError) as exc:
            last = exc
        if attempt < max_attempts:
            time.sleep(wait)
            delay *= 2
    raise TransientTranslationError(f"Gemini request failed after {max_attempts} attempts: {last}")


def translate_section_with_gemini(
    section_text: str,
    target_locale: str,
    language_name: str,
    glossary: dict[str, Any],
    api_key: str,
    model: str = DEFAULT_TRANSLATION_MODEL,
) -> str:
    """Translate (already masked) Markdown prose with Gemini. Protected content never reaches this call."""
    prompt = build_translation_prompt(section_text, target_locale, language_name, glossary)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.1},
    }
    body = _post_json(url, payload, api_key)
    candidates = body.get("candidates") or []
    parts = candidates[0].get("content", {}).get("parts", []) if candidates else []
    translated = "".join(p.get("text", "") for p in parts if isinstance(p, dict)).strip()
    if not translated:
        raise RuntimeError(f"Empty translation response from Gemini for locale {target_locale}")
    return translated + "\n"


WIDGET_LOCALE_RE = re.compile(
    r'("page"\s*:\s*"introduction"\s*)(?:,\s*"locale"\s*:\s*"[a-zA-Z_-]+")?'
)


def localize_widget_blocks(text: str, target_locale: str) -> str:
    """Deterministically set the `{anywidget}` `"locale"` property (never delegated to the model)."""
    return WIDGET_LOCALE_RE.sub(rf'\1,\n  "locale": "{target_locale}"', text)


def _load_existing_provenance(prov_path: Path) -> dict[str, Any]:
    if not prov_path.is_file():
        return {}
    try:
        data = json.loads(prov_path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


FRONTMATTER_TRANSLATABLE = ("title", "description", "subtitle", "short_title")
FRONTMATTER_LINE_RE = re.compile(r"^(" + "|".join(FRONTMATTER_TRANSLATABLE) + r"):[ \t]*(.+?)[ \t]*$")


class _Ctx:
    """Per-locale translation context; counts model calls."""

    def __init__(self, root, locale, lang, glossary, api_key, fn, overwrite, force, reassess):
        self.root, self.locale, self.lang, self.glossary = root, locale, lang, glossary
        self.api_key, self.fn = api_key, fn
        self.overwrite, self.force, self.reassess = overwrite, force, reassess
        self.calls = 0

    def translate(self, text: str) -> str:
        def call(masked: str) -> str:
            self.calls += 1
            return self.fn(masked, self.locale, self.lang, self.glossary, self.api_key)

        out = translate_protected(text, call)
        out = localize_widget_blocks(out, self.locale)
        return out if out.endswith("\n") or not text.endswith("\n") else out + "\n"


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def _translate_frontmatter(ctx: _Ctx, en_fm: str) -> str:
    out = []
    for line in en_fm.splitlines(keepends=True):
        body = line.rstrip("\r\n")
        m = FRONTMATTER_LINE_RE.match(body)
        if m:
            translated = ctx.translate(_unquote(m.group(2))).strip().replace("\n", " ")
            out.append(f"{m.group(1)}: {json.dumps(translated, ensure_ascii=False)}" + line[len(body):])
        else:
            out.append(line)
    return "".join(out)


def _policy_stale(entry: dict[str, Any], old_prov: dict[str, Any], glossary_sha: str, policy_sha: str) -> bool:
    if entry.get("glossary_sha256", old_prov.get("glossary_sha256")) != glossary_sha:
        return True
    return "policy_sha256" in entry and entry["policy_sha256"] != policy_sha


def _update_markdown(ctx: _Ctx, en_path: Path, loc_path: Path, entry: dict[str, Any], force_all: bool) -> dict[str, Any]:
    en_text = en_path.read_text(encoding="utf-8")
    en_fm, en_secs = split_markdown_sections(en_text)
    old_all = entry.get("sections", []) if isinstance(entry.get("sections"), list) else []
    fm_old = next((s for s in old_all if str(s.get("index")) == "frontmatter"), None)
    body_old = [s for s in old_all if str(s.get("index")) != "frontmatter"]
    conflicts: list[str] = []
    preserved: list[str] = []

    loc_exists = loc_path.is_file()
    loc_text = loc_path.read_text(encoding="utf-8") if loc_exists else ""
    unedited_doc = bool(entry) and loc_exists and entry.get("translated_sha256") == sha256_file(loc_path)

    if not loc_exists:
        decisions = [{"action": "translate", "content": s["content"]} for s in en_secs]
        loc_fm = ""
    elif not entry and not ctx.overwrite:
        return {
            "outcome": "conflict",
            "conflicts": ["existing translation has no provenance record; accept it with --accept-reviewed "
                          "after review, or pass --overwrite-human-edits"],
        }
    else:
        loc_fm, loc_secs = split_markdown_sections(loc_text)
        try:
            decisions, conflicts, kept_edits = decide_sections(en_secs, loc_secs, body_old, force_all=force_all)
            preserved.extend(f"section:{p}" for p in kept_edits)
        except ValueError:
            if unedited_doc or ctx.overwrite:
                decisions = [{"action": "translate", "content": s["content"]} for s in en_secs]  # regenerate document
            else:
                return {
                    "outcome": "conflict",
                    "conflicts": ["document structure no longer matches provenance and the localized file has "
                                  "unrecorded edits; refresh explicitly"],
                }

    # Frontmatter
    out_fm = ""
    if en_fm:
        en_fm_sha = sha256_text(en_fm.strip())
        can_keep = bool(loc_fm) and fm_old is not None and not force_all and fm_old.get("source_sha256") == en_fm_sha
        if can_keep:
            out_fm = loc_fm
            if fm_old.get("translated_sha256") != sha256_text(loc_fm.strip()):
                preserved.append("frontmatter")
        elif (
            loc_fm and fm_old is not None and fm_old.get("translated_sha256") != sha256_text(loc_fm.strip())
            and not ctx.overwrite
        ):
            conflicts.append("frontmatter: English changed and the localized frontmatter was edited")
        else:
            out_fm = "<translate>"

    if conflicts and not ctx.overwrite:
        return {"outcome": "conflict", "conflicts": conflicts}

    before = ctx.calls
    if out_fm == "<translate>":
        out_fm = _translate_frontmatter(ctx, en_fm)
        if not out_fm.endswith("\n"):
            out_fm += "\n"
    parts = []
    for d in decisions:
        if d["action"] == "keep":
            parts.append(d["content"])
        else:
            t = ctx.translate(d["content"])
            parts.append(t if t.endswith("\n") else t + "\n")
    assembled = out_fm + "".join(parts)
    return {
        "outcome": "unchanged" if assembled == loc_text else "generated",
        "content": assembled,
        "preserved": preserved,
        "calls": ctx.calls - before,
        "conflicts": [],
    }


def _update_notebook(ctx: _Ctx, en_path: Path, loc_path: Path, entry: dict[str, Any], force_all: bool) -> dict[str, Any]:
    en_nb = json.loads(en_path.read_text(encoding="utf-8"))
    en_cells = en_nb.get("cells", [])
    old_by_key = {
        str(s.get("index")): s for s in (entry.get("sections") or []) if isinstance(s, dict)
    }
    loc_exists = loc_path.is_file()
    loc_nb = json.loads(loc_path.read_text(encoding="utf-8")) if loc_exists else None
    loc_cells = loc_nb.get("cells", []) if isinstance(loc_nb, dict) else []
    unedited_doc = bool(entry) and loc_exists and entry.get("translated_sha256") == sha256_file(loc_path)

    mappable = loc_exists and len(loc_cells) == len(en_cells) and all(
        a.get("cell_type") == b.get("cell_type") for a, b in zip(en_cells, loc_cells)
    )
    if loc_exists and not entry and not ctx.overwrite:
        return {"outcome": "conflict", "conflicts": ["existing notebook translation has no provenance record"]}
    if loc_exists and not mappable and not (unedited_doc or ctx.overwrite):
        return {
            "outcome": "conflict",
            "conflicts": ["notebook cell structure changed and the localized notebook has unrecorded edits"],
        }

    out_nb = json.loads(json.dumps(en_nb))  # code cells, outputs, ids and metadata come from English
    conflicts: list[str] = []
    preserved: list[str] = []
    plan: dict[int, str | None] = {}
    for idx, cell in enumerate(en_cells):
        if cell.get("cell_type") != "markdown":
            continue
        en_src = "".join(cell.get("source", []))
        if not mappable:
            plan[idx] = None
            continue
        rec = old_by_key.get(f"cell-{idx}")
        loc_src = "".join(loc_cells[idx].get("source", []))
        en_changed = force_all or rec is None or rec.get("source_sha256") != sha256_text(en_src)
        edited = rec is None or rec.get("translated_sha256") != sha256_text(loc_src)
        if not en_changed:
            plan[idx] = loc_src
            if edited:
                preserved.append(f"cell-{idx}")
        elif edited and not ctx.overwrite and rec is not None:
            conflicts.append(f"cell-{idx}: English changed and the localized cell was edited")
        else:
            plan[idx] = None
    if conflicts:
        return {"outcome": "conflict", "conflicts": conflicts}

    before = ctx.calls
    for idx, kept in plan.items():
        if kept is not None:
            out_nb["cells"][idx]["source"] = loc_cells[idx]["source"]
            continue
        en_src = "".join(en_cells[idx].get("source", []))
        translated = ctx.translate(en_src).rstrip("\r\n")
        out_nb["cells"][idx]["source"] = translated.splitlines(keepends=True)
    same = loc_exists and out_nb == loc_nb
    return {
        "outcome": "unchanged" if same else "generated",
        "content": json.dumps(out_nb, indent=1, ensure_ascii=False) + "\n",
        "preserved": preserved,
        "calls": ctx.calls - before,
        "conflicts": [],
    }


def update_locale_translations(
    root: Path,
    locale: str,
    docs: list[str],
    glossary: dict[str, Any],
    api_key: str,
    translate_fn: Callable[[str, str, str, dict[str, Any], str], str] | None = None,
    force: bool = False,
    overwrite_human_edits: bool = False,
    reassess_policy: bool = False,
    only_docs: set[str] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Reconcile one locale: create missing, update stale, preserve human edits, record only justified provenance.

    Returns (manifest, report). The provenance file is written only when at least one document was
    generated or legitimately refreshed; documents left untouched keep their previous record verbatim.
    """
    locales_cfg = load_locales_config(root)
    enabled = get_enabled_locales(locales_cfg)
    if locale not in enabled:
        raise ValueError(f"Unknown or disabled locale: {locale}")
    info = enabled[locale]
    lang = str(info.get("english_name") or info.get("name") or locale)
    loc_dir = root / str(info.get("source_dir", f"i18n/{locale}"))
    prov_path = loc_dir / "provenance.json"
    old_prov = _load_existing_provenance(prov_path)
    old_docs = old_prov.get("documents", {}) if isinstance(old_prov.get("documents"), dict) else {}
    glossary_sha = sha256_json(glossary)
    policy_sha = translation_policy_fingerprint(root)
    model = str(((locales_cfg.get("localization") or {}).get("translation") or {}).get("model", DEFAULT_TRANSLATION_MODEL))
    if translate_fn is None:
        def translate_fn(text, loc, lg, gl, key, _m=model):  # type: ignore[no-redef]
            return translate_section_with_gemini(text, loc, lg, gl, key, model=_m)

    ctx = _Ctx(root, locale, lang, glossary, api_key, translate_fn, overwrite_human_edits, force, reassess_policy)
    report: dict[str, Any] = {
        "locale": locale, "generated": [], "refreshed": [], "unchanged": [], "conflicts": {},
        "preserved_human_edits": {}, "policy_pending": [], "failed": {}, "translate_calls": 0,
    }
    record: set[str] = set()
    extra: dict[str, dict[str, Any]] = {}
    states: dict[str, str] = {}

    for rel in docs:
        if only_docs is not None and rel not in only_docs:
            continue
        en_path, loc_path = root / rel, loc_dir / rel
        entry = old_docs.get(rel) if isinstance(old_docs.get(rel), dict) else {}
        src_changed = (
            not entry
            or entry.get("source_sha256") != sha256_file(en_path)
            or ("dependency_sha256" in entry and entry["dependency_sha256"] != dependency_fingerprint(root, rel))
        )
        pol_stale = bool(entry) and _policy_stale(entry, old_prov, glossary_sha, policy_sha)
        file_changed = (
            loc_path.is_file() and bool(entry) and entry.get("translated_sha256") != sha256_file(loc_path)
        )
        if not loc_path.is_file() or src_changed or force or (pol_stale and reassess_policy):
            pass
        else:
            if pol_stale:
                report["policy_pending"].append(rel)
            if file_changed:
                report["preserved_human_edits"][rel] = ["unaccepted edit; use --accept-reviewed"]
            report["unchanged"].append(rel)
            continue

        force_all = force or (pol_stale and reassess_policy)
        previous = loc_path.read_text(encoding="utf-8") if loc_path.is_file() else None
        try:
            loc_path.parent.mkdir(parents=True, exist_ok=True)
            fn = _update_markdown if en_path.suffix == ".md" else _update_notebook
            res = fn(ctx, en_path, loc_path, entry, force_all)
        except FatalTranslationError:
            raise
        except Exception as exc:  # per-document isolation: keep last coherent state
            report["failed"][rel] = f"{type(exc).__name__}: {exc}"
            continue

        if res["outcome"] == "conflict":
            report["conflicts"][rel] = res["conflicts"]
            continue

        if res["outcome"] == "generated":
            atomic_write_text(loc_path, res["content"])
            problems = verify_document_preservation(en_path, loc_path, locale)
            if problems:
                if previous is None:
                    loc_path.unlink(missing_ok=True)
                else:
                    atomic_write_text(loc_path, previous)
                report["failed"][rel] = "preservation validation failed: " + "; ".join(problems[:3])
                continue
            report["generated"].append(rel)
        else:
            if res.get("preserved") or (entry and file_changed):
                report["preserved_human_edits"][rel] = res.get("preserved") or ["unaccepted edit"]
                report["unchanged"].append(rel)
                continue
            if not src_changed:
                report["unchanged"].append(rel)
                continue
            report["refreshed"].append(rel)

        record.add(rel)
        states[rel] = "draft"
        extra[rel] = {}
        if pol_stale and not force_all:
            # Only changed sections were retranslated; do not claim the new glossary/policy for the rest.
            extra[rel] = {
                "glossary_sha256": entry.get("glossary_sha256", old_prov.get("glossary_sha256")),
                "policy_sha256": entry.get("policy_sha256"),
            }
        if res.get("preserved"):
            extra[rel]["preserved_human_edits"] = res["preserved"]
            report["preserved_human_edits"][rel] = res["preserved"]

    report["translate_calls"] = ctx.calls
    manifest = old_prov
    if record:
        manifest = build_provenance_manifest(
            root=root, locale=locale, docs=docs, revision_state="draft",
            per_doc_revision_states=states, record_docs=record, old_manifest=old_prov, extra_by_doc=extra,
        )
        atomic_write_json(prov_path, manifest)
    return manifest, report


def prepare_locale_translations(
    root: Path,
    locale: str,
    docs: list[str],
    glossary: dict[str, Any],
    api_key: str,
    translate_fn: Callable[[str, str, str, dict[str, Any], str], str] | None = None,
    force: bool = False,
    **kwargs: Any,
) -> dict[str, Any]:
    """Backward-compatible wrapper returning only the provenance manifest."""
    manifest, _ = update_locale_translations(
        root, locale, docs, glossary, api_key, translate_fn=translate_fn, force=force, **kwargs
    )
    return manifest


def accept_reviewed_translations(
    root: Path, locale: str, docs: list[str], only_docs: set[str] | None = None
) -> dict[str, Any]:
    """Explicitly accept human-edited localized text as reviewed.

    Validated, never automatic: the English source must still match the recorded revision (else the
    translation is stale and must be updated first) and all preservation checks must pass. Records the
    new translated hashes with revision_state 'reviewed'. Narration is refreshed afterwards from the
    accepted text by the narration stage.
    """
    locales_cfg = load_locales_config(root)
    enabled = get_enabled_locales(locales_cfg)
    loc_dir = root / str(enabled[locale].get("source_dir", f"i18n/{locale}"))
    prov_path = loc_dir / "provenance.json"
    old_prov = _load_existing_provenance(prov_path)
    old_docs = old_prov.get("documents", {}) if isinstance(old_prov.get("documents"), dict) else {}
    accepted: list[str] = []
    refused: dict[str, str] = {}
    for rel in docs:
        if only_docs is not None and rel not in only_docs:
            continue
        entry, loc_path, en_path = old_docs.get(rel), loc_dir / rel, root / rel
        if not isinstance(entry, dict) or not loc_path.is_file():
            refused[rel] = "no provenance record or localized file"
            continue
        if entry.get("translated_sha256") == sha256_file(loc_path) and entry.get("revision_state") in ACCEPTED_REVISION_STATES:
            continue  # nothing to accept
        if entry.get("source_sha256") != sha256_file(en_path):
            refused[rel] = "English changed since the recorded translation; update the translation first"
            continue
        problems = verify_document_preservation(en_path, loc_path, locale)
        if problems:
            refused[rel] = "; ".join(problems[:3])
            continue
        accepted.append(rel)
    manifest = old_prov
    if accepted:
        manifest = build_provenance_manifest(
            root=root, locale=locale, docs=docs, revision_state="reviewed",
            record_docs=set(accepted), old_manifest=old_prov,
            extra_by_doc={r: {"accepted_from": "human_edit"} for r in accepted},
        )
        atomic_write_json(prov_path, manifest)
    return {"locale": locale, "accepted": accepted, "refused": refused}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare, synchronize, and verify SoftCloud multilingual source translations."
    )
    parser.add_argument(
        "--locale",
        action="append",
        dest="locales",
        help="Target locale code (e.g. pl, de, es, fr). Defaults to all non-default enabled locales.",
    )
    parser.add_argument(
        "--sync-provenance",
        action="store_true",
        help="Compute and write i18n/<locale>/provenance.json for reviewed translations.",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Verify translation completeness, provenance hashes, and byte-for-byte code preservation.",
    )
    parser.add_argument(
        "--progressive",
        action="store_true",
        help="Allow missing locale pages to be omitted rather than blocking publication.",
    )
    parser.add_argument(
        "--prepare",
        action="store_true",
        help="Draft or incrementally update changed sections/cells using GEMINI_API_KEY and record provenance.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-translate every section of the selected documents (human-edited sections still conflict).",
    )
    parser.add_argument(
        "--overwrite-human-edits",
        action="store_true",
        help="Allow --prepare to replace unaccepted human edits. Never used by automation.",
    )
    parser.add_argument(
        "--reassess-policy",
        action="store_true",
        help="Re-translate documents whose glossary/translation policy fingerprint is outdated.",
    )
    parser.add_argument(
        "--accept-reviewed",
        action="store_true",
        help="Validate and record human-edited localized text as 'reviewed' (never automatic).",
    )
    parser.add_argument(
        "--doc",
        action="append",
        dest="only_docs",
        help="Restrict --prepare/--accept-reviewed to this published document (repeatable).",
    )
    parser.add_argument("--report", default="", help="Write a JSON report of the run to this path.")
    parser.add_argument(
        "--revision-state",
        default="reviewed",
        choices=("reviewed", "draft"),
        help="Revision state recorded by --sync-provenance (default: reviewed; 'approved' is a human merge decision).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = Path.cwd().resolve()
    locales_cfg = load_locales_config(root)
    default_locale = str(locales_cfg.get("default_locale", "en"))
    enabled_locales = get_enabled_locales(locales_cfg)

    target_locales = args.locales or [
        code for code in enabled_locales.keys() if code != default_locale
    ]
    for code in target_locales:
        if code not in enabled_locales or code == default_locale:
            raise SystemExit(f"Invalid target locale {code!r}: must be an enabled non-default locale.")
    docs = discover_source_documents(root)
    only_docs = set(args.only_docs) if args.only_docs else None
    if only_docs and not only_docs <= set(docs):
        raise SystemExit(f"Unknown published document(s): {sorted(only_docs - set(docs))}")

    if args.sync_provenance:
        for locale in target_locales:
            old = _load_existing_provenance(
                root / str(enabled_locales[locale].get("source_dir", f"i18n/{locale}")) / "provenance.json"
            )
            manifest = build_provenance_manifest(
                root,
                locale,
                docs,
                revision_state=args.revision_state,
                record_docs=only_docs,
                old_manifest=old,
                progressive=args.progressive,
            )
            loc_dir = root / str(enabled_locales[locale].get("source_dir", f"i18n/{locale}"))
            prov_path = loc_dir / "provenance.json"
            atomic_write_json(prov_path, manifest)
            print(
                f"[OK] Wrote {prov_path.relative_to(root)} "
                f"({len(docs)} documents, state={args.revision_state}, sha256={manifest['provenance_sha256'][:12]})"
            )

    reports: list[dict[str, Any]] = []
    failed = False
    if args.accept_reviewed:
        for locale in target_locales:
            rep = accept_reviewed_translations(root, locale, docs, only_docs)
            reports.append({"accept_reviewed": rep})
            print(f"[{locale}] accepted={rep['accepted']} refused={rep['refused']}")
            failed = failed or bool(rep["refused"])

    if args.prepare:
        # The key is required lazily: a fully current locale makes zero API calls and needs no credentials.
        api_key = os.environ.get("GEMINI_API_KEY", "").strip()
        glossary = load_glossary(root)
        for locale in target_locales:
            try:
                _, rep = update_locale_translations(
                    root=root,
                    locale=locale,
                    docs=docs,
                    glossary=glossary,
                    api_key=api_key,
                    force=args.force,
                    overwrite_human_edits=args.overwrite_human_edits,
                    reassess_policy=args.reassess_policy,
                    only_docs=only_docs,
                )
            except FatalTranslationError as exc:
                raise SystemExit(f"[{locale}] fatal translation error: {exc}")
            reports.append(rep)
            print(
                f"[{locale}] generated={rep['generated']} refreshed={rep['refreshed']} "
                f"conflicts={list(rep['conflicts'])} failed={list(rep['failed'])} "
                f"api_calls={rep['translate_calls']}"
            )
            failed = failed or bool(rep["failed"])

    if args.report:
        atomic_write_json(Path(args.report), {"reports": reports})
    if failed:
        return 1

    if args.check_only or not (args.sync_provenance or args.prepare):
        all_errors: list[str] = []
        for locale in target_locales:
            all_errors.extend(check_locale_provenance(root, locale, docs, progressive=args.progressive))
        if all_errors:
            for err in all_errors:
                print(f"ERROR: {err}", file=sys.stderr)
            raise SystemExit(f"Translation provenance check failed with {len(all_errors)} error(s).")
        print(
            f"[OK] Verified translation provenance & byte-for-byte code preservation "
            f"across {len(target_locales)} locales ({', '.join(target_locales)}) and {len(docs)} documents."
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
