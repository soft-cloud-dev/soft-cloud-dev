/**
 * SoftCloud Documentation Hub — Interactive AI Audio Narration Player
 *
 * Compatible with MyST `{anywidget}` (ESM default export `{ render({ model, el }) }`).
 * Operates exclusively against build-time static assets (`manifest.json`, `transcript.json`,
 * and content-addressed `.mp3` chunks) without runtime API calls or credentials.
 */

const SPEEDS = [0.75, 1.0, 1.25, 1.5, 1.75, 2.0];

export const PLAYER_STRINGS = {
  en: {
    voice_overview: "Voice overview",
    audio_narration: "Audio Narration",
    loading_narration: "Loading narration...",
    listen: "Listen",
    collapse: "Collapse",
    section_of: "SECTION {current} OF {total}",
    section_fallback: "Section {current}",
    previous_section: "Previous section",
    next_section: "Next section",
    play: "Play",
    pause: "Pause",
    playback_rate: "Playback rate",
    scrubber_label: "Audio playback scrubber",
    topics_unit: "topics",
    min_unit: "min",
    sec_unit: "sec",
    narration_unavailable: "Narration assets unavailable",
    playback_failed: "Playback failed",
  },
  pl: {
    voice_overview: "Przegląd głosowy",
    audio_narration: "Narracja audio",
    loading_narration: "Ładowanie narracji...",
    listen: "Słuchaj",
    collapse: "Zwiń",
    section_of: "SEKCJA {current} Z {total}",
    section_fallback: "Sekcja {current}",
    previous_section: "Poprzednia sekcja",
    next_section: "Następna sekcja",
    play: "Odtwórz",
    pause: "Wstrzymaj",
    playback_rate: "Szybkość odtwarzania",
    scrubber_label: "Suwak postępu odtwarzania audio",
    topics_unit: "tematy",
    min_unit: "min",
    sec_unit: "sek",
    narration_unavailable: "Zasoby narracji są niedostępne",
    playback_failed: "Błąd odtwarzania",
  },
  de: {
    voice_overview: "Sprachübersicht",
    audio_narration: "Audio-Narration",
    loading_narration: "Narration wird geladen...",
    listen: "Anhören",
    collapse: "Einklappen",
    section_of: "ABSCHNITT {current} VON {total}",
    section_fallback: "Abschnitt {current}",
    previous_section: "Vorheriger Abschnitt",
    next_section: "Nächster Abschnitt",
    play: "Abspielen",
    pause: "Pause",
    playback_rate: "Wiedergabegeschwindigkeit",
    scrubber_label: "Audio-Wiedergaberegler",
    topics_unit: "Themen",
    min_unit: "Min",
    sec_unit: "Sek",
    narration_unavailable: "Narrations-Assets nicht verfügbar",
    playback_failed: "Wiedergabe fehlgeschlagen",
  },
  es: {
    voice_overview: "Resumen de voz",
    audio_narration: "Narración de audio",
    loading_narration: "Cargando narración...",
    listen: "Escuchar",
    collapse: "Contraer",
    section_of: "SECCIÓN {current} DE {total}",
    section_fallback: "Sección {current}",
    previous_section: "Sección anterior",
    next_section: "Siguiente sección",
    play: "Reproducir",
    pause: "Pausar",
    playback_rate: "Velocidad de reproducción",
    scrubber_label: "Control deslizante de reproducción de audio",
    topics_unit: "temas",
    min_unit: "min",
    sec_unit: "s",
    narration_unavailable: "Recursos de narración no disponibles",
    playback_failed: "Error de reproducción",
  },
  fr: {
    voice_overview: "Aperçu vocal",
    audio_narration: "Narration audio",
    loading_narration: "Chargement de la narration...",
    listen: "Écouter",
    collapse: "Réduire",
    section_of: "SECTION {current} SUR {total}",
    section_fallback: "Section {current}",
    previous_section: "Section précédente",
    next_section: "Section suivante",
    play: "Lire",
    pause: "Pause",
    playback_rate: "Vitesse de lecture",
    scrubber_label: "Curseur de progression audio",
    topics_unit: "sujets",
    min_unit: "min",
    sec_unit: "s",
    narration_unavailable: "Ressources de narration indisponibles",
    playback_failed: "Échec de la lecture",
  },
};

export function detectDocumentLocale(explicitLocale) {
  if (explicitLocale && typeof explicitLocale === "string" && explicitLocale.trim()) {
    return explicitLocale.trim().toLowerCase().split("-")[0];
  }
  if (typeof document !== "undefined") {
    const metaLocale = document.querySelector('meta[name="sc-locale"]')?.getAttribute("content");
    if (metaLocale && metaLocale.trim()) {
      return metaLocale.trim().toLowerCase().split("-")[0];
    }
  }
  if (typeof window !== "undefined" && window.location?.pathname) {
    const match = window.location.pathname.match(/^\/(?:[^/]+\/)?(pl|de|es|fr)(?:\/|$)/i);
    if (match) {
      return match[1].toLowerCase();
    }
  }
  if (typeof document !== "undefined" && document.documentElement?.lang) {
    const htmlLang = document.documentElement.lang.trim().toLowerCase().split("-")[0];
    if (htmlLang && PLAYER_STRINGS[htmlLang]) {
      return htmlLang;
    }
  }
  return "en";
}

export function isDarkModeActive(doc = typeof document !== "undefined" ? document : null, el = null) {
  if (!doc) return false;
  const docEl = doc.documentElement;
  const body = doc.body;

  // 1. Explicit dark class or data attributes on root / body
  if (
    docEl?.classList?.contains("dark") ||
    body?.classList?.contains("dark") ||
    docEl?.getAttribute?.("data-theme") === "dark" ||
    docEl?.getAttribute?.("data-mode") === "dark" ||
    body?.getAttribute?.("data-theme") === "dark" ||
    body?.getAttribute?.("data-mode") === "dark"
  ) {
    return true;
  }

  // 2. Explicit light class or data attributes on root / body
  if (
    docEl?.classList?.contains("light") ||
    body?.classList?.contains("light") ||
    docEl?.getAttribute?.("data-theme") === "light" ||
    docEl?.getAttribute?.("data-mode") === "light" ||
    body?.getAttribute?.("data-theme") === "light" ||
    body?.getAttribute?.("data-mode") === "light"
  ) {
    return false;
  }

  // 3. Enclosing ancestor outside the widget host (e.g. section container, #root, .book-theme)
  const host = el?.host || (typeof el?.getRootNode === "function" && el.getRootNode()?.host);
  const contextNode = host || el;
  const ancestor = contextNode?.parentElement?.closest?.(
    ".dark, .light, [data-theme], [data-mode], [data-theme-mode]"
  );
  if (ancestor) {
    if (
      ancestor.classList.contains("dark") ||
      ancestor.getAttribute("data-theme") === "dark" ||
      ancestor.getAttribute("data-mode") === "dark" ||
      ancestor.getAttribute("data-theme-mode") === "dark"
    ) {
      return true;
    }
    if (
      ancestor.classList.contains("light") ||
      ancestor.getAttribute("data-theme") === "light" ||
      ancestor.getAttribute("data-mode") === "light" ||
      ancestor.getAttribute("data-theme-mode") === "light"
    ) {
      return false;
    }
  }

  // 4. Check for any top-level app wrapper with dark class in the document
  if (
    doc.querySelector?.(
      "html.dark, body.dark, #root.dark, #__next.dark, .myst-app.dark"
    )
  ) {
    return true;
  }

  // 5. Check <meta name="color-scheme">
  const metaScheme = doc.querySelector?.('meta[name="color-scheme"]')?.getAttribute("content");
  if (metaScheme === "dark") return true;
  if (metaScheme === "light") return false;

  // 6. Stored preference
  try {
    if (typeof window !== "undefined" && window.localStorage) {
      const stored =
        window.localStorage.getItem("theme") ||
        window.localStorage.getItem("myst-theme") ||
        window.localStorage.getItem("color-theme") ||
        window.localStorage.getItem("color-scheme") ||
        window.localStorage.getItem("theme-mode");
      if (stored === "dark") return true;
      if (stored === "light") return false;
    }
  } catch (_e) {}

  // 7. Computed style color-scheme or background brightness on body/root
  try {
    if (typeof window !== "undefined" && window.getComputedStyle) {
      const targetElement = body || docEl;
      if (targetElement) {
        const cs = window.getComputedStyle(targetElement);
        if (cs.colorScheme === "dark") return true;
        if (cs.colorScheme === "light") return false;
        const bg = cs.backgroundColor;
        if (bg && bg !== "transparent" && bg !== "rgba(0, 0, 0, 0)") {
          const m = bg.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
          if (m) {
            const r = Number(m[1]), g = Number(m[2]), b = Number(m[3]);
            const brightness = (r * 299 + g * 587 + b * 114) / 1000;
            if (brightness < 90) return true;
            if (brightness > 180) return false;
          }
        }
      }
    }
  } catch (_e) {}

  // 8. System color scheme
  if (typeof window !== "undefined" && window.matchMedia) {
    if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
      return true;
    }
  }

  return false;
}

