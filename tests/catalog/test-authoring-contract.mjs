import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const read = path => readFileSync(new URL('../../' + path, import.meta.url), 'utf8');

test('authoring guide has unambiguous nested MyST example fences', () => {
  const guide = read('components/authoring-guide.md');
  assert.match(guide, /:::::\{tab-set\}/);
  assert.match(guide, /::::\{tab-item\} MyST note/);
  assert.match(guide, /````markdown\n:::\{note\}\nUse this for publication notes\.\n:::\n````/);
  assert.match(guide, /\| Phase \| Status \| Deliverable \|/);
  assert.match(guide, /Component selection hierarchy/);
  assert.match(guide, /A `<noscript>` message is not sufficient/);
});

test('authoring and catalog routes are separate navigation groups', () => {
  const myst = read('myst.yml');
  const catalog = read('components/index.md');
  assert.match(myst, /- title: Contributor Guide\n      children:\n        - file: components\/authoring-guide\.md/);
  assert.equal((myst.match(/file: components\/authoring-guide\.md/g) || []).length, 1);
  assert.match(catalog, /^---\nslug: components\n/);
});

test('typed SSR and browser widget responsibilities are documented', () => {
  const guide = read('components/authoring-guide.md');
  const button = read('components/actions/button.md');
  assert.match(guide, /Use the existing typed Web Awesome directives/);
  assert.match(guide, /Use \x60\{anywidget\}\x60 for client-side previews/);
  assert.match(button, /genuine Lit SSR\/DSD/);
});
