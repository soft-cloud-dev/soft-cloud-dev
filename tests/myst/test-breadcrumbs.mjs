import test from 'node:test';
import assert from 'node:assert/strict';

import {
  resolveBreadcrumbTrail,
  renderBreadcrumbNav,
  mountBreadcrumbs,
} from '../../widgets/breadcrumbs.mjs';

function makeMockDocument() {
  class MockElement {
    constructor(tagName, ownerDocument) {
      this.tagName = String(tagName || 'DIV').toUpperCase();
      this.ownerDocument = ownerDocument;
      this.attributes = {};
      this.children = [];
      this.parentElement = null;
      this.className = '';
      this.id = '';
      this.hidden = false;
      this._text = '';
    }
    set textContent(v) {
      this._text = String(v ?? '');
      this.children = [];
    }
    get textContent() {
      if (this.children.length === 0) return this._text;
      return this.children.map((c) => c.textContent).join('');
    }
    setAttribute(k, v) {
      this.attributes[k] = String(v);
      if (k === 'id') this.id = String(v);
      if (k === 'class') this.className = String(v);
    }
    getAttribute(k) {
      if (k === 'id' && this.id) return this.id;
      if (k === 'class' && this.className) return this.className;
      return Object.prototype.hasOwnProperty.call(this.attributes, k) ? this.attributes[k] : null;
    }
    removeAttribute(k) {
      delete this.attributes[k];
    }
    appendChild(child) {
      child.parentElement = this;
      this.children.push(child);
      return child;
    }
    replaceChildren(...nodes) {
      this.children = [];
      for (const n of nodes) {
        this.appendChild(n);
      }
    }
    querySelector(sel) {
      const wantNav = sel === 'nav.sc-breadcrumbs';
      const walk = (node) => {
        for (const c of node.children) {
          if (wantNav && c.tagName === 'NAV' && c.className.split(/\s+/).includes('sc-breadcrumbs')) {
            return c;
          }
          const found = walk(c);
          if (found) return found;
        }
        return null;
      };
      return walk(this);
    }
  }

  return {
    documentElement: { getAttribute: () => 'en' },
    createElement(tag) {
      return new MockElement(tag, this);
    },
  };
}

const sampleManifest = {
  schema_version: '1.0',
  default_locale: 'en',
  base_url: '',
  locales: {
    en: { code: 'en', prefix: '', html_lang: 'en', ui: { breadcrumbs_label: 'Breadcrumbs' } },
    pl: { code: 'pl', prefix: '/pl', html_lang: 'pl', ui: { breadcrumbs_label: 'Nawigacja okruszkowa' } },
  },
  aliases: {
    'index-1': 'components',
    'components/index': 'components',
  },
  pages: {
    guides: { slug: 'guides', translations: { en: { available: true, route: '/guides' } } },
    components: { slug: 'components', translations: { en: { available: true, route: '/components' } } },
  },
  breadcrumbs: {
    en: {
      label: 'Breadcrumbs',
      nodes: [
        { label: 'SoftCloud Hub', href: '/' },
        { label: 'Platform Engineering' },
        { label: 'Guides', href: '/guides' },
        { label: 'Web Awesome — Component Catalog', href: '/components' },
        { label: 'Unsafe', href: 'javascript:alert(1)' },
        { label: 'ProtoRel', href: '//evil.example/a' },
      ],
      trails: {
        guides: [0, 1, 2],
        components: [0, 1, 3],
        unsafe: [0, 4, 5, 2],
      },
    },
    pl: {
      label: 'Nawigacja okruszkowa',
      nodes: [
        { label: 'SoftCloud Hub', href: '/pl/' },
        { label: 'Inżynieria platformy' },
        { label: 'Poradniki', href: '/pl/guides' },
      ],
      trails: {
        guides: [0, 1, 2],
      },
    },
  },
};

test('resolveBreadcrumbTrail returns null for homepage and unknown routes', () => {
  assert.equal(resolveBreadcrumbTrail(sampleManifest, 'en', ''), null);
  assert.equal(resolveBreadcrumbTrail(sampleManifest, 'en', 'index'), null);
  assert.equal(resolveBreadcrumbTrail(sampleManifest, 'en', 'README'), null);
  assert.equal(resolveBreadcrumbTrail(sampleManifest, 'en', 'nonexistent'), null);
});

