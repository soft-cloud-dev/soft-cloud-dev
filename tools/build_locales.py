#!/usr/bin/env python3
"""
build_locales.py
----------------
Isolated multi-locale MyST / Jupyter Book 2 build orchestrator and artifact assembler.

Responsibilities:
1. Stage an isolated workspace per enabled locale under `_build/locales/<locale>/workspace/`
   with a locale-specific `myst.yml`, localized Markdown/Notebook sources, widgets, images,
   and locale-matched narration audio.
2. Execute `jupyter book clean --all --execute -y` and `jupyter book build --html --strict --execute`
    inside each isolated locale workspace with the locale's explicit `BASE_URL` prefix
   (`""` for `en`, `"/pl"`, `"/de"`, `"/es"`, `"/fr"`).
3. Assemble the combined static site artifact into `_build/html/`:
   - English at `_build/html/`
   - Localized builds at `_build/html/<locale>/`
   - Audio assets at both `/audio/<locale>/<page>/` and `/<locale>/audio/<page>/`
   - Route availability manifest at `_build/html/i18n/route-manifest.json`
   - Accessible language switcher widget mounted in every HTML page
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from i18n_utils import (
    atomic_write_json,
    atomic_write_text,
    canonical_url_for_page,
    dump_yaml_text,
    get_enabled_locales,
    load_locales_config,
    load_yaml_file,
    page_slug_from_rel_path,
    route_url_for_page,
    sha256_file,
)
from generate_audio import page_id_from_path


def strip_voice_player_widget(text: str) -> str:
    """Strip MyST {anywidget} blocks referencing voice-player.mjs so un-narrated pages render no audio controls."""
    pattern = re.compile(
        r"```\{anywidget\}\s+[^\n]*voice-player\.mjs[^\n]*\n.*?\n```\s*\n?",
        re.DOTALL,
    )
    return pattern.sub("", text)


def is_page_narration_current(
    root: Path,
    locale_code: str,
    default_locale: str,
    rel_file: str,
) -> bool:
    """Check if narration is fully generated and current for a specific page and locale."""
    is_default = locale_code == default_locale
    audio_dir = root / ("audio" if is_default else f"audio/{locale_code}")
    page_id = page_id_from_path(rel_file)
    page_audio_dir = audio_dir / page_id
    manifest_path = page_audio_dir / "manifest.json"
    if not manifest_path.is_file():
        return False
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("locale") != locale_code:
            return False
        src_file = (root / rel_file) if is_default else (root / "i18n" / locale_code / rel_file)
        if not src_file.is_file():
            return False
        if manifest.get("source_file_sha256") != sha256_file(src_file):
            return False
        t_path = page_audio_dir / str(manifest.get("transcript_file", "transcript.json"))
        if not t_path.is_file():
            return False
        for ch in manifest.get("chunks", []):
            ch_f = page_audio_dir / str(ch.get("audio_file", ""))
            if not ch_f.is_file() or sha256_file(ch_f) != ch.get("audio_sha256"):
                return False
        return True
    except Exception:
        return False


def is_page_translation_current(
    root: Path,
    locale_code: str,
    default_locale: str,
    rel_file: str,
    prov_cache: dict[str, dict[str, Any]],
) -> bool:
    """Check if translation is present and current for a specific page and locale."""
    if locale_code == default_locale:
        return (root / rel_file).is_file()
    loc_file = root / "i18n" / locale_code / rel_file
    if not loc_file.is_file():
        return False
    en_file = root / rel_file
    if not en_file.is_file():
        return False
    prov = prov_cache.get(locale_code)
    if prov is None:
        prov_path = root / "i18n" / locale_code / "provenance.json"
        if prov_path.is_file():
            try:
                prov = json.loads(prov_path.read_text(encoding="utf-8"))
            except Exception:
                prov = {}
        else:
            prov = {}
        prov_cache[locale_code] = prov

    doc_entry = prov.get("documents", {}).get(rel_file)
    if not isinstance(doc_entry, dict):
        return True
    try:
        if doc_entry.get("source_sha256") != sha256_file(en_file):
            return False
        if doc_entry.get("translated_sha256") != sha256_file(loc_file):
            return False
    except Exception:
        return False
    return True


def discover_toc_files(toc: list[dict[str, Any]]) -> list[str]:
    files: list[str] = []
    for entry in toc:
        if not isinstance(entry, dict):
            continue
        if "file" in entry and isinstance(entry["file"], str):
            files.append(entry["file"])
        if "children" in entry and isinstance(entry["children"], list):
            files.extend(discover_toc_files(entry["children"]))
    return files


def build_localized_myst_config(
    base_myst: dict[str, Any],
    locale_code: str,
    locale_info: dict[str, Any],
    staged_files: set[str] | None = None,
) -> dict[str, Any]:
    """Produce a locale-specific myst.yml dictionary preserving all JB2 profile rules."""
    cfg = copy.deepcopy(base_myst)
    project = cfg.setdefault("project", {})
    site_meta = locale_info.get("site", {})
    if isinstance(site_meta, dict):
        if site_meta.get("title"):
            project["title"] = site_meta["title"]
        if site_meta.get("short_title"):
            project["short_title"] = site_meta["short_title"]
        if site_meta.get("description"):
            project["description"] = site_meta["description"]

    toc_titles = (
        site_meta.get("toc_titles", {}) if isinstance(site_meta, dict) else {}
    ) or locale_info.get("toc_titles", {})
    if isinstance(toc_titles, dict) and isinstance(project.get("toc"), list):
        def localize_toc(entries: list[dict[str, Any]]) -> None:
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                if "title" in entry and entry["title"] in toc_titles:
                    entry["title"] = toc_titles[entry["title"]]
                if "children" in entry and isinstance(entry["children"], list):
                    localize_toc(entry["children"])

        localize_toc(project["toc"])

    # Progressive publication: prune TOC entries whose files are not staged for this locale
    if staged_files is not None and isinstance(project.get("toc"), list):
        def prune_toc(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
            pruned: list[dict[str, Any]] = []
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                f = entry.get("file")
                children = entry.get("children")
                new_children = prune_toc(children) if isinstance(children, list) else None
                if f in staged_files or new_children:
                    new_entry = dict(entry)
                    if new_children is not None:
                        new_entry["children"] = new_children
                    pruned.append(new_entry)
            return pruned

        project["toc"] = prune_toc(project["toc"])

    nav_titles = (
        site_meta.get("nav_titles", {}) if isinstance(site_meta, dict) else {}
    ) or locale_info.get("nav_titles", {})
    site = cfg.setdefault("site", {})
    if isinstance(nav_titles, dict) and isinstance(site.get("nav"), list):
        for item in site["nav"]:
            if isinstance(item, dict) and item.get("title") in nav_titles:
                item["title"] = nav_titles[item["title"]]

    return cfg


def compute_locale_base_url(outer_base_url: str, locale_prefix: str) -> str:
    clean_outer = outer_base_url.strip().rstrip("/")
    clean_prefix = ("/" + locale_prefix.strip("/")) if locale_prefix.strip("/") else ""
    combined = f"{clean_outer}{clean_prefix}"
    return combined


def stage_locale_workspace(
    root: Path,
    locale_code: str,
    locale_info: dict[str, Any],
    base_myst: dict[str, Any],
    default_locale: str,
    staging_root: Path,
) -> Path:
    """Create an isolated MyST workspace for a single locale."""
    ws = staging_root / locale_code / "workspace"
    if ws.exists():
        shutil.rmtree(ws)
    ws.mkdir(parents=True, exist_ok=True)

    # 1. Copy TOC source files from authoritative root (en) or i18n/<locale>/
    toc_files = discover_toc_files(base_myst.get("project", {}).get("toc", []))
    source_root = (
        root
        if locale_code == default_locale
        else (root / str(locale_info.get("source_dir", f"i18n/{locale_code}")))
    )

    staged_files: set[str] = set()
    for rel_file in toc_files:
        src_path = source_root / rel_file
        if not src_path.is_file():
            if locale_code != default_locale:
                # Progressive publication: unlocalized source is not staged as a translated route
                continue
            raise FileNotFoundError(
                f"Missing source file for locale '{locale_code}': {src_path.relative_to(root)}"
            )
        dst_path = ws / rel_file
        dst_path.parent.mkdir(parents=True, exist_ok=True)

        # Progressive audio controls: only render voice-player if narration is current
        text_content = src_path.read_text(encoding="utf-8")
        if not is_page_narration_current(root, locale_code, default_locale, rel_file):
            text_content = strip_voice_player_widget(text_content)
        atomic_write_text(dst_path, text_content)
        staged_files.add(rel_file)

    # 2. Write localized myst.yml with pruned TOC matching staged files
    localized_myst = build_localized_myst_config(
        base_myst, locale_code, locale_info, staged_files=staged_files
    )
    atomic_write_text(ws / "myst.yml", dump_yaml_text(localized_myst))

    # 3. Copy static assets (images, widgets, CNAME, sourcemaps)
    for asset_dir_name in ("images", "widgets"):
        src_dir = root / asset_dir_name
        if src_dir.is_dir():
            shutil.copytree(src_dir, ws / asset_dir_name, dirs_exist_ok=True)

    for single_asset in ("CNAME", "thebe-core.min.js.map"):
        src_asset = root / single_asset
        if src_asset.is_file():
            shutil.copy2(src_asset, ws / single_asset)

    # 3.1 Stage assets (plugins, static, python, shared) for Web Awesome SSR
    assets_src = root / "assets"
    if assets_src.is_dir():
        for asset_sub in ("plugins", "static", "python", "shared"):
            sub_src = assets_src / asset_sub
            if sub_src.is_dir():
                shutil.copytree(sub_src, ws / "assets" / asset_sub, dirs_exist_ok=True)

    # 3.2 Stage scripts/lib so plugin imports resolve cleanly in workspace
    scripts_lib_src = root / "scripts" / "lib"
    if scripts_lib_src.is_dir():
        shutil.copytree(scripts_lib_src, ws / "scripts" / "lib", dirs_exist_ok=True)

    # 4. Copy locale-specific audio into workspace/audio/
    locale_audio_src = root / str(
        locale_info.get("audio_dir", "audio" if locale_code == default_locale else f"audio/{locale_code}")
    )
    ws_audio_dst = ws / "audio"
    if locale_audio_src.is_dir():
        ws_audio_dst.mkdir(parents=True, exist_ok=True)
        for child in locale_audio_src.iterdir():
            if child.is_dir() and child.name not in ("pl", "de", "es", "fr", "en"):
                shutil.copytree(child, ws_audio_dst / child.name, dirs_exist_ok=True)

    return ws


SEARCH_LABELS: dict[str, str] = {
    "en": "Search",
    "pl": "Szukaj",
    "de": "Suchen",
    "es": "Buscar",
    "fr": "Rechercher",
}


def generate_mock_html_for_workspace(
    ws: Path,
    locale_code: str,
    locale_info: dict[str, Any],
    base_myst: dict[str, Any],
    locale_base_url: str,
) -> Path:
    """Generate deterministic static HTML files in ws/_build/html for testing when jupyter CLI is absent."""
    html_out = ws / "_build" / "html"
    html_out.mkdir(parents=True, exist_ok=True)
    toc_files = discover_toc_files(base_myst.get("project", {}).get("toc", []))
    html_lang = str(locale_info.get("html_lang", locale_code))
    site_title = str(
        locale_info.get("site", {}).get("title")
        or base_myst.get("project", {}).get("title", "SoftCloud")
    )
    search_label = str(
        locale_info.get("ui", {}).get("search") or SEARCH_LABELS.get(locale_code, "Search")
    )

    for rel_file in toc_files:
        slug = page_slug_from_rel_path(rel_file)
        src_path = ws / rel_file
        raw = src_path.read_text(encoding="utf-8")
        if src_path.suffix == ".ipynb":
            try:
                nb_obj = json.loads(raw)
                md_text = "\n\n".join(
                    "".join(c.get("source", []))
                    for c in nb_obj.get("cells", [])
                    if c.get("cell_type") == "markdown"
                )
            except Exception:
                md_text = raw
        else:
            md_text = raw
        title_match = re.search(r"^#\s+(.+)$", md_text, re.MULTILINE)
        page_title = title_match.group(1).strip() if title_match else (slug or site_title)

        out_file = (html_out / "index.html") if not slug else (html_out / slug / "index.html")
        out_file.parent.mkdir(parents=True, exist_ok=True)
        route_path = f"{locale_base_url}/" if not slug else f"{locale_base_url}/{slug}"
        if not route_path.startswith("/"):
            route_path = "/" + route_path

        html_doc = f"""<!DOCTYPE html>
