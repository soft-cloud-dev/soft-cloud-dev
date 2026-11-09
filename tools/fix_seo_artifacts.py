#!/usr/bin/env python3
"""
fix_seo_artifacts.py
---------------------
Multilingual SEO and accessibility post-build processor for SoftCloud MyST documentation sites.
Ensures:
1. robots.txt declares canonical domain and unified Sitemap URL.
2. Every built HTML page across all locales has:
   - Accurate `<html lang="...">` attribute matching its locale (`en`, `pl`, `de`, `es`, `fr`).
   - Self-referencing `<link rel="canonical" href="..." />`.
   - Reciprocal `<link rel="alternate" hreflang="..." href="..." />` for all available translations
     plus `hreflang="x-default"` pointing to the authoritative English URL.
3. One unified `/sitemap.xml` at the root of the combined artifact containing all localized canonical
   URLs and reciprocal `<xhtml:link rel="alternate" hreflang="..." href="..." />` annotations per
   Google's multilingual sitemap specification.
"""

from __future__ import annotations

import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from i18n_utils import (
    SEARCH_LABELS,
    atomic_write_text,
    canonical_url_for_page,
    get_enabled_locales,
    load_locales_config,
)


def _infer_locale_and_slug(
    rel_html_path: str,
    enabled_locales: dict[str, dict[str, Any]],
    default_locale: str,
) -> tuple[str, str]:
    """Infer (locale_code, page_slug) from a path relative to _build/html."""
    norm = Path(rel_html_path).as_posix().lstrip("./")
    parts = norm.split("/")

    matched_locale = default_locale
    remainder_parts = parts
    if parts:
        first = parts[0]
        for code, info in enabled_locales.items():
            if code == default_locale:
                continue
            prefix = str(info.get("prefix", f"/{code}")).strip("/")
            if first == prefix:
                matched_locale = code
                remainder_parts = parts[1:]
                break

    rem = "/".join(remainder_parts)
    if rem in ("", "index.html"):
        slug = ""
    elif rem.endswith("/index.html"):
        slug = rem[: -len("/index.html")]
    elif rem.endswith(".html"):
        slug = rem[: -len(".html")]
    else:
        slug = rem
    return matched_locale, slug


def _update_html_seo_head(
    html_text: str,
    html_lang: str,
    canonical_url: str,
    alternates: list[tuple[str, str]],
) -> str:
    """Update <html lang="...">, self-referencing canonical, and reciprocal hreflang links."""
    # 1. Set or update <html ... lang="...">
    def _replace_html_tag(match: re.Match[str]) -> str:
        attrs = match.group(1)
        if re.search(r'\blang\s*=\s*["\'][^"\']*["\']', attrs, flags=re.IGNORECASE):
            attrs = re.sub(
                r'\blang\s*=\s*["\'][^"\']*["\']',
                f'lang="{html_lang}"',
                attrs,
                flags=re.IGNORECASE,
            )
        else:
            attrs = f'{attrs} lang="{html_lang}"'
        return f"<html{attrs}>"

    if re.search(r"<html\b[^>]*>", html_text, flags=re.IGNORECASE):
        html_text = re.sub(r"<html\b([^>]*)>", _replace_html_tag, html_text, count=1, flags=re.IGNORECASE)

    # 2. Remove existing canonical or alternate hreflang tags to avoid duplicates
    html_text = re.sub(
        r'\s*<link\b[^>]*\brel\s*=\s*["\']canonical["\'][^>]*>\s*',
        "\n",
        html_text,
        flags=re.IGNORECASE,
    )
    html_text = re.sub(
        r'\s*<link\b[^>]*\bhreflang\s*=\s*["\'][^"\']+["\'][^>]*>\s*',
        "\n",
        html_text,
        flags=re.IGNORECASE,
    )

    seo_lines = [f'  <link rel="canonical" href="{canonical_url}" />']
    for hreflang, href in alternates:
        seo_lines.append(f'  <link rel="alternate" hreflang="{hreflang}" href="{href}" />')
    seo_block = "\n".join(seo_lines) + "\n"

    if "</head>" in html_text:
        html_text = html_text.replace("</head>", f"{seo_block}</head>", 1)
    return html_text


