/**
 * SoftCloud Documentation Hub — Accessible Multilingual Language Switcher
 *
 * Compatible both with MyST `{anywidget}` (`export default { render({ model, el }) }`)
 * and as a standalone site-wide header widget (`mountLanguageSwitcher`, `initSiteLanguageSwitcher`).
 *
 * Behavior:
 * - Reads availability and destination routes from `routeManifest.pages[slug].translations[locale]`.
 * - Preserves the current document route when a translation exists in the target locale.
 * - Explicitly marks untranslated pages as unavailable (`aria-disabled="true"`) rather than
 *   falling back to a hardcoded list or silently displaying English content.
 * - Automatically mounts into `[data-sc-lang-switcher]` (creating/anchoring the host if needed),
 *   parses `<script id="softcloud-i18n-manifest" type="application/json">`, and re-initializes
 *   across MyST client-side navigation (`pushState`, `replaceState`, `popstate`, DOM replacement).
 * - Full keyboard accessibility (Tab, ArrowDown/ArrowUp, Home/End, Enter/Space, Escape).
 */

export const DEFAULT_LOCALE_FLAGS = {
  en: "🇬🇧",
  pl: "🇵🇱",
  de: "🇩🇪",
  es: "🇪🇸",
  fr: "🇫🇷",
};

export function getLocaleFlag(localeCode, localeInfo = null) {
  const code = String(localeCode || "").toLowerCase();
  return (localeInfo && localeInfo.flag) || DEFAULT_LOCALE_FLAGS[code] || "🌐";
}

export const DEFAULT_LOCALES = {
  en: {
    code: "en",
    flag: "🇬🇧",
    name: "English",
    native_name: "English",
    html_lang: "en",
    prefix: "",
    base_route: "/",
    ui: {
      language_label: "Language",
      switch_language: "Select documentation language",
      translation_unavailable: "Translation unavailable for this page",
      go_to_locale_home: "Go to {language} home",
      current_language: "Current language",
    },
  },
  pl: {
    code: "pl",
    flag: "🇵🇱",
    name: "Polish",
    native_name: "Polski",
    html_lang: "pl",
    prefix: "/pl",
    base_route: "/pl/",
    ui: {
      language_label: "Język",
      switch_language: "Wybierz język dokumentacji",
      translation_unavailable: "Tłumaczenie tej strony jest niedostępne",
      go_to_locale_home: "Przejdź do strony głównej ({language})",
      current_language: "Bieżący język",
    },
  },
  de: {
    code: "de",
    flag: "🇩🇪",
    name: "German",
    native_name: "Deutsch",
    html_lang: "de",
    prefix: "/de",
    base_route: "/de/",
    ui: {
      language_label: "Sprache",
      switch_language: "Dokumentationssprache auswählen",
      translation_unavailable: "Übersetzung für diese Seite nicht verfügbar",
      go_to_locale_home: "Zur Startseite ({language})",
      current_language: "Aktuelle Sprache",
    },
  },
  es: {
    code: "es",
    flag: "🇪🇸",
    name: "Spanish",
    native_name: "Español",
    html_lang: "es",
    prefix: "/es",
    base_route: "/es/",
    ui: {
      language_label: "Idioma",
      switch_language: "Seleccionar idioma de la documentación",
      translation_unavailable: "Traducción no disponible para esta página",
      go_to_locale_home: "Ir al inicio ({language})",
      current_language: "Idioma actual",
    },
  },
  fr: {
    code: "fr",
    flag: "🇫🇷",
    name: "French",
    native_name: "Français",
    html_lang: "fr",
    prefix: "/fr",
    base_route: "/fr/",
    ui: {
      language_label: "Langue",
      switch_language: "Sélectionner la langue de la documentation",
      translation_unavailable: "Traduction indisponible pour cette page",
      go_to_locale_home: "Aller à l'accueil ({language})",
      current_language: "Langue actuelle",
    },
  },
};

/**
 * Normalize a page slug by stripping leading/trailing slashes and `.html` / `index.html`.
 */
export function normalizePageSlug(rawSlug) {
  let clean = String(rawSlug || "").trim();
  clean = clean.replace(/\/index\.html$/i, "").replace(/^index\.html$/i, "").replace(/\.html$/i, "");
  clean = clean.replace(/^\/+|\/+$/g, "");
  if (clean.toLowerCase() === "readme" || clean.toLowerCase() === "index") {
    return "";
  }
  return clean;
}

/**
 * Parse a URL pathname into { baseUrl, locale, pageSlug }.
 */
export function parsePathnameRoute(pathname, localesMap = DEFAULT_LOCALES, explicitBaseUrl = "") {
  const cleanBase = (explicitBaseUrl || "").replace(/\/+$/, "");
  let rel = (pathname || "/").trim();
  if (cleanBase && (rel === cleanBase || rel.startsWith(`${cleanBase}/`))) {
    rel = rel.slice(cleanBase.length) || "/";
  }
  rel = rel.replace(/\/index\.html$/i, "/").replace(/\.html$/i, "");
  if (!rel.startsWith("/")) rel = `/${rel}`;

  const nonDefaultLocales = Object.values(localesMap || DEFAULT_LOCALES).filter(
    (loc) => loc && loc.prefix && loc.prefix !== "/"
  );

  for (const loc of nonDefaultLocales) {
    const pfx = loc.prefix.replace(/\/+$/, "");
    if (rel === pfx || rel === `${pfx}/`) {
      return { baseUrl: cleanBase, locale: loc.code, pageSlug: "" };
    }
    if (rel.startsWith(`${pfx}/`)) {
      const slug = normalizePageSlug(rel.slice(pfx.length + 1));
      return { baseUrl: cleanBase, locale: loc.code, pageSlug: slug };
    }
  }

  const defaultSlug = normalizePageSlug(rel);
  return { baseUrl: cleanBase, locale: "en", pageSlug: defaultSlug };
}

