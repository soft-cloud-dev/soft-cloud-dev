import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const read = path => readFileSync(new URL('../../' + path, import.meta.url), 'utf8');
const page = read('components/design-tokens.md');
const styles = read('assets/static/softcloud.css');
const toc = read('myst.yml');
const index = read('components/index.md');

test('Design Tokens route is discoverable in MyST and the component catalog', () => {
  assert.equal((toc.match(/file: components\/design-tokens\.md/g) || []).length, 1);
  assert.match(index, /\[Design Tokens & Style Preview\]\(design-tokens\.md\)/);
  assert.match(page, /^# Design Tokens & Style Preview/m);
});

test('all primary previews render as semantic no-JS HTML with paired scoped themes', () => {
  assert.match(page, /class="sc-token-preview-grid"/);
  for (const mode of ['light', 'dark']) {
    assert.match(page, new RegExp('<section class="sc-token-panel wa-' + mode + '"'));
  }
  for (const variant of ['brand', 'neutral', 'success', 'warning', 'danger']) {
    assert.match(page, new RegExp('class="sc-token-color sc-token-' + variant + '"'));
    assert.match(styles, new RegExp('background: var\\(--wa-color-' + variant + '\\)'));
    assert.match(styles, new RegExp('color: var\\(--wa-color-' + variant + '-on\\)'));
  }
  for (const tint of ['20', '40', '60', '80', '95']) {
    assert.match(page, new RegExp('sc-token-brand-' + tint));
    assert.match(styles, new RegExp('--wa-color-brand-' + tint + '\\)'));
  }
  for (const token of ['2xs', 'xs', 's', 'm', 'l', 'xl', '2xl']) {
    assert.match(page, new RegExp('sc-token-space-' + token));
    assert.match(styles, new RegExp('calc\\(var\\(--wa-space-' + token + '\\)'));
  }
  for (const token of ['s', 'm', 'l', 'pill']) {
    assert.match(page, new RegExp('sc-token-radius-' + token));
    assert.match(styles, new RegExp('--wa-border-radius-' + token + '\\)'));
  }
  for (const token of ['s', 'm', 'l']) {
    assert.match(page, new RegExp('sc-token-shadow-' + token));
    assert.match(styles, new RegExp('--wa-shadow-' + token + '\\)'));
  }
  assert.doesNotMatch(page, /\{anywidget\}|<script\b|<iframe\b/i);
  assert.doesNotMatch(page, /data-demo-action|javascript:/i);
});

test('real SSR components are reused rather than visually approximated', () => {
  assert.match(page, /:::*\{wa-card\}/);
  assert.match(page, /:::*\{wa-callout\}/);
  assert.equal((page.match(/:::*\{wa-button\}/g) || []).length, 2);
  assert.ok(styles.includes('/* Standalone Design Tokens & Style Preview'));
  assert.match(styles, /\.sc-token-preview-grid/);
  assert.match(styles, /@media print/);
  assert.match(styles, /@media \(max-width: 460px\)/);
  assert.match(page, /\[Official Web Awesome design tokens\]\(https:\/\/webawesome\.com\/docs\/tokens\/\)/);
});