function formatDurationSeconds(seconds, ui = PLAYER_STRINGS.en) {
  const minUnit = ui.min_unit || "min";
  const secUnit = ui.sec_unit || "sec";
  if (!Number.isFinite(seconds) || seconds <= 0) return `0 ${minUnit} 0 ${secUnit}`;
  const total = Math.round(seconds);
  const mins = Math.floor(total / 60);
  const secs = total % 60;
  if (mins === 0) return `${secs} ${secUnit}`;
  return `${mins} ${minUnit} ${secs} ${secUnit}`;
}

export function resolveAudioDirUrls(pageId, locale = "en", explicitBaseUrl = "") {
  const normLocale = (locale || "en").toLowerCase();
  const encodedPage = encodeURIComponent(pageId);

  if (explicitBaseUrl) {
    const clean = explicitBaseUrl.replace(/\/+$/, "");
    if (normLocale === "en" || clean.endsWith(`/${normLocale}`)) {
      return [`${clean}/audio/${encodedPage}`];
    }
    return [
      `${clean}/${normLocale}/audio/${encodedPage}`,
      `${clean}/audio/${normLocale}/${encodedPage}`,
    ];
  }

  if (typeof window !== "undefined" && typeof window.BASE_URL === "string" && window.BASE_URL) {
    const clean = window.BASE_URL.replace(/\/+$/, "");
    if (normLocale === "en" || clean.endsWith(`/${normLocale}`)) {
      return [`${clean}/audio/${encodedPage}`];
    }
    return [
      `${clean}/${normLocale}/audio/${encodedPage}`,
      `${clean}/audio/${normLocale}/${encodedPage}`,
    ];
  }

  const pathname = (typeof window !== "undefined" && window.location?.pathname) || "/";
  let siteBase = pathname.replace(/\/index\.html$/, "");
  const knownSuffixes = [
    `/notebooks/${pageId.replace(/^notebooks-/, "")}`,
    "/notebooks/experiment",
    "/projects/linux",
    `/${pageId}`,
    "/introduction",
    "/architecture",
    "/readme",
  ];
  for (const suffix of knownSuffixes) {
    if (siteBase.endsWith(suffix) || siteBase.endsWith(`${suffix}/`)) {
      siteBase = siteBase.slice(0, siteBase.lastIndexOf(suffix));
      break;
    }
  }
  siteBase = siteBase.replace(/\/+$/, "");

  if (normLocale === "en") {
    return [`${siteBase}/audio/${encodedPage}`];
  }
  if (siteBase.endsWith(`/${normLocale}`)) {
    const rootBase = siteBase.slice(0, siteBase.length - (`/${normLocale}`).length);
    return [
      `${siteBase}/audio/${encodedPage}`,
      `${rootBase}/audio/${normLocale}/${encodedPage}`,
    ];
  }
  return [
    `${siteBase}/${normLocale}/audio/${encodedPage}`,
    `${siteBase}/audio/${normLocale}/${encodedPage}`,
  ];
}

export function validateNarrationManifest(manifestData, expectedPageId, expectedLocale) {
  if (!manifestData || typeof manifestData !== "object") {
    throw new Error("Invalid manifest JSON");
  }
  if (manifestData.status !== "complete") {
    throw new Error(`Incomplete manifest status: ${manifestData.status}`);
  }
  if (manifestData.page_id !== expectedPageId) {
    throw new Error(`Page ID mismatch: expected '${expectedPageId}', got '${manifestData.page_id}'`);
  }
  const manifestLocale = (manifestData.locale || "").toLowerCase();
  if (!manifestLocale || manifestLocale !== expectedLocale.toLowerCase()) {
    throw new Error(`Locale mismatch: expected '${expectedLocale}', got '${manifestData.locale || "missing"}'`);
  }
  if (!manifestData.manifest_sha256 || typeof manifestData.manifest_sha256 !== "string") {
    throw new Error("Missing manifest_sha256 integrity digest");
  }
  if (!Array.isArray(manifestData.chunks) || manifestData.chunks.length === 0) {
    throw new Error("Manifest contains zero narration chunks");
  }
  for (const ch of manifestData.chunks) {
    if (!ch.audio_file || !ch.audio_sha256 || (ch.locale && ch.locale !== expectedLocale)) {
      throw new Error(`Invalid chunk entry in manifest: ${ch?.chunk_id || "unknown"}`);
    }
  }
  return true;
}

function findHeadingElement(anchor) {
  if (typeof document === "undefined" || !anchor) return null;
  const direct = document.getElementById(anchor);
  if (direct) return direct;
  const bySelector = document.querySelector(
    `[id="${CSS.escape(anchor)}"], a[href="#${CSS.escape(anchor)}"]`
  );
  return bySelector || null;
}