/**
 * Build a fallback localized URL from locale prefix and pageSlug.
 */
export function buildLocalizedRouteUrl(localeInfo, pageSlug, baseUrl = "", hash = "") {
  const cleanBase = (baseUrl || "").replace(/\/+$/, "");
  const cleanPrefix = (localeInfo?.prefix || "").replace(/\/+$/, "");
  const cleanSlug = normalizePageSlug(pageSlug);
  let path = cleanSlug
    ? `${cleanBase}${cleanPrefix}/${cleanSlug}`
    : `${cleanBase}${cleanPrefix}/`;
  if (!path.startsWith("/")) path = `/${path}`;
  return `${path}${hash || ""}`;
}

/**
 * Look up translation availability and route for (localeCode, pageSlug) in `routeManifest`.
 *
 * Primarily consumes the builder schema:
 *   `routeManifest.pages[slugKey].translations[localeCode]` -> `{ available, route, canonical_url }`
 *
 * A missing manifest or missing page/locale entry strictly returns `{ available: false, route: null }`
 * without falling back to any hardcoded slug list.
 */
export function lookupPageTranslation(routeManifest, localeCode, pageSlug) {
  if (!routeManifest || typeof routeManifest !== "object" || !localeCode) {
    return { available: false, route: null, canonicalUrl: null };
  }

  const normSlug = normalizePageSlug(pageSlug);
  const slugKey = normSlug === "" ? "index" : normSlug;

  // Primary schema produced by tools/build_locales.py::build_route_manifest()
  if (routeManifest.pages && typeof routeManifest.pages === "object") {
    const pages = routeManifest.pages;
    let pageEntry = pages[slugKey] ?? pages[normSlug];

    if (!pageEntry) {
      for (const candidate of Object.values(pages)) {
        if (!candidate || typeof candidate !== "object") continue;
        const candidateSlug = normalizePageSlug(candidate.slug);
        const candidateSource = normalizePageSlug(
          String(candidate.source_file || "").replace(/\.(md|ipynb)$/i, "")
        );
        if (
          candidateSlug === normSlug ||
          candidateSource === normSlug ||
          (normSlug && candidateSlug.endsWith(`/${normSlug}`)) ||
          (normSlug && candidateSource.endsWith(`/${normSlug}`))
        ) {
          pageEntry = candidate;
          break;
        }
      }
    }

    if (!pageEntry || !pageEntry.translations || typeof pageEntry.translations !== "object") {
      return { available: false, route: null, canonicalUrl: null };
    }

    const tEntry = pageEntry.translations[localeCode];
    if (!tEntry || typeof tEntry !== "object" || tEntry.available !== true) {
      return { available: false, route: null, canonicalUrl: null };
    }

    const recordedRoute = typeof tEntry.route === "string" ? tEntry.route.trim() : "";
    if (!recordedRoute) {
      return { available: false, route: null, canonicalUrl: null };
    }

    return {
      available: true,
      route: recordedRoute,
      canonicalUrl: tEntry.canonical_url || null,
    };
  }

  // Secondary compatibility with locale-keyed manifest fixtures (only when `pages` is not used)
  if (routeManifest.locales && routeManifest.locales[localeCode]) {
    const locEntry = routeManifest.locales[localeCode];
    if (locEntry.routes && typeof locEntry.routes === "object") {
      const hasKey =
        Object.prototype.hasOwnProperty.call(locEntry.routes, normSlug) ||
        (normSlug === "" && Object.prototype.hasOwnProperty.call(locEntry.routes, "index"));
      if (hasKey) {
        const routeVal = locEntry.routes[normSlug] ?? locEntry.routes.index;
        return {
          available: Boolean(routeVal),
          route: typeof routeVal === "string" ? routeVal : null,
          canonicalUrl: null,
        };
      }
      return { available: false, route: null, canonicalUrl: null };
    }
    if (Array.isArray(locEntry.available_slugs)) {
      const isAvail =
        locEntry.available_slugs.includes(normSlug) ||
        (normSlug === "" && locEntry.available_slugs.includes("index"));
      if (isAvail) {
        return {
          available: true,
          route: buildLocalizedRouteUrl(locEntry, normSlug, routeManifest.base_url || "", ""),
          canonicalUrl: null,
        };
      }
      return { available: false, route: null, canonicalUrl: null };
    }
  }

  return { available: false, route: null, canonicalUrl: null };
}

/**
 * Determine whether a translation is available for (localeCode, pageSlug).
 */
export function isTranslationAvailable(routeManifest, localeCode, pageSlug) {
  return lookupPageTranslation(routeManifest, localeCode, pageSlug).available;
}

/**
 * Resolve the destination URL for (localeCode, pageSlug), preferring the manifest's recorded `route`.
 */
