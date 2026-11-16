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
import html as html_lib
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
    BREADCRUMB_LABELS,
    DEFAULT_LOCALE_FLAGS,
    SEARCH_LABELS,
    SWITCHER_UI_KEYS,
    atomic_write_json,
    atomic_write_text,
    canonical_url_for_page,
    discover_toc_files,
    dump_yaml_text,
    get_enabled_locales,
    infer_locale_and_slug,
    load_locales_config,
    load_yaml_file,
    load_yaml_text,
    page_slug_from_rel_path,
    route_url_for_page,
    sha256_file,
)
from generate_audio import page_id_from_path


FRONTMATTER_BLOCK_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", re.DOTALL)
STAGED_WORKSPACE_GITHUB_URL_RE = re.compile(
    r"(https://github\.com/[^/\"'\s>]+/[^/\"'\s>]+/(?:edit|blob)/[^/\"'\s>]+)/_build/locales/([a-zA-Z0-9_-]+)/workspace/([^\s\"'<>]+)"
)


def authoritative_repo_rel_path(
    locale_code: str,
    default_locale: str,
    locale_info: dict[str, Any],
    rel_file: str,
) -> str:
    """Return the authoritative repository-relative source path for a TOC entry."""
    clean_rel = rel_file.lstrip("./")
    if locale_code == default_locale:
        return clean_rel
    source_dir = str(locale_info.get("source_dir", f"i18n/{locale_code}")).strip("/")
    return f"{source_dir}/{clean_rel}" if source_dir else clean_rel


def authoritative_github_urls(
    base_myst: dict[str, Any],
    locale_code: str,
    default_locale: str,
    locale_info: dict[str, Any],
    rel_file: str,
    branch: str = "main",
) -> tuple[str, str]:
    """Return (edit_url, source_url) pointing to the real repository source file instead of _build/locales."""
    github_base = str(
        base_myst.get("project", {}).get("github", "https://github.com/soft-cloud-dev/soft-cloud-dev")
    ).rstrip("/")
    if not github_base.startswith(("http://", "https://")):
        github_base = f"https://github.com/{github_base.lstrip('/')}"
    repo_rel = authoritative_repo_rel_path(locale_code, default_locale, locale_info, rel_file)
    return f"{github_base}/edit/{branch}/{repo_rel}", f"{github_base}/blob/{branch}/{repo_rel}"


def inject_authoritative_repo_urls(
    text_content: str,
    rel_file: str,
    edit_url: str,
    source_url: str,
) -> str:
    """Inject authoritative edit_url and source_url into staged Markdown frontmatter or Notebook metadata."""
    if rel_file.endswith(".ipynb"):
        try:
            nb_obj = json.loads(text_content)
            if isinstance(nb_obj, dict):
                meta = nb_obj.setdefault("metadata", {})
                if isinstance(meta, dict):
                    if not meta.get("edit_url") or "/_build/locales/" in str(meta.get("edit_url")):
                        meta["edit_url"] = edit_url
                    if not meta.get("source_url") or "/_build/locales/" in str(meta.get("source_url")):
                        meta["source_url"] = source_url
                return json.dumps(nb_obj, ensure_ascii=False, indent=2) + "\n"
        except Exception:
            return text_content

    match = FRONTMATTER_BLOCK_RE.match(text_content)
    if match:
        fm_body = match.group(1)
        remainder = text_content[match.end() :]
        additions: list[str] = []
        if not re.search(r"^\s*edit_url\s*:", fm_body, re.MULTILINE):
            additions.append(f"edit_url: {edit_url}")
        if not re.search(r"^\s*source_url\s*:", fm_body, re.MULTILINE):
            additions.append(f"source_url: {source_url}")
        if not additions:
            return text_content
        updated_fm = fm_body.rstrip() + "\n" + "\n".join(additions)
        return f"---\n{updated_fm}\n---\n{remainder}"

    return f"---\nedit_url: {edit_url}\nsource_url: {source_url}\n---\n\n{text_content}"


def extract_explicit_frontmatter_slug(md_path: Path) -> str | None:
    """Extract an explicit `slug:` declaration from a Markdown file's YAML frontmatter, if present."""
    if not md_path.is_file() or md_path.suffix.lower() != ".md":
        return None
    try:
        text = md_path.read_text(encoding="utf-8")
    except Exception:
        return None
    match = FRONTMATTER_BLOCK_RE.match(text)
    if not match:
        return None
    slug_match = re.search(
        r"^\s*slug\s*:\s*['\"]?([a-zA-Z0-9_/-]+)['\"]?\s*$",
        match.group(1),
        re.MULTILINE,
    )
    if not slug_match:
        return None
    slug_val = slug_match.group(1).strip("/")
    return slug_val or None


