/**
 * Self-hosted Web Awesome catalog preview.
 * Runs inside the already installed MyST anywidget Shadow DOM renderer.
 * Model JSON is treated as structured data, never HTML.
 */
const native = new Set(['a', 'code', 'div', 'figcaption', 'figure', 'h3', 'img', 'li', 'p', 'small', 'source', 'span', 'strong', 'ul', 'video']);
const permittedAttrs = new Set([
  'active', 'alt', 'anchor', 'appearance', 'aria-controls', 'aria-expanded', 'aria-label', 'checked', 'class',
  'command', 'commandfor', 'content', 'controls', 'caret', 'date', 'day', 'decoding', 'duration', 'effect', 'expanded',
  'for', 'href', 'id', 'image', 'initials', 'label', 'length', 'loading', 'loop', 'max', 'min', 'month', 'mouse-dragging', 'muted',
  'name', 'navigation', 'open', 'page', 'pages', 'panel', 'pagination',
  'pill', 'placeholder', 'play', 'playsinline', 'position', 'poster', 'preload', 'referrerpolicy', 'rows', 'shape', 'size', 'slot', 'src',
  'status', 'step', 'summary', 'target', 'title', 'type', 'value', 'variant',
  'with-caret', 'page-size', 'total', 'copy-label',
  'width', 'year', 'zoom', 'height', 'data-demo-action', 'data-demo-target'
]);
const validUrl = /^(?:https:\/\/|\/(?!\/)|#)/i;
const moduleImports = new Map();
const allowedComponents = new Set(["button","button-group","copy-button","dropdown","dropdown-item","checkbox","checkbox-group","color-picker","input","known-date","number-input","otp-input","radio-group","radio","rating","select","option","slider","switch","textarea","time-input","accordion","accordion-item","card","details","dialog","divider","drawer","scroller","split-panel","breadcrumb","breadcrumb-item","pagination","tab-group","tab","tab-panel","tree","tree-item","badge","callout","progress-bar","progress-ring","skeleton","spinner","tag","tooltip","animated-image","avatar","carousel","carousel-item","comparison","icon","qr-code","zoomable-frame","animation","format-bytes","format-date","format-number","random-content","relative-time"]);

// Demo-only media token. The module URL is stable across root, nested and file deployments.
// No page source needs to embed a deployment-specific /static URL.
export function resolveShowcaseMedia(raw, moduleUrl = import.meta.url) {
  const match = /^showcase:([a-z0-9][a-z0-9._-]*)$/i.exec(raw);
  if (!match) return raw;
  return new URL('../static/showcase/' + match[1], moduleUrl).href;
}

function localShowcaseUrl(raw) {
  return resolveShowcaseMedia(raw);
}

function isSameOriginUrl(candidateUrl, referenceUrl = import.meta.url) {
  try {
    const resolvedCandidate = new URL(candidateUrl, referenceUrl).href;
    const resolvedRef = new URL(referenceUrl).href;
    if ('Origin' in globalThis) {
      return globalThis.Origin.from(resolvedCandidate).isSameOrigin(globalThis.Origin.from(resolvedRef));
    }
    const candidateParsed = new URL(resolvedCandidate);
    const refParsed = new URL(resolvedRef);
    return candidateParsed.origin !== 'null' && candidateParsed.origin === refParsed.origin;
  } catch {
    return false;
  }
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
    const isMedia = ['src', 'image', 'poster'].includes(attr);
    const rawValue = String(value);
    const isShowcase = isMedia && /^showcase:[a-z0-9][a-z0-9._-]*$/i.test(rawValue);
    const safeValue = isMedia ? localShowcaseUrl(rawValue) : rawValue;
    if (['href', 'src', 'image', 'poster'].includes(attr) &&
        !validUrl.test(safeValue) && !(isShowcase && safeValue.startsWith('file://'))) continue;
    node.setAttribute(attr, safeValue);
  }
  const demoTarget = node.getAttribute('data-demo-target');
  const demoAction = node.getAttribute('data-demo-action');
  if (demoTarget && (demoAction === 'show' || demoAction === 'hide')) {
    if (!node.hasAttribute('commandfor')) node.setAttribute('commandfor', demoTarget);
    if (!node.hasAttribute('command')) node.setAttribute('command', `--${demoAction}`);
    if (!node.hasAttribute('aria-controls')) node.setAttribute('aria-controls', demoTarget);
    if (!node.hasAttribute('aria-expanded')) node.setAttribute('aria-expanded', 'false');
  }
  for (const child of data.children || []) node.append(createNode(child));
  return node;
}

