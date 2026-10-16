/**
 * SoftCloud Documentation Hub — Accessible Multilingual Language Switcher
 *
 * Compatible both with MyST `{anywidget}` (`export default { render({ model, el }) }`)
 * and as a standalone site-wide header widget (`mountLanguageSwitcher`).
 *
 * Behavior:
 * - Preserves the current document route when a translation exists in the target locale.
 * - Explicitly marks untranslated pages as unavailable (`aria-disabled="true"`) rather than
 *   silently displaying English content under a localized route.
 * - Full keyboard accessibility (Tab, ArrowDown/ArrowUp, Home/End, Enter/Space, Escape).
 */

export const DEFAULT_LOCALES = {
  en: {
    code: "en",
    name: "English",
    native_name: "English",
    html_lang: "en",
    prefix: "",
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
    name: "Polish",
    native_name: "Polski",
    html_lang: "pl",
    prefix: "/pl",
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
    name: "German",
    native_name: "Deutsch",
    html_lang: "de",
    prefix: "/de",
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
    name: "Spanish",
    native_name: "Español",
    html_lang: "es",
    prefix: "/es",
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
    name: "French",
    native_name: "Français",
    html_lang: "fr",
    prefix: "/fr",
    ui: {
      language_label: "Langue",
      switch_language: "Sélectionner la langue de la documentation",
      translation_unavailable: "Traduction indisponible pour cette page",
      go_to_locale_home: "Aller à l'accueil ({language})",
      current_language: "Langue actuelle",
    },
  },
};

export const DEFAULT_AVAILABLE_SLUGS = [
  "",
  "introduction",
  "architecture",
  "projects/linux",
  "notebooks/experiment",
];

/**
 * Parse a URL pathname into { baseUrl, locale, pageSlug }.
 */
export function parsePathnameRoute(pathname, localesMap = DEFAULT_LOCALES, explicitBaseUrl = "") {
  const cleanBase = (explicitBaseUrl || "").replace(/\/+$/, "");
  let rel = (pathname || "/").trim();
  if (cleanBase && rel.startsWith(cleanBase)) {
    rel = rel.slice(cleanBase.length) || "/";
  }
  rel = rel.replace(/\/index\.html$/i, "/").replace(/\.html$/i, "");
  if (!rel.startsWith("/")) rel = `/${rel}`;

  const nonDefaultLocales = Object.values(localesMap).filter(
    (loc) => loc.prefix && loc.prefix !== "/"
  );

  for (const loc of nonDefaultLocales) {
    const pfx = loc.prefix.replace(/\/+$/, "");
    if (rel === pfx || rel === `${pfx}/`) {
      return { baseUrl: cleanBase, locale: loc.code, pageSlug: "" };
    }
    if (rel.startsWith(`${pfx}/`)) {
      const slug = rel.slice(pfx.length + 1).replace(/^\/+|\/+$/g, "");
      return { baseUrl: cleanBase, locale: loc.code, pageSlug: slug };
    }
  }

  const defaultSlug = rel.replace(/^\/+|\/+$/g, "");
  return { baseUrl: cleanBase, locale: "en", pageSlug: defaultSlug === "readme" ? "" : defaultSlug };
}

/**
 * Build the target URL for a given locale and pageSlug.
 */
export function buildLocalizedRouteUrl(localeInfo, pageSlug, baseUrl = "", hash = "") {
  const cleanBase = (baseUrl || "").replace(/\/+$/, "");
  const cleanPrefix = (localeInfo?.prefix || "").replace(/\/+$/, "");
  const cleanSlug = (pageSlug || "").replace(/^\/+|\/+$/g, "");
  let path = cleanSlug
    ? `${cleanBase}${cleanPrefix}/${cleanSlug}`
    : `${cleanBase}${cleanPrefix}/`;
  if (!path.startsWith("/")) path = `/${path}`;
  return `${path}${hash || ""}`;
}

/**
 * Determine whether a translation is available for (localeCode, pageSlug).
 */