export function resolveTranslationUrl(
  routeManifest,
  localeCode,
  localeInfo,
  pageSlug,
  baseUrl = "",
  hash = ""
) {
  const lookup = lookupPageTranslation(routeManifest, localeCode, pageSlug);
  const cleanBase = (baseUrl || "").replace(/\/+$/, "");
  if (lookup.available && lookup.route) {
    let path = lookup.route;
    if (!path.startsWith("/")) {
      path = `/${path}`;
    }
    if (cleanBase && path !== cleanBase && !path.startsWith(`${cleanBase}/`)) {
      path = path === "/" ? `${cleanBase}/` : `${cleanBase}${path}`;
    }
    return `${path}${hash || ""}`;
  }
  return buildLocalizedRouteUrl(localeInfo, pageSlug, cleanBase, hash);
}

/**
 * Parse and return the embedded `#softcloud-i18n-manifest` JSON script from a document.
 */
export function loadEmbeddedRouteManifest(doc = typeof document !== "undefined" ? document : null) {
  if (doc && typeof doc.getElementById === "function") {
    const scriptEl =
      doc.getElementById("softcloud-i18n-manifest") ||
      (typeof doc.querySelector === "function"
        ? doc.querySelector('script#softcloud-i18n-manifest, script[data-sc-i18n-manifest]')
        : null);
    if (scriptEl && scriptEl.textContent) {
      try {
        const parsed = JSON.parse(scriptEl.textContent);
        if (typeof window !== "undefined") {
          window.__SC_ROUTE_MANIFEST__ = parsed;
          if (typeof parsed.base_url === "string" && window.__SC_ROOT_BASE_URL__ === undefined) {
            window.__SC_ROOT_BASE_URL__ = parsed.base_url;
          }
        }
        return parsed;
      } catch (_err) {
        // Ignore malformed JSON and fall through
      }
    }
  }
  if (typeof window !== "undefined" && window.__SC_ROUTE_MANIFEST__) {
    return window.__SC_ROUTE_MANIFEST__;
  }
  return null;
}

function addClass(el, name) {
  if (!el || !name) return;
  if (el.classList && typeof el.classList.add === "function") {
    el.classList.add(name);
  } else {
    const list = String(el.className || "").split(/\s+/).filter(Boolean);
    if (!list.includes(name)) {
      list.push(name);
      el.className = list.join(" ");
    }
  }
}

function removeClass(el, name) {
  if (!el || !name) return;
  if (el.classList && typeof el.classList.remove === "function") {
    el.classList.remove(name);
  } else {
    const list = String(el.className || "").split(/\s+/).filter((c) => c && c !== name);
    el.className = list.join(" ");
  }
}

function hasClass(el, name) {
  if (!el || !name) return false;
  if (el.classList && typeof el.classList.contains === "function") {
    return el.classList.contains(name);
  }
  return String(el.className || "").split(/\s+/).includes(name);
}

export function findThemeToggle(doc = typeof document !== "undefined" ? document : null) {
  if (!doc || typeof doc.querySelector !== "function") return null;

  const selector = [
    'button[aria-label*="theme" i]',
    'button[aria-label*="dark" i]',
    'button[aria-label*="light" i]',
    'button[aria-label*="mode" i]',
    'button[aria-label*="color" i]',
    'button[title*="theme" i]',
    'button[title*="dark" i]',
    'button[title*="light" i]',
    'button[title*="mode" i]',
    'button.theme-toggle',
    'button.theme-switch',
    'button.theme-switch-button',
    '.theme-switch-button button',
    '[data-theme-toggle]',
    '.myst-theme-toggle',
    'header button.theme-switch',
  ].join(", ");

  const direct = doc.querySelector(selector);
  if (direct) return direct;

  const headerButtons = doc.querySelectorAll("header button, .myst-top-nav button, nav button");
  for (const btn of headerButtons) {
    const text = `${btn.getAttribute("aria-label") || ""} ${btn.getAttribute("title") || ""} ${btn.className || ""} ${btn.id || ""}`.toLowerCase();
    if (text.includes("theme") || text.includes("dark") || text.includes("light") || text.includes("mode")) {
      return btn;
    }
  }

  for (const btn of headerButtons) {
    const html = btn.innerHTML || "";
    if (
      html.includes("moon") || html.includes("sun") ||
      html.includes("theme") || html.includes("mode")
    ) {
      return btn;
    }
  }

  return null;
}

function insertBeforeOrAppend(parent, newChild, refChild) {
  if (!parent || !newChild) return;
  if (refChild && typeof parent.insertBefore === "function") {
    parent.insertBefore(newChild, refChild);
  } else if (typeof parent.appendChild === "function") {
    parent.appendChild(newChild);
  }
}

function isAdjacent(el1, el2) {
  if (!el1 || !el2 || !el1.parentElement || el1.parentElement !== el2.parentElement) return false;
  const parent = el1.parentElement;
  if (Array.isArray(parent.children)) {
    const idx1 = parent.children.indexOf(el1);
    const idx2 = parent.children.indexOf(el2);
    return Math.abs(idx1 - idx2) === 1;
  }
  return el1.nextElementSibling === el2 || el1.previousElementSibling === el2;
}

/**
 * Ensure a `[data-sc-lang-switcher]` host element exists in the document and is positioned
 * next to the site theme switch toggle when available.
 */
