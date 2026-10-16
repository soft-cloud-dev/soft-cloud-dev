/**
 * SoftCloud Documentation Hub — Interactive AI Audio Narration Player
 *
 * Compatible with MyST `{anywidget}` (ESM default export `{ render({ model, el }) }`).
 * Operates exclusively against build-time static assets (`manifest.json`, `transcript.json`,
 * and content-addressed `.mp3` chunks) without runtime API calls or credentials.
 */

const SPEEDS = [0.75, 1.0, 1.25, 1.5, 1.75, 2.0];

function formatTime(seconds) {
  if (!Number.isFinite(seconds) || seconds < 0) return "0:00";
  const total = Math.floor(seconds);
  const mins = Math.floor(total / 60);
  const secs = total % 60;
  return `${mins}:${secs < 10 ? "0" : ""}${secs}`;
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
  // Detect site root by trimming known page slugs (`introduction`, `architecture`, `notebooks/...`)
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
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Inter, Helvetica, Arial, sans-serif;
    color: #0f172a;
  }

  @media (prefers-color-scheme: dark) {
    :host {
      color: #f1f5f9;
    }
  }

  .sc-player {
    border: 1px solid rgba(148, 163, 184, 0.35);
    border-radius: 12px;
    background: linear-gradient(180deg, rgba(248, 250, 252, 0.96), rgba(241, 245, 249, 0.92));
    box-shadow: 0 2px 10px rgba(15, 23, 42, 0.05);
    padding: 0.875rem 1rem;
    box-sizing: border-box;
  }

  @media (prefers-color-scheme: dark) {
    .sc-player {
      background: linear-gradient(180deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.95));
      border-color: rgba(148, 163, 184, 0.25);
      box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25);
    }
  }

  .sc-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem;
    flex-wrap: wrap;
    margin-bottom: 0.65rem;
  }

  .sc-title-group {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    min-width: 0;
  }

  .sc-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    padding: 0.2rem 0.5rem;
    border-radius: 999px;
    background: rgba(37, 99, 235, 0.12);
    color: #1d4ed8;
    white-space: nowrap;
  }

  @media (prefers-color-scheme: dark) {
    .sc-badge {
      background: rgba(59, 130, 246, 0.22);
      color: #93c5fd;
    }
  }

  .sc-section-label {
    font-size: 0.875rem;
    font-weight: 600;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .sc-meta {
    font-size: 0.75rem;
    opacity: 0.75;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .sc-controls-row {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex-wrap: wrap;
  }

  .sc-btn {
    appearance: none;
    border: 1px solid rgba(148, 163, 184, 0.4);
    background: rgba(255, 255, 255, 0.85);
    color: inherit;
    border-radius: 8px;
    padding: 0.38rem 0.65rem;
    font-size: 0.8125rem;
    font-weight: 500;
    line-height: 1.2;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 0.35rem;
    transition: background 0.15s ease, border-color 0.15s ease, transform 0.08s ease;
  }

  @media (prefers-color-scheme: dark) {
    .sc-btn {
      background: rgba(51, 65, 85, 0.75);
      border-color: rgba(148, 163, 184, 0.3);
    }
  }

  .sc-btn:hover:not(:disabled) {
    border-color: #3b82f6;
    background: rgba(59, 130, 246, 0.1);
  }

  .sc-btn:focus-visible,
  .sc-select:focus-visible,
  .sc-seek:focus-visible {
    outline: 2px solid #3b82f6;
    outline-offset: 2px;
  }

  .sc-btn:disabled {
    opacity: 0.45;
    cursor: not-allowed;
  }

  .sc-btn-primary {
    background: #2563eb;
    color: #ffffff;
    border-color: #1d4ed8;
    font-weight: 600;
    min-width: 5.2rem;
  }

  .sc-btn-primary:hover:not(:disabled) {
    background: #1d4ed8;
    color: #ffffff;
  }

  .sc-progress-group {
    flex: 1 1 180px;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    min-width: 160px;
  }

  .sc-time {
    font-size: 0.75rem;
    font-variant-numeric: tabular-nums;
    white-space: nowrap;
    opacity: 0.85;
  }

  .sc-seek {
    flex: 1;
    accent-color: #2563eb;
    cursor: pointer;
    height: 6px;
  }

  .sc-select {
    border: 1px solid rgba(148, 163, 184, 0.4);
    background: rgba(255, 255, 255, 0.85);
    color: inherit;
    border-radius: 8px;
    padding: 0.35rem 0.5rem;
    font-size: 0.78rem;
    cursor: pointer;
    max-width: 210px;
  }

  @media (prefers-color-scheme: dark) {
    .sc-select {
      background: rgba(51, 65, 85, 0.75);
      border-color: rgba(148, 163, 184, 0.3);
    }
  }

  .sc-transcript-panel {
    margin-top: 0.75rem;
    padding-top: 0.75rem;
    border-top: 1px solid rgba(148, 163, 184, 0.3);
    max-height: 320px;
    overflow-y: auto;
    font-size: 0.85rem;
    line-height: 1.55;
  }

  .sc-chunk-block {
    padding: 0.55rem 0.65rem;
    border-radius: 8px;
    margin-bottom: 0.5rem;
    border: 1px solid transparent;
    cursor: pointer;
    transition: background 0.15s ease, border-color 0.15s ease;
  }

  .sc-chunk-block:hover {
    background: rgba(148, 163, 184, 0.12);
  }

  .sc-chunk-block.active {
    background: rgba(37, 99, 235, 0.09);
    border-color: rgba(37, 99, 235, 0.35);
  }

  .sc-chunk-heading {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-weight: 600;
    font-size: 0.78rem;
    margin-bottom: 0.3rem;
    color: #2563eb;
  }

  @media (prefers-color-scheme: dark) {
    .sc-chunk-heading {
      color: #60a5fa;
    }
  }

  .sc-segment {
    margin: 0.25rem 0;
  }

  .sc-ai-pill {
    display: inline-block;
    font-size: 0.68rem;
    font-weight: 600;
    padding: 0.1rem 0.4rem;
    border-radius: 4px;
    background: rgba(124, 58, 237, 0.14);
    color: #6d28d9;
    margin-right: 0.35rem;
    vertical-align: baseline;
  }

  @media (prefers-color-scheme: dark) {
    .sc-ai-pill {
      background: rgba(139, 92, 246, 0.25);
      color: #c4b5fd;
    }
  }

  .sc-error {
    color: #dc2626;
    font-size: 0.82rem;
    font-weight: 500;
    padding: 0.35rem 0;
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

  // Header
  const header = document.createElement("div");
  header.className = "sc-header";

  const titleGroup = document.createElement("div");
  titleGroup.className = "sc-title-group";

  const badge = document.createElement("span");
  badge.className = "sc-badge";
  badge.textContent = "Gemini 3.8 Flash TTS";

  const sectionLabel = document.createElement("span");
  sectionLabel.className = "sc-section-label";
  sectionLabel.textContent = "Loading narration...";

  titleGroup.append(badge, sectionLabel);

  const metaGroup = document.createElement("div");
  metaGroup.className = "sc-meta";
  const chunkCounter = document.createElement("span");
  chunkCounter.textContent = "0 / 0";
  metaGroup.appendChild(chunkCounter);

  header.append(titleGroup, metaGroup);

  // Controls Row
  const controlsRow = document.createElement("div");
  controlsRow.className = "sc-controls-row";

  const prevBtn = document.createElement("button");
  prevBtn.type = "button";
  prevBtn.className = "sc-btn";
  prevBtn.textContent = "Prev";
  prevBtn.title = "Previous section (PageUp)";
  prevBtn.setAttribute("aria-label", "Previous section");
  prevBtn.disabled = true;

  const playBtn = document.createElement("button");
  playBtn.type = "button";
  playBtn.className = "sc-btn sc-btn-primary";
  playBtn.textContent = "Play";
  playBtn.title = "Play or pause narration (Space)";
  playBtn.setAttribute("aria-label", "Play narration");
  playBtn.disabled = true;

  const nextBtn = document.createElement("button");
  nextBtn.type = "button";
  nextBtn.className = "sc-btn";
  nextBtn.textContent = "Next";
  nextBtn.title = "Next section (PageDown)";
  nextBtn.setAttribute("aria-label", "Next section");
  nextBtn.disabled = true;

  const progressGroup = document.createElement("div");
  progressGroup.className = "sc-progress-group";

  const curTimeEl = document.createElement("span");
  curTimeEl.className = "sc-time";
  curTimeEl.textContent = "0:00";

  const seekSlider = document.createElement("input");
  seekSlider.type = "range";
  seekSlider.className = "sc-seek";
  seekSlider.min = "0";
  seekSlider.max = "100";
  seekSlider.step = "0.1";
  seekSlider.value = "0";
  seekSlider.setAttribute("aria-label", "Seek within current section");
  seekSlider.disabled = true;

  const durTimeEl = document.createElement("span");
  durTimeEl.className = "sc-time";
  durTimeEl.textContent = "0:00";

  progressGroup.append(curTimeEl, seekSlider, durTimeEl);

  const sectionSelect = document.createElement("select");
  sectionSelect.className = "sc-select";
  sectionSelect.setAttribute("aria-label", "Jump to narrated section");
  sectionSelect.disabled = true;

  const speedSelect = document.createElement("select");
  speedSelect.className = "sc-select";
  speedSelect.setAttribute("aria-label", "Playback speed");
  for (const s of SPEEDS) {
    const opt = document.createElement("option");
    opt.value = String(s);
    opt.textContent = `${s}x`;
    if (s === 1.0) opt.selected = true;
    speedSelect.appendChild(opt);
  }

  const syncAnchorBtn = document.createElement("button");
  syncAnchorBtn.type = "button";
  syncAnchorBtn.className = "sc-btn";
  syncAnchorBtn.textContent = "Sync Scroll: On";
  syncAnchorBtn.setAttribute("aria-pressed", "true");
  syncAnchorBtn.title = "Automatically scroll page to the active narrated section anchor";

  const transcriptToggleBtn = document.createElement("button");
  transcriptToggleBtn.type = "button";
  transcriptToggleBtn.className = "sc-btn";
  transcriptToggleBtn.textContent = "Transcript";
  transcriptToggleBtn.setAttribute("aria-expanded", "false");
  transcriptToggleBtn.disabled = true;

  controlsRow.append(
    prevBtn,
    playBtn,
    nextBtn,
    progressGroup,
    sectionSelect,
    speedSelect,
    syncAnchorBtn,
    transcriptToggleBtn
  );

  const errorBanner = document.createElement("div");
  errorBanner.className = "sc-error";
  errorBanner.hidden = true;

  const transcriptPanel = document.createElement("div");
  transcriptPanel.className = "sc-transcript-panel";
  transcriptPanel.hidden = true;

  container.append(header, controlsRow, errorBanner, transcriptPanel);
  el.append(styleEl, container);

  // State & Native Audio Element
  const audio = new Audio();
  audio.preload = "metadata";

  let manifest = null;
  let transcript = null;
  let currentIndex = 0;
  let isPlaying = false;
  let autoSyncScroll = true;
  let isDestroyed = false;

  function showError(msg) {
    errorBanner.textContent = msg;
    errorBanner.hidden = false;
    sectionLabel.textContent = "Narration unavailable";
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

  function updateTranscriptHighlight() {
    const blocks = transcriptPanel.querySelectorAll(".sc-chunk-block");
    blocks.forEach((b, idx) => {
      if (idx === currentIndex) {
        b.classList.add("active");
      } else {
        b.classList.remove("active");
      }
    });
  }

  function loadChunk(index, autoplay = false, syncScroll = false) {
    if (!manifest || !manifest.chunks || index < 0 || index >= manifest.chunks.length) {
      return;
    }
    currentIndex = index;
    const chunk = manifest.chunks[currentIndex];
    const audioUrl = `${audioDirUrl}/${chunk.audio_file}`;

    audio.src = audioUrl;
    audio.playbackRate = Number(speedSelect.value) || 1.0;

    sectionLabel.textContent = chunk.section_title || `Section ${currentIndex + 1}`;
    chunkCounter.textContent = `Section ${currentIndex + 1} of ${manifest.chunks.length}`;
    sectionSelect.value = String(currentIndex);

    prevBtn.disabled = currentIndex <= 0;
    nextBtn.disabled = currentIndex >= manifest.chunks.length - 1;

    seekSlider.max = String(chunk.duration_seconds || 100);
    seekSlider.value = "0";
    curTimeEl.textContent = "0:00";
    durTimeEl.textContent = formatTime(chunk.duration_seconds || 0);

    updateTranscriptHighlight();

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
        playBtn.textContent = "Play";
        playBtn.setAttribute("aria-label", "Play narration");
        showError(`Playback blocked or failed: ${err.message || err}`);
      });
    }
  }

  function buildTranscriptDom() {
    transcriptPanel.innerHTML = "";
    if (!transcript || ! Array.isArray(transcript.chunks)) return;

    transcript.chunks.forEach((tChunk, idx) => {
      const block = document.createElement("div");
      block.className = `sc-chunk-block${idx === currentIndex ? " active" : ""}`;
      block.setAttribute("role", "button");
      block.tabIndex = 0;
      block.setAttribute(
        "aria-label",
        `Play section ${idx + 1}: ${tChunk.section_title || tChunk.section_anchor}`
      );

      const heading = document.createElement("div");
      heading.className = "sc-chunk-heading";
      const hTitle = document.createElement("span");
      hTitle.textContent = `${idx + 1}. ${tChunk.section_title || tChunk.section_anchor}`;
      const hAnchor = document.createElement("span");
      hAnchor.textContent = `#${tChunk.section_anchor}`;
      heading.append(hTitle, hAnchor);
      block.appendChild(heading);

      const segments = Array.isArray(tChunk.segments) ? tChunk.segments : [];
      if (segments.length > 0) {
        for (const seg of segments) {
          const p = document.createElement("p");
          p.className = "sc-segment";
          if (seg.is_ai_summary) {
            const pill = document.createElement("span");
            pill.className = "sc-ai-pill";
            pill.textContent = "AI Code Explanation";
            p.appendChild(pill);
          }
          const span = document.createElement("span");
          span.textContent = seg.spoken_text;
          p.appendChild(span);
          block.appendChild(p);
        }
      } else {
        const p = document.createElement("p");
        p.className = "sc-segment";
        p.textContent = tChunk.text;
        block.appendChild(p);
      }

      const activateChunk = () => {
        loadChunk(idx, true, true);
      };
      block.addEventListener("click", activateChunk);
      block.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          activateChunk();
        }
      });

      transcriptPanel.appendChild(block);
    });
  }

  // Event Listeners
  playBtn.addEventListener("click", () => {
    if (!manifest) return;
    if (audio.paused) {
      audio.play().catch((err) => showError(`Unable to start playback: ${err.message || err}`));
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

  sectionSelect.addEventListener("change", () => {
    const idx = Number(sectionSelect.value);
    if (Number.isInteger(idx)) {
      loadChunk(idx, isPlaying, true);
    }
  });

  speedSelect.addEventListener("change", () => {
    const rate = Number(speedSelect.value) || 1.0;
    audio.playbackRate = rate;
  });

  seekSlider.addEventListener("input", () => {
    const target = Number(seekSlider.value);
    if (Number.isFinite(target)) {
      curTimeEl.textContent = formatTime(target);
    }
  });

  seekSlider.addEventListener("change", () => {
    const target = Number(seekSlider.value);
    if (Number.isFinite(target)) {
      audio.currentTime = target;
    }
  });

  syncAnchorBtn.addEventListener("click", () => {
    autoSyncScroll = !autoSyncScroll;
    syncAnchorBtn.textContent = `Sync Scroll: ${autoSyncScroll ? "On" : "Off"}`;
    syncAnchorBtn.setAttribute("aria-pressed", String(autoSyncScroll));
  });

  transcriptToggleBtn.addEventListener("click", () => {
    const willShow = transcriptPanel.hidden;
    transcriptPanel.hidden = !willShow;
    transcriptToggleBtn.setAttribute("aria-expanded", String(willShow));
  });

  // Keyboard shortcuts when focus is within the player region
  container.addEventListener("keydown", (e) => {
    const tag = (e.target && e.target.tagName) || "";
    if (tag === "INPUT" || tag === "SELECT" || tag === "BUTTON") return;
    if (e.key === " ") {
      e.preventDefault();
      playBtn.click();
    } else if (e.key === "ArrowLeft") {
      e.preventDefault();
      audio.currentTime = Math.max(0, (audio.currentTime || 0) - 5);
    } else if (e.key === "ArrowRight") {
      e.preventDefault();
      audio.currentTime = Math.min(audio.duration || 0, (audio.currentTime || 0) + 5);
    } else if (e.key === "PageUp") {
      e.preventDefault();
      prevBtn.click();
    } else if (e.key === "PageDown") {
      e.preventDefault();
      nextBtn.click();
    }
  });

  audio.addEventListener("play", () => {
    isPlaying = true;
    playBtn.textContent = "Pause";
    playBtn.setAttribute("aria-label", "Pause narration");
    errorBanner.hidden = true;
  });

  audio.addEventListener("pause", () => {
    isPlaying = false;
    playBtn.textContent = "Play";
    playBtn.setAttribute("aria-label", "Play narration");
  });

  audio.addEventListener("loadedmetadata", () => {
    if (Number.isFinite(audio.duration) && audio.duration > 0) {
      seekSlider.max = String(audio.duration);
      durTimeEl.textContent = formatTime(audio.duration);
    }
  });

  audio.addEventListener("timeupdate", () => {
    curTimeEl.textContent = formatTime(audio.currentTime);
    seekSlider.value = String(audio.currentTime);
  });

  audio.addEventListener("ended", () => {
    // Continuous playback across audio chunks
    if (manifest && currentIndex < manifest.chunks.length - 1) {
      loadChunk(currentIndex + 1, true, true);
    } else {
      isPlaying = false;
      playBtn.textContent = "Play";
      playBtn.setAttribute("aria-label", "Play narration");
    }
  });

  audio.addEventListener("error", () => {
    showError("Failed to load or decode audio chunk.");
  });

  // Load static manifest.json and transcript.json
  (async () => {
    try {
      const [manifestResp, transcriptResp] = await Promise.all([
        fetch(`${audioDirUrl}/manifest.json`),
        fetch(`${audioDirUrl}/transcript.json`),
      ]);
      if (!manifestResp.ok) {
        throw new Error(`Manifest HTTP ${manifestResp.status}`);
      }
      if (!transcriptResp.ok) {
        throw new Error(`Transcript HTTP ${transcriptResp.status}`);
      }
      const [manifestData, transcriptData] = await Promise.all([
        manifestResp.json(),
        transcriptResp.json(),
      ]);
      if (isDestroyed) return;

      if (
        !manifestData ||
        manifestData.status !== "complete" ||
        !Array.isArray(manifestData.chunks) ||
        manifestData.chunks.length === 0
      ) {
        throw new Error("Invalid or incomplete audio manifest.");
      }

      manifest = manifestData;
      transcript = transcriptData;

      sectionSelect.innerHTML = "";
      manifest.chunks.forEach((ch, idx) => {
        const opt = document.createElement("option");
        opt.value = String(idx);
        opt.textContent = `${idx + 1}. ${ch.section_title || ch.section_anchor} (${formatTime(
          ch.duration_seconds
        )})`;
        sectionSelect.appendChild(opt);
      });

      playBtn.disabled = false;
      seekSlider.disabled = false;
      sectionSelect.disabled = false;
      transcriptToggleBtn.disabled = false;

      buildTranscriptDom();
      loadChunk(0, false, false);
    } catch (err) {
      if (!isDestroyed) {
        showError(`Audio narration assets unavailable (${err.message || err}).`);
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
