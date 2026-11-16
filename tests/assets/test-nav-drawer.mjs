/**
 * tests/assets/test-nav-drawer.mjs
 * Unit tests for widgets/nav-drawer.mjs modal navigation drawer controller.
 */

import test from 'node:test';
import assert from 'node:assert/strict';

import {
  DRAWER_LABELS,
  getNavDrawerLocale,
  getNavDrawerLabel,
  isHideTocDrawer,
  isDrawerViewport,
  installNavDrawerController,
} from '../../widgets/nav-drawer.mjs';

function createMockElement(tagName, doc) {
  const listeners = new Map();
  const attrs = new Map();
  const classSet = new Set();
  const el = {
    tagName: String(tagName).toUpperCase(),
    ownerDocument: doc,
    parentElement: null,
    children: [],
    isConnected: true,
    inert: false,
    textContent: '',
    _innerHTML: '',
    get id() {
      return attrs.get('id') || '';
    },
    set id(val) {
      attrs.set('id', String(val));
    },
    get className() {
      return Array.from(classSet).join(' ');
    },
    set className(val) {
      classSet.clear();
      for (const tok of String(val || '').split(/\s+/).filter(Boolean)) {
        classSet.add(tok);
      }
    },
    classList: {
      add: (...tokens) => tokens.forEach((t) => classSet.add(t)),
      remove: (...tokens) => tokens.forEach((t) => classSet.delete(t)),
      contains: (t) => classSet.has(t),
    },
    get innerHTML() {
      return el._innerHTML;
    },
    set innerHTML(val) {
      el._innerHTML = String(val);
    },
    setAttribute(k, v) {
      attrs.set(k, String(v));
      if (k === 'class') el.className = String(v);
    },
    getAttribute(k) {
      return attrs.has(k) ? attrs.get(k) : null;
    },
    hasAttribute(k) {
      return attrs.has(k);
    },
    removeAttribute(k) {
      attrs.delete(k);
    },
    appendChild(child) {
      if (child.parentElement) {
        const idx = child.parentElement.children.indexOf(child);
        if (idx >= 0) child.parentElement.children.splice(idx, 1);
      }
      child.parentElement = el;
      el.children.push(child);
      return child;
    },
    append(...nodes) {
      nodes.forEach((n) => el.appendChild(n));
    },
    insertBefore(newChild, refChild) {
      if (!refChild) return el.appendChild(newChild);
      const idx = el.children.indexOf(refChild);
      if (idx === -1) return el.appendChild(newChild);
      newChild.parentElement = el;
      el.children.splice(idx, 0, newChild);
      return newChild;
    },
    remove() {
      if (el.parentElement) {
        const idx = el.parentElement.children.indexOf(el);
        if (idx >= 0) el.parentElement.children.splice(idx, 1);
        el.parentElement = null;
      }
    },
    contains(target) {
      if (target === el) return true;
      return el.children.some((c) => c.contains(target));
    },
    addEventListener(type, fn) {
      if (!listeners.has(type)) listeners.set(type, []);
      listeners.get(type).push(fn);
    },
    removeEventListener(type, fn) {
      if (!listeners.has(type)) return;
      listeners.set(type, listeners.get(type).filter((f) => f !== fn));
    },
    dispatchEvent(evt) {
      evt.target = evt.target || el;
      for (const fn of listeners.get(evt.type) || []) {
        fn(evt);
      }
    },
    focus() {
      doc.activeElement = el;
    },
    getClientRects() {
      return classSet.has('hidden') ? [] : [{ width: 40, height: 40 }];
    },
    closest(sel) {
      if (sel === 'a[href]' && el.tagName === 'A' && el.hasAttribute('href')) return el;
      return el.parentElement ? el.parentElement.closest(sel) : null;
    },
    matches(sel) {
      if (sel === 'button.myst-top-nav-menu-button') {
        return el.tagName === 'BUTTON' && classSet.has('myst-top-nav-menu-button');
      }
      if (sel.startsWith('.')) return classSet.has(sel.slice(1));
      if (sel.startsWith('[data-sc-fallback-overlay="1"]')) return el.getAttribute('data-sc-fallback-overlay') === '1';
      return false;
    },
    querySelectorAll(sel) {
      const out = [];
      const parts = sel.split(',').map((s) => s.trim());
      const walk = (node) => {
        for (const c of node.children) {
          if (parts.some((p) => c.matches(p))) out.push(c);
          walk(c);
        }
      };
      walk(el);
      return out;
    },
    querySelector(sel) {
      return el.querySelectorAll(sel)[0] || null;
    },
  };
  return el;
}

