/**
 * tests/transform/test-placeholder-transform.mjs
 * Unit tests verifying placeholder transformation into custom elements.
 */

import test from 'node:test';
import assert from 'node:assert/strict';
import { transformPlaceholders } from '../../scripts/lib/placeholder-transform.mjs';

test('Transforms wa-card placeholder preserving light DOM and slots', () => {
  const input = `
<div class="sc-wa-host sc-wa-card my-card-class">
  <span class="sc-wa-meta" style="display:none">{"schema_version":"1.0.0","component":"wa-card","header":"Card Title","image":"/images/logo.png","image_alt":"Logo","appearance":"elevated"}</span>
  <p>First paragraph with <b>bold text</b>.</p>
  <!-- comment inside card -->
  <ul><li>Item 1</li></ul>
</div>`;

  const { html, transformedCount } = transformPlaceholders(input, { isFragment: true });
  assert.equal(transformedCount, 1);
  assert.ok(html.includes('<wa-card'));
  assert.ok(!html.includes('sc-wa-host'));
  assert.ok(!html.includes('sc-wa-meta'));
  assert.ok(html.includes('appearance="filled-outlined"'));
  assert.ok(html.includes('with-header'));
  assert.ok(html.includes('with-media'));
  assert.ok(html.includes('<img slot="media" src="/images/logo.png" alt="Logo">'));
  assert.ok(html.includes('<div slot="header">Card Title</div>'));
  assert.ok(html.includes('<p>First paragraph with <b>bold text</b>.</p>'));
  assert.ok(html.includes('<!-- comment inside card -->'));
  assert.ok(html.includes('<ul><li>Item 1</li></ul>'));
  assert.ok(html.includes('sc-elevation'));
  assert.ok(html.includes('my-card-class'));
});

test('Transforms wa-callout placeholder with slots and variant', () => {
  const input = `
<div class="sc-wa-host sc-wa-callout">
  <span class="sc-wa-meta">{"schema_version":"1.0.0","component":"wa-callout","variant":"brand","appearance":"soft","icon":"info","title":"Notice"}</span>
  <p>Callout description text.</p>
</div>`;

  const { html, transformedCount } = transformPlaceholders(input, { isFragment: true });
  assert.equal(transformedCount, 1);
  assert.ok(html.includes('<wa-callout'));
  assert.ok(html.includes('variant="brand"'));
  assert.ok(html.includes('appearance="filled-outlined"'));
  assert.ok(!html.includes('icon="info"'));
  assert.ok(html.includes('<wa-icon slot="icon" name="circle-info"'));
  assert.ok(html.includes('<div class="sc-wa-callout-content">'));
  assert.ok(html.includes('<strong class="sc-wa-callout-title">Notice</strong>'));
  assert.ok(html.includes('<p>Callout description text.</p>'));
});

test('Transforms wa-button placeholder with link attributes', () => {
  const input = `
<div class="sc-wa-host sc-wa-button">
  <span class="sc-wa-meta">{"schema_version":"1.0.0","component":"wa-button","variant":"primary","href":"https://my.softcloud.dev/docs","target":"_blank","rel":"noopener noreferrer"}</span>
  Explore Docs
</div>`;

  const { html, transformedCount } = transformPlaceholders(input, { isFragment: true });
  assert.equal(transformedCount, 1);
  assert.ok(html.includes('<wa-button'));
  assert.ok(html.includes('variant="brand"'));
  assert.ok(html.includes('href="https://my.softcloud.dev/docs"'));
  assert.ok(html.includes('target="_blank"'));
  assert.ok(html.includes('rel="noopener noreferrer"'));
  assert.ok(html.includes('Explore Docs'));
});

test('Transforms inline wa-icon placeholder', () => {
  const input = `
<p>Prefix <span class="sc-wa-host sc-wa-icon"><span class="sc-wa-meta">{"schema_version":"1.0.0","component":"wa-icon","name":"rocket","style":"solid","family":"classic"}</span></span> suffix.</p>`;

  const { html, transformedCount } = transformPlaceholders(input, { isFragment: true });
  assert.equal(transformedCount, 1);
  assert.ok(html.includes('<wa-icon name="rocket" family="classic" variant="solid" aria-hidden="true"></wa-icon>'));
  assert.ok(!html.includes('style="solid"'));
  assert.ok(html.includes('Prefix '));
  assert.ok(html.includes(' suffix.'));
});

test('Transforms nested components (button inside card)', () => {
  const input = `
<div class="sc-wa-host sc-wa-card">
  <span class="sc-wa-meta">{"schema_version":"1.0.0","component":"wa-card","header":"Card With Button"}</span>
  <p>Inside card:</p>
  <div class="sc-wa-host sc-wa-button">
    <span class="sc-wa-meta">{"schema_version":"1.0.0","component":"wa-button","variant":"success","href":"/action"}</span>
    Action
  </div>
</div>`;

  const { html, transformedCount } = transformPlaceholders(input, { isFragment: true });
  assert.equal(transformedCount, 2);
  assert.ok(html.includes('<wa-card'));
  assert.ok(html.includes('<wa-button variant="success" href="/action">'));
  assert.ok(html.includes('Action'));
  assert.ok(html.includes('</wa-button>'));
  assert.ok(!html.includes('sc-wa-host'));
});

test('Maps button caret metadata to the Web Awesome 3.14 attribute', () => {
  const input = '<div class="sc-wa-host sc-wa-button"><span class="sc-wa-meta">{"schema_version":"1.0.0","component":"wa-button","caret":true}</span>Menu</div>';
  const { html } = transformPlaceholders(input, { isFragment: true });
  assert.ok(html.includes('<wa-button with-caret="">'));
  assert.ok(!html.includes(' caret='));
});
