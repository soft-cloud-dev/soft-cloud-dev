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
)


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

    # 1. Write localized myst.yml
    localized_myst = build_localized_myst_config(base_myst, locale_code, locale_info)
    atomic_write_text(ws / "myst.yml", dump_yaml_text(localized_myst))

    # 2. Copy TOC source files from authoritative root (en) or i18n/<locale>/
    toc_files = discover_toc_files(base_myst.get("project", {}).get("toc", []))
    source_root = (
        root
        if locale_code == default_locale
        else (root / str(locale_info.get("source_dir", f"i18n/{locale_code}")))
    )

    for rel_file in toc_files:
        src_path = source_root / rel_file
        if not src_path.is_file():
            raise FileNotFoundError(
                f"Missing source file for locale '{locale_code}': {src_path.relative_to(root)}"
            )
        dst_path = ws / rel_file
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_path, dst_path)

    # 3. Copy static assets (images, widgets, CNAME, sourcemaps)
    for asset_dir_name in ("images", "widgets"):
        src_dir = root / asset_dir_name
        if src_dir.is_dir():
            shutil.copytree(src_dir, ws / asset_dir_name, dirs_exist_ok=True)

    for single_asset in ("CNAME", "thebe-core.min.js.map"):
        src_asset = root / single_asset
        if src_asset.is_file():
            shutil.copy2(src_asset, ws / single_asset)

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

    for rel_file in toc_files:
        slug = page_slug_from_rel_path(rel_file)
        src_path = ws / rel_file
        raw = src_path.read_text(encoding="utf-8")
        title_match = re.search(r"^#\s+(.+)$", raw, re.MULTILINE)
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

    locales_meta: dict[str, Any] = {}
    for code, info in enabled_locales.items():
        prefix = str(info.get("prefix", ""))
        locales_meta[code] = {
            "code": code,
            "html_lang": str(info.get("html_lang", code)),
            "hreflang": str(info.get("hreflang", code)),
            "native_name": str(info.get("native_name", code)),
            "english_name": str(info.get("english_name", code)),
            "prefix": prefix,
            "base_route": route_url_for_page(prefix, "", base_url=outer_base_url),
            "ui": info.get("ui", {}),
        }

    pages_meta: dict[str, Any] = {}
    for rel_file in toc_files:
        raw_slug = page_slug_from_rel_path(rel_file)
        flat_slug = Path(raw_slug).name if raw_slug else ""
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
            exists = src_file.is_file()
            route = route_url_for_page(prefix, active_slug, base_url=outer_base_url)
            canonical = canonical_url_for_page(domain, prefix, active_slug)
            translations[code] = {
                "available": exists,
                "route": route if exists else None,
                "canonical_url": canonical if exists else None,
                "source_path": src_file.relative_to(root).as_posix() if exists else None,
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
    """Inject the language switcher widget script and route manifest into built HTML files."""
    clean_base = outer_base_url.rstrip("/")
    widget_src = f"{clean_base}/widgets/language-switcher.mjs"
    manifest_json = json.dumps(route_manifest, ensure_ascii=False, separators=(",", ":"))
    snippet = (
        f'<script id="softcloud-i18n-manifest" type="application/json">{manifest_json}</script>\n'
        f'<script type="module" src="{widget_src}" data-softcloud-lang-switcher="1"></script>\n'
    )

    count = 0
    for html_file in sorted(html_dir.rglob("*.html")):
        if html_file.name.startswith("404") or "_locales" in html_file.parts:
            continue
        text = html_file.read_text(encoding="utf-8")
        if 'id="softcloud-i18n-manifest"' in text:
            continue
        if "</body>" in text:
            text = text.replace("</body>", f"{snippet}</body>", 1)
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

    # 3. Ensure widgets (language-switcher.mjs and voice-player.mjs) are present at root and per-locale
    widgets_src = root / "widgets"
    if widgets_src.is_dir():
        shutil.copytree(widgets_src, output_html_dir / "widgets", dirs_exist_ok=True)
        for code, info in enabled_locales.items():
            if code == default_locale:
                continue
            prefix = str(info.get("prefix", f"/{code}")).strip("/")
            shutil.copytree(widgets_src, output_html_dir / prefix / "widgets", dirs_exist_ok=True)

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
