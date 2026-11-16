/**
 * SoftCloud Documentation Hub — Semantic Breadcrumb Navigation
 *
 * Renders and synchronizes accessible `<nav aria-label="Breadcrumbs"><ol>...</ol></nav>`
 * trails derived from the localized `myst.yml` TOC hierarchy in `#softcloud-i18n-manifest`.
 *
 * Behavior:
 * - Preserves server-rendered no-JS HTML when the rendered key matches the current route.
 * - Omitted on locale homepages (`/`, `/pl/`, `/de/`, `/es/`, `/fr/`).
 * - Synchronizes across MyST client-side SPA navigation (`pushState`, `replaceState`,
 *   `popstate`, and React DOM/attribute updates).
 */

import {
  DEFAULT_LOCALES,
  loadEmbeddedRouteManifest,
  normalizePageSlug,
  parsePathnameRoute,
  sanitizeRelativeHref,
} from "./language-switcher.mjs";

function safeInternalHref(rawHref) {
  if (typeof rawHref !== "string") return null;
  const trimmed = rawHref.trim();
  if (!trimmed.startsWith("/") || trimmed.startsWith("//")) return null;
  return sanitizeRelativeHref(trimmed);
}

/**
 * Resolve the breadcrumb trail `{ ariaLabel, key, items }` for `(localeCode, pageSlug)`
 * from `routeManifest.breadcrumbs`. Returns `null` on homepages or unknown routes.
 *
 * @param {object|null} routeManifest
 * @param {string} localeCode
 * @param {string} pageSlug
 * @returns {{ ariaLabel: string, key: string, items: Array<{ label: string, href: string|null, current: boolean }> } | null}
 */
export function resolveBreadcrumbTrail(routeManifest, localeCode, pageSlug) {
  if (!routeManifest || typeof routeManifest !== "object" || !localeCode) {
    return null;
  }

  const normSlug = normalizePageSlug(pageSlug);
  if (!normSlug) {
    return null;
  }

  const bcRoot = routeManifest.breadcrumbs;
  if (!bcRoot || typeof bcRoot !== "object") {
    return null;
  }

  const localeBc = bcRoot[localeCode];
  if (!localeBc || typeof localeBc !== "object") {
    return null;
  }

  const nodes = Array.isArray(localeBc.nodes) ? localeBc.nodes : [];
  const trails = localeBc.trails && typeof localeBc.trails === "object" ? localeBc.trails : {};
  const aliases =
    routeManifest.aliases && typeof routeManifest.aliases === "object"
      ? routeManifest.aliases
      : {};

  const aliasTarget = aliases[normSlug];
  let resolvedKey = null;
  if (Array.isArray(trails[normSlug])) {
    resolvedKey = normSlug;
  } else if (aliasTarget && Array.isArray(trails[aliasTarget])) {
    resolvedKey = aliasTarget;
  } else {
    for (const candidateKey of Object.keys(trails)) {
      if (candidateKey.endsWith(`/${normSlug}`)) {
        resolvedKey = candidateKey;
        break;
      }
    }
  }

  if (!resolvedKey) {
    return null;
  }

  const indices = trails[resolvedKey];
  if (!Array.isArray(indices) || indices.length === 0) {
    return null;
  }

  const localesMap = routeManifest.locales || DEFAULT_LOCALES;
  const localeUi = localesMap[localeCode]?.ui || DEFAULT_LOCALES[localeCode]?.ui || DEFAULT_LOCALES.en.ui;
  const ariaLabel =
    (typeof localeBc.label === "string" && localeBc.label.trim()) ||
    localeUi?.breadcrumbs_label ||
    "Breadcrumbs";

  const items = [];
  for (let i = 0; i < indices.length; i++) {
    const node = nodes[indices[i]];
    if (!node || typeof node !== "object") continue;
    const label = String(node.label || "").trim();
    if (!label) continue;
    const isCurrent = i === indices.length - 1;
    let href = node.href ? safeInternalHref(node.href) : null;
    if (isCurrent && !href) {
      const recordedRoute = routeManifest.pages?.[resolvedKey]?.translations?.[localeCode]?.route;
      href = safeInternalHref(recordedRoute || "/");
    }
    items.push({ label, href, current: isCurrent });
  }

  if (items.length === 0) {
    return null;
  }

  return {
    ariaLabel,
    key: `${localeCode}:${resolvedKey}`,
    items,
  };
}

/**
 * Create a semantic `<nav aria-label="..."><ol>...</ol></nav>` DOM tree for `trail`.
 */
export function renderBreadcrumbNav(doc, trail) {
  const nav = doc.createElement("nav");
  nav.className = "sc-breadcrumbs not-prose";
  nav.setAttribute("aria-label", trail.ariaLabel);
  nav.setAttribute("data-sc-rendered-key", trail.key);

  const list = doc.createElement("ol");
  list.className = "sc-breadcrumbs__list";

  for (const item of trail.items) {
    const li = doc.createElement("li");
    li.className = "sc-breadcrumbs__item";

    if (item.href) {
      const link = doc.createElement("a");
      link.className = "sc-breadcrumbs__link";
      link.setAttribute("href", item.href);
      if (item.current) {
        link.setAttribute("aria-current", "page");
      }
      link.textContent = item.label;
      li.appendChild(link);
    } else {
      const span = doc.createElement("span");
      span.className = "sc-breadcrumbs__label";
      span.textContent = item.label;
      li.appendChild(span);
    }

    list.appendChild(li);
  }

  nav.appendChild(list);
  return nav;
}