function createHarness({ lang = 'en', width = 900, hideToc = true } = {}) {
  const docListeners = new Map();
  const winListeners = new Map();
  const doc = {
    activeElement: null,
    documentElement: null,
    body: null,
    createElement(tag) {
      return createMockElement(tag, doc);
    },
    getElementById(id) {
      const walk = (n) => {
        if (n.id === id) return n;
        for (const c of n.children) {
          const found = walk(c);
          if (found) return found;
        }
        return null;
      };
      return walk(doc.body);
    },
    querySelector(sel) {
      return doc.body.querySelector(sel);
    },
    querySelectorAll(sel) {
      return doc.body.querySelectorAll(sel);
    },
    addEventListener(type, fn) {
      if (!docListeners.has(type)) docListeners.set(type, []);
      docListeners.get(type).push(fn);
    },
    removeEventListener(type, fn) {
      if (!docListeners.has(type)) return;
      docListeners.set(type, docListeners.get(type).filter((f) => f !== fn));
    },
    dispatchKeyDown(key) {
      let prevented = false;
      const evt = {
        type: 'keydown',
        key,
        preventDefault() {
          prevented = true;
        },
        stopPropagation() {},
      };
      for (const fn of docListeners.get('keydown') || []) fn(evt);
      return prevented;
    },
    dispatchClick(target) {
      const evt = {
        type: 'click',
        target,
        preventDefault() {},
        stopPropagation() {},
      };
      for (const fn of docListeners.get('click') || []) fn(evt);
    },
  };

  doc.documentElement = createMockElement('html', doc);
  doc.documentElement.setAttribute('lang', lang);
  doc.body = createMockElement('body', doc);

  const topNav = createMockElement('div', doc);
  topNav.className = 'myst-top-nav';
  const menuBtn = createMockElement('button', doc);
  menuBtn.className = 'myst-top-nav-menu-button';
  menuBtn.setAttribute('aria-expanded', 'false');
  const srOnly = createMockElement('span', doc);
  srOnly.className = 'sr-only';
  srOnly.textContent = 'Open Menu';
  menuBtn.appendChild(srOnly);
  topNav.appendChild(menuBtn);

  const sidebar = createMockElement('div', doc);
  sidebar.id = 'myst-primary-sidebar';
  sidebar.className = hideToc ? 'myst-primary-sidebar lg:hidden hidden' : 'myst-primary-sidebar hidden';
  sidebar.setAttribute('data-sc-drawer-open', 'false');
  sidebar.setAttribute('data-sc-hide-toc', hideToc ? 'true' : 'false');
  const pointer = createMockElement('div', doc);
  pointer.className = 'myst-primary-sidebar-pointer';
  const nav = createMockElement('div', doc);
  nav.className = 'myst-primary-sidebar-nav';
  const link = createMockElement('a', doc);
  link.setAttribute('href', '/guides');
  link.textContent = 'Guides';
  nav.appendChild(link);
  pointer.appendChild(nav);
  sidebar.appendChild(pointer);

  const main = createMockElement('main', doc);
  doc.body.append(topNav, sidebar, main);

  const win = {
    innerWidth: width,
    location: { pathname: '/', hash: '' },
    document: doc,
    history: {
      pushState(_s, _t, url) {
        win.location.pathname = url;
      },
      replaceState(_s, _t, url) {
        win.location.pathname = url;
      },
    },
    matchMedia(query) {
      const m = query.match(/min-width:\s*(\d+)px/);
      const min = m ? Number(m[1]) : 0;
      return {
        matches: win.innerWidth >= min,
        addEventListener() {},
        removeEventListener() {},
      };
    },
    getComputedStyle() {
      return { display: 'block', visibility: 'visible' };
    },
    addEventListener(type, fn) {
      if (!winListeners.has(type)) winListeners.set(type, []);
      winListeners.get(type).push(fn);
    },
    removeEventListener(type, fn) {
      if (!winListeners.has(type)) return;
      winListeners.set(type, winListeners.get(type).filter((f) => f !== fn));
    },
    dispatchEvent(evt) {
      for (const fn of winListeners.get(evt.type) || []) fn(evt);
    },
  };
  doc.defaultView = win;

  return { doc, win, topNav, menuBtn, sidebar, main, link };
}

test('localized drawer labels resolve for all 5 supported locales with fallback', () => {
  for (const code of Object.keys(DRAWER_LABELS)) {
    const doc = { documentElement: { getAttribute: (k) => (k === 'lang' ? code : null) } };
    assert.equal(getNavDrawerLocale(doc), code);
    assert.ok(getNavDrawerLabel('close', doc).length > 0);
    assert.ok(getNavDrawerLabel('drawer', doc).length > 0);
  }
  const regionalDoc = { documentElement: { getAttribute: () => 'pl-PL' } };
  assert.equal(getNavDrawerLocale(regionalDoc), 'pl');
  const unknownDoc = { documentElement: { getAttribute: () => 'ja' } };
  assert.equal(getNavDrawerLocale(unknownDoc), 'en');
});

