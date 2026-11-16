/**
 * SoftCloud Documentation Hub — Accessible Modal Navigation Drawer Controller
 *
 * Coordinates with MyST book-theme's PrimarySidebar (.myst-primary-sidebar) and
 * TopNav menu button (.myst-top-nav-menu-button) to enforce consistent modal
 * behavior on mobile and tablet viewports while preserving the desktop sidebar:
 * - Moves focus into the drawer close button on open and restores focus to the
 *   menu toggle button on explicit dismissal (close button, backdrop, Escape).
 * - Marks background page landmarks `inert` while open in drawer mode and
 *   restores interactivity immediately on close.
 * - Dismisses on Escape, outside/backdrop clicks, navigation link clicks,
 *   SPA route transitions, and viewport resizes across desktop breakpoints.
 * - Prevents background scroll chaining in Safari/WebKit and Chromium without
 *   mutating root <html>/<body> overflow or breaking sticky positioning.
 */

export const DRAWER_LABELS = {
  en: {
    title: "Menu",
    drawer: "Navigation menu",
    close: "Close menu",
    open: "Open Menu",
  },
  pl: {
    title: "Menu",
    drawer: "Menu nawigacji",
    close: "Zamknij menu",
    open: "Otwórz menu",
  },
  de: {
    title: "Menü",
    drawer: "Navigationsmenü",
    close: "Menü schließen",
    open: "Menü öffnen",
  },
  es: {
    title: "Menú",
    drawer: "Menú de navegación",
    close: "Cerrar menú",
    open: "Abrir menú",
  },
  fr: {
    title: "Menu",
    drawer: "Menu de navigation",
    close: "Fermer le menu",
    open: "Ouvrir le menu",
  },
};

export function getNavDrawerLocale(doc = typeof document !== "undefined" ? document : null) {
  const rawLang =
    doc?.documentElement?.getAttribute?.("lang") ||
    doc?.documentElement?.getAttribute?.("data-sc-expected-lang") ||
    "en";
  const base = String(rawLang).trim().toLowerCase().split(/[-_]/)[0];
  return Object.prototype.hasOwnProperty.call(DRAWER_LABELS, base) ? base : "en";
}

export function getNavDrawerLabel(kind, doc = typeof document !== "undefined" ? document : null) {
  const locale = getNavDrawerLocale(doc);
  const pack = DRAWER_LABELS[locale] || DRAWER_LABELS.en;
  return pack[kind] || DRAWER_LABELS.en[kind] || "";
}

function getSidebar(doc) {
  return doc?.getElementById?.("myst-primary-sidebar") || doc?.querySelector?.(".myst-primary-sidebar") || null;
}

function getMenuButton(doc) {
  return doc?.querySelector?.("button.myst-top-nav-menu-button") || null;
}

function getOverlay(doc) {
  return doc?.querySelector?.(".myst-navigation-overlay") || null;
}

function getCloseButton(doc) {
  return doc?.querySelector?.(".myst-drawer-close-button") || null;
}

function hasToken(el, token) {
  if (!el) return false;
  if (el.classList && typeof el.classList.contains === "function") {
    return el.classList.contains(token);
  }
  return String(el.className || "").split(/\s+/).includes(token);
}

export function isHideTocDrawer(sidebar) {
  if (!sidebar) return false;
  if (sidebar.getAttribute?.("data-sc-hide-toc") === "true") return true;
  return hasToken(sidebar, "lg:hidden");
}

export function isDrawerViewport(sidebar, win = typeof window !== "undefined" ? window : null) {
  if (!win) return true;
  const minDesktopPx = isHideTocDrawer(sidebar) ? 1024 : 1280;
  if (typeof win.matchMedia === "function") {
    return !win.matchMedia(`(min-width: ${minDesktopPx}px)`).matches;
  }
  const width = win.innerWidth ?? win.document?.documentElement?.clientWidth ?? 1024;
  return width < minDesktopPx;
}

export function isDrawerOpen(doc = typeof document !== "undefined" ? document : null) {
  const sidebar = getSidebar(doc);
  if (!sidebar) return false;
  const attr = sidebar.getAttribute?.("data-sc-drawer-open");
  if (attr === "true") return true;
  if (attr === "false") return false;
  return !hasToken(sidebar, "hidden") && isDrawerViewport(sidebar, doc?.defaultView || (typeof window !== "undefined" ? window : null));
}