function clearHost(hostEl) {
  if (!hostEl) return;
  if (typeof hostEl.replaceChildren === "function") {
    hostEl.replaceChildren();
  } else {
    hostEl.textContent = "";
  }
  hostEl.hidden = true;
  hostEl.removeAttribute?.("data-sc-mounted");
}

/**
 * Mount or synchronize breadcrumbs inside `hostEl` for the active route.
 */
export function mountBreadcrumbs(hostEl, options = {}) {
  if (!hostEl || typeof document === "undefined") return () => {};
  const doc = options.document || hostEl.ownerDocument || document;
  const routeManifest = options.routeManifest || loadEmbeddedRouteManifest(doc) || null;
  const localesMap = (routeManifest && routeManifest.locales) || options.locales || DEFAULT_LOCALES;

  const explicitBaseUrl =
    options.baseUrl ??
    hostEl.getAttribute?.("data-sc-base-url") ??
    (routeManifest && typeof routeManifest.base_url === "string"
      ? routeManifest.base_url
      : typeof window !== "undefined" && typeof window.__SC_ROOT_BASE_URL__ === "string"
      ? window.__SC_ROOT_BASE_URL__
      : "");

  const hasExplicitPathname = typeof options.pathname === "string" && options.pathname.length > 0;
  const livePathname = typeof window !== "undefined" ? window.location?.pathname : undefined;
  const hasPathname = hasExplicitPathname || (typeof livePathname === "string" && livePathname.length > 0);
  const pathname = hasExplicitPathname ? options.pathname : livePathname || "/";

  const parsed = parsePathnameRoute(pathname, localesMap, explicitBaseUrl);
  const localeCode = String(
    options.locale ||
      (hasPathname ? parsed.locale : doc.documentElement?.getAttribute?.("lang")) ||
      parsed.locale ||
      "en"
  ).toLowerCase();

  const resolvedSlug = normalizePageSlug(
    options.pageSlug !== undefined
      ? options.pageSlug
      : hasPathname
      ? parsed.pageSlug
      : hostEl.getAttribute?.("data-sc-page-slug") || ""
  );

  const trail = resolveBreadcrumbTrail(routeManifest, localeCode, resolvedSlug);
  if (!trail) {
    clearHost(hostEl);
    return () => {};
  }

  const existingNav =
    typeof hostEl.querySelector === "function" ? hostEl.querySelector("nav.sc-breadcrumbs") : null;
  if (existingNav && existingNav.getAttribute?.("data-sc-rendered-key") === trail.key) {
    hostEl.hidden = false;
    hostEl.setAttribute?.("data-sc-mounted", "true");
    return () => clearHost(hostEl);
  }

  const nav = renderBreadcrumbNav(doc, trail);
  if (typeof hostEl.replaceChildren === "function") {
    hostEl.replaceChildren(nav);
  } else {
    hostEl.textContent = "";
    hostEl.appendChild(nav);
  }
  hostEl.hidden = false;
  hostEl.setAttribute?.("data-sc-mounted", "true");
  return () => clearHost(hostEl);
}

/**
 * Initialize or refresh breadcrumbs in `[data-sc-breadcrumbs]` when present.
 */
export function initSiteBreadcrumbs(options = {}) {
  const doc = options.document || (typeof document !== "undefined" ? document : null);
  if (!doc || typeof doc.querySelector !== "function") return () => {};
  const hostEl = options.hostEl || doc.querySelector("[data-sc-breadcrumbs]");
  if (!hostEl) return () => {};
  const routeManifest = options.routeManifest || loadEmbeddedRouteManifest(doc);
  return mountBreadcrumbs(hostEl, { ...options, document: doc, routeManifest });
}

/**
 * Install SPA navigation hooks so MyST client-side route transitions keep breadcrumbs updated.
 */
export function installBreadcrumbsSync(options = {}) {
  if (typeof window === "undefined" || typeof document === "undefined") return;
  if (window.__SC_BREADCRUMBS_NAV_SYNC_INSTALLED__) return;
  window.__SC_BREADCRUMBS_NAV_SYNC_INSTALLED__ = true;

  const scheduleSync = () => {
    if (typeof queueMicrotask === "function") {
      queueMicrotask(() => initSiteBreadcrumbs(options));
    } else {
      Promise.resolve().then(() => initSiteBreadcrumbs(options));
    }
  };

  window.addEventListener("popstate", scheduleSync);

  if (window.history) {
    for (const method of ["pushState", "replaceState"]) {
      const orig = window.history[method];
      if (typeof orig === "function") {
        window.history[method] = function (...args) {
          const result = orig.apply(this, args);
          scheduleSync();
          return result;
        };
      }
    }
  }

  if (typeof MutationObserver !== "undefined" && document.body) {
    const observer = new MutationObserver((mutations) => {
      for (let i = 0; i < mutations.length; i++) {
        const m = mutations[i];
        if (m.type === "attributes" && m.attributeName === "data-sc-page-slug") {
          initSiteBreadcrumbs(options);
          return;
        }
        if (m.type === "childList" && m.addedNodes.length > 0) {
          const hostEl = document.querySelector("[data-sc-breadcrumbs]");
          if (hostEl && !hostEl.querySelector("nav.sc-breadcrumbs")) {
            initSiteBreadcrumbs(options);
            return;
          }
        }
      }
    });
    observer.observe(document.body, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ["data-sc-page-slug"],
    });
  }
}

if (typeof document !== "undefined") {
  const boot = () => {
    initSiteBreadcrumbs();
    installBreadcrumbsSync();
  };
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot, { once: true });
  } else {
    boot();
  }
}

export default {
  resolveBreadcrumbTrail,
  renderBreadcrumbNav,
  mountBreadcrumbs,
  initSiteBreadcrumbs,
  installBreadcrumbsSync,
};