const componentDependencies = {
  'time-input': ['icon'],
  'date-input': ['icon'],
  'date-picker': ['icon'],
  'color-picker': ['icon'],
  'copy-button': ['icon'],
  'carousel': ['icon'],
  'rating': ['icon'],
  'combobox': ['icon']
};

function componentNames(data) {
  const out = new Set();
  const visit = item => {
    if (typeof item === 'string' || !item) return;
    if (Array.isArray(item)) {
      item.forEach(visit);
      return;
    }
    if (item.tag && item.tag.startsWith('wa-')) {
      const name = item.tag.slice(3);
      out.add(name);
      const deps = componentDependencies[name];
      if (deps) deps.forEach(dep => out.add(dep));
    }
    (item.children || []).forEach(visit);
  };
  visit(data);
  return out;
}

function runtimeRoot() {
  return new URL('../vendor/webawesome/', import.meta.url);
}

let runtimeConfigPromise = null;

function ensureRuntimeConfig() {
  if (!runtimeConfigPromise) {
    const root = runtimeRoot();
    const iconRoot = new URL('../vendor/fontawesome/svgs/', import.meta.url);
    runtimeConfigPromise = import(new URL('webawesome.js', root).href)
      .then(mod => {
        if (typeof mod.setBasePath === 'function') {
          mod.setBasePath(root.pathname.replace(/\/$/, ''));
        }
        if (typeof mod.setIconPath === 'function') {
          mod.setIconPath(iconRoot.pathname.replace(/\/$/, ''));
        }
      })
      .catch(() => {});
  }
  return runtimeConfigPromise;
}

function hasStylesheetHref(container, suffix) {
  const links = container.getElementsByTagName ? Array.from(container.getElementsByTagName('link')) : [];
  return links.some(link => {
    const href = link.getAttribute('href') || '';
    return href.endsWith(suffix) && (href.startsWith('/') || isSameOriginUrl(href));
  });
}

function ensureStylesheets() {
  if (typeof document === 'undefined' || !document.head) return;
  const root = runtimeRoot();
  const sheets = [
    [new URL('styles/webawesome.css', root).href, '/vendor/webawesome/styles/webawesome.css'],
    [new URL('../vendor/fontawesome/css/all.min.css', import.meta.url).href, '/vendor/fontawesome/css/all.min.css'],
    [new URL('../static/softcloud.css', import.meta.url).href, '/static/softcloud.css']
  ];
  for (const [href, suffix] of sheets) {
    if (!hasStylesheetHref(document.head, suffix)) {
      const link = document.createElement('link');
      link.setAttribute('rel', 'stylesheet');
      link.setAttribute('href', href);
      document.head.appendChild(link);
    }
  }
}

let themeObserverInstalled = false;

function syncDocumentTheme() {
  if (typeof document === 'undefined' || !document.documentElement) return;
  const root = document.documentElement;
  const isDark = root.classList.contains('dark');
  const wantClass = isDark ? 'wa-dark' : 'wa-light';
  const dropClass = isDark ? 'wa-light' : 'wa-dark';
  const wantTheme = isDark ? 'dark' : 'light';
  if (root.classList.contains(dropClass)) root.classList.remove(dropClass);
  if (!root.classList.contains(wantClass)) root.classList.add(wantClass);
  if (root.getAttribute('data-theme') !== wantTheme) root.setAttribute('data-theme', wantTheme);
  if (root.style && root.style.colorScheme !== wantTheme) root.style.colorScheme = wantTheme;
  if (!themeObserverInstalled && typeof MutationObserver !== 'undefined') {
    themeObserverInstalled = true;
    const obs = new MutationObserver(() => syncDocumentTheme());
    obs.observe(root, { attributes: true, attributeFilter: ['class'] });
  }
}

