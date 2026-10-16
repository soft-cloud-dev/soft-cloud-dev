/**
 * scripts/lib/asset-injection.mjs
 * Injects required stylesheets and scripts into parsed HTML documents exactly once,
 * respecting BASE_URL prefixes.
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

  // Theme script
  const themeSrc = `${baseUrl}/static/softcloud-theme.js`;
  const themeAlreadyPresent = existingScripts.some((s) => s.endsWith('softcloud-theme.js'));
  if (!themeAlreadyPresent) {
    const script = createElement('script');
    setAttr(script, 'src', themeSrc);
    head.childNodes.push(script);
    script.parentNode = head;
    injectedScripts.push(themeSrc);
  }

  // Web Awesome SSR loader (must not load standard autoloader)
  const ssrLoaderSrc = `${baseUrl}/vendor/webawesome/webawesome.ssr-loader.js`;
  const ssrAlreadyPresent = existingScripts.some((s) => s.endsWith('webawesome.ssr-loader.js'));
  const standardAlreadyPresent = existingScripts.some((s) => s.endsWith('webawesome.loader.js'));

  if (standardAlreadyPresent) {
    // Remove or avoid standard loader
    function removeStandardLoader(node) {
      if (node.childNodes) {
        node.childNodes = node.childNodes.filter(
          (c) => !(c.tagName === 'script' && (getAttr(c, 'src') || '').endsWith('webawesome.loader.js'))
        );
        for (const child of node.childNodes) {
          removeStandardLoader(child);
        }
      }
    }
    removeStandardLoader(ast);
  }

  if (!ssrAlreadyPresent) {
    const script = createElement('script');
    setAttr(script, 'type', 'module');
    setAttr(script, 'src', ssrLoaderSrc);
    head.childNodes.push(script);
    script.parentNode = head;
    injectedScripts.push(ssrLoaderSrc);
  }

  return { injectedStylesheets, injectedScripts };
}
