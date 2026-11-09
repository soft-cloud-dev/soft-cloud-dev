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

import subprocess
import generate_audio as ga
from i18n_utils import (
    canonical_url_for_page,
    extract_fenced_code_blocks_from_markdown,
    get_enabled_locales,
    load_glossary,
    load_locales_config,
    load_yaml_file,
    page_slug_from_rel_path,
)
from translate_sources import (
    build_translation_prompt,
    check_locale_provenance,
    discover_source_documents,
    verify_document_preservation,
)

API_KEY_LEAK_RE = re.compile(r"AIza[0-9A-Za-z_-]{35}")


def verify_locales_configuration(root: Path) -> list[str]:
    """Validate i18n/locales.yml and i18n/glossary.yml structure, prompt glossary injection, and validator invariants."""
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
            # Verify glossary domain_terms reach build_translation_prompt for all target locales
            for code, info in enabled.items():
                if code == default_locale:
                    continue
                prompt_text = build_translation_prompt(
                    "# Heading", code, str(info.get("english_name") or info.get("name", code)), glossary
                )
                for term_id, term_entry in domain_terms.items():
                    if isinstance(term_entry, dict):
                        en_val = str(term_entry.get("en", "")).strip()
                        loc_val = str(term_entry.get(code, "")).strip()
                        if en_val and loc_val and f'"{en_val}": "{loc_val}"' not in prompt_text:
                            errors.append(
                                f"[{code}] Glossary term {term_id!r} ({en_val!r} -> {loc_val!r}) missing from translation prompt"
                            )
    except Exception as exc:
        errors.append(f"Failed to load i18n/glossary.yml: {exc}")

    # Self-test code-preservation validator against tilde fences and nested directive code blocks
    b_tilde_1 = extract_fenced_code_blocks_from_markdown("~~~python\nprint(1)\n~~~\n")
    b_tilde_2 = extract_fenced_code_blocks_from_markdown("~~~python\nprint(2)\n~~~\n")
    if len(b_tilde_1) != 1 or b_tilde_1 == b_tilde_2:
        errors.append("Code-preservation extractor failed to distinguish ~~~python tilde fences")

    b_nested_1 = extract_fenced_code_blocks_from_markdown(":::{note}\n```python\nprint(1)\n```\n:::\n")
    b_nested_2 = extract_fenced_code_blocks_from_markdown(":::{note}\n```python\nprint(2)\n```\n:::\n")
    if len(b_nested_1) != 1 or b_nested_1 == b_nested_2:
        errors.append("Code-preservation extractor failed to inspect code blocks nested inside ::: directives")

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

    route_manifest_obj: dict[str, Any] = {}
    if route_manifest_path.is_file():
        try:
            route_manifest_obj = json.loads(route_manifest_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    rm_pages = route_manifest_obj.get("pages", {})
    rm_aliases = route_manifest_obj.get("aliases", {})

    # 3. Verify every localized page route exists and has valid lang, canonical, and reciprocal hreflang
    expected_sitemap_locs: set[str] = set()
    for rel_doc in docs:
        raw_slug = page_slug_from_rel_path(rel_doc)
        flat_name = Path(raw_slug).name if raw_slug else ""
        flat_slug = "index-1" if flat_name.lower() in ("index", "readme") else flat_name

        # Detect which slug form (nested vs flat) the build produced in the default locale
        active_slug = raw_slug
        if raw_slug and raw_slug != flat_slug:
            if not (build_dir / raw_slug / "index.html").is_file() and (
                (build_dir / flat_slug / "index.html").is_file()
                or (build_dir / f"{flat_slug}.html").is_file()
            ):
                active_slug = flat_slug

        slug_key = active_slug if active_slug else "index"
        raw_key = raw_slug if raw_slug else "index"
        alias_target = rm_aliases.get(slug_key) or rm_aliases.get(raw_key)
        page_rec = (
            rm_pages.get(slug_key)
            or rm_pages.get(raw_key)
            or (rm_pages.get(alias_target) if alias_target else None)
            or {}
        )
        page_translations = page_rec.get("translations", {})

        expected_alternates: dict[str, str] = {}
        for code, info in enabled_locales.items():
            t_info = page_translations.get(code, {})
            # Progressive publication: only include available translations in alternate hreflang
            if t_info.get("available") is not False:
                prefix = str(info.get("prefix", ""))
                hreflang = str(info.get("hreflang", code))
                expected_alternates[hreflang] = canonical_url_for_page(domain, prefix, active_slug)
        expected_alternates["x-default"] = canonical_url_for_page(domain, "", active_slug)

        for code, info in enabled_locales.items():
            t_info = page_translations.get(code, {})
            is_available = t_info.get("available") is not False
            if not is_available:
                # Progressive publication: unready/untranslated page is NOT expected to have a built route
                continue

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

            # Verify language switcher host element, embedded manifest, and explicit initializer
            if not re.search(r'<[a-zA-Z0-9-]+\b[^>]*\bdata-sc-lang-switcher\b', html_text):
                errors.append(
                    f"[{code}] Missing [data-sc-lang-switcher] host element in {found_html.relative_to(build_dir)}"
                )
            if "language-switcher.mjs" not in html_text or "mountLanguageSwitcher(" not in html_text or "loadEmbeddedRouteManifest(" not in html_text:
                errors.append(
                    f"[{code}] Missing language-switcher.mjs mount initializer in {found_html.relative_to(build_dir)}"
                )

            # Verify button accessibility: all buttons (especially myst-search-bar) must have discernible text
            search_btn_match = re.search(
                r'<button\b[^>]*\bclass="[^"]*\bmyst-search-bar\b[^"]*"[^>]*>',
                html_text,
                re.IGNORECASE,
            )
            if search_btn_match:
                tag = search_btn_match.group(0)
                if not re.search(r'\baria-label\s*=', tag, re.IGNORECASE):
                    errors.append(
                        f"[{code}] <button class=\"myst-search-bar\"> missing aria-label in {found_html.relative_to(build_dir)}"
                    )

            manifest_match = re.search(
                r'<script\b[^>]*\bid=["\']softcloud-i18n-manifest["\'][^>]*>(.*?)</script>',
                html_text,
                flags=re.IGNORECASE | re.DOTALL,
            )
            if not manifest_match:
                errors.append(
                    f"[{code}] Missing #softcloud-i18n-manifest script in {found_html.relative_to(build_dir)}"
                )
            else:
                try:
                    embedded_rm = json.loads(manifest_match.group(1))
                    embedded_pages = embedded_rm.get("pages", {})
                    embedded_aliases = embedded_rm.get("aliases", {})
                    slug_key = active_slug if active_slug else "index"
                    raw_key = raw_slug if raw_slug else "index"
                    emb_alias = embedded_aliases.get(slug_key) or embedded_aliases.get(raw_key)
                    page_rec = (
                        embedded_pages.get(slug_key)
                        or embedded_pages.get(raw_key)
                        or (embedded_pages.get(emb_alias) if emb_alias else None)
                    )
                    if not isinstance(page_rec, dict):
                        errors.append(
                            f"[{code}] Embedded manifest missing page entry for '{slug_key}' in {found_html.relative_to(build_dir)}"
                        )
                    else:
                        t_rec = page_rec.get("translations", {}).get(code)
                        if not isinstance(t_rec, dict) or t_rec.get("available") is not True or not t_rec.get("route"):
                            errors.append(
                                f"[{code}] Embedded manifest missing available route for '{slug_key}' in {found_html.relative_to(build_dir)}"
                            )
                except Exception as exc:
                    errors.append(
                        f"[{code}] Malformed JSON in #softcloud-i18n-manifest in {found_html.relative_to(build_dir)}: {exc}"
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

    # 5. Execute language-switcher runtime DOM & navigation verification against built artifact
    errors.extend(verify_language_switcher_runtime(root, build_dir))

    return errors


def verify_language_switcher_runtime(root: Path, build_dir: Path) -> list[str]:
    """Execute widgets/language-switcher.mjs against the built HTML manifest to verify mounting,
    builder manifest schema consumption, nested-source routing, SPA navigation, and unavailable fixtures."""
    import shutil

    errors: list[str] = []
    intro_html = build_dir / "introduction" / "index.html"
    switcher_mjs = build_dir / "widgets" / "language-switcher.mjs"
    if not switcher_mjs.is_file():
        switcher_mjs = root / "widgets" / "language-switcher.mjs"
    if not intro_html.is_file() or not switcher_mjs.is_file():
        return errors

    html_text = intro_html.read_text(encoding="utf-8")
    m_match = re.search(
        r'<script\b[^>]*\bid=["\']softcloud-i18n-manifest["\'][^>]*>(.*?)</script>',
        html_text,
        flags=re.S,
    )
    if not m_match:
        return ["Missing #softcloud-i18n-manifest in built introduction/index.html"]
    embedded_manifest_str = m_match.group(1)

    jsc_bin = Path("/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc")
    node_bin = shutil.which("node")
    runner_cmd: list[str] | None = None
    if jsc_bin.is_file():
        runner_cmd = [str(jsc_bin)]
    elif node_bin:
        runner_cmd = [node_bin]
    if not runner_cmd:
        return errors

    switcher_code = switcher_mjs.read_text(encoding="utf-8")
    switcher_plain = re.sub(r"^export\s+default\s+\{.*?\};?\s*$", "", switcher_code, flags=re.M | re.S)
    switcher_plain = re.sub(r"^export\s+(const|function)\s+", r"\1 ", switcher_plain, flags=re.M)

    js_script = f"""
const _out = (typeof print === "function") ? print : console.log;
const _quit = (typeof quit === "function") ? quit : (c) => process.exit(c);
class MockElement {{
  constructor(tagName, ownerDocument) {{
    this.tagName = String(tagName || "DIV").toUpperCase();
    this.ownerDocument = ownerDocument;
    this.attributes = {{}};
    this.children = [];
    this.parentElement = null;
    this.textContent = "";
    this._innerHTML = "";
    this.className = "";
    this.id = "";
    this.hidden = false;
    this.type = "";
    this.href = "";
    this.listeners = {{}};
  }}
  set innerHTML(val) {{ this._innerHTML = String(val); if (val === "") this.children = []; }}
  get innerHTML() {{ return this._innerHTML; }}
  setAttribute(k, v) {{
    this.attributes[k] = String(v);
    if (k === "id") this.id = String(v);
    if (k === "href") this.href = String(v);
    if (k === "class") this.className = String(v);
  }}
  getAttribute(k) {{
    if (k === "id" && this.id) return this.id;
    if (k === "href" && this.href) return this.href;
    return Object.prototype.hasOwnProperty.call(this.attributes, k) ? this.attributes[k] : null;
  }}
  removeAttribute(k) {{ delete this.attributes[k]; }}
  appendChild(child) {{
    if (child.parentElement) {{
      const idx = child.parentElement.children.indexOf(child);
      if (idx >= 0) child.parentElement.children.splice(idx, 1);
    }}
    child.parentElement = this;
    this.children.push(child);
    return child;
  }}
  append(...nodes) {{ nodes.forEach(n => this.appendChild(n)); }}
  remove() {{
    if (this.parentElement) {{
      const idx = this.parentElement.children.indexOf(this);
      if (idx >= 0) this.parentElement.children.splice(idx, 1);
      this.parentElement = null;
    }}
  }}
  contains(target) {{
    if (target === this) return true;
    return this.children.some(c => c.contains && c.contains(target));
  }}
  addEventListener(type, fn) {{
    if (!this.listeners[type]) this.listeners[type] = [];
    this.listeners[type].push(fn);
  }}
  removeEventListener(type, fn) {{
    if (!this.listeners[type]) return;
    this.listeners[type] = this.listeners[type].filter(f => f !== fn);
  }}
  click() {{
    let defaultPrevented = false;
    const evt = {{ target: this, preventDefault: () => {{ defaultPrevented = true; }} }};
    (this.listeners["click"] || []).forEach(fn => fn(evt));
    return !defaultPrevented;
  }}
  focus() {{ if (this.ownerDocument) this.ownerDocument.activeElement = this; }}
  matches(sel) {{
    if (sel === "[data-sc-lang-switcher]") return this.getAttribute("data-sc-lang-switcher") !== null;
    if (sel === ".sc-lang-switcher") return this.className.split(/\\s+/).includes("sc-lang-switcher");
    if (sel === ".sc-lang-option") return this.className.split(/\\s+/).includes("sc-lang-option");
    if (sel === ".sc-lang-notice") return this.className.split(/\\s+/).includes("sc-lang-notice");
    if (sel === ".sc-lang-notice-link") return this.className.split(/\\s+/).includes("sc-lang-notice-link");
    if (sel.includes("myst-header-bar")) return this.tagName === "HEADER" || this.className.includes("myst-header-bar");
    if (sel.includes("softcloud-i18n-manifest")) return this.tagName === "SCRIPT" && this.id === "softcloud-i18n-manifest";
    return false;
  }}
  querySelectorAll(sel) {{
    const out = [];
    const walk = (node) => {{
      for (const c of node.children) {{
        if (c.matches && c.matches(sel)) out.push(c);
        walk(c);
      }}
    }};
    walk(this);
    return out;
  }}
  querySelector(sel) {{ return this.querySelectorAll(sel)[0] || null; }}
}}
class MockDocument {{
  constructor(manifestJsonText) {{
    this.readyState = "complete";
    this.activeElement = null;
    this.listeners = {{}};
    this.body = new MockElement("BODY", this);
    this.headerBar = new MockElement("DIV", this);
    this.headerBar.className = "myst-header-bar";
    this.body.appendChild(this.headerBar);
    const host = new MockElement("DIV", this);
    host.setAttribute("id", "softcloud-lang-switcher-root");
    host.setAttribute("data-sc-lang-switcher", "1");
    host.setAttribute("data-sc-base-url", "");
    this.headerBar.appendChild(host);
    const script = new MockElement("SCRIPT", this);
    script.setAttribute("id", "softcloud-i18n-manifest");
    script.textContent = manifestJsonText;
    this.body.appendChild(script);
  }}
  createElement(tag) {{ return new MockElement(tag, this); }}
  getElementById(id) {{
    const walk = (n) => {{
      if (n.id === id) return n;
      for (const c of n.children) {{ const f = walk(c); if (f) return f; }}
      return null;
    }};
    return walk(this.body);
  }}
  querySelectorAll(sel) {{ return this.body.querySelectorAll(sel); }}
  querySelector(sel) {{ return this.body.querySelector(sel); }}
  addEventListener() {{}}
  removeEventListener() {{}}
}}
globalThis.window = {{
  location: {{ pathname: "/introduction", hash: "" }},
  listeners: {{}},
  addEventListener(type, fn) {{ (this.listeners[type] = this.listeners[type] || []).push(fn); }},
  history: {{
    pushState(_s, _t, u) {{ window.location.pathname = u; }},
    replaceState(_s, _t, u) {{ window.location.pathname = u; }},
  }},
}};
globalThis.document = new MockDocument({json.dumps(embedded_manifest_str)});
{switcher_plain}
function check(cond, msg) {{ if (!cond) {{ _out("FAIL: " + msg); _quit(1); }} }}
const sw = document.querySelector(".sc-lang-switcher");
check(sw !== null, "Switcher must mount into [data-sc-lang-switcher] on initial load");
check(sw.getAttribute("data-sc-locale") === "en" && sw.getAttribute("data-sc-page-slug") === "introduction", "Initial route state");
const plOpt = sw.querySelectorAll(".sc-lang-option").find(o => o.getAttribute("data-locale-code") === "pl");
check(plOpt && plOpt.tagName === "A" && plOpt.getAttribute("href") === "/pl/introduction", "Polish introduction href");
window.location.pathname = "/projects/linux";
initSiteLanguageSwitcher();
const deLinux = document.querySelector(".sc-lang-switcher").querySelectorAll(".sc-lang-option").find(o => o.getAttribute("data-locale-code") === "de");
const expectedDeLinux = lookupPageTranslation(window.__SC_ROUTE_MANIFEST__, "de", "projects/linux");
check(
  expectedDeLinux.available &&
    expectedDeLinux.route &&
    deLinux &&
    deLinux.getAttribute("href") === expectedDeLinux.route,
  "German nested-source route href"
);
window.history.pushState({{}}, "", "/es/architecture");
(window.listeners["popstate"] || []).forEach(fn => fn());
check(document.querySelector(".sc-lang-switcher").getAttribute("data-sc-locale") === "es", "SPA pushState locale update");
const unavailManifest = {{
  schema_version: "1.0",
  default_locale: "en",
  locales: window.__SC_ROUTE_MANIFEST__.locales,
  pages: {{ introduction: {{ slug: "introduction", translations: {{ en: {{ available: true, route: "/introduction" }}, pl: {{ available: false, route: null }} }} }} }}
}};
window.location.pathname = "/introduction";
initSiteLanguageSwitcher({{ routeManifest: unavailManifest }});
const plBtn = document.querySelector(".sc-lang-switcher").querySelectorAll(".sc-lang-option").find(o => o.getAttribute("data-locale-code") === "pl");
check(plBtn && plBtn.tagName === "BUTTON" && plBtn.getAttribute("aria-disabled") === "true", "Unavailable translation renders disabled button");
check(plBtn.click() === false, "Clicking unavailable option prevents navigation");
check(document.querySelector(".sc-lang-notice").hidden === false, "Unavailable notice shown");
"""
    tmp_js = build_dir / ".tmp_verify_switcher.js"
    try:
        tmp_js.write_text(js_script, encoding="utf-8")
        proc = subprocess.run(
            [*runner_cmd, str(tmp_js)],
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            errors.append(
                f"Language-switcher runtime verification failed ({proc.returncode}): "
                f"{(proc.stdout + proc.stderr).strip()}"
            )
    finally:
        tmp_js.unlink(missing_ok=True)

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
    parser.add_argument(
        "--progressive",
        action="store_true",
        help="Permit progressive publication coverage (untranslated pages omitted from locale routes).",
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
        errors.extend(check_locale_provenance(root, code, docs, progressive=args.progressive))

    # 3. Localized Narration Audio Verification across all enabled locales
    ga_args = ["--all-locales", "--narrated-only", "--check-only"]
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