export function ensureLanguageSwitcherHost(doc = typeof document !== "undefined" ? document : null) {
  if (!doc || typeof doc.querySelector !== "function") return null;

  const themeToggle = findThemeToggle(doc);
  const searchControl = doc.querySelector(
    '.DocSearch-Button, button[aria-label*="Search" i], input[type="search"], [data-search-button]'
  );
  const headerContainer =
    (themeToggle && themeToggle.parentElement) ||
    (searchControl && searchControl.closest("nav, header, .flex")) ||
    doc.querySelector(
      "header .navbar-header-items__end, .navbar-header-items__end, .myst-top-nav .myst-header-bar, .myst-top-nav, header nav, nav, header"
    );

  let hostEl = doc.querySelector("[data-sc-lang-switcher]");
  if (!hostEl) {
    hostEl = doc.createElement("div");
    hostEl.id = "softcloud-lang-switcher-root";
    hostEl.setAttribute("data-sc-lang-switcher", "1");
    if (themeToggle && themeToggle.parentElement) {
      insertBeforeOrAppend(themeToggle.parentElement, hostEl, themeToggle);
    } else if (searchControl && searchControl.parentElement) {
      if (searchControl.nextSibling) {
        searchControl.parentElement.insertBefore(hostEl, searchControl.nextSibling);
      } else {
        searchControl.parentElement.appendChild(hostEl);
      }
    } else if (headerContainer) {
      headerContainer.appendChild(hostEl);
    } else if (doc.body) {
      addClass(hostEl, "sc-lang-host-floating");
      doc.body.appendChild(hostEl);
    }
    return hostEl;
  }

  // If hostEl exists, position it immediately next to the theme toggle or search control
  if (themeToggle && themeToggle.parentElement) {
    if (!isAdjacent(hostEl, themeToggle)) {
      removeClass(hostEl, "sc-lang-host-floating");
      insertBeforeOrAppend(themeToggle.parentElement, hostEl, themeToggle);
    }
  } else if (searchControl && searchControl.parentElement && !isAdjacent(hostEl, searchControl)) {
    removeClass(hostEl, "sc-lang-host-floating");
    if (searchControl.nextSibling) {
      searchControl.parentElement.insertBefore(hostEl, searchControl.nextSibling);
    } else {
      searchControl.parentElement.appendChild(hostEl);
    }
  } else if (
    headerContainer &&
    hostEl.parentElement === doc.body &&
    !headerContainer.contains(hostEl)
  ) {
    removeClass(hostEl, "sc-lang-host-floating");
    headerContainer.appendChild(hostEl);
  }
  return hostEl;
}

