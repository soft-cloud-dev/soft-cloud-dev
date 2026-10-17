/**
 * Self-hosted Web Awesome catalog preview.
 * Runs inside the already installed MyST anywidget Shadow DOM renderer.
 * Model JSON is treated as structured data, never HTML.
 */
const native = new Set(['a', 'code', 'div', 'figcaption', 'figure', 'h3', 'img', 'li', 'p', 'small', 'source', 'span', 'strong', 'ul', 'video']);
const permittedAttrs = new Set([
  'active', 'alt', 'anchor', 'appearance', 'aria-label', 'checked', 'class',
  'content', 'controls', 'caret', 'date', 'day', 'decoding', 'duration', 'effect', 'expanded',
  'for', 'href', 'id', 'image', 'initials', 'label', 'length', 'loading', 'loop', 'max', 'min', 'month', 'mouse-dragging', 'muted',
  'name', 'navigation', 'open', 'page', 'pages', 'panel', 'pagination',
  'pill', 'placeholder', 'play', 'playsinline', 'position', 'poster', 'preload', 'referrerpolicy', 'rows', 'shape', 'size', 'slot', 'src',
  'status', 'step', 'summary', 'target', 'title', 'type', 'value', 'variant',
  'with-caret', 'page-size', 'total', 'copy-label',
  'width', 'year', 'zoom', 'height', 'data-demo-action', 'data-demo-target'
]);
const validUrl = /^(?:https:\/\/|\/(?!\/)|#)/i;
const moduleImports = new Map();

// Retain the documented /static/showcase paths but resolve them relative to
// the deployed Web Awesome bundle, including a custom BASE_URL prefix.
function localShowcaseUrl(raw) {
  if (!/^\/static\/showcase\/[a-z0-9][a-z0-9._-]*$/i.test(raw)) return raw;
  const root = runtimeRoot();
  return root ? new URL('../../' + raw.slice(1), root).href : raw;
}

function createNode(data) {
  if (typeof data === 'string') return document.createTextNode(data);
  if (!data || typeof data !== 'object' || typeof data.tag !== 'string') {
    throw new TypeError('Invalid component preview node');
  }
  const tag = data.tag;
  if (!native.has(tag) && !/^wa-[a-z][a-z0-9-]*$/.test(tag)) {
    throw new TypeError('Disallowed component preview tag');
  }
  const node = document.createElement(tag);
  for (const [attr, value] of Object.entries(data.attrs || {})) {
    if (!permittedAttrs.has(attr) || attr.toLowerCase().startsWith('on')) continue;
    if (['href', 'src', 'image', 'poster'].includes(attr) && !validUrl.test(String(value))) continue;
    const safeValue = ['src', 'image', 'poster'].includes(attr)
      ? localShowcaseUrl(String(value)) : String(value);
    node.setAttribute(attr, safeValue);
  }
  for (const child of data.children || []) node.append(createNode(child));
  return node;
}

function componentNames(data) {
  const out = new Set();
  const visit = item => {
    if (typeof item === 'string' || !item) return;
    if (Array.isArray(item)) {
      item.forEach(visit);
      return;
    }
    if (item.tag && item.tag.startsWith('wa-')) out.add(item.tag.slice(3));
    (item.children || []).forEach(visit);
  };
  visit(data);
  return out;
}

function runtimeRoot() {
  const loader = document.querySelector('script[src*="/vendor/webawesome/webawesome.ssr-loader.js"]');
  if (loader) return new URL('.', loader.src);
  const bootstrap = document.querySelector('script[src*="/static/softcloud-webawesome.mjs"]');
  if (bootstrap) return new URL('../vendor/webawesome/', bootstrap.src);
  const sheet = document.querySelector('link[href*="/vendor/webawesome/styles/webawesome.css"]');
  return sheet ? new URL('../', sheet.href) : null;
}

async function loadComponents(names) {
  const root = runtimeRoot();
  if (!root) throw new Error('Self-hosted Web Awesome loader not found.');
  await Promise.all(Array.from(names, name => {
    if (customElements.get('wa-' + name)) return Promise.resolve();
    if (!moduleImports.has(name)) {
      const path = 'components/' + name + '/' + name + '.js';
      moduleImports.set(name, import(new URL(path, root).href));
    }
    return moduleImports.get(name);
  }));
}

export default {
  async render({ model, el }) {
    const tree = model.get('tree');
    const nodes = Array.isArray(tree) ? tree : [tree];
    const style = document.createElement('style');
    style.textContent = [
      '.sc-wa-showcase { display: flex; flex-wrap: wrap; align-items: center; gap: 1rem;',
      'padding: 1.25rem; border: 1px solid var(--wa-color-neutral-30,#adb4bf);',
      'border-radius: 0.6rem; background: var(--wa-color-surface-default,transparent); min-height: 75px; }',
      '.sc-wa-showcase > wa-accordion, .sc-wa-showcase > wa-card,',
      '.sc-wa-showcase > wa-carousel, .sc-wa-showcase > wa-split-panel,',
      '.sc-wa-showcase > wa-tab-group, .sc-wa-showcase > wa-tree { width:100%; max-width:100%; }',
      '.sc-wa-showcase img { display:block; max-width:100%; height:auto; }',
      '.sc-wa-showcase > wa-card { max-width: min(100%, 360px); }',
      '.sc-wa-showcase > wa-comparison, .sc-wa-showcase > wa-zoomable-frame { width:100%; }',
      '.sc-wa-showcase wa-carousel-item img { width:100%; aspect-ratio:16/9; object-fit:cover; }',
      '.sc-wa-showcase wa-comparison img { width:100%; height:100%; object-fit:cover; }',
      '.sc-wa-showcase .sc-demo-grayscale { filter: grayscale(1); }',
      '.sc-wa-showcase > wa-scroller { width:100%; }',
      '.sc-wa-showcase .sc-demo-thumb-row { display:flex; gap:0.75rem; width:max-content; }',
      '.sc-wa-showcase .sc-demo-thumb-row img { width:180px; aspect-ratio:16/9; object-fit:cover; }',
      '.sc-wa-showcase wa-tab-panel img { width:100%; max-height:320px; aspect-ratio:16/9; object-fit:cover; }',
      '.sc-wa-showcase wa-card video { width:100%; aspect-ratio:16/9; object-fit:cover; }',
      '.sc-wa-showcase > wa-animated-image { max-width: min(100%, 360px); }',
      '.sc-wa-catalog-status { font-size:0.82rem; opacity:0.85; }'
    ].join(' ');
    const message = document.createElement('p');
    message.className = 'sc-wa-catalog-status';
    message.textContent = 'Loading local component modules…';
    const frame = document.createElement('div');
    frame.className = 'sc-wa-showcase';
    frame.setAttribute('role', 'group');
    frame.setAttribute('aria-label', 'Live component preview');
    el.append(style, message, frame);
    try {
      const names = componentNames(nodes);
      if (!names.size || names.size > 25) throw new Error('Invalid component count.');
      await loadComponents(names);
      for (const node of nodes) frame.append(createNode(node));
      frame.addEventListener('click', event => {
        const actionNode = event.target.closest?.('[data-demo-target]');
        if (!actionNode || !frame.contains(actionNode)) return;
        const action = actionNode.getAttribute('data-demo-action');
        const id = actionNode.getAttribute('data-demo-target');
        if (!id || (action !== 'show' && action !== 'hide')) return;
        const receiver = frame.querySelector('#' + CSS.escape(id));
        if (!receiver) return;
        if (typeof receiver[action] === 'function') receiver[action]();
        else receiver.open = action === 'show';
      });
      message.remove();
    } catch (error) {
      message.textContent = 'Preview unavailable: ' + (error?.message || 'component initialization failed');
      console.error('[SoftCloud component catalog]', error);
    }
  }
};