async function loadComponents(names) {
  await ensureRuntimeConfig();
  ensureStylesheets();
  syncDocumentTheme();
  const root = runtimeRoot();
  for (const name of names) {
    if (!allowedComponents.has(name)) throw new Error('Unsupported Web Awesome component: ' + name);
  }
  await Promise.all(Array.from(names, name => {
    if (customElements.get('wa-' + name)) return Promise.resolve();
    if (!moduleImports.has(name)) {
      const path = 'components/' + name + '/' + name + '.js';
      moduleImports.set(name, import(new URL(path, root).href).catch(error => {
        moduleImports.delete(name);
        throw new Error('Failed to import Web Awesome component ' + name + ': ' + (error?.message || String(error)), { cause: error });
      }));
    }
    return moduleImports.get(name);
  }));
  const drawerCtor = customElements.get('wa-drawer');
  if (drawerCtor?.prototype && !drawerCtor.prototype.__scPatched) {
    drawerCtor.prototype.__scPatched = true;
    drawerCtor.prototype.handleOpenChange = function() {
      if (this.open && !this.drawer?.open) {
        this.show();
      } else if (!this.open && this.drawer?.open) {
        this.open = true;
        this.requestClose(this.drawer);
      } else if (!this.open) {
        this.renderedWatcher?.stop();
      }
    };
  }
}

export default {
  async render({ model, el }) {
    const tree = model.get('tree');
    const nodes = Array.isArray(tree) ? tree : [tree];
    const style = document.createElement('style');
    style.textContent = [
      '.sc-wa-showcase { display: flex; flex-wrap: wrap; align-items: center; gap: 1rem;',
      'padding: 1.25rem; border: 1px solid var(--wa-color-neutral-30,#adb4bf);',
      'border-radius: 0.6rem; background: var(--wa-color-surface-default,transparent); min-height: 75px; margin-bottom: 1.25rem; }',
      '.sc-wa-showcase > wa-accordion, .sc-wa-showcase > wa-card,',
      '.sc-wa-showcase > wa-carousel, .sc-wa-showcase > wa-split-panel,',
      '.sc-wa-showcase > wa-tab-group, .sc-wa-showcase > wa-tree { width:100%; max-width:100%; }',
      '.sc-wa-showcase img { display:block; max-width:100%; height:auto; }',
      '.sc-wa-showcase > wa-card { max-width: min(100%, 360px); }',
      '.sc-wa-showcase > wa-progress-bar { flex: 1 1 100%; min-width: 0; }',
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
      const applyDemoCommand = (receiver, action) => {
        if (!receiver || (action !== 'show' && action !== 'hide')) return;
        const isShowing = action === 'show';
        if (typeof receiver[action] === 'function') receiver[action]();
        else receiver.open = isShowing;
        if (receiver.id) {
          const triggers = frame.querySelectorAll(`[data-demo-target="${CSS.escape(receiver.id)}"], [commandfor="${CSS.escape(receiver.id)}"]`);
          for (const trig of triggers) {
            trig.setAttribute('aria-expanded', String(isShowing));
          }
        }
      };
      frame.addEventListener('command', event => {
        const target = event.composedPath ? event.composedPath()[0] : event.target;
        const command = event.command;
        if (command === '--show' || command === '--hide') {
          applyDemoCommand(target, command.slice(2));
        }
      }, { capture: true });
      frame.addEventListener('click', event => {
        const actionNode = event.target.closest?.('[data-demo-target]');
        if (!actionNode || !frame.contains(actionNode)) return;
        event.stopPropagation();
        if ('commandForElement' in HTMLButtonElement.prototype && actionNode.tagName === 'BUTTON' && actionNode.hasAttribute('commandfor')) {
          return;
        }
        const action = actionNode.getAttribute('data-demo-action');
        const id = actionNode.getAttribute('data-demo-target');
        if (!id || (action !== 'show' && action !== 'hide')) return;
        const receiver = frame.querySelector('#' + CSS.escape(id));
        applyDemoCommand(receiver, action);
      });
      message.remove();
    } catch (error) {
      message.textContent = 'Preview unavailable: ' + (error?.message || 'component initialization failed');
      console.error('[SoftCloud component catalog]', error);
    }
  }
};