test('resolveBreadcrumbTrail resolves subpage trails, aliases, and localized routes', () => {
  const enGuides = resolveBreadcrumbTrail(sampleManifest, 'en', 'guides');
  assert.deepEqual(enGuides, {
    ariaLabel: 'Breadcrumbs',
    key: 'en:guides',
    items: [
      { label: 'SoftCloud Hub', href: '/', current: false },
      { label: 'Platform Engineering', href: null, current: false },
      { label: 'Guides', href: '/guides', current: true },
    ],
  });

  const compAlias = resolveBreadcrumbTrail(sampleManifest, 'en', 'index-1');
  assert.equal(compAlias.key, 'en:components');
  assert.equal(compAlias.items.at(-1).href, '/components');
  assert.equal(compAlias.items.at(-1).current, true);

  const plGuides = resolveBreadcrumbTrail(sampleManifest, 'pl', 'guides');
  assert.equal(plGuides.ariaLabel, 'Nawigacja okruszkowa');
  assert.equal(plGuides.items[0].href, '/pl/');
  assert.equal(plGuides.items[2].label, 'Poradniki');
});

test('resolveBreadcrumbTrail strips unsafe href schemes', () => {
  const unsafeTrail = resolveBreadcrumbTrail(sampleManifest, 'en', 'unsafe');
  assert.equal(unsafeTrail.items[1].href, null);
  assert.equal(unsafeTrail.items[2].href, null);
});

test('mountBreadcrumbs renders semantic DOM and preserves matching SSR DOM', () => {
  const prevDoc = globalThis.document;
  const doc = makeMockDocument();
  globalThis.document = doc;
  try {
    const host = doc.createElement('div');
    host.setAttribute('id', 'softcloud-breadcrumbs-root');
    host.setAttribute('data-sc-breadcrumbs', '1');

    mountBreadcrumbs(host, { routeManifest: sampleManifest, pathname: '/guides', document: doc });
    assert.equal(host.hidden, false);
    const nav = host.querySelector('nav.sc-breadcrumbs');
    assert.ok(nav);
    assert.equal(nav.getAttribute('aria-label'), 'Breadcrumbs');
    assert.equal(nav.getAttribute('data-sc-rendered-key'), 'en:guides');
    const list = nav.children[0];
    assert.equal(list.tagName, 'OL');
    assert.equal(list.children.length, 3);
    assert.equal(list.children[0].children[0].tagName, 'A');
    assert.equal(list.children[0].children[0].getAttribute('href'), '/');
    assert.equal(list.children[1].children[0].tagName, 'SPAN');
    assert.equal(list.children[2].children[0].getAttribute('aria-current'), 'page');

    // Second mount on the same route preserves the exact nav node reference
    mountBreadcrumbs(host, { routeManifest: sampleManifest, pathname: '/guides/', document: doc });
    assert.equal(host.querySelector('nav.sc-breadcrumbs'), nav);

    // Navigating to Polish route updates breadcrumbs cleanly
    mountBreadcrumbs(host, { routeManifest: sampleManifest, pathname: '/pl/guides', document: doc });
    const plNav = host.querySelector('nav.sc-breadcrumbs');
    assert.equal(plNav.getAttribute('aria-label'), 'Nawigacja okruszkowa');
    assert.equal(plNav.getAttribute('data-sc-rendered-key'), 'pl:guides');

    // Navigating back to homepage clears and hides host
    mountBreadcrumbs(host, { routeManifest: sampleManifest, pathname: '/', document: doc });
    assert.equal(host.hidden, true);
    assert.equal(host.querySelector('nav.sc-breadcrumbs'), null);
  } finally {
    globalThis.document = prevDoc;
  }
});

test('renderBreadcrumbNav escapes text safely via textContent without raw separator text', () => {
  const doc = makeMockDocument();
  const nav = renderBreadcrumbNav(doc, {
    ariaLabel: 'Breadcrumbs',
    key: 'en:breadcrumb',
    items: [
      { label: 'SoftCloud Hub', href: '/', current: false },
      { label: 'Breadcrumb <wa-breadcrumb>', href: '/breadcrumb', current: true },
    ],
  });
  assert.equal(nav.children[0].children[1].children[0].textContent, 'Breadcrumb <wa-breadcrumb>');
  assert.equal(nav.textContent.includes('/'), false);
});
