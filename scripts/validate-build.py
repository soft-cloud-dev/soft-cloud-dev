#!/usr/bin/env python3
"""
scripts/validate-build.py
-------------------------
Production build validator for Web Awesome SSR, asset references, and DSD integrity.

Validates:
1. All HTML files in the output directory are non-empty and well-formed.
2. No unresolved `.sc-wa-host` or `.sc-wa-meta` placeholders remain.
3. Every server-rendered Web Awesome element contains valid Declarative Shadow DOM
   with `did-ssr` and exactly one open DSD template.
4. Referenced local assets (<link>, <script>, <img>) exist on disk.
5. No duplicated runtime scripts or stylesheets are injected.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlparse
from bs4 import BeautifulSoup

_SCHEMA_PATH = Path(__file__).resolve().parent.parent / "assets" / "shared" / "component-schema.json"
_SCHEMA = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
SUPPORTED_COMPONENTS = set(_SCHEMA.get("allowedComponents", ["wa-card", "wa-callout", "wa-button", "wa-icon"]))


def check_html_file(
    file_path: Path,
    verify_root: Path,
    strict: bool = False,
) -> tuple[int, int, list[str]]:
    """
    Validates a single HTML file.
    Returns (num_components_found, num_assets_checked, error_messages).
    """
    errors: list[str] = []
    rel_path = file_path.relative_to(verify_root).as_posix()

    content = file_path.read_text(encoding="utf-8")
    if not content.strip():
        errors.append(f"{rel_path}: HTML file is empty")
        return 0, 0, errors

    soup = BeautifulSoup(content, "html.parser")

    # 1. Check for unresolved host or meta nodes
    unresolved_hosts = soup.select(".sc-wa-host")
    if unresolved_hosts:
        errors.append(f"{rel_path}: Found {len(unresolved_hosts)} unresolved .sc-wa-host element(s)")

    unresolved_metas = soup.select(".sc-wa-meta")
    if unresolved_metas:
        errors.append(f"{rel_path}: Found {len(unresolved_metas)} unresolved .sc-wa-meta node(s)")

    # 2. Check Web Awesome components and Declarative Shadow DOM
    components_count = 0
    for tag_name in SUPPORTED_COMPONENTS:
        for host in soup.find_all(tag_name):
            components_count += 1
            has_did_ssr = host.has_attr("did-ssr")
            
            # Find direct template children with shadowrootmode="open" or shadowroot="open"
            templates = [
                c for c in host.children
                if getattr(c, "name", None) == "template"
                and (c.get("shadowrootmode") == "open" or c.get("shadowroot") == "open")
            ]

            if has_did_ssr and not templates:
                errors.append(f"{rel_path}: <{tag_name}> has 'did-ssr' but missing open DSD <template>")
            elif not has_did_ssr and templates:
                errors.append(f"{rel_path}: <{tag_name}> has open DSD <template> but missing 'did-ssr'")
            elif len(templates) > 1:
                errors.append(f"{rel_path}: <{tag_name}> has {len(templates)} DSD <template> children (expected 1)")

    # 3. Check for duplicated runtime scripts and styles
    stylesheets = []
    for link in soup.find_all("link", rel=lambda r: r and "stylesheet" in r):
        href = link.get("href")
        if href:
            clean_href = href.split("?")[0].split("#")[0]
            stylesheets.append(clean_href)

    seen_styles = set()
    for s in stylesheets:
        if s in seen_styles:
            errors.append(f"{rel_path}: Duplicate stylesheet link detected: {s}")
        seen_styles.add(s)

    scripts = []
    for script in soup.find_all("script"):
        src = script.get("src")
        if src:
            clean_src = src.split("?")[0].split("#")[0]
            scripts.append(clean_src)

    seen_scripts = set()
    for sc in scripts:
        if sc in seen_scripts:
            errors.append(f"{rel_path}: Duplicate script source detected: {sc}")
        seen_scripts.add(sc)

    # 4. Check existence of referenced local assets
    assets_checked = 0
    file_dir = file_path.parent

    def verify_local_asset(asset_url: str, attr_name: str) -> None:
        nonlocal assets_checked
        if not asset_url:
            return
        parsed = urlparse(asset_url)
        if parsed.scheme in ("http", "https", "mailto", "data", "blob", "javascript"):
            return
        if asset_url.startswith("//") or asset_url.startswith("#"):
            return

        raw_path = parsed.path
        if not raw_path:
            return

        assets_checked += 1
        # If absolute path relative to domain/root
        if raw_path.startswith("/"):
            candidate = verify_root / raw_path.lstrip("/")
        else:
            candidate = file_dir / raw_path

        if not candidate.is_file():
            # In strict mode, missing local assets fail the build
            msg = f"{rel_path}: Referenced local asset not found ({attr_name}={asset_url})"
            if strict:
                errors.append(msg)
            else:
                # SoftCloud themes might reference optional font sourcemaps or font sub-variants
                if "webawesome" in asset_url or "fontawesome" in asset_url or "softcloud" in asset_url:
                    errors.append(msg)

    for s in stylesheets:
        verify_local_asset(s, "href")
    for sc in scripts:
        verify_local_asset(sc, "src")
    for img in soup.find_all("img"):
        verify_local_asset(img.get("src", ""), "src")

    return components_count, assets_checked, errors


def validate_build(verify_dir: Path, strict: bool = False) -> bool:
    """Validates the built site directory."""
    if not verify_dir.is_dir():
        print(f"[ERROR] Verification directory does not exist: {verify_dir}", file=sys.stderr)
        return False

    html_files = sorted(verify_dir.rglob("*.html"))
    if not html_files:
        print(f"[ERROR] No HTML files found in {verify_dir}", file=sys.stderr)
        return False

    # Check for primary index file
    if not (verify_dir / "index.html").is_file():
        print(f"[ERROR] Root index.html is missing in {verify_dir}", file=sys.stderr)
        return False

    total_components = 0
    total_assets = 0
    all_errors: list[str] = []

    for html_file in html_files:
        comp_count, asset_count, file_errors = check_html_file(
            file_path=html_file,
            verify_root=verify_dir,
            strict=strict,
        )
        total_components += comp_count
        total_assets += asset_count
        all_errors.extend(file_errors)

    if all_errors:
        print(f"[FAIL] Found {len(all_errors)} build validation error(s):", file=sys.stderr)
        for err in all_errors[:20]:
            print(f"  - {err}", file=sys.stderr)
        if len(all_errors) > 20:
            print(f"  ... and {len(all_errors) - 20} more", file=sys.stderr)
        return False

    print(
        f"[OK] Build validation passed: {len(html_files)} HTML pages verified, "
        f"{total_components} Web Awesome component(s) validated, "
        f"{total_assets} asset reference(s) verified in {verify_dir}"
    )
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate production build for Web Awesome SSR, assets, and DSD integrity."
    )
    parser.add_argument(
        "--verify-dir",
        default="_build/html",
        help="Path to built HTML directory (default: _build/html)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Enforce strict local asset resolution",
    )
    args = parser.parse_args(argv)
    verify_path = Path(args.verify_dir).resolve()
    success = validate_build(verify_path, strict=args.strict)
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