function isVisibleElement(el) {
  if (!el || !el.isConnected) return false;
  if (typeof el.getClientRects === "function" && el.getClientRects().length === 0) {
    return false;
  }
  const view = el.ownerDocument?.defaultView;
  if (view && typeof view.getComputedStyle === "function") {
    const style = view.getComputedStyle(el);
    if (style.display === "none" || style.visibility === "hidden") return false;
  }
  return true;
}

const SKIP_INERT_TAGS = new Set(["SCRIPT", "STYLE", "LINK", "META", "TEMPLATE", "NOSCRIPT", "DIALOG"]);

export function installNavDrawerController(options = {}) {
  const doc = options.document || (typeof document !== "undefined" ? document : null);
  const win = options.window || doc?.defaultView || (typeof window !== "undefined" ? window : null);
  if (!doc || !win) return () => {};

  if (win.__SC_NAV_DRAWER_CLEANUP__) {
    win.__SC_NAV_DRAWER_CLEANUP__();
  }

  const inertedElements = new Set();
  let observer = null;
  let wasOpen = false;
  let isSyncing = false;
  let lastDismissReason = null;
  let pendingOpenBeforeHydration = false;
  let lastPathname = win.location?.pathname || "/";
  let lastHash = win.location?.hash || "";
  let lastTouchY = null;
  let boundOverlayEl = null;
  let boundSidebarEl = null;

  function applyBackgroundInert(sidebar) {
    const body = doc.body;
    if (!body || !body.children) return;
    for (const child of Array.from(body.children)) {
      if (!child || child === sidebar) continue;
      if (hasToken(child, "myst-navigation-overlay")) continue;
      if (SKIP_INERT_TAGS.has(child.tagName)) continue;
      if (child.hasAttribute?.("data-sc-inert-ignore")) continue;
      if (child.inert) continue;
      child.inert = true;
      inertedElements.add(child);
    }
  }

  function clearBackgroundInert() {
    for (const el of inertedElements) {
      try {
        el.inert = false;
        el.removeAttribute?.("inert");
      } catch (_err) {
        // Ignore disconnected/non-standard mock nodes
      }
    }
    inertedElements.clear();
  }

  function setAttrIfChanged(el, name, value) {
    if (!el || el.getAttribute?.(name) === value) return;
    el.setAttribute(name, value);
  }

  function syncLabels() {
    const menuBtn = getMenuButton(doc);
    if (menuBtn) {
      const openLabel = getNavDrawerLabel("open", doc);
      const sr = menuBtn.querySelector?.(".sr-only");
      if (sr && sr.textContent !== openLabel) {
        sr.textContent = openLabel;
      }
    }
    const sidebar = getSidebar(doc);
    if (sidebar && isDrawerOpen(doc)) {
      setAttrIfChanged(sidebar, "aria-label", getNavDrawerLabel("drawer", doc));
      const titleEl = sidebar.querySelector?.(".myst-primary-sidebar-title");
      const titleLabel = getNavDrawerLabel("title", doc);
      if (titleEl && titleEl.textContent !== titleLabel) {
        titleEl.textContent = titleLabel;
      }
      const closeBtn = getCloseButton(doc);
      if (closeBtn) {
        const closeLabel = getNavDrawerLabel("close", doc);
        setAttrIfChanged(closeBtn, "aria-label", closeLabel);
        setAttrIfChanged(closeBtn, "title", closeLabel);
      }
    }
  }

  function setFallbackDomState(open) {
    const sidebar = getSidebar(doc);
    const menuBtn = getMenuButton(doc);
    if (!sidebar) return;

    sidebar.setAttribute("data-sc-drawer-open", open ? "true" : "false");
    if (open) {
      sidebar.classList?.remove("hidden");
      sidebar.setAttribute("role", "dialog");
      sidebar.setAttribute("aria-modal", "true");
      sidebar.setAttribute("aria-label", getNavDrawerLabel("drawer", doc));
      sidebar.setAttribute("tabindex", "-1");
      if (menuBtn) menuBtn.setAttribute("aria-expanded", "true");

      const pointer = sidebar.querySelector?.(".myst-primary-sidebar-pointer");
      pointer?.classList?.add("flex", "bg-myst-bg");
      if (pointer && !pointer.querySelector?.(".myst-primary-sidebar-header")) {
        const header = doc.createElement("div");
        header.className = "myst-primary-sidebar-header flex items-center justify-between px-4 py-3 border-b border-myst-border shrink-0 xl:hidden";
        const title = doc.createElement("span");
        title.className = "myst-primary-sidebar-title text-sm font-semibold text-myst-text";
        title.textContent = getNavDrawerLabel("title", doc);
        const closeBtn = doc.createElement("button");
        closeBtn.type = "button";
        closeBtn.className = "myst-drawer-close-button flex items-center justify-center w-10 h-10 rounded-lg text-myst-text-secondary hover:text-myst-text hover:bg-myst-surface focus-visible:outline outline-myst-focus-outline outline-2";
        const closeLabel = getNavDrawerLabel("close", doc);
        closeBtn.setAttribute("aria-label", closeLabel);
        closeBtn.setAttribute("title", closeLabel);
        closeBtn.innerHTML =
          '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" width="1.25rem" height="1.25rem"><path d="M6 6L18 18M18 6L6 18"></path></svg>';
        closeBtn.addEventListener("click", () => dismissDrawer("close-button"));
        header.append(title, closeBtn);
        pointer.insertBefore(header, pointer.firstChild);
      }

      if (!getOverlay(doc) && sidebar.parentElement) {
        const overlay = doc.createElement("div");
        overlay.className = "myst-navigation-overlay fixed inset-0 max-xl:z-40 xl:z-30 bg-black opacity-50 max-xl:!mt-0";
        overlay.setAttribute("aria-hidden", "true");
        overlay.setAttribute("data-sc-fallback-overlay", "1");
        overlay.addEventListener("click", () => dismissDrawer("backdrop"));
        sidebar.parentElement.insertBefore(overlay, sidebar);
      }
    } else {
      sidebar.classList?.add("hidden");
      sidebar.removeAttribute("role");
      sidebar.removeAttribute("aria-modal");
      sidebar.removeAttribute("aria-label");
      sidebar.removeAttribute("tabindex");
      if (menuBtn) menuBtn.setAttribute("aria-expanded", "false");
      const fallbackOverlay = doc.querySelector?.('[data-sc-fallback-overlay="1"]');
      fallbackOverlay?.remove?.();
    }
  }

  function focusDrawerEntry(sidebar) {
    const target =
      getCloseButton(doc) ||
      sidebar?.querySelector?.('a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])') ||
      sidebar;
    if (!target || typeof target.focus !== "function") return;
    if (sidebar && doc.activeElement && sidebar.contains?.(doc.activeElement)) return;
    target.focus({ preventScroll: true });
    if (typeof win.requestAnimationFrame === "function" && doc.activeElement !== target) {
      win.requestAnimationFrame(() => {
        if (isDrawerOpen(doc) && target.isConnected && doc.activeElement !== target) {
          target.focus({ preventScroll: true });
        }
      });
    }
  }

  function restoreTriggerFocus() {
    const menuBtn = getMenuButton(doc);
    if (!menuBtn || typeof menuBtn.focus !== "function") return;
    if (!isVisibleElement(menuBtn)) return;
    menuBtn.focus({ preventScroll: true });
  }

  function onOverlayBlockScroll(event) {
    if (event.cancelable !== false) {
      event.preventDefault();
    }
  }

  function getDrawerScrollNav(sidebar) {
    return sidebar?.querySelector?.(".myst-primary-sidebar-nav") || sidebar;
  }

  function onSidebarTouchStart(event) {
    lastTouchY = event.touches?.[0]?.clientY ?? null;
  }

  function shouldContainWheelOrTouch(navEl, deltaY) {
    if (!navEl) return true;
    const maxScroll = (navEl.scrollHeight || 0) - (navEl.clientHeight || 0);
    if (maxScroll <= 1) return true;
    const top = navEl.scrollTop || 0;
    if (deltaY < 0 && top <= 0) return true;
    if (deltaY > 0 && top >= maxScroll - 1) return true;
    return false;
  }

  function onSidebarWheel(event) {
    const sidebar = getSidebar(doc);
    if (!sidebar || !isDrawerOpen(doc)) return;
    const navEl = getDrawerScrollNav(sidebar);
    if (shouldContainWheelOrTouch(navEl, event.deltaY || 0) && event.cancelable !== false) {
      event.preventDefault();
    }
  }

  function onSidebarTouchMove(event) {
    const sidebar = getSidebar(doc);
    if (!sidebar || !isDrawerOpen(doc)) return;
    const navEl = getDrawerScrollNav(sidebar);
    const currentY = event.touches?.[0]?.clientY ?? null;
    const deltaY = lastTouchY !== null && currentY !== null ? lastTouchY - currentY : 0;
    lastTouchY = currentY;
    if (shouldContainWheelOrTouch(navEl, deltaY) && event.cancelable !== false) {
      event.preventDefault();
    }
  }

  function attachScrollContainment(sidebar) {
    const overlay = getOverlay(doc);
    if (overlay !== boundOverlayEl) {
      detachOverlayScrollContainment();
      if (overlay) {
        overlay.addEventListener("wheel", onOverlayBlockScroll, { passive: false });
        overlay.addEventListener("touchmove", onOverlayBlockScroll, { passive: false });
        boundOverlayEl = overlay;
      }
    }
    if (sidebar && sidebar !== boundSidebarEl) {
      detachSidebarScrollContainment();
      sidebar.addEventListener("wheel", onSidebarWheel, { passive: false });
      sidebar.addEventListener("touchstart", onSidebarTouchStart, { passive: true });
      sidebar.addEventListener("touchmove", onSidebarTouchMove, { passive: false });
      boundSidebarEl = sidebar;
    }
  }

  function detachOverlayScrollContainment() {
    if (!boundOverlayEl) return;
    boundOverlayEl.removeEventListener("wheel", onOverlayBlockScroll);
    boundOverlayEl.removeEventListener("touchmove", onOverlayBlockScroll);
    boundOverlayEl = null;
  }

  function detachSidebarScrollContainment() {
    if (!boundSidebarEl) return;
    boundSidebarEl.removeEventListener("wheel", onSidebarWheel);
    boundSidebarEl.removeEventListener("touchstart", onSidebarTouchStart);
    boundSidebarEl.removeEventListener("touchmove", onSidebarTouchMove);
    boundSidebarEl = null;
    lastTouchY = null;
  }

  function detachScrollContainment() {
    detachOverlayScrollContainment();
    detachSidebarScrollContainment();
  }

  function dismissDrawer(reason = "programmatic") {
    lastDismissReason = reason;
    clearBackgroundInert();
    detachScrollContainment();

    if (typeof win.__scSetNavDrawerOpen === "function") {
      win.__scSetNavDrawerOpen(false);
    } else {
      setFallbackDomState(false);
      syncDrawerState();
    }
  }

  function openDrawer() {
    const sidebar = getSidebar(doc);
    if (sidebar && !isDrawerViewport(sidebar, win)) return;

    if (typeof win.__scSetNavDrawerOpen === "function") {
      win.__scSetNavDrawerOpen(true);
    } else if (win.__remixManifest) {
      pendingOpenBeforeHydration = true;
    } else {
      setFallbackDomState(true);
      syncDrawerState();
    }
  }

  function syncDrawerState() {
    if (isSyncing) return;
    isSyncing = true;
    try {
      const sidebar = getSidebar(doc);
      if (!sidebar) {
        if (wasOpen) {
          wasOpen = false;
          clearBackgroundInert();
          detachScrollContainment();
        }
        return;
      }

      if (pendingOpenBeforeHydration && typeof win.__scSetNavDrawerOpen === "function") {
        pendingOpenBeforeHydration = false;
        if (isDrawerViewport(sidebar, win)) {
          win.__scSetNavDrawerOpen(true);
        }
        return;
      }

      const open = isDrawerOpen(doc);
      if (open && !isDrawerViewport(sidebar, win)) {
        dismissDrawer("breakpoint");
        return;
      }

      syncLabels();

      if (open) {
        applyBackgroundInert(sidebar);
        attachScrollContainment(sidebar);
        if (!wasOpen) {
          wasOpen = true;
          lastDismissReason = null;
          focusDrawerEntry(sidebar);
        }
      } else if (wasOpen) {
        wasOpen = false;
        clearBackgroundInert();
        detachScrollContainment();
        const reason = lastDismissReason;
        lastDismissReason = null;
        if (reason !== "navigation" && reason !== "breakpoint") {
          restoreTriggerFocus();
        }
      }
    } finally {
      observer?.takeRecords?.();
      isSyncing = false;
    }
  }

  function onReactDrawerState() {
    syncDrawerState();
  }

  function onDocumentKeyDown(event) {
    if (event.key === "Escape" && isDrawerOpen(doc)) {
      event.preventDefault();
      if (typeof event.stopPropagation === "function") {
        event.stopPropagation();
      }
      dismissDrawer("escape");
    }
  }

  function onDocumentClick(event) {
    const sidebar = getSidebar(doc);
    const menuBtn = getMenuButton(doc);

    if (!isDrawerOpen(doc)) {
      if (menuBtn && (event.target === menuBtn || menuBtn.contains?.(event.target))) {
        if (typeof win.__scSetNavDrawerOpen !== "function") {
          openDrawer();
        }
      }
      return;
    }

    if (sidebar && sidebar.contains?.(event.target)) {
      const link = event.target?.closest?.("a[href]");
      if (link) {
        lastDismissReason = "navigation";
        if (typeof win.__scSetNavDrawerOpen !== "function") {
          dismissDrawer("navigation");
        }
      }
      return;
    }

    if (menuBtn && (event.target === menuBtn || menuBtn.contains?.(event.target))) {
      return;
    }

    if (!hasToken(event.target, "myst-navigation-overlay")) {
      event.preventDefault?.();
      event.stopPropagation?.();
    }
    dismissDrawer("backdrop");
  }

  function onRouteChange() {
    const nextPath = win.location?.pathname || "/";
    const nextHash = win.location?.hash || "";
    if (nextPath !== lastPathname || nextHash !== lastHash) {
      lastPathname = nextPath;
      lastHash = nextHash;
      if (isDrawerOpen(doc)) {
        dismissDrawer("navigation");
      }
    }
  }

  function onBreakpointOrResize() {
    const sidebar = getSidebar(doc);
    if (isDrawerOpen(doc) && sidebar && !isDrawerViewport(sidebar, win)) {
      dismissDrawer("breakpoint");
    }
  }

  win.__scGetNavDrawerLabel = (kind) => getNavDrawerLabel(kind, doc);
  win.__scNavDrawerDismiss = (reason) => dismissDrawer(reason);

  win.addEventListener("sc:nav-drawer-state", onReactDrawerState);
  doc.addEventListener("keydown", onDocumentKeyDown, true);
  doc.addEventListener("click", onDocumentClick, true);
  win.addEventListener("popstate", onRouteChange);
  win.addEventListener("hashchange", onRouteChange);
  win.addEventListener("resize", onBreakpointOrResize);

  const mqLg = typeof win.matchMedia === "function" ? win.matchMedia("(min-width: 1024px)") : null;
  const mqXl = typeof win.matchMedia === "function" ? win.matchMedia("(min-width: 1280px)") : null;
  mqLg?.addEventListener?.("change", onBreakpointOrResize);
  mqXl?.addEventListener?.("change", onBreakpointOrResize);

  let origPushState = null;
  let origReplaceState = null;
  if (win.history && !win.history.__scNavDrawerHooked) {
    win.history.__scNavDrawerHooked = true;
    origPushState = win.history.pushState;
    origReplaceState = win.history.replaceState;
    if (typeof origPushState === "function") {
      win.history.pushState = function (...args) {
        const result = origPushState.apply(this, args);
        onRouteChange();
        return result;
      };
    }
    if (typeof origReplaceState === "function") {
      win.history.replaceState = function (...args) {
        const result = origReplaceState.apply(this, args);
        onRouteChange();
        return result;
      };
    }
  }

  if (typeof MutationObserver !== "undefined" && doc.documentElement) {
    observer = new MutationObserver((mutations) => {
      let shouldSync = false;
      for (const m of mutations) {
        if (m.target === doc.documentElement && m.attributeName === "lang") {
          shouldSync = true;
          break;
        }
        if (
          m.target?.id === "myst-primary-sidebar" ||
          hasToken(m.target, "myst-primary-sidebar") ||
          m.type === "childList"
        ) {
          shouldSync = true;
          break;
        }
      }
      if (shouldSync) {
        syncDrawerState();
      }
    });
    observer.observe(doc.documentElement, {
      attributes: true,
      attributeFilter: ["lang", "class", "data-sc-drawer-open"],
      childList: true,
      subtree: true,
    });
  }

  syncDrawerState();

  const cleanup = () => {
    clearBackgroundInert();
    detachScrollContainment();
    win.removeEventListener("sc:nav-drawer-state", onReactDrawerState);
    doc.removeEventListener("keydown", onDocumentKeyDown, true);
    doc.removeEventListener("click", onDocumentClick, true);
    win.removeEventListener("popstate", onRouteChange);
    win.removeEventListener("hashchange", onRouteChange);
    win.removeEventListener("resize", onBreakpointOrResize);
    mqLg?.removeEventListener?.("change", onBreakpointOrResize);
    mqXl?.removeEventListener?.("change", onBreakpointOrResize);
    observer?.disconnect?.();
    if (win.__SC_NAV_DRAWER_CLEANUP__ === cleanup) {
      delete win.__SC_NAV_DRAWER_CLEANUP__;
    }
  };

  win.__SC_NAV_DRAWER_CLEANUP__ = cleanup;
  return cleanup;
}

export function initNavDrawer(options = {}) {
  return installNavDrawerController(options);
}

export default {
  DRAWER_LABELS,
  getNavDrawerLocale,
  getNavDrawerLabel,
  isHideTocDrawer,
  isDrawerViewport,
  isDrawerOpen,
  installNavDrawerController,
  initNavDrawer,
};