const PLAYER_STYLES = `
  :host {
    display: block;
    margin: 1rem 0 1.5rem 0;
    font-family: inherit;
    color: inherit;
  }

  /* Default container: Pure White (#ffffff) on light theme */
  .sc-player {
    border: 1px solid #e4e4e7;
    border-radius: 12px;
    background: #ffffff !important;
    color: #18181b !important;
    box-shadow: none;
    padding: 1rem 1.25rem;
    box-sizing: border-box;
    transition: background-color 0.15s ease, border-color 0.15s ease, color 0.15s ease;
  }

  /* Dark mode */
  .sc-player.dark,
  .sc-player[data-theme="dark"],
  :host(.dark) .sc-player,
  :host([data-theme="dark"]) .sc-player,
  :host([data-mode="dark"]) .sc-player,
  :host-context(html.dark) .sc-player,
  :host-context(body.dark) .sc-player,
  :host-context(:root.dark) .sc-player,
  :host-context(.dark) .sc-player,
  :host-context([data-theme="dark"]) .sc-player,
  :host-context([data-mode="dark"]) .sc-player,
  html.dark .sc-player,
  body.dark .sc-player,
  :root.dark .sc-player,
  .dark .sc-player,
  [data-theme="dark"] .sc-player,
  [data-mode="dark"] .sc-player {
    border-color: #27272a !important;
    background: #121214 !important;
    color: #fafafa !important;
  }

  /* Header / Overview Row */
  .sc-header-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
  }

  .sc-overview-left {
    display: flex;
    align-items: center;
    gap: 0.85rem;
    min-width: 0;
  }

  .sc-headphones-icon {
    width: 22px;
    height: 22px;
    color: #71717a !important;
    flex-shrink: 0;
  }

  .sc-player.dark .sc-headphones-icon,
  .sc-player[data-theme="dark"] .sc-headphones-icon,
  :host(.dark) .sc-headphones-icon,
  :host([data-theme="dark"]) .sc-headphones-icon,
  :host([data-mode="dark"]) .sc-headphones-icon,
  :host-context(html.dark) .sc-headphones-icon,
  :host-context(body.dark) .sc-headphones-icon,
  :host-context(:root.dark) .sc-headphones-icon,
  :host-context(.dark) .sc-headphones-icon,
  :host-context([data-theme="dark"]) .sc-headphones-icon,
  :host-context([data-mode="dark"]) .sc-headphones-icon,
  html.dark .sc-headphones-icon,
  body.dark .sc-headphones-icon,
  :root.dark .sc-headphones-icon,
  .dark .sc-headphones-icon,
  [data-theme="dark"] .sc-headphones-icon,
  [data-mode="dark"] .sc-headphones-icon {
    color: #a1a1aa !important;
  }

  .sc-overview-text {
    display: flex;
    flex-direction: column;
    gap: 0.15rem;
    min-width: 0;
  }

  .sc-overview-title {
    font-size: 0.9375rem;
    font-weight: 600;
    color: inherit;
    line-height: 1.25;
  }

  .sc-player.dark .sc-overview-title,
  .sc-player[data-theme="dark"] .sc-overview-title,
  :host(.dark) .sc-overview-title,
  :host([data-theme="dark"]) .sc-overview-title,
  :host-context(.dark) .sc-overview-title,
  html.dark .sc-overview-title,
  .dark .sc-overview-title {
    color: #fafafa !important;
  }

  .sc-overview-subtitle {
    font-size: 0.75rem;
    color: #71717a !important;
    line-height: 1.2;
  }

  .sc-player.dark .sc-overview-subtitle,
  .sc-player[data-theme="dark"] .sc-overview-subtitle,
  :host(.dark) .sc-overview-subtitle,
  :host([data-theme="dark"]) .sc-overview-subtitle,
  :host([data-mode="dark"]) .sc-overview-subtitle,
  :host-context(html.dark) .sc-overview-subtitle,
  :host-context(body.dark) .sc-overview-subtitle,
  :host-context(:root.dark) .sc-overview-subtitle,
  :host-context(.dark) .sc-overview-subtitle,
  :host-context([data-theme="dark"]) .sc-overview-subtitle,
  :host-context([data-mode="dark"]) .sc-overview-subtitle,
  html.dark .sc-overview-subtitle,
  body.dark .sc-overview-subtitle,
  :root.dark .sc-overview-subtitle,
  .dark .sc-overview-subtitle,
  [data-theme="dark"] .sc-overview-subtitle,
  [data-mode="dark"] .sc-overview-subtitle {
    color: #a1a1aa !important;
  }

  /* Listen Pill Button (High Contrast Flat) */
  .sc-btn-listen {
    appearance: none;
    border: none;
    background: #18181b !important;
    color: #ffffff !important;
    border-radius: 9999px;
    padding: 0.45rem 1.15rem;
    font-size: 0.8125rem;
    font-weight: 600;
    line-height: 1.2;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    box-shadow: none;
    transition: opacity 0.15s ease;
    white-space: nowrap;
  }

  .sc-player.dark .sc-btn-listen,
  .sc-player[data-theme="dark"] .sc-btn-listen,
  :host(.dark) .sc-btn-listen,
  :host([data-theme="dark"]) .sc-btn-listen,
  :host([data-mode="dark"]) .sc-btn-listen,
  :host-context(html.dark) .sc-btn-listen,
  :host-context(body.dark) .sc-btn-listen,
  :host-context(:root.dark) .sc-btn-listen,
  :host-context(.dark) .sc-btn-listen,
  :host-context([data-theme="dark"]) .sc-btn-listen,
  :host-context([data-mode="dark"]) .sc-btn-listen,
  html.dark .sc-btn-listen,
  body.dark .sc-btn-listen,
  :root.dark .sc-btn-listen,
  .dark .sc-btn-listen,
  [data-theme="dark"] .sc-btn-listen,
  [data-mode="dark"] .sc-btn-listen {
    background: #fafafa !important;
    color: #18181b !important;
  }

  .sc-btn-listen:hover:not(:disabled) {
    opacity: 0.88;
  }

  .sc-btn-listen:active:not(:disabled) {
    opacity: 0.78;
  }

  .sc-btn-listen:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }

  /* Collapse Pill Button (Flat Outline) */
  .sc-btn-collapse {
    appearance: none;
    border: 1px solid #e4e4e7 !important;
    background: transparent !important;
    color: #18181b !important;
    border-radius: 9999px;
    padding: 0.38rem 0.95rem;
    font-size: 0.78125rem;
    font-weight: 500;
    line-height: 1.2;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    box-shadow: none;
    transition: background-color 0.15s ease, border-color 0.15s ease;
    white-space: nowrap;
  }

  .sc-player.dark .sc-btn-collapse,
  .sc-player[data-theme="dark"] .sc-btn-collapse,
  :host(.dark) .sc-btn-collapse,
  :host([data-theme="dark"]) .sc-btn-collapse,
  :host([data-mode="dark"]) .sc-btn-collapse,
  :host-context(html.dark) .sc-btn-collapse,
  :host-context(body.dark) .sc-btn-collapse,
  :host-context(:root.dark) .sc-btn-collapse,
  :host-context(.dark) .sc-btn-collapse,
  :host-context([data-theme="dark"]) .sc-btn-collapse,
  :host-context([data-mode="dark"]) .sc-btn-collapse,
  html.dark .sc-btn-collapse,
  body.dark .sc-btn-collapse,
  :root.dark .sc-btn-collapse,
  .dark .sc-btn-collapse,
  [data-theme="dark"] .sc-btn-collapse,
  [data-mode="dark"] .sc-btn-collapse {
    border-color: #27272a !important;
    color: #fafafa !important;
  }

  .sc-btn-collapse:hover {
    background: rgba(0, 0, 0, 0.04) !important;
  }

  .sc-player.dark .sc-btn-collapse:hover,
  .sc-player[data-theme="dark"] .sc-btn-collapse:hover,
  :host(.dark) .sc-btn-collapse:hover,
  :host([data-theme="dark"]) .sc-btn-collapse:hover,
  :host-context(html.dark) .sc-btn-collapse:hover,
  :host-context(body.dark) .sc-btn-collapse:hover,
  :host-context(:root.dark) .sc-btn-collapse:hover,
  :host-context(.dark) .sc-btn-collapse:hover,
  :host-context([data-theme="dark"]) .sc-btn-collapse:hover,
  html.dark .sc-btn-collapse:hover,
  body.dark .sc-btn-collapse:hover,
  .dark .sc-btn-collapse:hover,
  [data-theme="dark"] .sc-btn-collapse:hover {
    background: rgba(255, 255, 255, 0.08) !important;
  }

  /* Expanded Section Body — Crucial: display: none when hidden */
  .sc-expanded-body {
    margin-top: 1rem;
    padding-top: 0.85rem;
    border-top: 1px solid #e4e4e7 !important;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .sc-expanded-body[hidden],
  .sc-expanded-body.is-hidden {
    display: none !important;
  }

  .sc-player.dark .sc-expanded-body,
  .sc-player[data-theme="dark"] .sc-expanded-body,
  :host(.dark) .sc-expanded-body,
  :host([data-theme="dark"]) .sc-expanded-body,
  :host([data-mode="dark"]) .sc-expanded-body,
  :host-context(html.dark) .sc-expanded-body,
  :host-context(body.dark) .sc-expanded-body,
  :host-context(:root.dark) .sc-expanded-body,
  :host-context(.dark) .sc-expanded-body,
  :host-context([data-theme="dark"]) .sc-expanded-body,
  :host-context([data-mode="dark"]) .sc-expanded-body,
  html.dark .sc-expanded-body,
  body.dark .sc-expanded-body,
  :root.dark .sc-expanded-body,
  .dark .sc-expanded-body,
  [data-theme="dark"] .sc-expanded-body,
  [data-mode="dark"] .sc-expanded-body {
    border-top-color: #27272a !important;
  }

  .sc-meta-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 0.75rem;
    color: #71717a !important;
  }

  .sc-player.dark .sc-meta-row,
  .sc-player[data-theme="dark"] .sc-meta-row,
  :host(.dark) .sc-meta-row,
  :host([data-theme="dark"]) .sc-meta-row,
  :host([data-mode="dark"]) .sc-meta-row,
  :host-context(html.dark) .sc-meta-row,
  :host-context(body.dark) .sc-meta-row,
  :host-context(:root.dark) .sc-meta-row,
  :host-context(.dark) .sc-meta-row,
  :host-context([data-theme="dark"]) .sc-meta-row,
  :host-context([data-mode="dark"]) .sc-meta-row,
  html.dark .sc-meta-row,
  body.dark .sc-meta-row,
  :root.dark .sc-meta-row,
  .dark .sc-meta-row,
  [data-theme="dark"] .sc-meta-row,
  [data-mode="dark"] .sc-meta-row {
    color: #a1a1aa !important;
  }

  .sc-section-indicator {
    font-size: 0.6875rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    color: inherit;
  }

  .sc-time-display {
    font-size: 0.75rem;
    font-variant-numeric: tabular-nums;
    color: inherit;
  }

  .sc-section-heading {
    font-size: 0.9375rem;
    font-weight: 600;
    color: inherit;
    line-height: 1.35;
    margin: 0;
  }

  .sc-player.dark .sc-section-heading,
  .sc-player[data-theme="dark"] .sc-section-heading,
  :host(.dark) .sc-section-heading,
  :host([data-theme="dark"]) .sc-section-heading,
  :host-context(.dark) .sc-section-heading,
  html.dark .sc-section-heading,
  .dark .sc-section-heading {
    color: #fafafa !important;
  }

  /* Flat Scrubber Bar */
  .sc-scrubber-container {
    position: relative;
    width: 100%;
    height: 8px;
    background: #f4f4f5 !important;
    border-radius: 9999px;
    cursor: pointer;
    margin: 0.35rem 0 0.5rem 0;
    display: flex;
    align-items: center;
  }

  .sc-player.dark .sc-scrubber-container,
  .sc-player[data-theme="dark"] .sc-scrubber-container,
  :host(.dark) .sc-scrubber-container,
  :host([data-theme="dark"]) .sc-scrubber-container,
  :host([data-mode="dark"]) .sc-scrubber-container,
  :host-context(html.dark) .sc-scrubber-container,
  :host-context(body.dark) .sc-scrubber-container,
  :host-context(:root.dark) .sc-scrubber-container,
  :host-context(.dark) .sc-scrubber-container,
  :host-context([data-theme="dark"]) .sc-scrubber-container,
  :host-context([data-mode="dark"]) .sc-scrubber-container,
  html.dark .sc-scrubber-container,
  body.dark .sc-scrubber-container,
  :root.dark .sc-scrubber-container,
  .dark .sc-scrubber-container,
  [data-theme="dark"] .sc-scrubber-container,
  [data-mode="dark"] .sc-scrubber-container {
    background: #27272a !important;
  }

  .sc-scrubber-fill {
    height: 100%;
    background: #18181b !important;
    border-radius: 9999px;
    width: 0%;
    pointer-events: none;
    transition: width 0.05s linear;
  }

  .sc-player.dark .sc-scrubber-fill,
  .sc-player[data-theme="dark"] .sc-scrubber-fill,
  :host(.dark) .sc-scrubber-fill,
  :host([data-theme="dark"]) .sc-scrubber-fill,
  :host([data-mode="dark"]) .sc-scrubber-fill,
  :host-context(html.dark) .sc-scrubber-fill,
  :host-context(body.dark) .sc-scrubber-fill,
  :host-context(:root.dark) .sc-scrubber-fill,
  :host-context(.dark) .sc-scrubber-fill,
  :host-context([data-theme="dark"]) .sc-scrubber-fill,
  :host-context([data-mode="dark"]) .sc-scrubber-fill,
  html.dark .sc-scrubber-fill,
  body.dark .sc-scrubber-fill,
  :root.dark .sc-scrubber-fill,
  .dark .sc-scrubber-fill,
  [data-theme="dark"] .sc-scrubber-fill,
  [data-mode="dark"] .sc-scrubber-fill {
    background: #fafafa !important;
  }

  .sc-scrubber-knob {
    position: absolute;
    top: 50%;
    left: 0%;
    margin-top: -8px;
    margin-left: -8px;
    width: 16px;
    height: 16px;
    background: #18181b !important;
    border-radius: 9999px;
    box-shadow: none;
    cursor: grab;
    pointer-events: none;
    transform: scale(1);
    transform-origin: center center;
    transition: transform 0.15s ease;
  }

  .sc-player.dark .sc-scrubber-knob,
  .sc-player[data-theme="dark"] .sc-scrubber-knob,
  :host(.dark) .sc-scrubber-knob,
  :host([data-theme="dark"]) .sc-scrubber-knob,
  :host([data-mode="dark"]) .sc-scrubber-knob,
  :host-context(html.dark) .sc-scrubber-knob,
  :host-context(body.dark) .sc-scrubber-knob,
  :host-context(:root.dark) .sc-scrubber-knob,
  :host-context(.dark) .sc-scrubber-knob,
  :host-context([data-theme="dark"]) .sc-scrubber-knob,
  :host-context([data-mode="dark"]) .sc-scrubber-knob,
  html.dark .sc-scrubber-knob,
  body.dark .sc-scrubber-knob,
  :root.dark .sc-scrubber-knob,
  .dark .sc-scrubber-knob,
  [data-theme="dark"] .sc-scrubber-knob,
  [data-mode="dark"] .sc-scrubber-knob {
    background: #fafafa !important;
    box-shadow: none;
  }

  .sc-scrubber-container:hover .sc-scrubber-knob {
    transform: scale(1.15);
  }

  .sc-scrubber-container:focus-visible {
    outline: 2px solid #18181b;
    outline-offset: 2px;
  }
  .sc-player.dark .sc-scrubber-container:focus-visible,
  .sc-player[data-theme="dark"] .sc-scrubber-container:focus-visible,
  :host(.dark) .sc-scrubber-container:focus-visible,
  :host-context(.dark) .sc-scrubber-container:focus-visible,
  html.dark .sc-scrubber-container:focus-visible,
  .dark .sc-scrubber-container:focus-visible {
    outline-color: #fafafa;
  }

  /* Controls Row */
  .sc-controls-row {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    flex-wrap: wrap;
    margin-top: 0.25rem;
  }

  .sc-icon-btn {
    appearance: none;
    background: transparent !important;
    border: none !important;
    color: #71717a !important;
    cursor: pointer;
    padding: 0.4rem;
    border-radius: 6px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    transition: color 0.15s ease;
  }

  .sc-player.dark .sc-icon-btn,
  .sc-player[data-theme="dark"] .sc-icon-btn,
  :host(.dark) .sc-icon-btn,
  :host([data-theme="dark"]) .sc-icon-btn,
  :host([data-mode="dark"]) .sc-icon-btn,
  :host-context(html.dark) .sc-icon-btn,
  :host-context(body.dark) .sc-icon-btn,
  :host-context(:root.dark) .sc-icon-btn,
  :host-context(.dark) .sc-icon-btn,
  :host-context([data-theme="dark"]) .sc-icon-btn,
  :host-context([data-mode="dark"]) .sc-icon-btn,
  html.dark .sc-icon-btn,
  body.dark .sc-icon-btn,
  :root.dark .sc-icon-btn,
  .dark .sc-icon-btn,
  [data-theme="dark"] .sc-icon-btn,
  [data-mode="dark"] .sc-icon-btn {
    color: #a1a1aa !important;
  }

  .sc-icon-btn:hover:not(:disabled) {
    color: #18181b !important;
  }

  .sc-player.dark .sc-icon-btn:hover:not(:disabled),
  .sc-player[data-theme="dark"] .sc-icon-btn:hover:not(:disabled),
  :host(.dark) .sc-icon-btn:hover:not(:disabled),
  :host([data-theme="dark"]) .sc-icon-btn:hover:not(:disabled),
  :host([data-mode="dark"]) .sc-icon-btn:hover:not(:disabled),
  :host-context(html.dark) .sc-icon-btn:hover:not(:disabled),
  :host-context(body.dark) .sc-icon-btn:hover:not(:disabled),
  :host-context(:root.dark) .sc-icon-btn:hover:not(:disabled),
  :host-context(.dark) .sc-icon-btn:hover:not(:disabled),
  :host-context([data-theme="dark"]) .sc-icon-btn:hover:not(:disabled),
  :host-context([data-mode="dark"]) .sc-icon-btn:hover:not(:disabled),
  html.dark .sc-icon-btn:hover:not(:disabled),
  body.dark .sc-icon-btn:hover:not(:disabled),
  :root.dark .sc-icon-btn:hover:not(:disabled),
  .dark .sc-icon-btn:hover:not(:disabled),
  [data-theme="dark"] .sc-icon-btn:hover:not(:disabled),
  [data-mode="dark"] .sc-icon-btn:hover:not(:disabled) {
    color: #fafafa !important;
  }

  .sc-icon-btn:disabled {
    opacity: 0.3;
    cursor: not-allowed;
  }

  /* Play Pill Button (Flat High Contrast) */
  .sc-play-pill {
    appearance: none;
    background: #18181b !important;
    color: #ffffff !important;
    border: none;
    border-radius: 9999px;
    padding: 0.45rem 1.15rem;
    font-size: 0.8125rem;
    font-weight: 600;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 0.4rem;
    box-shadow: none;
    transition: opacity 0.15s ease;
    min-width: 4.5rem;
  }

  .sc-player.dark .sc-play-pill,
  .sc-player[data-theme="dark"] .sc-play-pill,
  :host(.dark) .sc-play-pill,
  :host([data-theme="dark"]) .sc-play-pill,
  :host([data-mode="dark"]) .sc-play-pill,
  :host-context(html.dark) .sc-play-pill,
  :host-context(body.dark) .sc-play-pill,
  :host-context(:root.dark) .sc-play-pill,
  :host-context(.dark) .sc-play-pill,
  :host-context([data-theme="dark"]) .sc-play-pill,
  :host-context([data-mode="dark"]) .sc-play-pill,
  html.dark .sc-play-pill,
  body.dark .sc-play-pill,
  :root.dark .sc-play-pill,
  .dark .sc-play-pill,
  [data-theme="dark"] .sc-play-pill,
  [data-mode="dark"] .sc-play-pill {
    background: #fafafa !important;
    color: #18181b !important;
  }

  .sc-play-pill:hover:not(:disabled) {
    opacity: 0.88;
  }

  /* Speed Dropdown (Flat Select) */
  .sc-speed-dropdown {
    appearance: none;
    background-color: #ffffff !important;
    border: 1px solid #e4e4e7 !important;
    color: #18181b !important;
    border-radius: 9999px;
    padding: 0.4rem 1.8rem 0.4rem 0.85rem;
    font-size: 0.78125rem;
    font-weight: 500;
    cursor: pointer;
    box-shadow: none;
    position: relative;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%2371717a' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: right 0.65rem center;
    background-size: 10px;
  }

  .sc-player.dark .sc-speed-dropdown,
  .sc-player[data-theme="dark"] .sc-speed-dropdown,
  :host(.dark) .sc-speed-dropdown,
  :host([data-theme="dark"]) .sc-speed-dropdown,
  :host([data-mode="dark"]) .sc-speed-dropdown,
  :host-context(html.dark) .sc-speed-dropdown,
  :host-context(body.dark) .sc-speed-dropdown,
  :host-context(:root.dark) .sc-speed-dropdown,
  :host-context(.dark) .sc-speed-dropdown,
  :host-context([data-theme="dark"]) .sc-speed-dropdown,
  :host-context([data-mode="dark"]) .sc-speed-dropdown,
  html.dark .sc-speed-dropdown,
  body.dark .sc-speed-dropdown,
  :root.dark .sc-speed-dropdown,
  .dark .sc-speed-dropdown,
  [data-theme="dark"] .sc-speed-dropdown,
  [data-mode="dark"] .sc-speed-dropdown {
    background-color: #18181b !important;
    border-color: #27272a !important;
    color: #fafafa !important;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23a1a1aa' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E") !important;
  }

  .sc-speed-dropdown:focus-visible {
    outline: 2px solid #18181b;
  }
  .sc-player.dark .sc-speed-dropdown:focus-visible,
  .sc-player[data-theme="dark"] .sc-speed-dropdown:focus-visible,
  :host(.dark) .sc-speed-dropdown:focus-visible,
  :host([data-theme="dark"]) .sc-speed-dropdown:focus-visible,
  :host-context(html.dark) .sc-speed-dropdown:focus-visible,
  :host-context(body.dark) .sc-speed-dropdown:focus-visible,
  :host-context(:root.dark) .sc-speed-dropdown:focus-visible,
  :host-context(.dark) .sc-speed-dropdown:focus-visible,
  :host-context([data-theme="dark"]) .sc-speed-dropdown:focus-visible,
  html.dark .sc-speed-dropdown:focus-visible,
  body.dark .sc-speed-dropdown:focus-visible,
  :root.dark .sc-speed-dropdown:focus-visible,
  .dark .sc-speed-dropdown:focus-visible,
  [data-theme="dark"] .sc-speed-dropdown:focus-visible {
    outline-color: #fafafa;
  }

  .sc-error {
    color: #ef4444;
    font-size: 0.8125rem;
    padding: 0.4rem 0;
  }

  .sc-player.dark .sc-error,
  .sc-player[data-theme="dark"] .sc-error,
  :host(.dark) .sc-error,
  :host-context(.dark) .sc-error,
  html.dark .sc-error,
  .dark .sc-error {
    color: #f87171 !important;
  }

  /* Automatic dark mode via prefers-color-scheme when not explicitly in light mode */
  @media (prefers-color-scheme: dark) {
    :host(:not(.light):not([data-theme="light"])) .sc-player:not(.light):not([data-theme="light"]),
    .sc-player:not(.light):not([data-theme="light"]) {
      border-color: #27272a !important;
      background: #121214 !important;
      color: #fafafa !important;
    }

    :host(:not(.light):not([data-theme="light"])) .sc-player:not(.light):not([data-theme="light"]) .sc-headphones-icon,
    .sc-player:not(.light):not([data-theme="light"]) .sc-headphones-icon {
      color: #a1a1aa !important;
    }

    :host(:not(.light):not([data-theme="light"])) .sc-player:not(.light):not([data-theme="light"]) .sc-overview-title,
    .sc-player:not(.light):not([data-theme="light"]) .sc-overview-title {
      color: #fafafa !important;
    }

    :host(:not(.light):not([data-theme="light"])) .sc-player:not(.light):not([data-theme="light"]) .sc-overview-subtitle,
    .sc-player:not(.light):not([data-theme="light"]) .sc-overview-subtitle {
      color: #a1a1aa !important;
    }

    :host(:not(.light):not([data-theme="light"])) .sc-player:not(.light):not([data-theme="light"]) .sc-btn-listen,
    .sc-player:not(.light):not([data-theme="light"]) .sc-btn-listen {
      background: #fafafa !important;
      color: #18181b !important;
    }

    :host(:not(.light):not([data-theme="light"])) .sc-player:not(.light):not([data-theme="light"]) .sc-btn-collapse,
    .sc-player:not(.light):not([data-theme="light"]) .sc-btn-collapse {
      border-color: #27272a !important;
      color: #fafafa !important;
    }

    :host(:not(.light):not([data-theme="light"])) .sc-player:not(.light):not([data-theme="light"]) .sc-btn-collapse:hover,
    .sc-player:not(.light):not([data-theme="light"]) .sc-btn-collapse:hover {
      background: rgba(255, 255, 255, 0.08) !important;
    }

    :host(:not(.light):not([data-theme="light"])) .sc-player:not(.light):not([data-theme="light"]) .sc-expanded-body,
    .sc-player:not(.light):not([data-theme="light"]) .sc-expanded-body {
      border-top-color: #27272a !important;
    }

    :host(:not(.light):not([data-theme="light"])) .sc-player:not(.light):not([data-theme="light"]) .sc-meta-row,
    .sc-player:not(.light):not([data-theme="light"]) .sc-meta-row {
      color: #a1a1aa !important;
    }

    :host(:not(.light):not([data-theme="light"])) .sc-player:not(.light):not([data-theme="light"]) .sc-section-heading,
    .sc-player:not(.light):not([data-theme="light"]) .sc-section-heading {
      color: #fafafa !important;
    }

    :host(:not(.light):not([data-theme="light"])) .sc-player:not(.light):not([data-theme="light"]) .sc-scrubber-container,
    .sc-player:not(.light):not([data-theme="light"]) .sc-scrubber-container {
      background: #27272a !important;
    }

    :host(:not(.light):not([data-theme="light"])) .sc-player:not(.light):not([data-theme="light"]) .sc-scrubber-fill,
    .sc-player:not(.light):not([data-theme="light"]) .sc-scrubber-fill {
      background: #fafafa !important;
    }

    :host(:not(.light):not([data-theme="light"])) .sc-player:not(.light):not([data-theme="light"]) .sc-scrubber-knob,
    .sc-player:not(.light):not([data-theme="light"]) .sc-scrubber-knob {
      background: #fafafa !important;
      box-shadow: none;
    }

    :host(:not(.light):not([data-theme="light"])) .sc-player:not(.light):not([data-theme="light"]) .sc-icon-btn,
    .sc-player:not(.light):not([data-theme="light"]) .sc-icon-btn {
      color: #a1a1aa !important;
    }

    :host(:not(.light):not([data-theme="light"])) .sc-player:not(.light):not([data-theme="light"]) .sc-icon-btn:hover:not(:disabled),
    .sc-player:not(.light):not([data-theme="light"]) .sc-icon-btn:hover:not(:disabled) {
      color: #fafafa !important;
    }

    :host(:not(.light):not([data-theme="light"])) .sc-player:not(.light):not([data-theme="light"]) .sc-play-pill,
    .sc-player:not(.light):not([data-theme="light"]) .sc-play-pill {
      background: #fafafa !important;
      color: #18181b !important;
    }

    :host(:not(.light):not([data-theme="light"])) .sc-player:not(.light):not([data-theme="light"]) .sc-speed-dropdown,
    .sc-player:not(.light):not([data-theme="light"]) .sc-speed-dropdown {
      background-color: #18181b !important;
      border-color: #27272a !important;
      color: #fafafa !important;
      background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23a1a1aa' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E") !important;
    }

    :host(:not(.light):not([data-theme="light"])) .sc-player:not(.light):not([data-theme="light"]) .sc-error,
    .sc-player:not(.light):not([data-theme="light"]) .sc-error {
      color: #f87171 !important;
    }
  }
`;