const SWITCHER_STYLES = `
  [data-sc-lang-switcher] {
    display: inline-flex;
    align-items: center;
    vertical-align: middle;
    margin: 0 0.5rem;
    margin-inline: 0.5rem;
    padding: 0;
  }

  [data-sc-lang-switcher].sc-lang-host-floating {
    margin: 0;
    position: fixed;
    top: 0.75rem;
    right: 1rem;
    z-index: 1000;
  }

  .sc-lang-switcher {
    position: relative;
    display: inline-flex;
    flex-direction: column;
    align-items: flex-end;
    height: 36px;
    min-height: 36px;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    font-size: 0.8125rem;
    z-index: 1000;
  }

  .sc-lang-trigger {
    anchor-name: --sc-lang-trigger;
    appearance: none;
    border: 1px solid #e4e4e7;
    background: #ffffff;
    color: #18181b;
    border-radius: 50%;
    width: 36px;
    height: 36px;
    min-width: 36px;
    min-height: 36px;
    padding: 0;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    line-height: 1;
    font-size: 1.25rem;
    box-sizing: border-box;
    transition: background-color 0.15s ease, border-color 0.15s ease, transform 0.1s ease;
    user-select: none;
  }

  html.dark .sc-lang-trigger,
  body.dark .sc-lang-trigger,
  :root.dark .sc-lang-trigger,
  .dark .sc-lang-trigger,
  [data-theme="dark"] .sc-lang-trigger,
  [data-mode="dark"] .sc-lang-trigger {
    border-color: #27272a;
    background: #18181b;
    color: #fafafa;
  }

  .sc-lang-trigger:hover {
    background: #f4f4f5;
  }

  html.dark .sc-lang-trigger:hover,
  body.dark .sc-lang-trigger:hover,
  .dark .sc-lang-trigger:hover,
  [data-theme="dark"] .sc-lang-trigger:hover {
    background: #27272a;
  }

  .sc-lang-trigger:focus-visible {
    outline: 2px solid #18181b;
    outline-offset: 2px;
  }

  html.dark .sc-lang-trigger:focus-visible,
  .dark .sc-lang-trigger:focus-visible {
    outline-color: #fafafa;
  }

  .sc-lang-icon {
    display: block;
    width: 18px;
    height: 18px;
    flex-shrink: 0;
    pointer-events: none;
  }

  .sc-lang-flag {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    line-height: 1;
    font-size: 1.25rem;
  }

  .sc-lang-code-badge {
    font-size: 0.6875rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    padding: 0.1rem 0.35rem;
    border-radius: 9999px;
    background: #f4f4f5;
    color: #3f3f46;
  }

  html.dark .sc-lang-code-badge,
  body.dark .sc-lang-code-badge,
  .dark .sc-lang-code-badge,
  [data-theme="dark"] .sc-lang-code-badge {
    background: #27272a;
    color: #d4d4d8;
  }

  .sc-lang-panel {
    position: absolute;
    position-anchor: --sc-lang-trigger;
    top: calc(100% + 0.4rem);
    right: 0;
    left: auto;
    min-width: 14.5rem;
    max-width: calc(100vw - 1.5rem);
    box-sizing: border-box;
    background: #ffffff;
    color: #18181b;
    border: 1px solid #e4e4e7;
    border-radius: 10px;
    padding: 0.35rem;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
    display: flex;
    flex-direction: column;
    gap: 0.15rem;
    z-index: 1001;
  }

  .sc-lang-panel.sc-lang-panel-align-left {
    left: 0;
    right: auto;
  }

  .sc-lang-panel.sc-lang-panel-align-right {
    left: auto;
    right: 0;
  }

  @supports (position-area: bottom span-left) {
    .sc-lang-panel.sc-lang-TriggerAnchored {
      position-area: bottom span-left;
      position-try-fallbacks: flip-inline, flip-block, flip-block flip-inline;
      top: auto;
      left: auto;
      right: auto;
      bottom: auto;
    }
  }

  @supports not (position-area: bottom span-left) {
    @supports (position-area: block-end span-inline-start) {
      .sc-lang-panel.sc-lang-TriggerAnchored {
        position-area: block-end span-inline-start;
        position-try-fallbacks: flip-inline, flip-block, flip-block flip-inline;
        top: auto;
        left: auto;
        right: auto;
        bottom: auto;
      }
    }
  }

  .sc-lang-panel[hidden] {
    display: none !important;
  }

  html.dark .sc-lang-panel,
  body.dark .sc-lang-panel,
  :root.dark .sc-lang-panel,
  .dark .sc-lang-panel,
  [data-theme="dark"] .sc-lang-panel,
  [data-mode="dark"] .sc-lang-panel {
    background: #18181b;
    color: #fafafa;
    border-color: #27272a;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
  }

  .sc-lang-option {
    appearance: none;
    border: none;
    background: transparent;
    color: inherit;
    text-align: left;
    text-decoration: none;
    border-radius: 6px;
    min-block-size: 32px;
    padding: 0.45rem 0.65rem;
    font-size: 0.8125rem;
    line-height: 1.3;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem;
    transition: background-color 0.12s ease;
  }

  .sc-lang-option:hover:not([aria-disabled="true"]) {
    background: #f4f4f5;
  }

  html.dark .sc-lang-option:hover:not([aria-disabled="true"]),
  body.dark .sc-lang-option:hover:not([aria-disabled="true"]),
  .dark .sc-lang-option:hover:not([aria-disabled="true"]),
  [data-theme="dark"] .sc-lang-option:hover:not([aria-disabled="true"]) {
    background: #27272a;
  }

  .sc-lang-option:focus-visible {
    outline: 2px solid #18181b;
    outline-offset: -2px;
  }

  html.dark .sc-lang-option:focus-visible,
  .dark .sc-lang-option:focus-visible {
    outline-color: #fafafa;
  }

  .sc-lang-option[aria-current="true"] {
    font-weight: 600;
    background: rgba(24, 24, 27, 0.05);
  }

  html.dark .sc-lang-option[aria-current="true"],
  .dark .sc-lang-option[aria-current="true"] {
    background: rgba(250, 250, 250, 0.08);
  }

  .sc-lang-option[aria-disabled="true"] {
    opacity: 0.55;
    cursor: not-allowed;
  }

  .sc-lang-option-left {
    display: flex;
    align-items: center;
    gap: 0.65rem;
    min-width: 0;
  }

  .sc-lang-option-flag {
    font-size: 1.25rem;
    line-height: 1;
    flex-shrink: 0;
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }

  .sc-lang-option-main {
    display: flex;
    flex-direction: column;
    gap: 0.1rem;
    min-width: 0;
  }

  .sc-lang-option-native {
    font-weight: 500;
  }

  .sc-lang-option-sub {
    font-size: 0.6875rem;
    color: #71717a;
  }

  html.dark .sc-lang-option-sub,
  .dark .sc-lang-option-sub {
    color: #a1a1aa;
  }

  .sc-lang-notice {
    margin-top: 0.35rem;
    padding: 0.45rem 0.6rem;
    border-radius: 6px;
    background: #fef2f2;
    border: 1px solid #fecaca;
    color: #991b1b;
    font-size: 0.75rem;
    line-height: 1.35;
  }

  .sc-lang-notice[hidden] {
    display: none !important;
  }

  html.dark .sc-lang-notice,
  .dark .sc-lang-notice {
    background: #2c1517;
    border-color: #7f1d1d;
    color: #fca5a5;
  }

  .sc-lang-notice-link {
    display: inline-block;
    margin-top: 0.25rem;
    color: inherit;
    font-weight: 600;
    text-decoration: underline;
  }
`;

