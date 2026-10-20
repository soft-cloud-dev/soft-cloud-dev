import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';

const root = process.cwd();
const read = path => readFileSync(join(root, path), 'utf8');
const page = read('components/design-tokens.md');
const css = read('assets/static/softcloud.css');
const toc = read('myst.yml');
const index = read('components/index.md');

const families = [
  'Color',
  'Typography',
  'Space',
  'Borders',
  'Shadows',
  'Focus',
  'Transitions',
  'Component Groups',
];
const palette = [
  'red', 'orange', 'yellow', 'green', 'cyan',
  'blue', 'indigo', 'purple', 'pink', 'gray',
];
const variants = ['brand', 'neutral', 'success', 'warning', 'danger'];
const sizes = ['3xs', '2xs', 'xs', 's', 'm', 'l', 'xl', '2xl', '3xl', '4xl', '5xl'];

test('Frontmatter remains parseable by the strict MyST profile', () => {
  assert.match(page, /^---\ndescription: >-\n  Live reference for Web Awesome design tokens in SoftCloud:/);
  assert.match(page, /\n---\n\n# Design Tokens\n/);
});

test('Design Tokens page is discoverable and covers all eight token groups', () => {
  assert.match(toc, /- file: components\/design-tokens\.md/);
  assert.match(index, /\[Design tokens\]\(design-tokens\.md\)/);
  for (const title of families) {
    const slug = title.toLowerCase().replaceAll(' ', '-');
    assert.ok(page.includes('\n## ' + title + '\n'), 'Missing family: ' + title);
    assert.ok(page.includes('](#' + slug + ')'), 'Missing jump link: ' + title);
    assert.ok(
      page.includes('https://webawesome.com/docs/tokens/' + slug + '/'),
      'Missing upstream source: ' + title
    );
  }
});

test('Swatches use paired on-colors from the active theme, not fixed screenshot colors', () => {
  assert.match(css, /\.sc-tokens__patch\s*{/);
  assert.match(css, /background: var\(--sc-token-color/);
  assert.match(css, /color: var\(--sc-token-on/);
  for (const name of [...palette, ...variants]) {
    assert.ok(
      page.includes('sc-tokens__swatch--' + name),
      'Missing rendered swatch: ' + name
    );
    assert.ok(
      css.includes('sc-tokens__swatch--' + name),
      'Missing CSS mapping: ' + name
    );
    assert.ok(
      css.includes('--wa-color-' + name + '-on'),
      'Missing readable foreground: ' + name
    );
  }
});

test('Space scale uses actual Web Awesome variables and is mobile-safe', () => {
  for (const size of sizes) {
    assert.ok(page.includes('--wa-space-' + size));
    assert.ok(page.includes('sc-tokens__space-bar--' + size));
    assert.ok(css.includes('--sc-space-length: var(--wa-space-' + size + ')'));
  }
  assert.match(css, /grid-template-columns: minmax\(/);
  assert.match(css, /width: min\(100%, var\(--sc-space-length/);
  assert.match(css, /@media \(max-width: 460px\)/);
});

test('Document remains readable without JavaScript or external demo media', () => {
  assert.match(page, /type="text"\s+placeholder="Tab to focus this field"/);
  assert.match(page, /<fieldset class="sc-tokens__native-form">/);
  assert.match(page, /<figure class="sc-tokens__swatch/);
  assert.match(page, /```css\n\.feature-panel/);
  assert.match(page, /```\{anywidget\} \.\.\/widgets\/webawesome-demo\.mjs/);
  assert.doesNotMatch(page, /(?:src|href)="\/static\//);
  assert.doesNotMatch(page, /<script[\s>]/);
});

test('Focus and motion preserve keyboard use and reduced-motion preference', () => {
  assert.match(css, /\.sc-tokens__focus-example input:focus-visible/);
  assert.match(css, /outline: var\(--wa-focus-ring/);
  assert.match(css, /outline-offset: var\(--wa-focus-ring-offset/);
  assert.match(css, /\.sc-tokens__motion:is\(:hover, :focus-visible\)/);
  assert.match(css, /@media \(prefers-reduced-motion: reduce\)/);
  assert.match(css, /\.sc-tokens__motion, \.sc-tokens__motion span \{ transition: none !important; \}/);
});

test('SSR typed primitives and interactive atoms reuse the existing integration', () => {
  assert.match(page, /:::\{wa-card\}/);
  assert.match(page, /:::\{wa-callout\}/);
  assert.match(page, /:::\{wa-button\}/);
  for (const element of ['wa-input', 'wa-select', 'wa-option', 'wa-checkbox']) {
    assert.ok(page.includes('"tag": "' + element + '"'));
    assert.ok(page.includes('<' + element));
  }
  assert.match(page, /--wa-panel-border-radius/);
  assert.match(page, /--wa-form-control-background-color/);
});
