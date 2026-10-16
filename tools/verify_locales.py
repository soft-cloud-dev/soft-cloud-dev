#!/usr/bin/env python3
"""
verify_locales.py
-----------------
Comprehensive validator for SoftCloud multilingual configuration, translations,
code/notebook preservation, localized TTS audio manifests, SEO metadata, and
combined build artifacts.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import generate_audio as ga
from i18n_utils import (
    canonical_url_for_page,
    get_enabled_locales,
    load_glossary,
    load_locales_config,
    load_yaml_file,
    page_slug_from_rel_path,
)
from translate_sources import check_locale_provenance, discover_source_documents

API_KEY_LEAK_RE = re.compile(r"AIza[0-9A-Za-z_-]{35}")


def verify_locales_configuration(root: Path) -> list[str]:
    """Validate i18n/locales.yml and i18n/glossary.yml structure and completeness."""
    errors: list[str] = []
    try:
        locales_cfg = load_locales_config(root)
    except Exception as exc:
        return [f"Failed to load i18n/locales.yml: {exc}"]

    if not locales_cfg.get("schema_version") and locales_cfg.get("version") != 1:
        errors.append("i18n/locales.yml must declare schema_version or version")

    default_locale = locales_cfg.get("default_locale")
    enabled = get_enabled_locales(locales_cfg)
    if not default_locale or default_locale not in enabled:
        errors.append(f"default_locale {default_locale!r} must be an enabled locale in i18n/locales.yml")

    seen_prefixes: set[str] = set()
    required_ui_keys = {
        "language_label",
        "switch_language",
        "translation_unavailable",
        "listen",
        "play",
        "pause",
        "previous_section",
        "next_section",
        "playback_rate",
        "narration_unavailable",
    }

    for code, info in enabled.items():
        prefix = info.get("prefix")
        if not isinstance(prefix, str):
            errors.append(f"[{code}] Missing string prefix in i18n/locales.yml")
        else:
            if code == default_locale and prefix != "":
                errors.append(f"[{code}] Default locale must have empty prefix '', got {prefix!r}")
            if code != default_locale and (not prefix.startswith("/") or prefix.endswith("/")):
                errors.append(f"[{code}] Non-default locale prefix must look like '/{code}', got {prefix!r}")
            if prefix in seen_prefixes:
                errors.append(f"[{code}] Duplicate locale prefix {prefix!r}")
            seen_prefixes.add(prefix)

        ui = info.get("ui", {})
        if not isinstance(ui, dict):
            errors.append(f"[{code}] ui must be a mapping in i18n/locales.yml")
        else:
            missing_ui = required_ui_keys - set(ui.keys())
            if missing_ui:
                errors.append(f"[{code}] Missing ui keys: {sorted(missing_ui)}")

    try:
        glossary = load_glossary(root)
        domain_terms = glossary.get("domain_terms", {})
        if isinstance(domain_terms, dict):
            for term_id, term_entry in domain_terms.items():
                if isinstance(term_entry, dict):
                    for code in enabled:
                        if not term_entry.get(code):
                            errors.append(
                                f"Glossary term {term_id!r} missing translation for locale '{code}'"
                            )
    except Exception as exc:
        errors.append(f"Failed to load i18n/glossary.yml: {exc}")

    return errors


def verify_no_api_key_leaks(root: Path, build_dir: Path | None = None) -> list[str]:
    """Ensure no Gemini API keys or secret tokens are present in widgets, i18n, audio, or built HTML."""
    errors: list[str] = []
    scan_roots = [root / "widgets", root / "i18n", root / "audio"]
    if build_dir and build_dir.is_dir():
        scan_roots.append(build_dir)

    for sroot in scan_roots:
        if not sroot.exists():
            continue
        for fpath in sroot.rglob("*"):
            if not fpath.is_file() or fpath.suffix in (".mp3", ".png", ".ico", ".svg", ".whl"):
                continue
            try:
                text = fpath.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            if API_KEY_LEAK_RE.search(text):
                errors.append(f"Potential API key leak detected in {fpath.relative_to(root)}")
    return errors


def verify_built_html_artifact(root: Path, build_dir: Path) -> list[str]:
    """Verify combined _build/html routes, <html lang>, canonical URLs, reciprocal hreflang, and sitemap.xml."""
    errors: list[str] = []
    if not build_dir.is_dir():
        return [f"Built HTML directory does not exist: {build_dir}"]

    locales_cfg = load_locales_config(root)
    default_locale = str(locales_cfg.get("default_locale", "en"))
    domain = str(locales_cfg.get("canonical_domain", "https://my.softcloud.dev")).rstrip("/")
    enabled_locales = get_enabled_locales(locales_cfg)
    docs = discover_source_documents(root)

    # 1. Verify route-manifest.json
    route_manifest_path = build_dir / "i18n" / "route-manifest.json"
    if not route_manifest_path.is_file():
        errors.append(f"Missing route manifest in built artifact: {route_manifest_path.relative_to(root)}")

    # 2. Verify widgets exist in built artifact
    for wname in ("language-switcher.mjs", "voice-player.mjs"):
        if not (build_dir / "widgets" / wname).is_file():
            errors.append(f"Missing widget in built artifact: _build/html/widgets/{wname}")

    # 3. Verify every localized page route exists and has valid lang, canonical, and reciprocal hreflang
    expected_sitemap_locs: set[str] = set()
    for rel_doc in docs:
        raw_slug = page_slug_from_rel_path(rel_doc)
        flat_slug = Path(raw_slug).name if raw_slug else ""

        # Detect which slug form (nested vs flat) the build produced in the default locale
        active_slug = raw_slug
        if raw_slug and raw_slug != flat_slug:
            if not (build_dir / raw_slug / "index.html").is_file() and (
                (build_dir / flat_slug / "index.html").is_file()
                or (build_dir / f"{flat_slug}.html").is_file()
            ):
                active_slug = flat_slug

        expected_alternates: dict[str, str] = {}
        for code, info in enabled_locales.items():
            prefix = str(info.get("prefix", ""))
            hreflang = str(info.get("hreflang", code))
            expected_alternates[hreflang] = canonical_url_for_page(domain, prefix, active_slug)
        expected_alternates["x-default"] = canonical_url_for_page(domain, "", active_slug)

        for code, info in enabled_locales.items():
            prefix = str(info.get("prefix", "")).strip("/")
            html_lang = str(info.get("html_lang", code))
            self_canonical = canonical_url_for_page(domain, str(info.get("prefix", "")), active_slug)
            expected_sitemap_locs.add(self_canonical)

            base_sub = (build_dir / prefix) if prefix else build_dir
            if not active_slug:
                candidates = [base_sub / "index.html"]
            else:
                candidates = [base_sub / active_slug / "index.html", base_sub / f"{active_slug}.html"]

            found_html = next((c for c in candidates if c.is_file()), None)
            if found_html is None:
                errors.append(
                    f"[{code}] Missing built HTML route for '{rel_doc}' (checked {[str(c.relative_to(build_dir)) for c in candidates]})"
                )
                continue

            html_text = found_html.read_text(encoding="utf-8")
            # Verify <html ... lang="<html_lang>">
            html_tag_match = re.search(r"<html\b([^>]*)>", html_text, flags=re.IGNORECASE)
            if not html_tag_match or f'lang="{html_lang}"' not in html_tag_match.group(1):
                errors.append(
                    f"[{code}] Missing or wrong <html lang=\"{html_lang}\"> in {found_html.relative_to(build_dir)}"
                )

            # Verify self-referencing canonical
            can_pattern = rf'<link\b[^>]*rel=["\']canonical["\'][^>]*href=["\']{re.escape(self_canonical)}["\']'
            if not re.search(can_pattern, html_text, flags=re.IGNORECASE):
                errors.append(
                    f"[{code}] Missing self-referencing canonical ({self_canonical}) in {found_html.relative_to(build_dir)}"
                )

            # Verify reciprocal hreflang links
            for hlang, hurl in expected_alternates.items():
                alt_pattern = (
                    rf'<link\b[^>]*rel=["\']alternate["\'][^>]*hreflang=["\']{re.escape(hlang)}["\']'
                    rf'[^>]*href=["\']{re.escape(hurl)}["\']'
                )
                if not re.search(alt_pattern, html_text, flags=re.IGNORECASE):
                    errors.append(
                        f"[{code}] Missing hreflang='{hlang}' -> '{hurl}' in {found_html.relative_to(build_dir)}"
                    )

            # Verify language switcher script injection
            if "language-switcher.mjs" not in html_text:
                errors.append(
                    f"[{code}] Language switcher not injected in {found_html.relative_to(build_dir)}"
                )

    # 4. Verify unified root sitemap.xml and absence of duplicate per-locale sitemaps
    sitemap_path = build_dir / "sitemap.xml"
    if not sitemap_path.is_file():
        errors.append("Missing root _build/html/sitemap.xml")
    else:
        try:
            tree = ET.fromstring(sitemap_path.read_bytes())
            ns = {
                "sm": "http://www.sitemaps.org/schemas/sitemap/0.9",
                "xhtml": "http://www.w3.org/1999/xhtml",
            }
            locs = {
                el.text.strip()
                for el in tree.findall("sm:url/sm:loc", ns)
                if el.text and el.text.strip()
            }
            missing_locs = expected_sitemap_locs - locs
            if missing_locs:
                errors.append(f"Unified sitemap.xml is missing canonical URLs: {sorted(missing_locs)}")
        except Exception as exc:
            errors.append(f"Invalid XML in _build/html/sitemap.xml: {exc}")

    for code, info in enabled_locales.items():
        if code == default_locale:
            continue
        prefix = str(info.get("prefix", f"/{code}")).strip("/")
        nested_sitemap = build_dir / prefix / "sitemap.xml"
        if nested_sitemap.exists():
            errors.append(f"Duplicate per-locale sitemap found at {nested_sitemap.relative_to(build_dir)}")

    return errors


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify SoftCloud multilingual configuration, translations, audio manifests, and build output."
    )
    parser.add_argument(
        "--verify-build-dir",
        default="",
        help="Optional built HTML directory (e.g. _build/html) to validate routes, SEO tags, and published audio.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = Path.cwd().resolve()
    errors: list[str] = []

    # 1. Configuration & Glossary
    errors.extend(verify_locales_configuration(root))

    # 2. Translation Provenance & Byte-for-Byte Code Preservation
    locales_cfg = load_locales_config(root)
    default_locale = str(locales_cfg.get("default_locale", "en"))
    enabled_locales = get_enabled_locales(locales_cfg)
    docs = discover_source_documents(root)

    for code in enabled_locales:
        if code == default_locale:
            continue
        errors.extend(check_locale_provenance(root, code, docs))

    # 3. Localized Narration Audio Verification across all enabled locales
    ga_args = ["--all-locales", "--page", "introduction.md", "--check-only"]
    if args.verify_build_dir:
        ga_args.extend(["--verify-build-dir", args.verify_build_dir])
    if ga.main(ga_args) != 0:
        errors.append("Localized audio narration check failed via generate_audio.py")

    # 4. Built HTML Artifact Verification (if requested)
    build_dir = (root / args.verify_build_dir).resolve() if args.verify_build_dir else None
    if build_dir is not None:
        errors.extend(verify_built_html_artifact(root, build_dir))

    # 5. API Key Leak Check
    errors.extend(verify_no_api_key_leaks(root, build_dir))

    if errors:
        for err in errors:
            print(f"[VERIFY FAILURE] {err}", file=sys.stderr)
        return 1

    print(
        f"[OK] Multilingual verification passed across {len(enabled_locales)} locales "
        f"({', '.join(enabled_locales.keys())})"
        + (f" and build artifact {build_dir.relative_to(root)}" if build_dir else "")
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