export function mountLanguageSwitcher(hostEl, options = {}) {
  if (!hostEl || typeof document === "undefined") return () => {};

  const doc = hostEl.ownerDocument || document;

  // Clean up any previous switcher instance mounted into the same host element
  if (typeof hostEl._scCleanup === "function") {
    hostEl._scCleanup();
  }

  const routeManifest =
    options.routeManifest ||
    loadEmbeddedRouteManifest(doc) ||
    null;

  const localesMap =
    (routeManifest && routeManifest.locales) ||
    options.locales ||
    DEFAULT_LOCALES;

  const explicitBaseUrl =
    options.baseUrl ??
    hostEl.getAttribute?.("data-sc-base-url") ??
    (routeManifest && typeof routeManifest.base_url === "string"
      ? routeManifest.base_url
      : typeof window !== "undefined" && typeof window.__SC_ROOT_BASE_URL__ === "string"
      ? window.__SC_ROOT_BASE_URL__
      : "");

  const pathname =
    options.pathname ||
    (typeof window !== "undefined" && window.location?.pathname) ||
    "/";

  const parsed = parsePathnameRoute(pathname, localesMap, explicitBaseUrl);

  // Only fall back to static <meta> tags when pathname was not explicitly overridden
  // and matches the initial document URL.
  const metaLocale =
    !options.pathname && typeof doc.querySelector === "function"
      ? doc.querySelector('meta[name="sc-locale"]')?.getAttribute("content")
      : null;
  const metaSlug =
    !options.pathname && typeof doc.querySelector === "function"
      ? doc.querySelector('meta[name="sc-page-slug"]')?.getAttribute("content")
      : null;

  const currentLocaleCode = (
    options.locale ||
    parsed.locale ||
    metaLocale ||
    "en"
  ).toLowerCase();

  const currentPageSlug = normalizePageSlug(
    options.pageSlug !== undefined
      ? options.pageSlug
      : parsed.pageSlug !== ""
      ? parsed.pageSlug
      : metaSlug !== null && metaSlug !== undefined
      ? metaSlug
      : parsed.pageSlug
  );

  const currentLocaleInfo = localesMap[currentLocaleCode] || DEFAULT_LOCALES.en;
  const ui = {
    ...DEFAULT_LOCALES.en.ui,
    ...(DEFAULT_LOCALES[currentLocaleCode]?.ui || {}),
    ...(currentLocaleInfo.ui || {}),
  };

  const styleEl = doc.createElement("style");
  styleEl.textContent = SWITCHER_STYLES;

  const wrapper = doc.createElement("div");
  wrapper.className = "sc-lang-switcher";
  wrapper.setAttribute("data-sc-locale", currentLocaleCode);
  wrapper.setAttribute("data-sc-page-slug", currentPageSlug);

  const panelId = `sc-lang-panel-${Math.random().toString(36).slice(2, 8)}`;

  const currentFlag = getLocaleFlag(currentLocaleCode, currentLocaleInfo);

  const triggerBtn = doc.createElement("button");
  triggerBtn.type = "button";
  triggerBtn.className = "sc-lang-trigger";
  triggerBtn.setAttribute("aria-haspopup", "true");
  triggerBtn.setAttribute("aria-expanded", "false");
  triggerBtn.setAttribute("aria-controls", panelId);
  triggerBtn.setAttribute("aria-label", `${ui.switch_language}: ${currentLocaleInfo.native_name}`);
  triggerBtn.setAttribute("title", `${ui.switch_language}: ${currentLocaleInfo.native_name}`);
  triggerBtn.innerHTML = `
    <svg class="sc-lang-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
      <circle cx="12" cy="12" r="10"></circle>
      <line x1="2" y1="12" x2="22" y2="12"></line>
      <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
    </svg>
  `.trim();

  const panel = doc.createElement("div");
  panel.id = panelId;
  panel.className = "sc-lang-panel sc-lang-TriggerAnchored";
  panel.setAttribute("role", "group");
  panel.setAttribute("aria-label", ui.switch_language);
  panel.hidden = true;

  const noticeBox = doc.createElement("div");
  noticeBox.className = "sc-lang-notice";
  noticeBox.setAttribute("role", "status");
  noticeBox.setAttribute("aria-live", "polite");
  noticeBox.hidden = true;

  const optionEls = [];

  for (const [code, locInfo] of Object.entries(localesMap)) {
    const lookup = lookupPageTranslation(routeManifest, code, currentPageSlug);
    const available = lookup.available;
    const isCurrent = code === currentLocaleCode;
    const hash =
      options.hash !== undefined
        ? options.hash
        : (typeof window !== "undefined" && window.location?.hash) || "";
    const targetUrl = resolveTranslationUrl(
      routeManifest,
      code,
      locInfo,
      currentPageSlug,
      parsed.baseUrl,
      hash
    );
    const homeUrl =
      (typeof locInfo.base_route === "string" && locInfo.base_route) ||
      buildLocalizedRouteUrl(locInfo, "", parsed.baseUrl, "");

    const item = doc.createElement(available ? "a" : "button");
    item.className = "sc-lang-option";
    item.setAttribute("lang", locInfo.html_lang || code);
    item.setAttribute("data-locale-code", code);

    if (available) {
      item.setAttribute("href", targetUrl);
      if (isCurrent) {
        item.setAttribute("aria-current", "true");
      }
    } else {
      item.type = "button";
      item.setAttribute("aria-disabled", "true");
    }

    const flagSpan = doc.createElement("span");
    flagSpan.className = "sc-lang-option-flag";
    flagSpan.setAttribute("role", "img");
    flagSpan.setAttribute("aria-hidden", "true");
    flagSpan.textContent = getLocaleFlag(code, locInfo);

    const mainSpan = doc.createElement("span");
    mainSpan.className = "sc-lang-option-main";

    const nativeSpan = doc.createElement("span");
    nativeSpan.className = "sc-lang-option-native";
    nativeSpan.textContent = locInfo.native_name || code;

    const subSpan = doc.createElement("span");
    subSpan.className = "sc-lang-option-sub";
    const locUi = {
      ...DEFAULT_LOCALES.en.ui,
      ...(DEFAULT_LOCALES[code]?.ui || {}),
      ...(locInfo.ui || {}),
    };
    const displayEnglishName =
      (locInfo.english_name && locInfo.english_name !== code)
        ? locInfo.english_name
        : (locInfo.name || DEFAULT_LOCALES[code]?.name || code);
    subSpan.textContent = available
      ? displayEnglishName
      : locUi.translation_unavailable || ui.translation_unavailable;

    mainSpan.append(nativeSpan, subSpan);

    const leftContainer = doc.createElement("div");
    leftContainer.className = "sc-lang-option-left";
    leftContainer.append(flagSpan, mainSpan);

    const badge = doc.createElement("span");
    badge.className = "sc-lang-code-badge";
    badge.setAttribute("aria-hidden", "true");
    badge.textContent = isCurrent ? `✓ ${code.toUpperCase()}` : code.toUpperCase();

    item.append(leftContainer, badge);

    item.addEventListener("click", (e) => {
      if (!available) {
        e.preventDefault();
        const unavailMsg = locUi.translation_unavailable || ui.translation_unavailable;
        const homeLabel = (locUi.go_to_locale_home || ui.go_to_locale_home).replace(
          "{language}",
          locInfo.native_name || code
        );
        noticeBox.innerHTML = "";
        const msgSpan = doc.createElement("div");
        msgSpan.textContent = `${locInfo.native_name}: ${unavailMsg}.`;
        const homeLink = doc.createElement("a");
        homeLink.className = "sc-lang-notice-link";
        homeLink.href = homeUrl;
        homeLink.textContent = homeLabel;
        noticeBox.append(msgSpan, homeLink);
        noticeBox.hidden = false;
        return;
      }
      if (typeof options.onNavigate === "function") {
        e.preventDefault();
        options.onNavigate({ locale: code, url: targetUrl, pageSlug: currentPageSlug });
        setOpen(false);
      } else {
        setOpen(false);
      }
    });

    panel.appendChild(item);
    optionEls.push(item);
  }

  panel.appendChild(noticeBox);
  wrapper.append(triggerBtn, panel);
  hostEl.append(styleEl, wrapper);
  hostEl.setAttribute("data-sc-mounted", "true");

  let isOpen = false;

  function adjustPanelAlignment() {
    if (!isOpen) return;

    if (
      typeof window === "undefined" ||
      typeof triggerBtn.getBoundingClientRect !== "function" ||
      typeof panel.getBoundingClientRect !== "function"
    ) {
      removeClass(panel, "sc-lang-panel-align-left");
      addClass(panel, "sc-lang-panel-align-right");
      return;
    }

    const triggerRect = triggerBtn.getBoundingClientRect();
    const viewportWidth =
      (doc.documentElement && doc.documentElement.clientWidth) ||
      window.innerWidth ||
      1024;

    const isRightSide = triggerRect.left > viewportWidth / 2;

    if (isRightSide) {
      removeClass(panel, "sc-lang-panel-align-left");
      addClass(panel, "sc-lang-panel-align-right");
      const currentRect = panel.getBoundingClientRect();
      if (
        currentRect.left < 8 &&
        currentRect.width > 0 &&
        triggerRect.left + currentRect.width <= viewportWidth - 8
      ) {
        removeClass(panel, "sc-lang-panel-align-right");
        addClass(panel, "sc-lang-panel-align-left");
      }
    } else {
      removeClass(panel, "sc-lang-panel-align-right");
      addClass(panel, "sc-lang-panel-align-left");
      const currentRect = panel.getBoundingClientRect();
      if (
        currentRect.right > viewportWidth - 8 &&
        currentRect.width > 0 &&
        triggerRect.right - currentRect.width >= 8
      ) {
        removeClass(panel, "sc-lang-panel-align-left");
        addClass(panel, "sc-lang-panel-align-right");
      }
    }
  }

  function setOpen(open) {
    isOpen = Boolean(open);
    panel.hidden = !isOpen;
    triggerBtn.setAttribute("aria-expanded", String(isOpen));
    if (!isOpen) {
      noticeBox.hidden = true;
    } else {
      adjustPanelAlignment();
    }
  }

  triggerBtn.addEventListener("click", () => {
    setOpen(!isOpen);
    if (isOpen && optionEls.length > 0) {
      const currentIdx = optionEls.findIndex(
        (el) => el.getAttribute("data-locale-code") === currentLocaleCode
      );
      const targetEl = optionEls[currentIdx >= 0 ? currentIdx : 0];
      targetEl?.focus();
    }
  });

  wrapper.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && isOpen) {
      e.preventDefault();
      setOpen(false);
      triggerBtn.focus();
      return;
    }
    if (!isOpen && (e.key === "ArrowDown" || e.key === "ArrowUp")) {
      e.preventDefault();
      setOpen(true);
      optionEls[0]?.focus();
      return;
    }
    if (isOpen && optionEls.length > 0) {
      const activeIdx = optionEls.indexOf(doc.activeElement);
      if (e.key === "ArrowDown") {
        e.preventDefault();
        const nextIdx = activeIdx < optionEls.length - 1 ? activeIdx + 1 : 0;
        optionEls[nextIdx]?.focus();
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        const prevIdx = activeIdx > 0 ? activeIdx - 1 : optionEls.length - 1;
        optionEls[prevIdx]?.focus();
      } else if (e.key === "Home") {
        e.preventDefault();
        optionEls[0]?.focus();
      } else if (e.key === "End") {
        e.preventDefault();
        optionEls[optionEls.length - 1]?.focus();
      }
    }
  });

  function onDocumentPointerDown(e) {
    if (isOpen && !wrapper.contains(e.target)) {
      setOpen(false);
    }
  }

  doc.addEventListener("pointerdown", onDocumentPointerDown);

  const onResize = () => {
    if (isOpen) {
      adjustPanelAlignment();
    }
  };
  if (typeof window !== "undefined" && typeof window.addEventListener === "function") {
    window.addEventListener("resize", onResize);
  }

  const cleanup = () => {
    doc.removeEventListener("pointerdown", onDocumentPointerDown);
    if (typeof window !== "undefined" && typeof window.removeEventListener === "function") {
      window.removeEventListener("resize", onResize);
    }
    wrapper.remove();
    styleEl.remove();
    hostEl.removeAttribute("data-sc-mounted");
    if (hostEl._scCleanup === cleanup) {
      delete hostEl._scCleanup;
    }
  };
  hostEl._scCleanup = cleanup;
  return cleanup;
}

