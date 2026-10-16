/**
 * SoftCloud Documentation Hub — Interactive AI Audio Narration Player
 *
 * Compatible with MyST `{anywidget}` (ESM default export `{ render({ model, el }) }`).
 * Operates exclusively against build-time static assets (`manifest.json`, `transcript.json`,
 * and content-addressed `.mp3` chunks) without runtime API calls or credentials.
 */

const SPEEDS = [0.75, 1.0, 1.25, 1.5, 1.75, 2.0];

function formatDurationSeconds(seconds) {
  if (!Number.isFinite(seconds) || seconds <= 0) return "0 min 0 sec";
  const total = Math.round(seconds);
  const mins = Math.floor(total / 60);
  const secs = total % 60;
  if (mins === 0) return `${secs} sec`;
  return `${mins} min ${secs} sec`;
}

function resolveAudioDirUrl(pageId, explicitBaseUrl) {
  if (explicitBaseUrl) {
    const clean = explicitBaseUrl.replace(/\/+$/, "");
    return `${clean}/audio/${encodeURIComponent(pageId)}`;
  }

  if (typeof window !== "undefined" && typeof window.BASE_URL === "string" && window.BASE_URL) {
    const clean = window.BASE_URL.replace(/\/+$/, "");
    return `${clean}/audio/${encodeURIComponent(pageId)}`;
  }

  const pathname = (typeof window !== "undefined" && window.location?.pathname) || "/";
  let siteBase = pathname.replace(/\/index\.html$/, "");
  const knownSuffixes = [
    `/notebooks/${pageId.replace(/^notebooks-/, "")}`,
    "/notebooks/experiment",
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
  return `${siteBase}/audio/${encodeURIComponent(pageId)}`;
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

  /* Default container inheriting theme tokens — purely flat, no shadows */
  .sc-player {
    border: 1px solid var(--border, #e4e4e7);
    border-radius: 12px;
    background: var(--card, #ffffff);
    color: var(--foreground, #18181b);
    box-shadow: none;
    padding: 1rem 1.25rem;
    box-sizing: border-box;
    transition: background-color 0.15s ease, border-color 0.15s ease, color 0.15s ease;
  }

  /* Dark mode - system preference */
  @media (prefers-color-scheme: dark) {
    .sc-player {
      border-color: var(--border, #27272a);
      background: var(--card, #121214);
      color: var(--foreground, #fafafa);
    }
  }

  /* Dark mode - document classes / attributes */
  html.dark .sc-player,
  [data-theme="dark"] .sc-player,
  [data-mode="dark"] .sc-player,
  :root.dark .sc-player {
    border-color: var(--border, #27272a);
    background: var(--card, #121214);
    color: var(--foreground, #fafafa);
  }

  /* Light mode - document classes / attributes */
  html.light .sc-player,
  [data-theme="light"] .sc-player,
  [data-mode="light"] .sc-player,
  :root.light .sc-player {
    border-color: var(--border, #e4e4e7);
    background: var(--card, #ffffff);
    color: var(--foreground, #18181b);
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
    color: var(--muted-foreground, #71717a);
    flex-shrink: 0;
  }

  @media (prefers-color-scheme: dark) {
    .sc-headphones-icon {
      color: var(--muted-foreground, #a1a1aa);
    }
  }
  html.dark .sc-headphones-icon,
  [data-theme="dark"] .sc-headphones-icon {
    color: var(--muted-foreground, #a1a1aa);
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

  .sc-overview-subtitle {
    font-size: 0.75rem;
    color: var(--muted-foreground, #71717a);
    line-height: 1.2;
  }

  @media (prefers-color-scheme: dark) {
    .sc-overview-subtitle {
      color: var(--muted-foreground, #a1a1aa);
    }
  }
  html.dark .sc-overview-subtitle,
  [data-theme="dark"] .sc-overview-subtitle {
    color: var(--muted-foreground, #a1a1aa);
  }

  /* Listen Pill Button (High Contrast Flat) */
  .sc-btn-listen {
    appearance: none;
    border: none;
    background: var(--foreground, #18181b);
    color: var(--background, #ffffff);
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

  @media (prefers-color-scheme: dark) {
    .sc-btn-listen {
      background: var(--foreground, #fafafa);
      color: var(--background, #18181b);
    }
  }
  html.dark .sc-btn-listen,
  [data-theme="dark"] .sc-btn-listen,
  [data-mode="dark"] .sc-btn-listen {
    background: var(--foreground, #fafafa);
    color: var(--background, #18181b);
  }
  html.light .sc-btn-listen,
  [data-theme="light"] .sc-btn-listen,
  [data-mode="light"] .sc-btn-listen {
    background: var(--foreground, #18181b);
    color: var(--background, #ffffff);
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
    border: 1px solid var(--border, #e4e4e7);
    background: transparent;
    color: inherit;
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

  @media (prefers-color-scheme: dark) {
    .sc-btn-collapse {
      border-color: var(--border, #27272a);
    }
  }
  html.dark .sc-btn-collapse,
  [data-theme="dark"] .sc-btn-collapse,
  [data-mode="dark"] .sc-btn-collapse {
    border-color: var(--border, #27272a);
  }
  html.light .sc-btn-collapse,
  [data-theme="light"] .sc-btn-collapse,
  [data-mode="light"] .sc-btn-collapse {
    border-color: var(--border, #e4e4e7);
  }

  .sc-btn-collapse:hover {
    background: var(--muted, rgba(0, 0, 0, 0.04));
  }
  @media (prefers-color-scheme: dark) {
    .sc-btn-collapse:hover {
      background: var(--muted, rgba(255, 255, 255, 0.06));
    }
  }
  html.dark .sc-btn-collapse:hover,
  [data-theme="dark"] .sc-btn-collapse:hover,
  [data-mode="dark"] .sc-btn-collapse:hover {
    background: var(--muted, rgba(255, 255, 255, 0.06));
  }

  /* Expanded Section Body */
  .sc-expanded-body {
    margin-top: 1rem;
    padding-top: 0.85rem;
    border-top: 1px solid var(--border, #e4e4e7);
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  @media (prefers-color-scheme: dark) {
    .sc-expanded-body {
      border-top-color: var(--border, #27272a);
    }
  }
  html.dark .sc-expanded-body,
  [data-theme="dark"] .sc-expanded-body,
  [data-mode="dark"] .sc-expanded-body {
    border-top-color: var(--border, #27272a);
  }

  .sc-meta-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 0.75rem;
    color: var(--muted-foreground, #71717a);
  }

  @media (prefers-color-scheme: dark) {
    .sc-meta-row {
      color: var(--muted-foreground, #a1a1aa);
    }
  }
  html.dark .sc-meta-row,
  [data-theme="dark"] .sc-meta-row {
    color: var(--muted-foreground, #a1a1aa);
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

  /* Flat Scrubber Bar */
  .sc-scrubber-container {
    position: relative;
    width: 100%;
    height: 8px;
    background: var(--secondary, #f4f4f5);
    border-radius: 9999px;
    cursor: pointer;
    margin: 0.35rem 0 0.5rem 0;
    display: flex;
    align-items: center;
  }

  @media (prefers-color-scheme: dark) {
    .sc-scrubber-container {
      background: var(--secondary, #27272a);
    }
  }
  html.dark .sc-scrubber-container,
  [data-theme="dark"] .sc-scrubber-container {
    background: var(--secondary, #27272a);
  }
  html.light .sc-scrubber-container,
  [data-theme="light"] .sc-scrubber-container {
    background: var(--secondary, #f4f4f5);
  }

  .sc-scrubber-fill {
    height: 100%;
    background: var(--foreground, #18181b);
    border-radius: 9999px;
    width: 0%;
    pointer-events: none;
    transition: width 0.05s linear;
  }

  @media (prefers-color-scheme: dark) {
    .sc-scrubber-fill {
      background: var(--foreground, #fafafa);
    }
  }
  html.dark .sc-scrubber-fill,
  [data-theme="dark"] .sc-scrubber-fill {
    background: var(--foreground, #fafafa);
  }

  .sc-scrubber-knob {
    position: absolute;
    top: 50%;
    left: 0%;
    margin-top: -8px;
    margin-left: -8px;
    width: 16px;
    height: 16px;
    background: var(--foreground, #18181b);
    border-radius: 9999px;
    box-shadow: none;
    cursor: grab;
    pointer-events: none;
    transform: scale(1);
    transform-origin: center center;
    transition: transform 0.15s ease;
  }

  @media (prefers-color-scheme: dark) {
    .sc-scrubber-knob {
      background: var(--foreground, #fafafa);
      box-shadow: none;
    }
  }
  html.dark .sc-scrubber-knob,
  [data-theme="dark"] .sc-scrubber-knob {
    background: var(--foreground, #fafafa);
    box-shadow: none;
  }
  html.light .sc-scrubber-knob,
  [data-theme="light"] .sc-scrubber-knob {
    background: var(--foreground, #18181b);
    box-shadow: none;
  }

  .sc-scrubber-container:hover .sc-scrubber-knob {
    transform: scale(1.15);
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
    background: transparent;
    border: none;
    color: var(--muted-foreground, #71717a);
    cursor: pointer;
    padding: 0.4rem;
    border-radius: 6px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    transition: color 0.15s ease;
  }

  @media (prefers-color-scheme: dark) {
    .sc-icon-btn {
      color: var(--muted-foreground, #a1a1aa);
    }
  }
  html.dark .sc-icon-btn,
  [data-theme="dark"] .sc-icon-btn {
    color: var(--muted-foreground, #a1a1aa);
  }

  .sc-icon-btn:hover:not(:disabled) {
    color: var(--foreground, #18181b);
  }
  @media (prefers-color-scheme: dark) {
    .sc-icon-btn:hover:not(:disabled) {
      color: var(--foreground, #fafafa);
    }
  }
  html.dark .sc-icon-btn:hover:not(:disabled),
  [data-theme="dark"] .sc-icon-btn:hover:not(:disabled) {
    color: var(--foreground, #fafafa);
  }

  .sc-icon-btn:disabled {
    opacity: 0.3;
    cursor: not-allowed;
  }

  /* Play Pill Button (Flat High Contrast) */
  .sc-play-pill {
    appearance: none;
    background: var(--foreground, #18181b);
    color: var(--background, #ffffff);
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

  @media (prefers-color-scheme: dark) {
    .sc-play-pill {
      background: var(--foreground, #fafafa);
      color: var(--background, #18181b);
    }
  }
  html.dark .sc-play-pill,
  [data-theme="dark"] .sc-play-pill {
    background: var(--foreground, #fafafa);
    color: var(--background, #18181b);
  }
  html.light .sc-play-pill,
  [data-theme="light"] .sc-play-pill {
    background: var(--foreground, #18181b);
    color: var(--background, #ffffff);
  }

  .sc-play-pill:hover:not(:disabled) {
    opacity: 0.88;
  }

  /* Speed Dropdown (Flat Select) */
  .sc-speed-dropdown {
    appearance: none;
    background-color: var(--card, #ffffff);
    border: 1px solid var(--border, #e4e4e7);
    color: inherit;
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

  @media (prefers-color-scheme: dark) {
    .sc-speed-dropdown {
      background-color: var(--card, #18181b);
      border-color: var(--border, #27272a);
      background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23a1a1aa' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
    }
  }
  html.dark .sc-speed-dropdown,
  [data-theme="dark"] .sc-speed-dropdown {
    background-color: var(--card, #18181b);
    border-color: var(--border, #27272a);
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23a1a1aa' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  }
  html.light .sc-speed-dropdown,
  [data-theme="light"] .sc-speed-dropdown {
    background-color: var(--card, #ffffff);
    border-color: var(--border, #e4e4e7);
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%2371717a' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  }

  .sc-speed-dropdown:focus-visible {
    outline: 2px solid var(--foreground, #18181b);
  }

  .sc-error {
    color: #ef4444;
    font-size: 0.8125rem;
    padding: 0.4rem 0;
  }
`;

function render({ model, el }) {
  const pageId = (model && typeof model.get === "function" && model.get("page")) || "introduction";
  const explicitBaseUrl =
    (model && typeof model.get === "function" && model.get("base_url")) || "";
  const titleOverride =
    (model && typeof model.get === "function" && model.get("title")) || "Audio Narration";

  const audioDirUrl = resolveAudioDirUrl(pageId, explicitBaseUrl);

  const styleEl = document.createElement("style");
  styleEl.textContent = PLAYER_STYLES;

  const container = document.createElement("section");
  container.className = "sc-player";
  container.setAttribute("role", "region");
  container.setAttribute("aria-label", `${titleOverride} Player`);
  container.tabIndex = 0;

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
  headphonesSvg.innerHTML = `
    <path d="M3 18v-6a9 9 0 0 1 18 0v6"></path>
    <path d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3zM3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z"></path>
  `;

  const overviewText = document.createElement("div");
  overviewText.className = "sc-overview-text";

  const overviewTitle = document.createElement("span");
  overviewTitle.className = "sc-overview-title";
  overviewTitle.textContent = "Voice overview";

  const overviewSubtitle = document.createElement("span");
  overviewSubtitle.className = "sc-overview-subtitle";
  overviewSubtitle.textContent = "Loading narration...";

  overviewText.append(overviewTitle, overviewSubtitle);
  overviewLeft.append(headphonesSvg, overviewText);

  // Single Action Button: "Listen" when collapsed, "^ Collapse" when expanded
  const toggleBtn = document.createElement("button");
  toggleBtn.type = "button";
  toggleBtn.className = "sc-btn-listen";

  function renderToggleButton() {
    if (isExpanded) {
      toggleBtn.className = "sc-btn-collapse";
      toggleBtn.innerHTML = `
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="18 15 12 9 6 15"></polyline>
        </svg>
        <span>Collapse</span>
      `;
    } else {
      toggleBtn.className = "sc-btn-listen";
      toggleBtn.innerHTML = `
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <polygon points="6 4 20 12 6 20 6 4" fill="currentColor"></polygon>
        </svg>
        <span>Listen</span>
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
  sectionIndicator.textContent = "SECTION 1 OF 4";

  const timeDisplay = document.createElement("span");
  timeDisplay.className = "sc-time-display";
  timeDisplay.textContent = "0s / 0s";

  metaRow.append(sectionIndicator, timeDisplay);

  // Section Heading
  const sectionHeading = document.createElement("h3");
  sectionHeading.className = "sc-section-heading";
  sectionHeading.textContent = "Introduction";

  // Modern Scrubber Bar
  const scrubberContainer = document.createElement("div");
  scrubberContainer.className = "sc-scrubber-container";
  scrubberContainer.setAttribute("role", "slider");
  scrubberContainer.setAttribute("aria-label", "Audio playback scrubber");
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
  prevBtn.title = "Previous section";
  prevBtn.disabled = true;
  prevBtn.innerHTML = `
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <polygon points="19 20 9 12 19 4 19 20" fill="currentColor"></polygon>
      <line x1="5" y1="19" x2="5" y2="5"></line>
    </svg>
  `;

  // Play / Pause Pill Button
  const playPill = document.createElement("button");
  playPill.type = "button";
  playPill.className = "sc-play-pill";
  playPill.innerHTML = `
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <circle cx="12" cy="12" r="10"></circle>
      <polygon points="10 8 16 12 10 16 10 8" fill="currentColor"></polygon>
    </svg>
  `;

  // Next Button (▶|)
  const nextBtn = document.createElement("button");
  nextBtn.type = "button";
  nextBtn.className = "sc-icon-btn";
  nextBtn.title = "Next section";
  nextBtn.disabled = true;
  nextBtn.innerHTML = `
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <polygon points="5 4 15 12 5 20 5 4" fill="currentColor"></polygon>
      <line x1="19" y1="5" x2="19" y2="19"></line>
    </svg>
  `;

  // Speed Dropdown
  const speedDropdown = document.createElement("select");
  speedDropdown.className = "sc-speed-dropdown";
  speedDropdown.setAttribute("aria-label", "Playback rate");
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
  errorBanner.hidden = true;

  expandedBody.append(metaRow, sectionHeading, scrubberContainer, controlsRow);
  container.append(headerRow, errorBanner, expandedBody);
  el.append(styleEl, container);

  // Audio & State
  const audio = new Audio();
  audio.preload = "metadata";

  let manifest = null;
  let currentIndex = 0;
  let isPlaying = false;
  let isExpanded = false;
  let autoSyncScroll = true;
  let isDestroyed = false;

  renderToggleButton();

  function showError(msg) {
    errorBanner.textContent = msg;
    errorBanner.hidden = false;
  }

  function setExpanded(expanded) {
    isExpanded = expanded;
    expandedBody.hidden = !isExpanded;
    renderToggleButton();
  }

  function updateScrubber(current, duration) {
    const safeDuration = duration > 0 ? duration : 1;
    const pct = Math.min(100, Math.max(0, (current / safeDuration) * 100));
    scrubberFill.style.width = `${pct}%`;
    scrubberKnob.style.left = `${pct}%`;
    scrubberContainer.setAttribute("aria-valuenow", String(Math.round(current)));
    timeDisplay.textContent = `${Math.floor(current)}s / ${Math.round(safeDuration)}s`;
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
    const audioUrl = `${audioDirUrl}/${chunk.audio_file}`;

    audio.src = audioUrl;
    audio.playbackRate = Number(speedDropdown.value) || 1.0;

    sectionIndicator.textContent = `SECTION ${currentIndex + 1} OF ${manifest.chunks.length}`;
    sectionHeading.textContent = chunk.section_title || `Section ${currentIndex + 1}`;

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
        showError(`Playback failed: ${err.message || err}`);
      });
    }
  }

  function updatePlayIcons() {
    if (isPlaying) {
      playPill.innerHTML = `
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="10" y1="15" x2="10" y2="9"></line>
          <line x1="14" y1="15" x2="14" y2="9"></line>
        </svg>
      `;
    } else {
      playPill.innerHTML = `
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"></circle>
          <polygon points="10 8 16 12 10 16 10 8" fill="currentColor"></polygon>
        </svg>
      `;
    }
  }

  // Toggle button: Listen -> expands & plays; ^ Collapse -> collapses & pauses
  toggleBtn.addEventListener("click", () => {
    if (!isExpanded) {
      setExpanded(true);
      if (audio.paused) {
        audio.play().catch((err) => showError(`Playback blocked: ${err.message || err}`));
      }
    } else {
      setExpanded(false);
      if (!audio.paused) {
        audio.pause();
      }
    }
  });

  playPill.addEventListener("click", () => {
    if (audio.paused) {
      audio.play().catch((err) => showError(`Playback error: ${err.message || err}`));
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
    showError("Failed to load audio chunk.");
  });

  // Keyboard accessibility
  container.addEventListener("keydown", (e) => {
    if (e.target && e.target.tagName === "SELECT") return;
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

  // Load manifest & transcript
  (async () => {
    try {
      const manifestResp = await fetch(`${audioDirUrl}/manifest.json`);
      if (!manifestResp.ok) throw new Error(`HTTP ${manifestResp.status}`);
      const manifestData = await manifestResp.json();
      if (isDestroyed) return;

      manifest = manifestData;

      const totalSec = manifest.total_duration_seconds || 128;
      overviewSubtitle.textContent = `${manifest.chunks.length} topics · ${formatDurationSeconds(totalSec)}`;

      toggleBtn.disabled = false;
      loadChunk(0, false, false);
    } catch (err) {
      if (!isDestroyed) {
        overviewSubtitle.textContent = "4 topics · 2 min 8 sec";
        showError(`Narration assets unavailable (${err.message || err}).`);
      }
    }
  })();

  return () => {
    isDestroyed = true;
    audio.pause();
    audio.removeAttribute("src");
    audio.load();
    container.remove();
    styleEl.remove();
  };
}

export default { render };