test('isHideTocDrawer and isDrawerViewport honor 1024px vs 1280px breakpoints', () => {
  const { sidebar: homeSidebar, win: homeWin } = createHarness({ width: 1024, hideToc: true });
  assert.equal(isHideTocDrawer(homeSidebar), true);
  assert.equal(isDrawerViewport(homeSidebar, homeWin), false);
  homeWin.innerWidth = 980;
  assert.equal(isDrawerViewport(homeSidebar, homeWin), true);

  const { sidebar: guideSidebar, win: guideWin } = createHarness({ width: 1180, hideToc: false });
  assert.equal(isHideTocDrawer(guideSidebar), false);
  assert.equal(isDrawerViewport(guideSidebar, guideWin), true);
  guideWin.innerWidth = 1280;
  assert.equal(isDrawerViewport(guideSidebar, guideWin), false);
});

test('controller manages focus, inert modality, Escape, outside click, and route changes', () => {
  const { doc, win, topNav, menuBtn, sidebar, main, link } = createHarness({ lang: 'pl', width: 980, hideToc: true });
  const cleanup = installNavDrawerController({ document: doc, window: win });

  // Open via menu button click
  doc.dispatchClick(menuBtn);
  assert.equal(sidebar.getAttribute('data-sc-drawer-open'), 'true');
  assert.equal(sidebar.getAttribute('role'), 'dialog');
  assert.equal(sidebar.getAttribute('aria-modal'), 'true');
  assert.equal(sidebar.getAttribute('aria-label'), DRAWER_LABELS.pl.drawer);
  assert.equal(topNav.inert, true);
  assert.equal(main.inert, true);
  assert.equal(doc.activeElement?.classList.contains('myst-drawer-close-button'), true);
  assert.ok(doc.querySelector('.myst-navigation-overlay'));

  // Dismiss via Escape -> restores inert and focuses menu button
  const prevented = doc.dispatchKeyDown('Escape');
  assert.equal(prevented, true);
  assert.equal(sidebar.getAttribute('data-sc-drawer-open'), 'false');
  assert.equal(topNav.inert, false);
  assert.equal(main.inert, false);
  assert.equal(doc.activeElement, menuBtn);

  // Reopen, then dismiss via clicking main outside drawer
  doc.dispatchClick(menuBtn);
  assert.equal(sidebar.getAttribute('data-sc-drawer-open'), 'true');
  doc.dispatchClick(main);
  assert.equal(sidebar.getAttribute('data-sc-drawer-open'), 'false');
  assert.equal(topNav.inert, false);
  assert.equal(main.inert, false);
  assert.equal(doc.activeElement, menuBtn);

  // Reopen, then click navigation link inside drawer -> closes without stealing focus to menuBtn
  doc.activeElement = null;
  doc.dispatchClick(menuBtn);
  assert.equal(sidebar.getAttribute('data-sc-drawer-open'), 'true');
  doc.dispatchClick(link);
  assert.equal(sidebar.getAttribute('data-sc-drawer-open'), 'false');
  assert.equal(topNav.inert, false);
  assert.equal(main.inert, false);
  assert.notEqual(doc.activeElement, menuBtn);

  // Reopen, then resize across desktop breakpoint -> auto-closes and clears inert
  doc.dispatchClick(menuBtn);
  assert.equal(sidebar.getAttribute('data-sc-drawer-open'), 'true');
  win.innerWidth = 1024;
  win.dispatchEvent({ type: 'resize' });
  assert.equal(sidebar.getAttribute('data-sc-drawer-open'), 'false');
  assert.equal(topNav.inert, false);
  assert.equal(main.inert, false);

  cleanup();
});

test('SPA history.pushState pathname change closes an open drawer', () => {
  const { doc, win, menuBtn, sidebar, main } = createHarness({ width: 820, hideToc: true });
  const cleanup = installNavDrawerController({ document: doc, window: win });

  doc.dispatchClick(menuBtn);
  assert.equal(sidebar.getAttribute('data-sc-drawer-open'), 'true');
  assert.equal(main.inert, true);

  win.history.pushState({}, '', '/guides');
  assert.equal(sidebar.getAttribute('data-sc-drawer-open'), 'false');
  assert.equal(main.inert, false);

  cleanup();
});