export function isTranslationAvailable(routeManifest, localeCode, pageSlug) {
  const normSlug = (pageSlug || "").replace(/^\/+|\/+$/g, "");
  if (routeManifest && routeManifest.locales && routeManifest.locales[localeCode]) {
    const locEntry = routeManifest.locales[localeCode];
    if (Array.isArray(locEntry.available_slugs)) {
      return locEntry.available_slugs.includes(normSlug);
    }
    if (locEntry.routes && typeof locEntry.routes === "object") {
      return Object.prototype.hasOwnProperty.call(locEntry.routes, normSlug);
    }
  }
  return DEFAULT_AVAILABLE_SLUGS.includes(normSlug);
}

const SWITCHER_STYLES = `
  .sc-lang-switcher {
    position: relative;
    display: inline-flex;
    flex-direction: column;
    align-items: flex-end;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    font-size: 0.8125rem;
    z-index: 1000;
  }

  .sc-lang-trigger {
    appearance: none;
    border: 1px solid #e4e4e7;
    background: #ffffff;
    color: #18181b;
    border-radius: 9999px;
    padding: 0.35rem 0.75rem;
    font-size: 0.8125rem;
    font-weight: 500;
    line-height: 1.25;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    transition: background-color 0.15s ease, border-color 0.15s ease;
    white-space: nowrap;
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
    top: calc(100% + 0.4rem);
    right: 0;
    min-width: 14rem;
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

  @supports (position-area: block-end span-inline-start) {
    .sc-lang-TriggerAnchored {
      position-try-fallbacks: flip-block, flip-inline, flip-block flip-inline;
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

  .sc-lang-option-main {
    display: flex;
    flex-direction: column;
    gap: 0.1rem;
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

  const routeManifest =
    options.routeManifest ||
    (typeof window !== "undefined" && window.__SC_ROUTE_MANIFEST__) ||
    null;

  const localesMap =
    (routeManifest && routeManifest.locales) ||
    options.locales ||
    DEFAULT_LOCALES;

  const explicitBaseUrl =
    options.baseUrl ??
    (typeof window !== "undefined" && typeof window.__SC_ROOT_BASE_URL__ === "string"
      ? window.__SC_ROOT_BASE_URL__
      : "");

  const pathname =
    options.pathname ||
    (typeof window !== "undefined" && window.location?.pathname) ||
    "/";

  const parsed = parsePathnameRoute(pathname, localesMap, explicitBaseUrl);

  const metaLocale =
    typeof document !== "undefined"
      ? document.querySelector('meta[name="sc-locale"]')?.getAttribute("content")
      : null;
  const metaSlug =
    typeof document !== "undefined"
      ? document.querySelector('meta[name="sc-page-slug"]')?.getAttribute("content")
      : null;

  const currentLocaleCode = (
    options.locale ||
    metaLocale ||
    parsed.locale ||
    "en"
  ).toLowerCase();
  const currentPageSlug =
    options.pageSlug !== undefined
      ? options.pageSlug
      : metaSlug !== null && metaSlug !== undefined
      ? metaSlug
      : parsed.pageSlug;

  const currentLocaleInfo = localesMap[currentLocaleCode] || DEFAULT_LOCALES.en;
  const ui = {
    ...DEFAULT_LOCALES.en.ui,
    ...(DEFAULT_LOCALES[currentLocaleCode]?.ui || {}),
    ...(currentLocaleInfo.ui || {}),
  };

  const styleEl = document.createElement("style");
  styleEl.textContent = SWITCHER_STYLES;

  const wrapper = document.createElement("div");
  wrapper.className = "sc-lang-switcher";
  wrapper.setAttribute("data-sc-locale", currentLocaleCode);
  wrapper.setAttribute("data-sc-page-slug", currentPageSlug);

  const panelId = `sc-lang-panel-${Math.random().toString(36).slice(2, 8)}`;

  const triggerBtn = document.createElement("button");
  triggerBtn.type = "button";
  triggerBtn.className = "sc-lang-trigger";
  triggerBtn.setAttribute("aria-expanded", "false");
  triggerBtn.setAttribute("aria-controls", panelId);
  triggerBtn.setAttribute("aria-label", `${ui.switch_language}: ${currentLocaleInfo.native_name}`);
  triggerBtn.innerHTML = `
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
      <circle cx="12" cy="12" r="10"></circle>
      <line x1="2" y1="12" x2="22" y2="12"></line>
      <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
    </svg>
    <span lang="${currentLocaleInfo.html_lang || currentLocaleCode}">${currentLocaleInfo.native_name}</span>
    <span class="sc-lang-code-badge" aria-hidden="true">${currentLocaleCode.toUpperCase()}</span>
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
      <polyline points="6 9 12 15 18 9"></polyline>
    </svg>
  `;

  const panel = document.createElement("div");
  panel.id = panelId;
  panel.className = "sc-lang-panel sc-lang-TriggerAnchored";
  panel.setAttribute("role", "group");
  panel.setAttribute("aria-label", ui.switch_language);
  panel.hidden = true;

  const noticeBox = document.createElement("div");
  noticeBox.className = "sc-lang-notice";
  noticeBox.setAttribute("role", "status");
  noticeBox.setAttribute("aria-live", "polite");
  noticeBox.hidden = true;

  const optionEls = [];

  for (const [code, locInfo] of Object.entries(localesMap)) {
    const available = isTranslationAvailable(routeManifest, code, currentPageSlug);
    const isCurrent = code === currentLocaleCode;
    const hash = (typeof window !== "undefined" && window.location?.hash) || "";
    const targetUrl = buildLocalizedRouteUrl(locInfo, currentPageSlug, parsed.baseUrl, hash);
    const homeUrl = buildLocalizedRouteUrl(locInfo, "", parsed.baseUrl, "");

    const item = document.createElement(available ? "a" : "button");
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

    const mainSpan = document.createElement("span");
    mainSpan.className = "sc-lang-option-main";

    const nativeSpan = document.createElement("span");
    nativeSpan.className = "sc-lang-option-native";
    nativeSpan.textContent = locInfo.native_name || code;

    const subSpan = document.createElement("span");
    subSpan.className = "sc-lang-option-sub";
    const locUi = {
      ...DEFAULT_LOCALES.en.ui,
      ...(DEFAULT_LOCALES[code]?.ui || {}),
      ...(locInfo.ui || {}),
    };
    subSpan.textContent = available
      ? `${locInfo.name || code}`
      : locUi.translation_unavailable || ui.translation_unavailable;

    mainSpan.append(nativeSpan, subSpan);

    const badge = document.createElement("span");
    badge.className = "sc-lang-code-badge";
    badge.setAttribute("aria-hidden", "true");
    badge.textContent = isCurrent ? `✓ ${code.toUpperCase()}` : code.toUpperCase();

    item.append(mainSpan, badge);

    item.addEventListener("click", (e) => {
      if (!available) {
        e.preventDefault();
        const unavailMsg = locUi.translation_unavailable || ui.translation_unavailable;
        const homeLabel = (locUi.go_to_locale_home || ui.go_to_locale_home).replace(
          "{language}",
          locInfo.native_name || code
        );
        noticeBox.innerHTML = "";
        const msgSpan = document.createElement("div");
        msgSpan.textContent = `${locInfo.native_name}: ${unavailMsg}.`;
        const homeLink = document.createElement("a");
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
      }
    });

    panel.appendChild(item);
    optionEls.push(item);
  }

  panel.appendChild(noticeBox);
  wrapper.append(triggerBtn, panel);
  hostEl.append(styleEl, wrapper);

  let isOpen = false;

  function setOpen(open) {
    isOpen = Boolean(open);
    panel.hidden = !isOpen;
    triggerBtn.setAttribute("aria-expanded", String(isOpen));
    if (!isOpen) {
      noticeBox.hidden = true;
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
      const activeIdx = optionEls.indexOf(document.activeElement);
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

  document.addEventListener("pointerdown", onDocumentPointerDown);

  return () => {
    document.removeEventListener("pointerdown", onDocumentPointerDown);
    wrapper.remove();
    styleEl.remove();
  };
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

// Auto-mount on static documentation pages when [data-sc-lang-switcher] is present
if (typeof document !== "undefined") {
  const autoMount = () => {
    const targets = document.querySelectorAll("[data-sc-lang-switcher]");
    for (const target of targets) {
      if (!target.getAttribute("data-sc-mounted")) {
        target.setAttribute("data-sc-mounted", "true");
        mountLanguageSwitcher(target);
      }
    }
  };
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", autoMount);
  } else {
    autoMount();
  }
}

export default { render, mountLanguageSwitcher, parsePathnameRoute, buildLocalizedRouteUrl, isTranslationAvailable };
