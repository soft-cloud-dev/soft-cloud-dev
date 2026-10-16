#!/usr/bin/env python3
"""
translate_sources.py
--------------------
Translation preparation and provenance verification workflow for SoftCloud multilingual docs.

Supports two distinct workflows per the Multilingual Implementation Memorandum:
1. Translation preparation (`--prepare` / `--sync-provenance`):
   - Uses Gemini (`gemini-2.5-flash`) with `i18n/glossary.yml` terminology rules to draft or
     incrementally update changed sections while preserving code blocks, executable cells,
     notebook metadata, math expressions, directives, and links byte-for-byte.
   - Records source hashes, section-level hashes, code fingerprints, and revision state in
     `i18n/<locale>/provenance.json`.
2. Publication verification (`--check-only`):
   - Strictly verifies that all translated documents exist, match their recorded `source_sha256`,
     `section_hashes`, and `translated_sha256` in `i18n/<locale>/provenance.json`, have
     `revision_state == "approved"`, and preserve all code blocks and notebook code cells/metadata
     byte-for-byte against the authoritative English source.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from i18n_utils import (
    atomic_write_json,
    extract_code_fingerprint,
    extract_fenced_code_blocks_from_markdown,
    extract_markdown_links,
    get_enabled_locales,
    load_glossary,
    load_locales_config,
    load_yaml_file,
    sha256_file,
    sha256_json,
    sha256_text,
    split_markdown_sections,
)

PROVENANCE_SCHEMA_VERSION = "1.0"
DEFAULT_TRANSLATION_MODEL = "gemini-2.5-flash"


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


def verify_document_preservation(en_path: Path, loc_path: Path, locale: str) -> list[str]:
    """Verify code blocks, notebook cells/metadata, and link targets between English and localized docs."""
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
        en_links = extract_markdown_links(en_text)
        loc_links = extract_markdown_links(loc_text)
        if en_links != loc_links:
            errors.append(
                f"[{locale}] Markdown link targets altered in {loc_path.name}: "
                f"expected {en_links}, got {loc_links}"
            )
        _, en_secs = split_markdown_sections(en_text)
        _, loc_secs = split_markdown_sections(loc_text)
        if len(en_secs) != len(loc_secs):
            errors.append(
                f"[{locale}] Markdown section count mismatch in {loc_path.name}: "
                f"expected {len(en_secs)}, got {len(loc_secs)}"
            )
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
    return errors


def build_provenance_manifest(
    root: Path,
    locale: str,
    docs: list[str],
    revision_state: str = "approved",
) -> dict[str, Any]:
    """Build deterministic provenance.json structure for a target locale."""
    locales_cfg = load_locales_config(root)
    locales_map = get_enabled_locales(locales_cfg)
    if locale not in locales_map:
        raise ValueError(f"Unknown or disabled locale: {locale}")
    locale_info = locales_map[locale]
    loc_root = root / str(locale_info.get("source_dir", f"i18n/{locale}"))
    glossary = load_glossary(root)
    glossary_sha = sha256_json(glossary)

    documents_meta: dict[str, Any] = {}
    for rel_doc in docs:
        en_path = root / rel_doc
        loc_path = loc_root / rel_doc
        if not en_path.is_file():
            raise FileNotFoundError(f"Missing authoritative source document: {en_path}")
        if not loc_path.is_file():
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

        documents_meta[rel_doc] = {
            "source_path": rel_doc,
            "localized_path": loc_path.relative_to(root).as_posix(),
            "source_sha256": sha256_file(en_path),
            "translated_sha256": sha256_file(loc_path),
            "code_fingerprint_sha256": en_fp["sha256"],
            "localized_code_fingerprint_sha256": loc_fp["sha256"],
            "code_block_count": en_fp["count"],
            "revision_state": revision_state,
            "sections": section_records,
        }

    manifest: dict[str, Any] = {
        "schema_version": PROVENANCE_SCHEMA_VERSION,
        "locale": locale,
        "source_locale": str(locales_cfg.get("default_locale", "en")),
        "glossary_sha256": glossary_sha,
        "documents": documents_meta,
    }
    manifest["provenance_sha256"] = sha256_json(manifest)
    return manifest


def check_locale_provenance(root: Path, locale: str, docs: list[str]) -> list[str]:
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
            errors.append(f"[{locale}] Missing translated document: {loc_path.relative_to(root)}")
            continue

        errors.extend(verify_document_preservation(en_path, loc_path, locale))

        doc_entry = prov_docs.get(rel_doc)
        if not isinstance(doc_entry, dict):
            errors.append(f"[{locale}] Missing provenance entry for document '{rel_doc}'")
            continue

        if doc_entry.get("revision_state") != "approved":
            errors.append(
                f"[{locale}] Document '{rel_doc}' has revision_state={doc_entry.get('revision_state')!r} "
                "(expected 'approved')"
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


def translate_section_with_gemini(
    section_text: str,
    target_locale: str,
    language_name: str,
    glossary: dict[str, Any],
    api_key: str,
    model: str = DEFAULT_TRANSLATION_MODEL,
) -> str:
    """Translate a Markdown section using Gemini while preserving code blocks and MyST directives byte-for-byte."""
    invariants = ", ".join(str(x) for x in glossary.get("invariant_terms", []))
    term_map = {
        entry["en"]: entry.get(target_locale, entry["en"])
        for entry in glossary.get("terms", [])
        if isinstance(entry, dict) and "en" in entry
    }
    prompt = (
        f"Translate the following MyST Markdown section from English into {language_name} ({target_locale}).\n"
        "STRICT RULES:\n"
        "1. Preserve ALL fenced code blocks, inline code spans, URLs, link targets, and MyST directive names/attributes byte-for-byte.\n"
        "2. Preserve mathematical expressions byte-for-byte.\n"
        f"3. Keep these technical identifiers untranslated: {invariants}\n"
        f"4. Preferred domain terminology in {language_name}: {json.dumps(term_map, ensure_ascii=False)}\n"
        "5. Output ONLY the translated Markdown text without wrapping it in outer code fences.\n\n"
        f"SOURCE SECTION:\n{section_text}"
    )
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.1},
    }
    req = urllib.request.Request(
        url=url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    candidates = body.get("candidates") or []
    parts = candidates[0].get("content", {}).get("parts", []) if candidates else []
    translated = "".join(p.get("text", "") for p in parts if isinstance(p, dict)).strip()
    if not translated:
        raise RuntimeError(f"Empty translation response from Gemini for locale {target_locale}")
    return translated + "\n"


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
        "--prepare",
        action="store_true",
        help="Draft or update changed sections using GEMINI_API_KEY and record draft provenance.",
    )
    parser.add_argument(
        "--revision-state",
        default="approved",
        choices=("approved", "draft"),
        help="Revision state to record when running --sync-provenance (default: approved).",
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
    docs = discover_source_documents(root)

    if args.sync_provenance:
        for locale in target_locales:
            manifest = build_provenance_manifest(
                root, locale, docs, revision_state=args.revision_state
            )
            loc_dir = root / str(enabled_locales[locale].get("source_dir", f"i18n/{locale}"))
            prov_path = loc_dir / "provenance.json"
            atomic_write_json(prov_path, manifest)
            print(
                f"[OK] Wrote {prov_path.relative_to(root)} "
                f"({len(docs)} documents, state={args.revision_state}, sha256={manifest['provenance_sha256'][:12]})"
            )

    if args.prepare:
        api_key = os.environ.get("GEMINI_API_KEY", "").strip()
        if not api_key:
            raise SystemExit("GEMINI_API_KEY is required for --prepare draft translation generation.")
        glossary = load_glossary(root)
        for locale in target_locales:
            loc_info = enabled_locales[locale]
            lang_name = str(loc_info.get("english_name", locale))
            loc_dir = root / str(loc_info.get("source_dir", f"i18n/{locale}"))
            for rel_doc in docs:
                en_path = root / rel_doc
                loc_path = loc_dir / rel_doc
                if not loc_path.is_file() and en_path.suffix == ".md":
                    loc_path.parent.mkdir(parents=True, exist_ok=True)
                    front, secs = split_markdown_sections(en_path.read_text(encoding="utf-8"))
                    translated_secs = [
                        translate_section_with_gemini(s["content"], locale, lang_name, glossary, api_key)
                        for s in secs
                    ]
                    loc_path.write_text(front + "\n".join(translated_secs), encoding="utf-8")
            manifest = build_provenance_manifest(root, locale, docs, revision_state="draft")
            atomic_write_json(loc_dir / "provenance.json", manifest)
            print(f"[OK] Prepared translations and provenance for locale '{locale}'")

    if args.check_only or not (args.sync_provenance or args.prepare):
        all_errors: list[str] = []
        for locale in target_locales:
            all_errors.extend(check_locale_provenance(root, locale, docs))
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