function render({ model, el }) {
  const pageId = (model && typeof model.get === "function" && model.get("page")) || "introduction";
  const explicitLocale = (model && typeof model.get === "function" && model.get("locale")) || "";
  const explicitBaseUrl =
    (model && typeof model.get === "function" && model.get("base_url")) || "";
  const locale = detectDocumentLocale(explicitLocale);
  const ui = {
    ...PLAYER_STRINGS.en,
    ...(PLAYER_STRINGS[locale] || {}),
  };
  const titleOverride =
    (model && typeof model.get === "function" && model.get("title")) || ui.audio_narration;

  const candidateAudioDirs = resolveAudioDirUrls(pageId, locale, explicitBaseUrl);
  let activeAudioDirUrl = candidateAudioDirs[0];

  const styleEl = document.createElement("style");
  styleEl.textContent = PLAYER_STYLES;

  const container = document.createElement("section");
  container.className = "sc-player";
  container.setAttribute("aria-label", titleOverride);
  container.setAttribute("data-sc-locale", locale);
  container.setAttribute("data-sc-page", pageId);
  container.tabIndex = 0;

  let isSyncingTheme = false;
  function syncTheme() {
    if (isSyncingTheme) return;
    isSyncingTheme = true;
    try {
      const targetDoc = container.ownerDocument || (typeof document !== "undefined" ? document : null);
      const isDark = isDarkModeActive(targetDoc, el);
      container.classList.toggle("dark", isDark);
      container.classList.toggle("light", !isDark);
      container.setAttribute("data-theme", isDark ? "dark" : "light");

      if (el && el.classList) {
        el.classList.toggle("dark", isDark);
        el.classList.toggle("light", !isDark);
        if (typeof el.setAttribute === "function") {
          el.setAttribute("data-theme", isDark ? "dark" : "light");
        }
      }
      const host = el?.host || (typeof el?.getRootNode === "function" && el.getRootNode()?.host);
      if (host && host.classList) {
        host.classList.toggle("dark", isDark);
        host.classList.toggle("light", !isDark);
        if (typeof host.setAttribute === "function") {
          host.setAttribute("data-theme", isDark ? "dark" : "light");
        }
      }
    } finally {
      isSyncingTheme = false;
    }
  }

  syncTheme();

  let themeObserver = null;
  const targetDoc = container.ownerDocument || (typeof document !== "undefined" ? document : null);
  if (typeof MutationObserver !== "undefined" && targetDoc) {
    themeObserver = new MutationObserver((mutations) => {
      const currentHost = el?.host || (typeof el?.getRootNode === "function" && el.getRootNode()?.host);
      const isInternal = mutations.every(
        (m) => m.target === container || m.target === el || m.target === currentHost || container.contains?.(m.target)
      );
      if (isInternal) return;
      syncTheme();
    });

    if (targetDoc.documentElement) {
      themeObserver.observe(targetDoc.documentElement, {
        attributes: true,
        attributeFilter: ["class", "data-theme", "data-mode", "style"],
        subtree: true,
      });
    }
    if (targetDoc.body && targetDoc.body !== targetDoc.documentElement) {
      themeObserver.observe(targetDoc.body, {
        attributes: true,
        attributeFilter: ["class", "data-theme", "data-mode", "style"],
      });
    }
  }

  // React to theme button clicks anywhere on the page without waiting for page reload
  const handleDocClick = (e) => {
    const btn = e.target?.closest?.("button, [role='button'], a, input");
    if (btn) {
      const desc = `${btn.getAttribute("aria-label") || ""} ${btn.getAttribute("title") || ""} ${btn.className || ""} ${btn.id || ""}`.toLowerCase();
      if (
        desc.includes("theme") ||
        desc.includes("dark") ||
        desc.includes("light") ||
        desc.includes("mode") ||
        desc.includes("color")
      ) {
        if (typeof requestAnimationFrame === "function") {
          requestAnimationFrame(() => syncTheme());
        }
        setTimeout(syncTheme, 50);
        setTimeout(syncTheme, 150);
        setTimeout(syncTheme, 300);
      }
    }
  };
  if (targetDoc && typeof targetDoc.addEventListener === "function") {
    targetDoc.addEventListener("click", handleDocClick, { passive: true });
  }

  const handleStorage = (e) => {
    if (!e.key || e.key.includes("theme") || e.key.includes("mode") || e.key.includes("color")) {
      syncTheme();
    }
  };
  const handleCustomThemeEvent = () => syncTheme();
  if (typeof window !== "undefined") {
    window.addEventListener("storage", handleStorage);
    window.addEventListener("theme-change", handleCustomThemeEvent);
    window.addEventListener("myst-theme-change", handleCustomThemeEvent);
  }

  let mediaQueryList = null;
  const handleMediaChange = () => syncTheme();
  if (typeof window !== "undefined" && window.matchMedia) {
    mediaQueryList = window.matchMedia("(prefers-color-scheme: dark)");
    if (typeof mediaQueryList.addEventListener === "function") {
      mediaQueryList.addEventListener("change", handleMediaChange);
    } else if (typeof mediaQueryList.addListener === "function") {
      mediaQueryList.addListener(handleMediaChange);
    }
  }

  // Header / Collapsed Overview Row
  const headerRow = document.createElement("div");
  headerRow.className = "sc-header-row";

  const overviewLeft = document.createElement("div");
  overviewLeft.className = "sc-overview-left";

  const headphonesSvg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  headphonesSvg.setAttribute("class", "sc-headphones-icon");
  headphonesSvg.setAttribute("viewBox", "0 0 24 24");
  headphonesSvg.setAttribute("fill", "none");
  headphonesSvg.setAttribute("stroke", "currentColor");
  headphonesSvg.setAttribute("stroke-width", "2");
  headphonesSvg.setAttribute("stroke-linecap", "round");
  headphonesSvg.setAttribute("stroke-linejoin", "round");
  headphonesSvg.setAttribute("aria-hidden", "true");
  headphonesSvg.innerHTML = `
    <path d="M3 18v-6a9 9 0 0 1 18 0v6"></path>
    <path d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3zM3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z"></path>
  `;

  const overviewText = document.createElement("div");
  overviewText.className = "sc-overview-text";

  const overviewTitle = document.createElement("span");
  overviewTitle.className = "sc-overview-title";
  overviewTitle.textContent = ui.voice_overview;

  const overviewSubtitle = document.createElement("span");
  overviewSubtitle.className = "sc-overview-subtitle";
  overviewSubtitle.textContent = ui.loading_narration;

  overviewText.append(overviewTitle, overviewSubtitle);
  overviewLeft.append(headphonesSvg, overviewText);

  // Single Action Button: localized "Listen" when collapsed, "^ Collapse" when expanded
  const toggleBtn = document.createElement("button");
  toggleBtn.type = "button";
  toggleBtn.className = "sc-btn-listen";
  toggleBtn.disabled = true;

  function renderToggleButton() {
    toggleBtn.setAttribute("aria-expanded", String(isExpanded));
    if (isExpanded) {
      toggleBtn.className = "sc-btn-collapse";
      toggleBtn.innerHTML = `
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <polyline points="18 15 12 9 6 15"></polyline>
        </svg>
        <span>${ui.collapse}</span>
      `;
    } else {
      toggleBtn.className = "sc-btn-listen";
      toggleBtn.innerHTML = `
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <polygon points="6 4 20 12 6 20 6 4" fill="currentColor"></polygon>
        </svg>
        <span>${ui.listen}</span>
      `;
    }
  }

  headerRow.append(overviewLeft, toggleBtn);

  // Expanded View Body (Collapsed by Default)
  const expandedBody = document.createElement("div");
  expandedBody.className = "sc-expanded-body";
  expandedBody.hidden = true;

  // Section Indicator and Time Counter
  const metaRow = document.createElement("div");
  metaRow.className = "sc-meta-row";

  const sectionIndicator = document.createElement("span");
  sectionIndicator.className = "sc-section-indicator";
  sectionIndicator.textContent = ui.section_of.replace("{current}", "1").replace("{total}", "4");

  const timeDisplay = document.createElement("span");
  timeDisplay.className = "sc-time-display";
  timeDisplay.textContent = `0${ui.sec_unit} / 0${ui.sec_unit}`;

  metaRow.append(sectionIndicator, timeDisplay);

  // Section Heading
  const sectionHeading = document.createElement("h3");
  sectionHeading.className = "sc-section-heading";
  sectionHeading.textContent = "";

  // Modern Scrubber Bar
  const scrubberContainer = document.createElement("div");
  scrubberContainer.className = "sc-scrubber-container";
  scrubberContainer.setAttribute("role", "slider");
  scrubberContainer.setAttribute("aria-label", ui.scrubber_label);
  scrubberContainer.setAttribute("aria-valuemin", "0");
  scrubberContainer.setAttribute("aria-valuemax", "100");
  scrubberContainer.setAttribute("aria-valuenow", "0");
  scrubberContainer.tabIndex = 0;

  const scrubberFill = document.createElement("div");
  scrubberFill.className = "sc-scrubber-fill";

  const scrubberKnob = document.createElement("div");
  scrubberKnob.className = "sc-scrubber-knob";

  scrubberContainer.append(scrubberFill, scrubberKnob);

  // Controls Row
  const controlsRow = document.createElement("div");
  controlsRow.className = "sc-controls-row";

  // Prev Button (|◀)
  const prevBtn = document.createElement("button");
  prevBtn.type = "button";
  prevBtn.className = "sc-icon-btn";
  prevBtn.setAttribute("aria-label", ui.previous_section);
  prevBtn.title = ui.previous_section;
  prevBtn.disabled = true;
  prevBtn.innerHTML = `
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
      <polygon points="19 20 9 12 19 4 19 20" fill="currentColor"></polygon>
      <line x1="5" y1="19" x2="5" y2="5"></line>
    </svg>
  `;

  // Play / Pause Pill Button
  const playPill = document.createElement("button");
  playPill.type = "button";
  playPill.className = "sc-play-pill";
  playPill.setAttribute("aria-label", ui.play);
  playPill.innerHTML = `
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
      <circle cx="12" cy="12" r="10"></circle>
      <polygon points="10 8 16 12 10 16 10 8" fill="currentColor"></polygon>
    </svg>
  `;

  // Next Button (▶|)
  const nextBtn = document.createElement("button");
  nextBtn.type = "button";
  nextBtn.className = "sc-icon-btn";
  nextBtn.setAttribute("aria-label", ui.next_section);
  nextBtn.title = ui.next_section;
  nextBtn.disabled = true;
  nextBtn.innerHTML = `
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
      <polygon points="5 4 15 12 5 20 5 4" fill="currentColor"></polygon>
      <line x1="19" y1="5" x2="19" y2="19"></line>
    </svg>
  `;

  // Speed Dropdown
  const speedDropdown = document.createElement("select");
  speedDropdown.className = "sc-speed-dropdown";
  speedDropdown.setAttribute("aria-label", ui.playback_rate);
  for (const s of SPEEDS) {
    const opt = document.createElement("option");
    opt.value = String(s);
    opt.textContent = `${s}x`;
    if (s === 1.0) opt.selected = true;
    speedDropdown.appendChild(opt);
  }

  controlsRow.append(prevBtn, playPill, nextBtn, speedDropdown);

  const errorBanner = document.createElement("div");
  errorBanner.className = "sc-error";
  errorBanner.setAttribute("role", "status");
  errorBanner.setAttribute("aria-live", "polite");
  errorBanner.hidden = true;

  expandedBody.append(metaRow, sectionHeading, scrubberContainer, controlsRow);
  container.append(headerRow, errorBanner, expandedBody);
  el.append(styleEl, container);
  syncTheme();
  if (typeof requestAnimationFrame === "function") {
    requestAnimationFrame(() => syncTheme());
  }

  // Audio & State
  const audio = new Audio();
  audio.preload = "metadata";

  let manifest = null;
  let currentIndex = 0;
  let isPlaying = false;
  let isExpanded = false;
  let autoSyncScroll = true;
  let isDestroyed = false;

  function showError(msg) {
    errorBanner.textContent = msg;
    errorBanner.hidden = false;
  }

  function setExpanded(expanded) {
    if (expanded && !manifest) {
      return;
    }
    isExpanded = Boolean(expanded);
    if (isExpanded) {
      expandedBody.hidden = false;
      expandedBody.classList.remove("is-hidden");
      expandedBody.style.setProperty("display", "flex", "important");
      container.classList.add("is-expanded");
    } else {
      expandedBody.hidden = true;
      expandedBody.classList.add("is-hidden");
      expandedBody.style.setProperty("display", "none", "important");
      container.classList.remove("is-expanded");
    }
    renderToggleButton();
  }

  setExpanded(false);

  function updateScrubber(current, duration) {
    const safeDuration = duration > 0 ? duration : 1;
    const pct = Math.min(100, Math.max(0, (current / safeDuration) * 100));
    scrubberFill.style.width = `${pct}%`;
    scrubberKnob.style.left = `${pct}%`;
    scrubberContainer.setAttribute("aria-valuenow", String(Math.round(current)));
    timeDisplay.textContent = `${Math.floor(current)}${ui.sec_unit} / ${Math.round(safeDuration)}${ui.sec_unit}`;
  }

  function syncDocumentAnchor(anchor, updateHash = false) {
    if (!autoSyncScroll || !anchor) return;
    const heading = findHeadingElement(anchor);
    if (heading && typeof heading.scrollIntoView === "function") {
      heading.scrollIntoView({ behavior: "smooth", block: "start" });
    }
    if (updateHash && typeof history !== "undefined" && history.replaceState) {
      history.replaceState(null, "", `#${anchor}`);
    }
  }

  function loadChunk(index, autoplay = false, syncScroll = false) {
    if (!manifest || !manifest.chunks || index < 0 || index >= manifest.chunks.length) {
      return;
    }
    currentIndex = index;
    const chunk = manifest.chunks[currentIndex];
    const audioUrl = `${activeAudioDirUrl}/${chunk.audio_file}`;

    audio.src = audioUrl;
    audio.playbackRate = Number(speedDropdown.value) || 1.0;

    sectionIndicator.textContent = ui.section_of
      .replace("{current}", String(currentIndex + 1))
      .replace("{total}", String(manifest.chunks.length));
    sectionHeading.textContent =
      chunk.section_title || ui.section_fallback.replace("{current}", String(currentIndex + 1));

    prevBtn.disabled = currentIndex <= 0;
    nextBtn.disabled = currentIndex >= manifest.chunks.length - 1;

    updateScrubber(0, chunk.duration_seconds || 10);

    if (model && typeof model.set === "function") {
      model.set("current_chunk", currentIndex);
      model.set("current_anchor", chunk.section_anchor);
    }

    if (syncScroll) {
      syncDocumentAnchor(chunk.section_anchor, true);
    }

    if (autoplay) {
      audio.play().catch((err) => {
        isPlaying = false;
        updatePlayIcons();
        showError(`${ui.playback_failed}: ${err.message || err}`);
      });
    }
  }

  function updatePlayIcons() {
    playPill.setAttribute("aria-label", isPlaying ? ui.pause : ui.play);
    if (isPlaying) {
      playPill.innerHTML = `
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="10" y1="15" x2="10" y2="9"></line>
          <line x1="14" y1="15" x2="14" y2="9"></line>
        </svg>
      `;
    } else {
      playPill.innerHTML = `
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <circle cx="12" cy="12" r="10"></circle>
          <polygon points="10 8 16 12 10 16 10 8" fill="currentColor"></polygon>
        </svg>
      `;
    }
  }

  // Toggle button: Listen -> expands & plays; ^ Collapse -> collapses & pauses
  toggleBtn.addEventListener("click", () => {
    if (!manifest) return;
    if (!isExpanded) {
      setExpanded(true);
      if (audio.paused) {
        audio.play().catch((err) => showError(`${ui.playback_failed}: ${err.message || err}`));
      }
    } else {
      setExpanded(false);
      if (!audio.paused) {
        audio.pause();
      }
    }
  });

  playPill.addEventListener("click", () => {
    if (!manifest) return;
    if (audio.paused) {
      audio.play().catch((err) => showError(`${ui.playback_failed}: ${err.message || err}`));
    } else {
      audio.pause();
    }
  });

  prevBtn.addEventListener("click", () => {
    if (currentIndex > 0) {
      loadChunk(currentIndex - 1, isPlaying, true);
    }
  });

  nextBtn.addEventListener("click", () => {
    if (manifest && currentIndex < manifest.chunks.length - 1) {
      loadChunk(currentIndex + 1, isPlaying, true);
    }
  });

  speedDropdown.addEventListener("change", () => {
    audio.playbackRate = Number(speedDropdown.value) || 1.0;
  });

  // Scrubber drag / click
  function seekWithPointer(e) {
    if (!manifest) return;
    const rect = scrubberContainer.getBoundingClientRect();
    const ratio = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
    const chunk = manifest.chunks[currentIndex];
    const duration = chunk.duration_seconds || audio.duration || 10;
    const target = ratio * duration;
    audio.currentTime = target;
    updateScrubber(target, duration);
  }

  scrubberContainer.addEventListener("click", seekWithPointer);

  audio.addEventListener("play", () => {
    isPlaying = true;
    updatePlayIcons();
    errorBanner.hidden = true;
  });

  audio.addEventListener("pause", () => {
    isPlaying = false;
    updatePlayIcons();
  });

  audio.addEventListener("timeupdate", () => {
    const chunk = manifest ? manifest.chunks[currentIndex] : null;
    const duration = chunk ? chunk.duration_seconds : audio.duration || 10;
    updateScrubber(audio.currentTime, duration);
  });

  audio.addEventListener("ended", () => {
    if (manifest && currentIndex < manifest.chunks.length - 1) {
      loadChunk(currentIndex + 1, true, true);
    } else {
      isPlaying = false;
      updatePlayIcons();
    }
  });

  audio.addEventListener("error", () => {
    showError(`${ui.playback_failed}.`);
  });

  // Keyboard accessibility
  container.addEventListener("keydown", (e) => {
    if (e.target && e.target.tagName === "SELECT") return;
    if (!manifest) return;
    if (e.key === " ") {
      e.preventDefault();
      if (!isExpanded) {
        setExpanded(true);
        audio.play().catch(() => {});
      } else {
        playPill.click();
      }
    } else if (e.key === "ArrowLeft") {
      e.preventDefault();
      audio.currentTime = Math.max(0, audio.currentTime - 5);
    } else if (e.key === "ArrowRight") {
      e.preventDefault();
      audio.currentTime = Math.min(audio.duration || 100, audio.currentTime + 5);
    } else if (e.key === "PageUp") {
      e.preventDefault();
      prevBtn.click();
    } else if (e.key === "PageDown") {
      e.preventDefault();
      nextBtn.click();
    }
  });

  // Load and verify localized manifest before enabling audio playback
  (async () => {
    let loadedManifest = null;
    let lastErr = null;

    for (const dirCandidate of candidateAudioDirs) {
      try {
        const manifestResp = await fetch(`${dirCandidate}/manifest.json`);
        if (!manifestResp.ok) {
          throw new Error(`HTTP ${manifestResp.status}`);
        }
        const manifestData = await manifestResp.json();
        validateNarrationManifest(manifestData, pageId, locale);
        activeAudioDirUrl = dirCandidate;
        loadedManifest = manifestData;
        break;
      } catch (err) {
        lastErr = err;
      }
    }

    if (isDestroyed) return;

    if (loadedManifest) {
      manifest = loadedManifest;
      container.hidden = false;
      container.style.display = "";
      const totalSec = manifest.total_duration_seconds || 0;
      overviewSubtitle.textContent = `${manifest.chunks.length} ${ui.topics_unit} · ${formatDurationSeconds(totalSec, ui)}`;
      toggleBtn.disabled = false;
      loadChunk(0, false, false);
    } else {
      manifest = null;
      toggleBtn.disabled = true;
      setExpanded(false);
      container.hidden = true;
      container.style.display = "none";
      overviewSubtitle.textContent = ui.narration_unavailable;
      showError(`${ui.narration_unavailable} (${lastErr?.message || "missing manifest"}).`);
    }
  })();

  return () => {
    isDestroyed = true;
    if (themeObserver) {
      themeObserver.disconnect();
      themeObserver = null;
    }
    if (targetDoc && typeof targetDoc.removeEventListener === "function") {
      targetDoc.removeEventListener("click", handleDocClick);
    }
    if (typeof window !== "undefined") {
      window.removeEventListener("storage", handleStorage);
      window.removeEventListener("theme-change", handleCustomThemeEvent);
      window.removeEventListener("myst-theme-change", handleCustomThemeEvent);
    }
    if (mediaQueryList) {
      if (typeof mediaQueryList.removeEventListener === "function") {
        mediaQueryList.removeEventListener("change", handleMediaChange);
      } else if (typeof mediaQueryList.removeListener === "function") {
        mediaQueryList.removeListener(handleMediaChange);
      }
    }
    audio.pause();
    audio.removeAttribute("src");
    audio.load();
    container.remove();
    styleEl.remove();
  };
}

export default { render, PLAYER_STRINGS, detectDocumentLocale, resolveAudioDirUrls, validateNarrationManifest, isDarkModeActive };