/**
 * Initialize or refresh the site-wide language switcher on direct page load and client-side navigation.
 */
export function initSiteLanguageSwitcher(options = {}) {
  const doc = options.document || (typeof document !== "undefined" ? document : null);
  if (!doc) return () => {};

  const routeManifest = options.routeManifest || loadEmbeddedRouteManifest(doc);
  const hostEl = options.hostEl || ensureLanguageSwitcherHost(doc);
  if (!hostEl) return () => {};

  const baseUrl =
    options.baseUrl ??
    hostEl.getAttribute?.("data-sc-base-url") ??
    (routeManifest && typeof routeManifest.base_url === "string" ? routeManifest.base_url : "");

  return mountLanguageSwitcher(hostEl, {
    ...options,
    routeManifest,
    baseUrl,
  });
}

/**
 * Install client-side navigation hooks (pushState, replaceState, popstate, DOM observer)
 * so MyST SPA transitions keep the language switcher mounted and synchronized with the current route.
 */
export function installNavigationSync(options = {}) {
  if (typeof window === "undefined" || typeof document === "undefined") return;
  if (window.__SC_LANG_NAV_SYNC_INSTALLED__) return;
  window.__SC_LANG_NAV_SYNC_INSTALLED__ = true;

  let lastPathname = window.location?.pathname || "/";

  const syncIfNeeded = () => {
    const currentPathname = window.location?.pathname || "/";
    const hostEl = document.querySelector("[data-sc-lang-switcher]");
    const mountedSwitcher = hostEl?.querySelector(".sc-lang-switcher");
    const themeToggle = findThemeToggle(document);
    const adjacent = themeToggle && hostEl ? isAdjacent(hostEl, themeToggle) : true;
    if (!hostEl || !mountedSwitcher || !adjacent || currentPathname !== lastPathname) {
      lastPathname = currentPathname;
      ensureLanguageSwitcherHost(document);
      initSiteLanguageSwitcher(options);
    }
  };

  window.addEventListener("popstate", syncIfNeeded);

  if (window.history) {
    for (const method of ["pushState", "replaceState"]) {
      const orig = window.history[method];
      if (typeof orig === "function") {
        window.history[method] = function (...args) {
          const result = orig.apply(this, args);
          if (typeof queueMicrotask === "function") {
            queueMicrotask(syncIfNeeded);
          } else {
            Promise.resolve().then(syncIfNeeded);
          }
          return result;
        };
      }
    }
  }

  if (typeof MutationObserver !== "undefined" && document.body) {
    const observer = new MutationObserver(() => {
      const hostEl = document.querySelector("[data-sc-lang-switcher]");
      const themeToggle = findThemeToggle(document);
      const adjacent = themeToggle && hostEl ? isAdjacent(hostEl, themeToggle) : true;
      if (!hostEl || !hostEl.querySelector(".sc-lang-switcher") || !adjacent) {
        syncIfNeeded();
      }
    });
    observer.observe(document.body, { childList: true, subtree: true });
  }
}