<html lang="{html_lang}">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{page_title} — {site_title}</title>
</head>
<body data-locale="{locale_code}" data-route="{route_path}">
  <header class="myst-top-nav">
    <div class="myst-header-bar">
      <a href="{locale_base_url or '/'}">{site_title}</a>
      <div class="navbar-header-items__end">
        <button type="button" aria-label="{search_label}" title="{search_label}" aria-haspopup="dialog" aria-expanded="false" data-state="closed" class="myst-search-bar flex items-center h-10 aspect-square sm:w-64 text-left text-myst-text-secondary border border-myst-border-strong rounded-lg bg-myst-bg-secondary dark:bg-myst-surface-hover myst-search-bar-disabled hover:ring-myst-focus-ring hover:border-myst-focus-ring">
          <span class="sr-only">{search_label}</span>
          <span class="myst-search-text-placeholder hidden sm:block grow">{search_label}</span>
        </button>
        <button class="theme-toggle" aria-label="Toggle Theme" title="Toggle Theme">🌙</button>
      </div>
    </div>
  </header>
  <main id="main-content">
    <article data-page-slug="{slug}">
      <h1>{page_title}</h1>
    </article>
  </main>
</body>
</html>
"""
        atomic_write_text(out_file, html_doc)

    # Also copy images, widgets, and audio into ws/_build/html
    for asset_dir in ("images", "widgets", "audio"):
        if (ws / asset_dir).is_dir():
            shutil.copytree(ws / asset_dir, html_out / asset_dir, dirs_exist_ok=True)

    return html_out


def run_jupyter_book_in_workspace(ws: Path, locale_code: str, locale_base_url: str) -> Path:
    """Run jupyter book clean & build inside the isolated locale workspace."""
    env = os.environ.copy()
    env["BASE_URL"] = locale_base_url
    env["JB_ALLOW_NODEENV"] = "0"
    env["SOFTCLOUD_LOCALE"] = locale_code
    staged_python = (ws / "assets" / "python").resolve()
    if staged_python.is_dir():
        orig_pypath = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = f"{staged_python}:{orig_pypath}" if orig_pypath else str(staged_python)

    subprocess.run(
        ["jupyter", "book", "clean", "--all", "--execute", "-y"],
        cwd=str(ws),
        env=env,
        check=True,
    )
    subprocess.run(
        ["jupyter", "book", "build", "--html", "--strict", "--execute"],
        cwd=str(ws),
        env=env,
        check=True,
    )
    html_out = ws / "_build" / "html"
    if not (html_out / "index.html").is_file():
        raise RuntimeError(f"Jupyter Book build for locale '{locale_code}' did not produce {html_out / 'index.html'}")
    return html_out


def build_route_manifest(
    root: Path,
    locales_cfg: dict[str, Any],
    base_myst: dict[str, Any],
    outer_base_url: str = "",
    output_html_dir: Path | None = None,
) -> dict[str, Any]:
    """Build the route availability manifest consumed by the language switcher and SEO tools."""
    default_locale = str(locales_cfg.get("default_locale", "en"))
    domain = str(locales_cfg.get("canonical_domain", "https://my.softcloud.dev")).rstrip("/")
    enabled_locales = get_enabled_locales(locales_cfg)
    toc_files = discover_toc_files(base_myst.get("project", {}).get("toc", []))

    DEFAULT_FLAGS = {
        "en": "🇬🇧",
        "pl": "🇵🇱",
        "de": "🇩🇪",
        "es": "🇪🇸",
        "fr": "🇫🇷",
    }

    locales_meta: dict[str, Any] = {}
    for code, info in enabled_locales.items():
        prefix = str(info.get("prefix", ""))
        locales_meta[code] = {
            "code": code,
            "flag": str(info.get("flag") or DEFAULT_FLAGS.get(code, "🌐")),
            "html_lang": str(info.get("html_lang", code)),
            "hreflang": str(info.get("hreflang", code)),
            "native_name": str(info.get("native_name", code)),
            "english_name": str(info.get("english_name") or info.get("name") or code),
            "name": str(info.get("name") or info.get("english_name") or code),
            "prefix": prefix,
            "base_route": route_url_for_page(prefix, "", base_url=outer_base_url),
            "ui": info.get("ui", {}),
        }

    prov_cache: dict[str, dict[str, Any]] = {}
    pages_meta: dict[str, Any] = {}
    for rel_file in toc_files:
        raw_slug = page_slug_from_rel_path(rel_file)
        flat_name = Path(raw_slug).name if raw_slug else ""
        flat_slug = "index-1" if flat_name.lower() in ("index", "readme") else flat_name
        active_slug = raw_slug
        if (
            output_html_dir is not None
            and raw_slug
            and raw_slug != flat_slug
            and not (output_html_dir / raw_slug / "index.html").is_file()
            and (
                (output_html_dir / flat_slug / "index.html").is_file()
                or (output_html_dir / f"{flat_slug}.html").is_file()
            )
        ):
            active_slug = flat_slug

        slug_key = raw_slug if raw_slug else "index"
        translations: dict[str, Any] = {}
        for code, info in enabled_locales.items():
            prefix = str(info.get("prefix", ""))
            src_dir = (
                root
                if code == default_locale
                else (root / str(info.get("source_dir", f"i18n/{code}")))
            )
            src_file = src_dir / rel_file
            is_avail = is_page_translation_current(root, code, default_locale, rel_file, prov_cache)
            route = route_url_for_page(prefix, active_slug, base_url=outer_base_url)
            canonical = canonical_url_for_page(domain, prefix, active_slug)
            translations[code] = {
                "available": is_avail,
                "route": route if is_avail else None,
                "canonical_url": canonical if is_avail else None,
                "source_path": src_file.relative_to(root).as_posix() if is_avail else None,
            }

        entry_obj = {
            "slug": active_slug,
            "source_file": rel_file,
            "translations": translations,
        }
        pages_meta[slug_key] = entry_obj
        if flat_slug and flat_slug != slug_key:
            pages_meta[flat_slug] = entry_obj

    return {
        "schema_version": "1.0",
        "default_locale": default_locale,
        "canonical_domain": domain,
        "base_url": outer_base_url,
        "locales": locales_meta,
        "pages": pages_meta,
    }


def inject_language_switcher_into_html(
    html_dir: Path,
    route_manifest: dict[str, Any],
    outer_base_url: str = "",
) -> int:
    """Inject the language switcher host element, route manifest, and module initializer into built HTML files."""
    clean_base = outer_base_url.rstrip("/")
    widget_src = f"{clean_base}/widgets/language-switcher.mjs"
    manifest_json = json.dumps(route_manifest, ensure_ascii=False, separators=(",", ":"))
    host_markup = (
        f'<div id="softcloud-lang-switcher-root" data-sc-lang-switcher="1" '
        f'data-sc-base-url="{clean_base}"></div>'
    )
    script_snippet = (
        f'<script id="softcloud-i18n-manifest" type="application/json">{manifest_json}</script>\n'
        f'<script type="module" data-softcloud-lang-switcher="1">\n'
        f'import {{ mountLanguageSwitcher, ensureLanguageSwitcherHost, loadEmbeddedRouteManifest, installNavigationSync }} from "{widget_src}";\n'
        f'const manifest = loadEmbeddedRouteManifest(document);\n'
        f'const baseUrl = {json.dumps(clean_base)};\n'
        f'window.__SC_ROUTE_MANIFEST__ = manifest;\n'
        f'window.__SC_ROOT_BASE_URL__ = baseUrl;\n'
        f'const hostEl = ensureLanguageSwitcherHost(document);\n'
        f'if (hostEl) {{\n'
        f'  mountLanguageSwitcher(hostEl, {{ routeManifest: manifest, baseUrl }});\n'
        f'}}\n'
        f'installNavigationSync({{ routeManifest: manifest, baseUrl }});\n'
        f'</script>\n'
    )

    count = 0
    for html_file in sorted(html_dir.rglob("*.html")):
        if html_file.name.startswith("404") or "_locales" in html_file.parts:
            continue
        text = html_file.read_text(encoding="utf-8")
        if 'id="softcloud-i18n-manifest"' in text:
            continue
        if "data-sc-lang-switcher" not in text:
            theme_btn_re = re.compile(
                r'(<button\b[^>]*\b(?:theme-toggle|theme-switch|theme-switch-button)[^>]*>.*?</button>|<button\b[^>]*(?:aria-label|title)="[^"]*(?:theme|dark|light|mode)[^"]*"[^>]*>.*?</button>)',
                re.I | re.DOTALL,
            )
            header_end_re = re.compile(r'(<div\b[^>]*\bclass="[^"]*\bnavbar-header-items__end\b[^"]*"[^>]*>)', re.I)
            header_bar_re = re.compile(r'(<div\b[^>]*\bclass="[^"]*\bmyst-header-bar\b[^"]*"[^>]*>)', re.I)

            if theme_btn_re.search(text):
                text = theme_btn_re.sub(rf"{host_markup}\n        \1", text, count=1)
            elif header_end_re.search(text):
                text = header_end_re.sub(rf"\1\n      {host_markup}", text, count=1)
            elif header_bar_re.search(text):
                text = header_bar_re.sub(rf"\1\n      {host_markup}", text, count=1)
            elif "</body>" in text:
                text = text.replace(
                    "</body>",
                    f'  <div id="softcloud-lang-switcher-root" class="sc-lang-host-floating" data-sc-lang-switcher="1" data-sc-base-url="{clean_base}"></div>\n</body>',
                    1,
                )
        # Ensure search bar buttons have discernible text and well-formed accessibility tree entries
        search_btn_re = re.compile(
            r'(<button\b[^>]*\bclass="[^"]*\bmyst-search-bar\b[^"]*"[^>]*>)(.*?)(</button>)',
            re.DOTALL | re.IGNORECASE,
        )

        def _patch_btn(m: re.Match[str]) -> str:
            open_tag = m.group(1)
            inner = m.group(2)
            close_tag = m.group(3)
            if not re.search(r'\baria-label\s*=', open_tag, re.IGNORECASE):
                open_tag = re.sub(r'(<button\b)', r'\1 aria-label="Search"', open_tag, count=1)
            if not re.search(r'\btitle\s*=', open_tag, re.IGNORECASE):
                open_tag = re.sub(r'(<button\b)', r'\1 title="Search"', open_tag, count=1)
            if '<span class="sr-only">' not in inner and "sr-only" not in inner:
                sr_span = '<span class="sr-only">Search</span>'
                if 'class="myst-search-text-placeholder' in inner:
                    inner = re.sub(
                        r'(<span\b[^>]*\bclass="[^"]*\bmyst-search-text-placeholder\b[^"]*"[^>]*>)',
                        rf"{sr_span}\1",
                        inner,
                        count=1,
                    )
                else:
                    inner = sr_span + inner
            return f"{open_tag}{inner}{close_tag}"

        text = search_btn_re.sub(_patch_btn, text)

        if "</body>" in text:
            text = text.replace("</body>", f"{script_snippet}</body>", 1)
            atomic_write_text(html_file, text)
            count += 1
    return count


def assemble_combined_html(
    root: Path,
    locale_html_dirs: dict[str, Path],
    locales_cfg: dict[str, Any],
    base_myst: dict[str, Any],
    output_html_dir: Path,
    outer_base_url: str = "",
) -> dict[str, Any]:
    """Combine all per-locale HTML build outputs into a single deployable _build/html artifact."""
    default_locale = str(locales_cfg.get("default_locale", "en"))
    enabled_locales = get_enabled_locales(locales_cfg)

    if output_html_dir.exists():
        shutil.rmtree(output_html_dir)
    output_html_dir.mkdir(parents=True, exist_ok=True)

    # 1. Copy default locale (English) to root of output_html_dir
    if default_locale not in locale_html_dirs:
        raise ValueError(f"Default locale '{default_locale}' build output is missing")
    shutil.copytree(locale_html_dirs[default_locale], output_html_dir, dirs_exist_ok=True)

    # 2. Copy non-default locales into output_html_dir/<locale_prefix>/
    for code, html_src in locale_html_dirs.items():
        if code == default_locale:
            continue
        prefix = str(enabled_locales[code].get("prefix", f"/{code}")).strip("/")
        target_subdir = output_html_dir / prefix
        shutil.copytree(html_src, target_subdir, dirs_exist_ok=True)

    # 3. Ensure widgets and static images are present at root and per-locale
    for asset_dir_name in ("widgets", "images"):
        asset_src = root / asset_dir_name
        if asset_src.is_dir():
            shutil.copytree(asset_src, output_html_dir / asset_dir_name, dirs_exist_ok=True)
            for code, info in enabled_locales.items():
                if code == default_locale:
                    continue
                prefix = str(info.get("prefix", f"/{code}")).strip("/")
                shutil.copytree(asset_src, output_html_dir / prefix / asset_dir_name, dirs_exist_ok=True)

    # 4. Copy top-level CNAME and thebe sourcemap if present
    if (root / "CNAME").is_file():
        shutil.copy2(root / "CNAME", output_html_dir / "CNAME")
    if (root / "thebe-core.min.js.map").is_file():
        shutil.copy2(root / "thebe-core.min.js.map", output_html_dir / "thebe-core.min.js.map")

    # 5. Write _build/html/i18n/route-manifest.json
    route_manifest = build_route_manifest(
        root, locales_cfg, base_myst, outer_base_url=outer_base_url, output_html_dir=output_html_dir
    )
    atomic_write_json(output_html_dir / "i18n" / "route-manifest.json", route_manifest)

    # 6. Inject language switcher into all built HTML files
    injected_count = inject_language_switcher_into_html(
        output_html_dir, route_manifest, outer_base_url=outer_base_url
    )
    print(f"[OK] Injected language switcher into {injected_count} HTML files in {output_html_dir}")

    return route_manifest


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Stage and build isolated MyST locale sites and assemble combined _build/html."
    )
    parser.add_argument(
        "--locale",
        action="append",
        dest="locales",
        help="Specific locale(s) to stage/build (defaults to all enabled locales in i18n/locales.yml).",
    )
    parser.add_argument(
        "--stage-only",
        action="store_true",
        help="Only stage isolated locale workspaces under _build/locales/<locale>/workspace without building.",
    )
    parser.add_argument(
        "--mock-html",
        action="store_true",
        help="Generate deterministic static HTML routes when the jupyter CLI is not installed locally.",
    )
    parser.add_argument(
        "--output-dir",
        default="_build/html",
        help="Combined HTML output directory (default: _build/html).",
    )
    parser.add_argument(
        "--staging-dir",
        default="_build/locales",
        help="Isolated per-locale staging directory (default: _build/locales).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = Path.cwd().resolve()
    locales_cfg = load_locales_config(root)
    default_locale = str(locales_cfg.get("default_locale", "en"))
    enabled_locales = get_enabled_locales(locales_cfg)
    base_myst = load_yaml_file(root / "myst.yml")
    outer_base_url = os.environ.get("BASE_URL", "")

    target_locales = args.locales or list(enabled_locales.keys())
    staging_root = (root / args.staging_dir).resolve()
    output_html_dir = (root / args.output_dir).resolve()

    staged_workspaces: dict[str, Path] = {}
    for code in target_locales:
        if code not in enabled_locales:
            raise SystemExit(f"Unknown or disabled locale: {code}")
        ws = stage_locale_workspace(
            root=root,
            locale_code=code,
            locale_info=enabled_locales[code],
            base_myst=base_myst,
            default_locale=default_locale,
            staging_root=staging_root,
        )
        staged_workspaces[code] = ws
        print(f"[OK] Staged isolated workspace for locale '{code}' -> {ws.relative_to(root)}")

    if args.stage_only:
        return 0

    locale_html_dirs: dict[str, Path] = {}
    for code, ws in staged_workspaces.items():
        prefix = str(enabled_locales[code].get("prefix", ""))
        loc_base_url = compute_locale_base_url(outer_base_url, prefix)
        if args.mock_html:
            html_out = generate_mock_html_for_workspace(
                ws=ws,
                locale_code=code,
                locale_info=enabled_locales[code],
                base_myst=base_myst,
                locale_base_url=loc_base_url,
            )
        else:
            html_out = run_jupyter_book_in_workspace(ws, code, loc_base_url)
        locale_html_dirs[code] = html_out
        print(f"[OK] Built HTML for locale '{code}' (BASE_URL={loc_base_url!r}) -> {html_out.relative_to(root)}")

    assemble_combined_html(
        root=root,
        locale_html_dirs=locale_html_dirs,
        locales_cfg=locales_cfg,
        base_myst=base_myst,
        output_html_dir=output_html_dir,
        outer_base_url=outer_base_url,
    )
    print(f"[OK] Assembled combined multilingual site in {output_html_dir.relative_to(root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
