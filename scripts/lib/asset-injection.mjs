/**
 * scripts/lib/asset-injection.mjs
 * Injects required stylesheets and scripts into parsed HTML documents exactly once,
 * respecting BASE_URL prefixes and initialization invariants (WA-ICON-003, WA-THEME-001).
 */

import { createElement, setAttr, getAttr } from './parse5-tree.mjs';

/**
 * Normalizes base URL to ensure no trailing slash.
 * @param {string} baseUrl
 * @returns {string}
 */
export function normalizeBaseUrl(baseUrl = '') {
  if (!baseUrl) return '';
  const trimmed = baseUrl.trim();
  if (trimmed === '/' || trimmed === '') return '';
  return '/' + trimmed.replace(/^\/+|\/+$/g, '');
}

/**
 * Injects Web Awesome runtime stylesheets and scripts into an HTML document AST.
 * @param {object} ast - parse5 document AST.
 * @param {string} rawBaseUrl - Outer base URL (e.g. '' or '/docs').
 * @returns {{ injectedStylesheets: string[], injectedScripts: string[] }}
 */
export function injectRuntimeAssets(ast, rawBaseUrl = '') {
  const baseUrl = normalizeBaseUrl(rawBaseUrl);

  // Locate <head> and <body>
  let head = null;
  let body = null;

  function findHeadAndBody(node) {
    if (node.tagName === 'head') head = node;
    if (node.tagName === 'body') body = node;
    if (head && body) return;
    for (const child of node.childNodes || []) {
      findHeadAndBody(child);
      if (head && body) return;
    }
  }

  findHeadAndBody(ast);

  if (!head) {
    throw new Error('Cannot inject assets: <head> element not found in document');
  }

  const existingLinks = (head.childNodes || [])
    .filter((n) => n.tagName === 'link' && getAttr(n, 'rel') === 'stylesheet')
    .map((n) => getAttr(n, 'href') || '');

  const existingScripts = [];
  function collectScripts(node) {
    if (node.tagName === 'script') {
      existingScripts.push(getAttr(node, 'src') || '');
    }
    for (const child of node.childNodes || []) {
      collectScripts(child);
    }
  }
  collectScripts(ast);

  const injectedStylesheets = [];
  const injectedScripts = [];

  // 1. Early theme initialization script (runs synchronously in <head> before paint)
  const themeInitSrc = `${baseUrl}/static/softcloud-theme-init.js`;
  const themeInitPresent = existingScripts.some((s) => s.endsWith('softcloud-theme-init.js'));
  if (!themeInitPresent) {
    const script = createElement('script');
    setAttr(script, 'src', themeInitSrc);
    head.childNodes.unshift(script);
    script.parentNode = head;
    injectedScripts.push(themeInitSrc);
  }

  // 2. Required stylesheets
  const requiredStyles = [
    `${baseUrl}/vendor/fontawesome/css/all.min.css`,
    `${baseUrl}/vendor/webawesome/styles/webawesome.css`,
    `${baseUrl}/static/softcloud.css`,
  ];

  for (const href of requiredStyles) {
    const filename = href.split('/').pop();
    const alreadyPresent = existingLinks.some(
      (l) => l === href || l.endsWith('/' + filename)
    );
    if (!alreadyPresent) {
      const link = createElement('link');
      setAttr(link, 'rel', 'stylesheet');
      setAttr(link, 'href', href);
      head.childNodes.push(link);
      link.parentNode = head;
      injectedStylesheets.push(href);
    }
  }

  // 3. Theme synchronization script
  const themeSrc = `${baseUrl}/static/softcloud-theme.js`;
  const themeAlreadyPresent = existingScripts.some((s) => s.endsWith('softcloud-theme.js'));
  if (!themeAlreadyPresent) {
    const script = createElement('script');
    setAttr(script, 'src', themeSrc);
    head.childNodes.push(script);
    script.parentNode = head;
    injectedScripts.push(themeSrc);
  }

  // 4. Web Awesome Runtime Bootstrap (WA-ICON-003)
  // Ensure any direct loader scripts are removed so the ordered bootstrap executes first
  function removeLegacyLoaders(node) {
    if (node.childNodes) {
      node.childNodes = node.childNodes.filter((c) => {
        if (c.tagName === 'script') {
          const src = getAttr(c, 'src') || '';
          if (src.endsWith('webawesome.ssr-loader.js') || src.endsWith('webawesome.loader.js')) {
            return false;
          }
        }
        return true;
      });
      for (const child of node.childNodes) {
        removeLegacyLoaders(child);
      }
    }
  }
  removeLegacyLoaders(ast);

  const bootstrapSrc = `${baseUrl}/static/softcloud-webawesome.mjs`;
  const bootstrapAlreadyPresent = existingScripts.some((s) => s.endsWith('softcloud-webawesome.mjs'));
  if (!bootstrapAlreadyPresent) {
    const script = createElement('script');
    setAttr(script, 'type', 'module');
    setAttr(script, 'src', bootstrapSrc);
    head.childNodes.push(script);
    script.parentNode = head;
    injectedScripts.push(bootstrapSrc);
  }

  return { injectedStylesheets, injectedScripts };
}
