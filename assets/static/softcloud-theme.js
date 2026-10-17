/**
 * assets/static/softcloud-theme.js
 * Synchronizes MyST book-theme dark/light mode with Web Awesome theme classes (wa-dark / wa-light),
 * and manages client-side Web Awesome placeholder transformation conforming to Web Awesome 3.14.0.
 */

(function () {
  'use strict';

  // 1. Theme Synchronization (WA-005, WA-THEME-001)
  let isUpdating = false;

  function syncTheme(force = false) {
    if (isUpdating && force !== true) return;
    isUpdating = true;
    try {
      const root = document.documentElement;
      const storedTheme = (() => {
        try {
          return localStorage.getItem('softcloud-theme') || localStorage.getItem('myst:theme');
        } catch (e) {
          return null;
        }
      })();

      let isDark;
      if (storedTheme === 'dark') {
        isDark = true;
      } else if (storedTheme === 'light') {
        isDark = false;
      } else if (root.classList.contains('dark')) {
        isDark = true;
      } else if (root.classList.contains('light')) {
        isDark = false;
      } else if (root.getAttribute('data-theme') === 'dark') {
        isDark = true;
      } else if (root.getAttribute('data-theme') === 'light') {
        isDark = false;
      } else {
        isDark = Boolean(window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches);
      }

      const targetTheme = isDark ? 'dark' : 'light';
      const targetWaClass = isDark ? 'wa-dark' : 'wa-light';
      const removeWaClass = isDark ? 'wa-light' : 'wa-dark';
      const removeTheme = isDark ? 'light' : 'dark';

      const currentTheme = root.getAttribute('data-theme');
      const hasTargetTheme = root.classList.contains(targetTheme);
      const hasRemoveTheme = root.classList.contains(removeTheme);
      const hasTargetWa = root.classList.contains(targetWaClass);
      const hasRemoveWa = root.classList.contains(removeWaClass);
      const hasLegacyDark = root.classList.contains('wa-theme-dark');
      const hasLegacyLight = root.classList.contains('wa-theme-light');

      if (
        currentTheme === targetTheme &&
        hasTargetTheme &&
        !hasRemoveTheme &&
        hasTargetWa &&
        !hasRemoveWa &&
        !hasLegacyDark &&
        !hasLegacyLight
      ) {
        return;
      }

      if (currentTheme !== targetTheme) {
        root.setAttribute('data-theme', targetTheme);
      }
      if (!hasTargetTheme) {
        root.classList.add(targetTheme);
      }
      if (hasRemoveTheme) {
        root.classList.remove(removeTheme);
      }
      if (!hasTargetWa) {
        root.classList.add(targetWaClass);
      }
      if (hasRemoveWa) {
        root.classList.remove(removeWaClass);
      }
      if (hasLegacyDark) root.classList.remove('wa-theme-dark');
      if (hasLegacyLight) root.classList.remove('wa-theme-light');
    } finally {
      setTimeout(function () {
        isUpdating = false;
      }, 0);
    }
  }

  // 2. Client-side Web Awesome placeholder transform (WA-002, WA-003, WA-007)
  function transformHosts(container) {
    const root = container || document;
    const hosts = root.querySelectorAll ? root.querySelectorAll('.sc-wa-host') : [];
    if (!hosts || hosts.length === 0) return;

    hosts.forEach(function (host) {
      const metaEl = host.querySelector(':scope > .sc-wa-meta');
      if (!metaEl) return;

      let meta;
      try {
        meta = JSON.parse(metaEl.textContent || '{}');
      } catch (err) {
        console.warn('[SoftCloud] Failed to parse component metadata:', err);
        return;
      }

      const tag = meta.component;
      if (!tag) return;

      const el = document.createElement(tag);
      // NOTE: Do NOT set did-ssr here: dynamic client elements are not server-rendered (WA-007)

      // Normalize legacy parameters
      let appearance = meta.appearance;
      let variant = meta.variant;
      let extraClass = meta.class || '';

      if (tag === 'wa-card') {
        if (appearance === 'default') appearance = 'outlined';
        else if (appearance === 'elevated') {
          appearance = 'filled-outlined';
          extraClass = extraClass ? extraClass + ' sc-elevation' : 'sc-elevation';
        } else if (appearance === 'flat') appearance = 'plain';
      } else if (tag === 'wa-callout') {
        if (appearance === 'soft') appearance = 'filled-outlined';
        else if (appearance === 'solid') appearance = 'filled';
        else if (appearance === 'outline') appearance = 'outlined';
        else if (appearance === 'default') appearance = 'outlined';
      } else if (tag === 'wa-button') {
        if (variant === 'primary') variant = 'brand';
        else if (variant === 'default') variant = 'neutral';
        if (appearance === 'text' || appearance === 'flat') appearance = 'plain';
        if (meta.outline) appearance = 'outlined';
        if (meta.circle) extraClass = extraClass ? extraClass + ' sc-button-circle' : 'sc-button-circle';
        if (meta.caret || meta['with-caret']) el.setAttribute('with-caret', '');
        if (meta.size) {
          const sMap = { small: 's', medium: 'm', large: 'l' };
          const normSize = sMap[String(meta.size).toLowerCase()] || meta.size;
          el.setAttribute('size', normSize);
        }
      } else if (tag === 'wa-icon') {
        let family = meta.family || 'classic';
        let iconVariant = meta.variant || 'solid';
        let name = meta.name;
        if (meta.style === 'brands' || family === 'brands') {
          family = 'brands';
          iconVariant = null;
        } else if (meta.style === 'regular' || iconVariant === 'regular') {
          iconVariant = 'regular';
        }
        if (name === 'info-circle' || name === 'info') name = 'circle-info';
        el.setAttribute('name', name);
        el.setAttribute('family', family);
        if (iconVariant) el.setAttribute('variant', iconVariant);
      }

      if (variant && tag !== 'wa-icon') el.setAttribute('variant', variant);
      if (appearance && tag !== 'wa-icon') el.setAttribute('appearance', appearance);
      if (extraClass) el.setAttribute('class', extraClass.trim());

      // Copy other standard attributes
      const excludeKeys = new Set([
        'schema_version',
        'component',
        'title',
        'header',
        'footer',
        'image',
        'image_alt',
        'icon',
        'variant',
        'appearance',
        'class',
        'caret',
        'with-caret',
        'outline',
        'circle',
        'size',
        'style',
        'family',
        'library',
        'name',
      ]);

      for (const [k, v] of Object.entries(meta)) {
        if (excludeKeys.has(k)) continue;
        if (typeof v === 'boolean') {
          if (v) el.setAttribute(k, '');
        } else if (v !== undefined && v !== null) {
          el.setAttribute(k, String(v));
        }
      }

      // Slot handling for callout (WA-002)
      if (tag === 'wa-callout') {
        if (meta.icon) {
          let iconName = meta.icon;
          if (iconName === 'info' || iconName === 'info-circle') iconName = 'circle-info';
          const iconEl = document.createElement('wa-icon');
          iconEl.setAttribute('slot', 'icon');
          iconEl.setAttribute('name', iconName);
          iconEl.setAttribute('family', 'classic');
          iconEl.setAttribute('variant', 'solid');
          iconEl.setAttribute('aria-hidden', 'true');
          el.appendChild(iconEl);
        }

        const contentDiv = document.createElement('div');
        contentDiv.className = 'sc-wa-callout-content';
        if (meta.title) {
          const titleStrong = document.createElement('strong');
          titleStrong.className = 'sc-wa-callout-title';
          titleStrong.textContent = meta.title;
          contentDiv.appendChild(titleStrong);
        }

        metaEl.remove();
        while (host.firstChild) {
          contentDiv.appendChild(host.firstChild);
        }
        el.appendChild(contentDiv);
        host.replaceWith(el);
        return;
      }

      // Slot handling for card (WA-004)
      if (tag === 'wa-card') {
        if (meta.image) {
          const img = document.createElement('img');
          img.slot = 'media';
          img.src = meta.image;
          img.alt = meta.image_alt || '';
          el.appendChild(img);
          el.setAttribute('with-media', '');
        }
        if (meta.header) {
          const hdr = document.createElement('div');
          hdr.slot = 'header';
          hdr.textContent = meta.header;
          el.appendChild(hdr);
          el.setAttribute('with-header', '');
        }
      }

      // Transfer light DOM children
      metaEl.remove();
      while (host.firstChild) {
        el.appendChild(host.firstChild);
      }

      // Slot handling for card footer
      if (tag === 'wa-card' && meta.footer) {
        const ftr = document.createElement('div');
        ftr.slot = 'footer';
        ftr.textContent = meta.footer;
        el.appendChild(ftr);
        el.setAttribute('with-footer', '');
      }

      host.replaceWith(el);
    });
  }

  // Initial setup
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      syncTheme();
      transformHosts(document);
    });
  } else {
    syncTheme();
    transformHosts(document);
  }

  // Observe theme class changes & dynamic DOM mutations
  const observer = new MutationObserver(function (mutations) {
    if (isUpdating) return;
    let themeChanged = false;
    let needsTransform = false;

    for (let i = 0; i < mutations.length; i++) {
      const m = mutations[i];
      if (m.type === 'attributes' && m.attributeName === 'class' && m.target === document.documentElement) {
        themeChanged = true;
      }
      if (m.type === 'childList' && m.addedNodes.length > 0) {
        for (let j = 0; j < m.addedNodes.length; j++) {
          const node = m.addedNodes[j];
          if (node.nodeType === 1) {
            if (node.classList && node.classList.contains('sc-wa-host')) {
              needsTransform = true;
              break;
            }
            if (node.querySelector && node.querySelector('.sc-wa-host')) {
              needsTransform = true;
              break;
            }
          }
        }
      }
    }

    if (themeChanged) {
      syncTheme();
    }
    if (needsTransform) {
      transformHosts(document);
    }
  });

  observer.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ['class', 'data-theme'],
    childList: true,
    subtree: true,
  });

  if (window.matchMedia) {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', syncTheme);
  }

  // Public SoftCloudTheme API
  window.SoftCloudTheme = {
    getTheme: function () {
      const root = document.documentElement;
      return root.classList.contains('wa-dark') || root.classList.contains('dark') ? 'dark' : 'light';
    },
    setTheme: function (theme) {
      const root = document.documentElement;
      if (theme === 'dark') {
        try {
          localStorage.setItem('softcloud-theme', 'dark');
          localStorage.setItem('myst:theme', 'dark');
        } catch (e) {}
        root.classList.add('dark');
        root.classList.remove('light', 'wa-light');
        syncTheme(true);
      } else if (theme === 'light') {
        try {
          localStorage.setItem('softcloud-theme', 'light');
          localStorage.setItem('myst:theme', 'light');
        } catch (e) {}
        root.classList.add('light');
        root.classList.remove('dark', 'wa-dark');
        syncTheme(true);
      } else if (theme === 'auto') {
        try {
          localStorage.setItem('softcloud-theme', 'auto');
          localStorage.removeItem('myst:theme');
        } catch (e) {}
        root.classList.remove('dark', 'light', 'wa-dark', 'wa-light');
        root.removeAttribute('data-theme');
        syncTheme(true);
      }
    },
    syncTheme: syncTheme,
    transformHosts: transformHosts,
  };
})();