def rewrite_staged_source_urls_in_text(text: str, locales_cfg: dict[str, Any]) -> str:
    """Rewrite any leaked _build/locales/<locale>/workspace/<path> GitHub URLs back to authoritative repo paths."""
    if "/_build/locales/" not in text:
        return text
    default_locale = str(locales_cfg.get("default_locale", "en"))
    enabled_locales = get_enabled_locales(locales_cfg)

    def _replace(match: re.Match[str]) -> str:
        prefix_url, loc_code, rel_path = match.group(1), match.group(2), match.group(3)
        loc_info = enabled_locales.get(loc_code, {})
        repo_rel = authoritative_repo_rel_path(loc_code, default_locale, loc_info, rel_path)
        return f"{prefix_url}/{repo_rel}"

    return STAGED_WORKSPACE_GITHUB_URL_RE.sub(_replace, text)


def rewrite_staged_source_urls_in_dir(html_dir: Path, locales_cfg: dict[str, Any]) -> int:
    """Sanitize any leaked _build/locales/<locale>/workspace/ URLs across built .html and .json files."""
    rewritten_files = 0
    for pattern in ("*.html", "*.json"):
        for file_path in sorted(html_dir.rglob(pattern)):
            if "_locales" in file_path.parts:
                continue
            try:
                raw = file_path.read_text(encoding="utf-8")
            except Exception:
                continue
            updated = rewrite_staged_source_urls_in_text(raw, locales_cfg)
            if updated != raw:
                atomic_write_text(file_path, updated)
                rewritten_files += 1
    return rewritten_files


def materialize_explicit_slug_routes(
    root: Path,
    base_myst: dict[str, Any],
    output_html_dir: Path,
    outer_base_url: str = "",
) -> list[str]:
    """Materialize built HTML and JSON routes for TOC pages that declare an explicit frontmatter `slug:`
    when MyST disambiguated their filename-based slug (e.g., components/index.md -> index-1 vs components)."""
    clean_base = outer_base_url.rstrip("/")
    toc_files = discover_toc_files(base_myst.get("project", {}).get("toc", []))
    materialized: list[str] = []

    for rel_file in toc_files:
        explicit_slug = extract_explicit_frontmatter_slug(root / rel_file)
        if not explicit_slug:
            continue
        raw_slug = page_slug_from_rel_path(rel_file)
        flat_name = Path(raw_slug).name if raw_slug else ""
        flat_slug = "index-1" if flat_name.lower() in ("index", "readme") else flat_name

        dst_html = output_html_dir / explicit_slug / "index.html"
        if dst_html.is_file():
            continue

        src_html: Path | None = None
        src_slug: str | None = None
        for candidate_slug in (flat_slug, raw_slug):
            if not candidate_slug:
                continue
            candidate_html = output_html_dir / candidate_slug / "index.html"
            if candidate_html.is_file():
                src_html = candidate_html
                src_slug = candidate_slug
                break

        if src_html is None or not src_slug:
            continue

        html_text = src_html.read_text(encoding="utf-8")
        src_route = f"{clean_base}/{src_slug}"
        dst_route = f"{clean_base}/{explicit_slug}"
        html_text = html_text.replace(f'"url":"{src_route}"', f'"url":"{dst_route}"')
        html_text = html_text.replace(f'href="{src_route}"', f'href="{dst_route}"')
        html_text = html_text.replace(f'"slug":"{src_slug}"', f'"slug":"{explicit_slug}"')
        html_text = html_text.replace(f'data-route="{src_route}"', f'data-route="{dst_route}"')
        html_text = html_text.replace(f'data-page-slug="{src_slug}"', f'data-page-slug="{explicit_slug}"')
        dst_html.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_text(dst_html, html_text)

        src_json = output_html_dir / f"{src_slug}.json"
        dst_json = output_html_dir / f"{explicit_slug}.json"
        if src_json.is_file() and not dst_json.is_file():
            json_text = src_json.read_text(encoding="utf-8")
            json_text = json_text.replace(f'"slug":"{src_slug}"', f'"slug":"{explicit_slug}"')
            atomic_write_text(dst_json, json_text)

        materialized.append(explicit_slug)

    return materialized


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

    # Route labels and destinations are both derived from the active locale.
    # Never send a translated navbar entry back to an unrelated English route.
    nav_sources = {
        "Guides": "guides.md",
        "Notebooks": "notebooks.md",
        "UI Library": "ui-library.md",
        "Projects": "projects.md",
    }
    nav_titles = (
        site_meta.get("nav_titles", {}) if isinstance(site_meta, dict) else {}
    ) or locale_info.get("nav_titles", {})
    site = cfg.setdefault("site", {})
    if isinstance(site.get("nav"), list):
        localized_nav: list[dict[str, Any]] = []
        for item in site["nav"]:
            if not isinstance(item, dict):
                continue
            new_item = dict(item)
            source = nav_sources.get(str(item.get("title", "")))
            if source is not None:
                if staged_files is not None and source not in staged_files:
                    continue
                # MyST adds BASE_URL (including the locale prefix) while
                # compiling the site. Adding it here produces /pl/pl/guides.
                new_item["url"] = route_url_for_page(
                    "", page_slug_from_rel_path(source)
                )
            if new_item.get("title") in nav_titles:
                new_item["title"] = nav_titles[new_item["title"]]
            localized_nav.append(new_item)
        site["nav"] = localized_nav

    return cfg