def fix_html_accessibility(
    html_text: str,
    loc_code: str = "en",
    ui: dict[str, Any] | None = None,
) -> str:
    """Ensure interactive controls, particularly button.myst-search-bar, have discernible accessible text.

    Resolves Lighthouse audit 'Buttons must have discernible text' by guaranteeing:
    1. aria-label and title attributes on button.myst-search-bar.
    2. A visually hidden .sr-only span with the localized search label inside the button,
       ensuring assistive tech and AI agents detect the button name even on mobile viewports
       where the placeholder span is hidden via CSS (.hidden.sm:block).
    """
    search_label = str((ui and ui.get("search")) or SEARCH_LABELS.get(loc_code, "Search"))

    def _patch_search_button(match: re.Match[str]) -> str:
        open_tag = match.group(1)
        inner = match.group(2)
        close_tag = match.group(3)

        if re.search(r'\baria-label\s*=', open_tag, re.IGNORECASE):
            open_tag = re.sub(
                r'\baria-label\s*=\s*["\'][^"\']*["\']',
                f'aria-label="{search_label}"',
                open_tag,
                count=1,
                flags=re.IGNORECASE,
            )
        else:
            open_tag = re.sub(
                r'(<button\b)',
                rf'\1 aria-label="{search_label}"',
                open_tag,
                count=1,
            )

        if re.search(r'\btitle\s*=', open_tag, re.IGNORECASE):
            open_tag = re.sub(
                r'\btitle\s*=\s*["\'][^"\']*["\']',
                f'title="{search_label}"',
                open_tag,
                count=1,
                flags=re.IGNORECASE,
            )
        else:
            open_tag = re.sub(
                r'(<button\b)',
                rf'\1 title="{search_label}"',
                open_tag,
                count=1,
            )

        sr_span = f'<span class="sr-only">{search_label}</span>'
        if re.search(r'<span\b[^>]*\bclass="[^"]*\bsr-only\b[^"]*"[^>]*>.*?</span>', inner, re.IGNORECASE | re.DOTALL):
            inner = re.sub(
                r'<span\b[^>]*\bclass="[^"]*\bsr-only\b[^"]*"[^>]*>.*?</span>',
                sr_span,
                inner,
                count=1,
                flags=re.IGNORECASE | re.DOTALL,
            )
        elif "sr-only" not in inner:
            placeholder_re = re.compile(
                r'(<span\b[^>]*\bclass="[^"]*\bmyst-search-text-placeholder\b[^"]*"[^>]*>)',
                re.IGNORECASE,
            )
            if placeholder_re.search(inner):
                inner = placeholder_re.sub(rf"{sr_span}\1", inner, count=1)
            else:
                inner = sr_span + inner

        return f"{open_tag}{inner}{close_tag}"

    button_re = re.compile(
        r'(<button\b[^>]*\bclass="[^"]*\bmyst-search-bar\b[^"]*"[^>]*>)(.*?)(</button>)',
        re.DOTALL | re.IGNORECASE,
    )
    return button_re.sub(_patch_search_button, html_text)