function render({ model, el }) {
  const locale = (model && typeof model.get === "function" && model.get("locale")) || undefined;
  const pageSlug = (model && typeof model.get === "function" && model.get("page")) || undefined;
  const baseUrl = (model && typeof model.get === "function" && model.get("base_url")) || undefined;
  const routeManifest =
    (model && typeof model.get === "function" && model.get("route_manifest")) || undefined;

  return mountLanguageSwitcher(el, {
    locale,
    pageSlug,
    baseUrl,
    routeManifest,
  });
}

// Auto-mount on static documentation pages and install client-side navigation sync
if (typeof document !== "undefined") {
  const boot = () => {
    initSiteLanguageSwitcher();
    installNavigationSync();
  };
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot, { once: true });
  } else {
    boot();
  }
}

export default {
  render,
  mountLanguageSwitcher,
  initSiteLanguageSwitcher,
  installNavigationSync,
  loadEmbeddedRouteManifest,
  ensureLanguageSwitcherHost,
  findThemeToggle,
  isAdjacent,
  getLocaleFlag,
  DEFAULT_LOCALE_FLAGS,
  DEFAULT_LOCALES,
  parsePathnameRoute,
  normalizePageSlug,
  buildLocalizedRouteUrl,
  lookupPageTranslation,
  isTranslationAvailable,
  resolveTranslationUrl,
};