def compute_locale_base_url(outer_base_url: str, locale_prefix: str) -> str:
    clean_outer = outer_base_url.strip().rstrip("/")
    clean_prefix = ("/" + locale_prefix.strip("/")) if locale_prefix.strip("/") else ""
    combined = f"{clean_outer}{clean_prefix}"
    return combined


def _safe_rmtree(path: Path) -> None:
    """Remove a directory tree resiliently (handles macOS Finder .DS_Store race conditions)."""
    if not path.exists():
        return
    shutil.rmtree(path, ignore_errors=True)
    if path.exists():
        subprocess.run(["rm", "-rf", str(path)], check=False)


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
        _safe_rmtree(ws)
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
        edit_url, source_url = authoritative_github_urls(
            base_myst, locale_code, default_locale, locale_info, rel_file
        )
        text_content = inject_authoritative_repo_urls(
            text_content, rel_file, edit_url, source_url
        )
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


def generate_mock_html_for_workspace(
    ws: Path,
    locale_code: str,
    locale_info: dict[str, Any],
    base_myst: dict[str, Any],
    locale_base_url: str,
    default_locale: str = "en",
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
        if not src_path.is_file():
            continue
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
        edit_url, _ = authoritative_github_urls(
            base_myst, locale_code, default_locale, locale_info, rel_file
        )

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
      <a href="{edit_url}" title="Edit This Page" class="myst-fm-edit-link">Edit This Page</a>
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


def _clean_inline_markdown(text: str) -> str:
    """Strip inline Markdown markers from headings/titles for plain-text breadcrumb labels."""
    cleaned = re.sub(r"`([^`]+)`", r"\1", text)
    cleaned = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", cleaned)
    cleaned = re.sub(r"\*\*([^*]+)\*\*", r"\1", cleaned)
    cleaned = re.sub(r"\*([^*]+)\*", r"\1", cleaned)
    return re.sub(r"\s+", " ", cleaned).strip()


def _extract_document_title(doc_path: Path, fallback: str) -> str:
    """Resolve a human-readable document title from frontmatter or first H1 heading."""
    if not doc_path.is_file():
        return fallback
    try:
        raw = doc_path.read_text(encoding="utf-8")
    except Exception:
        return fallback

    if doc_path.suffix.lower() == ".ipynb":
        try:
            nb = json.loads(raw)
            for cell in nb.get("cells", []):
                if cell.get("cell_type") == "markdown":
                    txt = "".join(cell.get("source", []))
                    m = re.search(r"^#\s+(.+)$", txt, re.MULTILINE)
                    if m:
                        return _clean_inline_markdown(m.group(1))
        except Exception:
            return fallback
        return fallback

    body = raw
    fm_match = FRONTMATTER_BLOCK_RE.match(raw)
    if fm_match:
        body = raw[fm_match.end() :]
        try:
            fm_data = load_yaml_text(fm_match.group(1))
            if isinstance(fm_data, dict):
                for key in ("short_title", "title"):
                    val = fm_data.get(key)
                    if isinstance(val, str) and val.strip():
                        return _clean_inline_markdown(val)
        except Exception:
            pass

    in_fence = False
    fence_char = ""
    fence_len = 0
    for line in body.splitlines():
        fence_m = re.match(r"^[ \t]*(`{3,}|~{3,}|:{3,})", line)
        if not in_fence and fence_m:
            in_fence = True
            fence_char = fence_m.group(1)[0]
            fence_len = len(fence_m.group(1))
            continue
        if in_fence:
            if re.match(rf"^[ \t]*{re.escape(fence_char)}{{{fence_len},}}[ \t]*$", line):
                in_fence = False
            continue
        h1_m = re.match(r"^#\s+(.+?)\s*$", line.strip())
        if h1_m:
            return _clean_inline_markdown(h1_m.group(1))

    return fallback


def _find_folder_landing_file(
    folder_entry: dict[str, Any],
    source_root: Path,
    fallback_root: Path,
    staged_files: set[str],
) -> str | None:
    """Identify a direct child page that serves as a TOC folder's landing/index page."""
    folder_title = str(folder_entry.get("title") or "").strip().casefold()
    for child in folder_entry.get("children", []):
        if not isinstance(child, dict):
            continue
        rel_file = child.get("file")
        if not isinstance(rel_file, str) or rel_file not in staged_files:
            continue
        if Path(rel_file).stem.lower() == "index":
            return rel_file
        if folder_title:
            doc_path = (source_root / rel_file) if (source_root / rel_file).is_file() else (fallback_root / rel_file)
            doc_title = _extract_document_title(doc_path, "").casefold()
            if doc_title and doc_title == folder_title:
                return rel_file
    return None


def _build_breadcrumbs_index(
    root: Path,
    locales_cfg: dict[str, Any],
    base_myst: dict[str, Any],
    outer_base_url: str,
    file_slug_map: dict[str, str],
    file_key_map: dict[str, str],
    prov_cache: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Build normalized per-locale breadcrumb node tables and trails from project.toc."""
    default_locale = str(locales_cfg.get("default_locale", "en"))
    enabled_locales = get_enabled_locales(locales_cfg)
    toc_files = discover_toc_files(base_myst.get("project", {}).get("toc", []))
    breadcrumbs: dict[str, Any] = {}

    for code, info in enabled_locales.items():
        prefix = str(info.get("prefix", ""))
        source_root = (
            root
            if code == default_locale
            else (root / str(info.get("source_dir", f"i18n/{code}")))
        )
        staged_files = {
            rel_file
            for rel_file in toc_files
            if is_page_translation_current(root, code, default_locale, rel_file, prov_cache)
        }
        loc_myst = build_localized_myst_config(base_myst, code, info, staged_files=staged_files)
        loc_toc = loc_myst.get("project", {}).get("toc", [])

        home_label = str(loc_myst.get("project", {}).get("short_title") or "SoftCloud Hub").strip()
        for entry in loc_toc:
            if isinstance(entry, dict) and isinstance(entry.get("file"), str):
                if page_slug_from_rel_path(entry["file"]) == "":
                    if entry.get("title"):
                        home_label = str(entry["title"]).strip()
                    break
        home_href = route_url_for_page(prefix, "", base_url=outer_base_url)

        nodes: list[dict[str, Any]] = []
        node_index: dict[tuple[str, str | None], int] = {}
        trails: dict[str, list[int]] = {}

        def add_node(label: str, href: str | None = None) -> int:
            clean_label = str(label).strip()
            clean_href = href if (isinstance(href, str) and href.startswith("/") and not href.startswith("//")) else None
            key = (clean_label, clean_href)
            if key not in node_index:
                node_index[key] = len(nodes)
                node_obj: dict[str, Any] = {"label": clean_label}
                if clean_href is not None:
                    node_obj["href"] = clean_href
                nodes.append(node_obj)
            return node_index[key]

        home_idx = add_node(home_label, home_href)

        def walk_toc(
            entries: list[dict[str, Any]],
            ancestors: list[tuple[str, str | None, str | None]],
        ) -> None:
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                rel_file = entry.get("file")
                children = entry.get("children")
                if isinstance(rel_file, str) and rel_file.strip():
                    rel_clean = rel_file.strip()
                    if page_slug_from_rel_path(rel_clean) != "":
                        leaf_slug = file_slug_map.get(rel_clean, page_slug_from_rel_path(rel_clean))
                        leaf_key = file_key_map.get(rel_clean, leaf_slug)
                        leaf_href = route_url_for_page(prefix, leaf_slug, base_url=outer_base_url)
                        doc_path = (
                            (source_root / rel_clean)
                            if (source_root / rel_clean).is_file()
                            else (root / rel_clean)
                        )
                        leaf_label = (
                            str(entry.get("title") or "").strip()
                            or _extract_document_title(doc_path, leaf_slug)
                        )

                        indices = [home_idx]
                        for anc_title, anc_file, anc_href in ancestors:
                            if anc_file == rel_clean:
                                continue
                            indices.append(add_node(anc_title, anc_href))
                        indices.append(add_node(leaf_label, leaf_href))
                        trails[leaf_key] = indices

                if isinstance(children, list) and children:
                    folder_title = str(entry.get("title") or "").strip()
                    next_ancestors = list(ancestors)
                    if folder_title:
                        landing_file = _find_folder_landing_file(
                            entry, source_root, root, staged_files
                        )
                        landing_href: str | None = None
                        if landing_file:
                            landing_slug = file_slug_map.get(
                                landing_file, page_slug_from_rel_path(landing_file)
                            )
                            landing_href = route_url_for_page(
                                prefix, landing_slug, base_url=outer_base_url
                            )
                        next_ancestors.append((folder_title, landing_file, landing_href))
                    walk_toc(children, next_ancestors)

        walk_toc(loc_toc, [])

        raw_ui = info.get("ui", {})
        aria_label = str(
            (raw_ui.get("breadcrumbs_label") if isinstance(raw_ui, dict) else None)
            or BREADCRUMB_LABELS.get(code, "Breadcrumbs")
        )
        breadcrumbs[code] = {
            "label": aria_label,
            "nodes": nodes,
            "trails": trails,
        }

    return breadcrumbs


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
        raw_ui = info.get("ui", {})
        compact_ui = {k: v for k, v in raw_ui.items() if k in SWITCHER_UI_KEYS} if isinstance(raw_ui, dict) else {}
        locales_meta[code] = {
            "code": code,
            "flag": str(info.get("flag") or DEFAULT_LOCALE_FLAGS.get(code, "🌐")),
            "html_lang": str(info.get("html_lang", code)),
            "hreflang": str(info.get("hreflang", code)),
            "native_name": str(info.get("native_name", code)),
            "english_name": str(info.get("english_name") or info.get("name") or code),
            "name": str(info.get("name") or info.get("english_name") or code),
            "prefix": prefix,
            "base_route": route_url_for_page(prefix, "", base_url=outer_base_url),
            "ui": compact_ui,
        }

    prov_cache: dict[str, dict[str, Any]] = {}
    pages_meta: dict[str, Any] = {}
    aliases: dict[str, str] = {}
    file_slug_map: dict[str, str] = {}
    file_key_map: dict[str, str] = {}
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
        canonical_key = active_slug if active_slug else "index"
        translations: dict[str, Any] = {}
        for code, info in enabled_locales.items():
            prefix = str(info.get("prefix", ""))
            is_avail = is_page_translation_current(root, code, default_locale, rel_file, prov_cache)
            if is_avail:
                route = route_url_for_page(prefix, active_slug, base_url=outer_base_url)
                translations[code] = {
                    "available": True,
                    "route": route,
                }
            else:
                translations[code] = {
                    "available": False,
                }

        pages_meta[canonical_key] = {
            "slug": active_slug,
            "translations": translations,
        }
        if slug_key != canonical_key:
            aliases[slug_key] = canonical_key
        if flat_slug and flat_slug != canonical_key:
            aliases[flat_slug] = canonical_key

        effective_slug = active_slug
        effective_key = canonical_key
        explicit_slug = extract_explicit_frontmatter_slug(root / rel_file)
        if explicit_slug and explicit_slug != canonical_key:
            explicit_translations: dict[str, Any] = {}
            for code, info in enabled_locales.items():
                prefix = str(info.get("prefix", ""))
                is_avail = is_page_translation_current(root, code, default_locale, rel_file, prov_cache)
                if is_avail:
                    explicit_translations[code] = {
                        "available": True,
                        "route": route_url_for_page(prefix, explicit_slug, base_url=outer_base_url),
                    }
                else:
                    explicit_translations[code] = {
                        "available": False,
                    }
            pages_meta[explicit_slug] = {
                "slug": explicit_slug,
                "translations": explicit_translations,
            }
            if (
                output_html_dir is None
                or (output_html_dir / explicit_slug / "index.html").is_file()
            ):
                aliases[canonical_key] = explicit_slug
                if slug_key != explicit_slug:
                    aliases[slug_key] = explicit_slug
                if flat_slug and flat_slug != explicit_slug:
                    aliases[flat_slug] = explicit_slug
                effective_slug = explicit_slug
                effective_key = explicit_slug

        file_slug_map[rel_file] = effective_slug
        file_key_map[rel_file] = effective_key

    breadcrumbs_index = _build_breadcrumbs_index(
        root=root,
        locales_cfg=locales_cfg,
        base_myst=base_myst,
        outer_base_url=outer_base_url,
        file_slug_map=file_slug_map,
        file_key_map=file_key_map,
        prov_cache=prov_cache,
    )

    return {
        "schema_version": "1.0",
        "default_locale": default_locale,
        "canonical_domain": domain,
        "base_url": outer_base_url,
        "locales": locales_meta,
        "pages": pages_meta,
        "aliases": aliases,
        "breadcrumbs": breadcrumbs_index,
    }


def inject_language_switcher_into_html(
    html_dir: Path,
    route_manifest: dict[str, Any],
    outer_base_url: str = "",
) -> int:
    """Inject the language switcher host element, route manifest, and module initializer into built HTML files."""
    clean_base = outer_base_url.rstrip("/")
    widget_src = f"{clean_base}/widgets/language-switcher.mjs"
    nav_drawer_src = f"{clean_base}/widgets/nav-drawer.mjs"
    manifest_json = json.dumps(route_manifest, ensure_ascii=False, separators=(",", ":"))
    host_markup = (
        f'<div id="softcloud-lang-switcher-root" data-sc-lang-switcher="1" '
        f'data-sc-base-url="{clean_base}"></div>'
    )
    script_snippet = (
        f'<script id="softcloud-i18n-manifest" type="application/json">{manifest_json}</script>\n'
        f'<script type="module" data-softcloud-lang-switcher="1">\n'
        f'import {{ mountLanguageSwitcher, ensureLanguageSwitcherHost, loadEmbeddedRouteManifest, installNavigationSync }} from "{widget_src}";\n'
        f'import {{ initNavDrawer }} from "{nav_drawer_src}";\n'
        f'const manifest = loadEmbeddedRouteManifest(document);\n'
        f'const baseUrl = {json.dumps(clean_base)};\n'
        f'window.__SC_ROUTE_MANIFEST__ = manifest;\n'
        f'window.__SC_ROOT_BASE_URL__ = baseUrl;\n'
        f'const hostEl = ensureLanguageSwitcherHost(document);\n'
        f'if (hostEl) {{\n'
        f'  mountLanguageSwitcher(hostEl, {{ routeManifest: manifest, baseUrl }});\n'
        f'}}\n'
        f'installNavigationSync({{ routeManifest: manifest, baseUrl }});\n'
        f'initNavDrawer();\n'
        f'</script>\n'
    )

    count = 0
    for html_file in sorted(html_dir.rglob("*.html")):
        if html_file.name.startswith("404") or "_locales" in html_file.parts:
            continue
        text = html_file.read_text(encoding="utf-8")
        if 'id="softcloud-i18n-manifest"' in text:
            updated = re.sub(
                r'<script\b[^>]*\bid=["\']softcloud-i18n-manifest["\'][^>]*>.*?</script>',
                lambda _: f'<script id="softcloud-i18n-manifest" type="application/json">{manifest_json}</script>',
                text,
                count=1,
                flags=re.DOTALL | re.IGNORECASE,
            )
            if updated != text:
                atomic_write_text(html_file, updated)
                count += 1
            continue
        if "data-sc-lang-switcher" not in text:
            theme_btn_re = re.compile(
                r'(<button\b[^>]*\b(?:theme-toggle|theme-switch|theme-switch-button)[^>]*>.*?</button>|<button\b[^>]*(?:aria-label|title)="[^"]*(?:theme|dark|light|mode)[^"]*"[^>]*>.*?</button>)',
                re.I | re.DOTALL,
            )
            header_end_re = re.compile(r'(<div\b[^>]*\bclass="[^"]*\bnavbar-header-items__end\b[^"]*"[^>]*>)', re.I)
            header_bar_re = re.compile(r'(<div\b[^>]*\bclass="[^"]*\bmyst-header-bar\b[^"]*"[^>]*>)', re.I)

            if theme_btn_re.search(text):
                text = theme_btn_re.sub(rf"{host_markup}\1", text, count=1)
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

        if "</body>" in text:
            text = text.replace("</body>", f"{script_snippet}</body>", 1)
            atomic_write_text(html_file, text)
            count += 1
    return count


def _resolve_trail_from_manifest(
    route_manifest: dict[str, Any],
    locale_code: str,
    slug: str,
) -> tuple[str, str, list[dict[str, Any]]] | None:
    """Resolve `(aria_label, rendered_key, items)` for `(locale_code, slug)` from route_manifest."""
    clean_slug = slug.strip("/")
    if not clean_slug or clean_slug.lower() in ("index", "readme"):
        return None
    bc_root = route_manifest.get("breadcrumbs")
    if not isinstance(bc_root, dict):
        return None
    locale_bc = bc_root.get(locale_code)
    if not isinstance(locale_bc, dict):
        return None

    nodes = locale_bc.get("nodes", [])
    trails = locale_bc.get("trails", {})
    aliases = route_manifest.get("aliases", {})
    if not isinstance(nodes, list) or not isinstance(trails, dict):
        return None

    alias_target = aliases.get(clean_slug) if isinstance(aliases, dict) else None
    resolved_key: str | None = None
    if isinstance(trails.get(clean_slug), list):
        resolved_key = clean_slug
    elif alias_target and isinstance(trails.get(alias_target), list):
        resolved_key = alias_target
    else:
        for cand_key in trails:
            if cand_key.endswith(f"/{clean_slug}"):
                resolved_key = cand_key
                break

    if not resolved_key:
        return None

    indices = trails.get(resolved_key, [])
    if not indices:
        return None

    aria_label = str(locale_bc.get("label") or BREADCRUMB_LABELS.get(locale_code, "Breadcrumbs"))
    items: list[dict[str, Any]] = []
    for idx_pos, node_idx in enumerate(indices):
        if not isinstance(node_idx, int) or node_idx < 0 or node_idx >= len(nodes):
            continue
        node = nodes[node_idx]
        if not isinstance(node, dict):
            continue
        label = str(node.get("label") or "").strip()
        if not label:
            continue
        is_current = idx_pos == len(indices) - 1
        href = node.get("href")
        clean_href = href if (isinstance(href, str) and href.startswith("/") and not href.startswith("//")) else None
        items.append({"label": label, "href": clean_href, "current": is_current})

    if not items:
        return None
    return aria_label, f"{locale_code}:{resolved_key}", items


def render_breadcrumbs_html(
    items: list[dict[str, Any]],
    aria_label: str,
    rendered_key: str,
) -> str:
    """Render semantic `<nav aria-label="..."><ol>...</ol></nav>` HTML for a breadcrumb trail."""
    escaped_label = html_lib.escape(aria_label, quote=True)
    escaped_key = html_lib.escape(rendered_key, quote=True)
    li_parts: list[str] = []
    for item in items:
        text_html = html_lib.escape(str(item.get("label") or ""), quote=False)
        href = item.get("href")
        is_current = bool(item.get("current"))
        if isinstance(href, str) and href.startswith("/") and not href.startswith("//"):
            href_esc = html_lib.escape(href, quote=True)
            current_attr = ' aria-current="page"' if is_current else ""
            li_parts.append(
                f'<li class="sc-breadcrumbs__item">'
                f'<a class="sc-breadcrumbs__link" href="{href_esc}"{current_attr}>{text_html}</a>'
                f"</li>"
            )
        else:
            li_parts.append(
                f'<li class="sc-breadcrumbs__item">'
                f'<span class="sc-breadcrumbs__label">{text_html}</span>'
                f"</li>"
            )
    return (
        f'<nav class="sc-breadcrumbs not-prose" aria-label="{escaped_label}" '
        f'data-sc-rendered-key="{escaped_key}">'
        f'<ol class="sc-breadcrumbs__list">{"".join(li_parts)}</ol>'
        f"</nav>"
    )


def inject_breadcrumbs_into_html(
    html_dir: Path,
    route_manifest: dict[str, Any],
    locales_cfg: dict[str, Any],
    outer_base_url: str = "",
) -> int:
    """Inject server-rendered breadcrumb trails on subpages and SPA sync script on all HTML pages."""
    clean_base = outer_base_url.rstrip("/")
    widget_src = f"{clean_base}/widgets/breadcrumbs.mjs"
    default_locale = str(locales_cfg.get("default_locale", "en"))
    enabled_locales = get_enabled_locales(locales_cfg)

    script_snippet = (
        f'<script type="module" data-softcloud-breadcrumbs="1">\n'
        f'import {{ initSiteBreadcrumbs, installBreadcrumbsSync }} from "{widget_src}";\n'
        f'const baseUrl = {json.dumps(clean_base)};\n'
        f'initSiteBreadcrumbs({{ baseUrl }});\n'
        f'installBreadcrumbsSync({{ baseUrl }});\n'
        f'</script>\n'
    )

    fm_marker_re = re.compile(
        r'(<div\b[^>]*\bid=["\']skip-to-frontmatter["\'][^>]*>)',
        re.IGNORECASE,
    )
    article_open_re = re.compile(r'(<article\b[^>]*>(?:\s*<div\b[^>]*\bclass=["\'][^"\']*\bhidden\b[^"\']*["\'][^>]*>\s*</div>)?)', re.IGNORECASE)
    existing_host_re = re.compile(
        r'<div\b[^>]*\bid=["\']softcloud-breadcrumbs-root["\'][^>]*>.*?</nav></div>',
        re.DOTALL | re.IGNORECASE,
    )
    existing_script_re = re.compile(
        r'<script\b[^>]*\bdata-softcloud-breadcrumbs=["\']1["\'][^>]*>.*?</script>\s*',
        re.DOTALL | re.IGNORECASE,
    )

    count = 0
    for html_file in sorted(html_dir.rglob("*.html")):
        if html_file.name.startswith("404") or "_locales" in html_file.parts:
            continue
        rel = html_file.relative_to(html_dir).as_posix()
        loc_code, slug = infer_locale_and_slug(rel, enabled_locales, default_locale)
        text = html_file.read_text(encoding="utf-8")
        updated = text

        trail_res = _resolve_trail_from_manifest(route_manifest, loc_code, slug)
        if trail_res is not None:
            aria_label, rendered_key, items = trail_res
            nav_html = render_breadcrumbs_html(items, aria_label, rendered_key)
            slug_esc = html_lib.escape(slug, quote=True)
            base_esc = html_lib.escape(clean_base, quote=True)
            host_markup = (
                f'<div id="softcloud-breadcrumbs-root" class="sc-breadcrumbs-host" '
                f'data-sc-breadcrumbs="1" data-sc-page-slug="{slug_esc}" '
                f'data-sc-base-url="{base_esc}">{nav_html}</div>'
            )
            if 'id="softcloud-breadcrumbs-root"' in updated:
                updated = existing_host_re.sub(lambda _: host_markup, updated, count=1)
            elif fm_marker_re.search(updated):
                updated = fm_marker_re.sub(lambda m: f"{host_markup}{m.group(1)}", updated, count=1)
            elif article_open_re.search(updated):
                updated = article_open_re.sub(lambda m: f"{m.group(1)}{host_markup}", updated, count=1)

        if 'data-softcloud-breadcrumbs="1"' in updated:
            updated = existing_script_re.sub("", updated, count=1)
        if "</body>" in updated:
            updated = updated.replace("</body>", f"{script_snippet}</body>", 1)

        if updated != text:
            atomic_write_text(html_file, updated)
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
        _safe_rmtree(output_html_dir)
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

    # 3. Ensure widgets exist at root and static images exist at root and per-locale
    widgets_src = root / "widgets"
    if widgets_src.is_dir():
        shutil.copytree(widgets_src, output_html_dir / "widgets", dirs_exist_ok=True)
    images_src = root / "images"
    if images_src.is_dir():
        shutil.copytree(images_src, output_html_dir / "images", dirs_exist_ok=True)
        for code, info in enabled_locales.items():
            if code == default_locale:
                continue
            prefix = str(info.get("prefix", f"/{code}")).strip("/")
            shutil.copytree(images_src, output_html_dir / prefix / "images", dirs_exist_ok=True)

    # 4. Copy top-level CNAME if present
    if (root / "CNAME").is_file():
        shutil.copy2(root / "CNAME", output_html_dir / "CNAME")

    # 4.1 Materialize explicit frontmatter slug routes (e.g. components/index.md -> /components)
    materialized_slugs = materialize_explicit_slug_routes(
        root, base_myst, output_html_dir, outer_base_url=outer_base_url
    )
    if materialized_slugs:
        print(f"[OK] Materialized explicit slug routes in {output_html_dir}: {materialized_slugs}")

    # 4.2 Sanitize any leaked _build/locales/<locale>/workspace/ GitHub URLs in HTML and JSON artifacts
    rewritten_urls = rewrite_staged_source_urls_in_dir(output_html_dir, locales_cfg)
    if rewritten_urls:
        print(f"[OK] Sanitized staged workspace GitHub URLs in {rewritten_urls} artifact files")

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

    # 7. Inject breadcrumb navigation on subpages and SPA sync on all HTML files
    bc_count = inject_breadcrumbs_into_html(
        output_html_dir, route_manifest, locales_cfg, outer_base_url=outer_base_url
    )
    print(f"[OK] Injected breadcrumb navigation into {bc_count} HTML files in {output_html_dir}")

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
        ws_disp = ws.relative_to(root) if ws.is_relative_to(root) else ws
        print(f"[OK] Staged isolated workspace for locale '{code}' -> {ws_disp}")

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
                default_locale=default_locale,
            )
        else:
            html_out = run_jupyter_book_in_workspace(ws, code, loc_base_url)
        locale_html_dirs[code] = html_out
        out_disp = html_out.relative_to(root) if html_out.is_relative_to(root) else html_out
        print(f"[OK] Built HTML for locale '{code}' (BASE_URL={loc_base_url!r}) -> {out_disp}")

    assemble_combined_html(
        root=root,
        locale_html_dirs=locale_html_dirs,
        locales_cfg=locales_cfg,
        base_myst=base_myst,
        output_html_dir=output_html_dir,
        outer_base_url=outer_base_url,
    )
    final_disp = output_html_dir.relative_to(root) if output_html_dir.is_relative_to(root) else output_html_dir
    print(f"[OK] Assembled combined multilingual site in {final_disp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