def process_site(domain: str, html_dir: str) -> None:
    domain = domain.rstrip("/")
    html_root = Path(html_dir).resolve()
    if not html_root.is_dir():
        print(f"Error: {html_dir} does not exist", file=sys.stderr)
        sys.exit(1)

    repo_root = TOOLS_DIR.parent
    locales_cfg = load_locales_config(repo_root)
    default_locale = str(locales_cfg.get("default_locale", "en"))
    enabled_locales = get_enabled_locales(locales_cfg)

    # 1. robots.txt
    robots_path = html_root / "robots.txt"
    robots_content = f"User-agent: *\nAllow: /\nSitemap: {domain}/sitemap.xml\n"
    atomic_write_text(robots_path, robots_content)
    print(f"[OK] Written {robots_path} with Sitemap: {domain}/sitemap.xml")

    # 2. Discover all HTML files and group available translations by page slug
    html_files: list[tuple[Path, str, str]] = []
    slug_to_locales: dict[str, dict[str, str]] = {}

    for path in sorted(html_root.rglob("*.html")):
        rel = path.relative_to(html_root).as_posix()
        if path.name.startswith("404") or path.name.startswith("_") or "_locales" in path.parts:
            continue
        loc_code, slug = _infer_locale_and_slug(rel, enabled_locales, default_locale)
        prefix = str(enabled_locales[loc_code].get("prefix", ""))
        can_url = canonical_url_for_page(domain, prefix, slug)
        html_files.append((path, loc_code, slug))
        slug_to_locales.setdefault(slug, {})[loc_code] = can_url

    # 3. Update every HTML file with <html lang="...">, self-referencing canonical, and reciprocal hreflang
    updated_pages = 0
    for path, loc_code, slug in html_files:
        loc_info = enabled_locales[loc_code]
        html_lang = str(loc_info.get("html_lang", loc_code))
        prefix = str(loc_info.get("prefix", ""))
        self_canonical = canonical_url_for_page(domain, prefix, slug)

        available_map = slug_to_locales.get(slug, {loc_code: self_canonical})
        alternates: list[tuple[str, str]] = []
        for alt_code in enabled_locales:
            if alt_code in available_map:
                alt_hreflang = str(enabled_locales[alt_code].get("hreflang", alt_code))
                alternates.append((alt_hreflang, available_map[alt_code]))
        if default_locale in available_map:
            alternates.append(("x-default", available_map[default_locale]))

        raw_html = path.read_text(encoding="utf-8")
        raw_html = re.sub(r"https?://localhost:3000/?", f"{domain}/", raw_html)
        updated_html = _update_html_seo_head(raw_html, html_lang, self_canonical, alternates)
        updated_html = fix_html_accessibility(updated_html, loc_code, loc_info.get("ui"))
        atomic_write_text(path, updated_html)
        updated_pages += 1

    print(
        f"[OK] Updated <html lang>, canonical, hreflang, and button accessibility in {updated_pages} HTML pages"
    )

    # 4. Remove any nested per-locale sitemap.xml or robots.txt so there is a single unified root sitemap
    for code, info in enabled_locales.items():
        if code == default_locale:
            continue
        prefix = str(info.get("prefix", f"/{code}")).strip("/")
        for extra_name in ("sitemap.xml", "robots.txt", "sitemap_style.xsl"):
            extra_file = html_root / prefix / extra_name
            if extra_file.is_file():
                extra_file.unlink()

    # 5. Generate unified multilingual sitemap.xml at root of html_root
    sitemap_path = html_root / "sitemap.xml"
    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">',
    ]

    all_entries: list[tuple[str, list[tuple[str, str]]]] = []
    for slug in sorted(slug_to_locales.keys()):
        available_map = slug_to_locales[slug]
        alternates = []
        for alt_code in enabled_locales:
            if alt_code in available_map:
                alt_hreflang = str(enabled_locales[alt_code].get("hreflang", alt_code))
                alternates.append((alt_hreflang, available_map[alt_code]))
        if default_locale in available_map:
            alternates.append(("x-default", available_map[default_locale]))

        for loc_code in enabled_locales:
            if loc_code in available_map:
                all_entries.append((available_map[loc_code], alternates))

    for loc_url, alternates in all_entries:
        xml_lines.append("  <url>")
        xml_lines.append(f"    <loc>{loc_url}</loc>")
        for hreflang, href in alternates:
            xml_lines.append(
                f'    <xhtml:link rel="alternate" hreflang="{hreflang}" href="{href}" />'
            )
        xml_lines.append("  </url>")

    xml_lines.append("</urlset>\n")
    sitemap_xml_text = "\n".join(xml_lines)

    # Validate well-formed XML via ElementTree
    ET.fromstring(sitemap_xml_text.encode("utf-8"))
    atomic_write_text(sitemap_path, sitemap_xml_text)
    print(
        f"[OK] Generated unified multilingual {sitemap_path} with {len(all_entries)} localized URLs"
    )


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: fix_seo_artifacts.py <canonical_domain_url> <html_output_directory>")
        print("Example: fix_seo_artifacts.py https://my.softcloud.dev _build/html")
        sys.exit(1)
    process_site(sys.argv[1], sys.argv[2])
