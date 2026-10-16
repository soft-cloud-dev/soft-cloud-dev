/**
 * assets/static/softcloud-theme.js
 * Synchronizes MyST book-theme dark/light mode with Web Awesome theme classes,
 * and manages client-side Web Awesome placeholder transformation.
 */

(function () {
  'use strict';

  // 1. Theme Synchronization
  let isUpdating = false;

  function syncTheme() {
    if (isUpdating) return;
    isUpdating = true;
    try {
      const root = document.documentElement;
      const isDark =
        root.classList.contains('dark') ||
        (!root.classList.contains('light') &&
          window.matchMedia &&
          window.matchMedia('(prefers-color-scheme: dark)').matches);

      const targetTheme = isDark ? 'dark' : 'light';
      const targetWaClass = isDark ? 'wa-theme-dark' : 'wa-theme-light';
      const removeWaClass = isDark ? 'wa-theme-light' : 'wa-theme-dark';

      if (root.getAttribute('data-theme') !== targetTheme) {
        root.setAttribute('data-theme', targetTheme);
      }
      if (!root.classList.contains(targetWaClass)) {
        root.classList.add(targetWaClass);
      }
      if (root.classList.contains(removeWaClass)) {
        root.classList.remove(removeWaClass);
      }
    } finally {
      isUpdating = false;
    }
  }

  // 2. Client-side Web Awesome placeholder transform
  function transformHosts(container) {
    const root = container || document;
    const hosts = root.querySelectorAll ? root.querySelectorAll('.sc-wa-host') : [];
    if (!hosts || hosts.length === 0) return;

    hosts.forEach(function (host) {
      // Find metadata child
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
      el.setAttribute('did-ssr', '');

      // Copy attributes
      const excludeKeys = new Set([
        'schema_version',
        'component',
        'title',
        'header',
        'footer',
        'image',
        'image_alt',
        'icon',
      ]);

      for (const [k, v] of Object.entries(meta)) {
        if (excludeKeys.has(k)) continue;
        if (typeof v === 'boolean') {
          if (v) el.setAttribute(k, '');
        } else if (v !== undefined && v !== null) {
          el.setAttribute(k === 'caret' ? 'with-caret' : k, String(v));
        }
      }

      // Web Awesome 3.14 callouts accept icon content in the icon slot.
      // Titles are placed in the default slot, not a nonexistent title slot.
      if (tag === 'wa-callout') {
        if (meta.icon) {
          const icon = document.createElement('wa-icon');
          icon.slot = 'icon';
          icon.name = meta.icon;
          el.appendChild(icon);
        }
        if (meta.title) {
          const heading = document.createElement('strong');
          heading.className = 'sc-wa-callout-title';
          heading.textContent = meta.title;
          el.appendChild(heading);
        }
      }

      // Slot handling for card
      if (tag === 'wa-card') {
        if (meta.image) {
          const img = document.createElement('img');
          img.slot = 'media';
          img.src = meta.image;
          img.alt = meta.image_alt || '';
          el.appendChild(img);
        }
        if (meta.header) {
          const hdr = document.createElement('div');
          hdr.slot = 'header';
          hdr.textContent = meta.header;
          el.appendChild(hdr);
        }
      }

      // Remove meta element and transfer light DOM children
      metaEl.remove();
      while (host.firstChild) {
        el.appendChild(host.firstChild);
      }

      // Slot handling for card footer (if placed after body)
      if (tag === 'wa-card' && meta.footer) {
        const ftr = document.createElement('div');
        ftr.slot = 'footer';
        ftr.textContent = meta.footer;
        el.appendChild(ftr);
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

  // Observe theme class changes & dynamic DOM mutations (e.g. client navigation/hydration)
  const observer = new MutationObserver(function (mutations) {
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
          if (node.nodeType === 1) { // Node.ELEMENT_NODE
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

  // Listen to system preference changes
  if (window.matchMedia) {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', syncTheme);
  }

  // Public SoftCloudTheme API
  window.SoftCloudTheme = {
    getTheme: function () {
      const root = document.documentElement;
      return root.classList.contains('wa-theme-dark') || root.classList.contains('dark') ? 'dark' : 'light';
    },
    setTheme: function (theme) {
      const root = document.documentElement;
      if (theme === 'dark') {
        root.classList.add('dark');
        root.classList.remove('light');
        try {
          localStorage.setItem('softcloud-theme', 'dark');
          localStorage.setItem('myst:theme', 'dark');
        } catch (e) {}
        syncTheme();
      } else if (theme === 'light') {
        root.classList.add('light');
        root.classList.remove('dark');
        try {
          localStorage.setItem('softcloud-theme', 'light');
          localStorage.setItem('myst:theme', 'light');
        } catch (e) {}
        syncTheme();
      } else if (theme === 'auto') {
        root.classList.remove('dark', 'light');
        root.removeAttribute('data-theme');
        try {
          localStorage.setItem('softcloud-theme', 'auto');
          localStorage.removeItem('myst:theme');
        } catch (e) {}
        syncTheme();
      }
    },
    syncTheme: syncTheme,
    transformHosts: transformHosts,
  };
})();
