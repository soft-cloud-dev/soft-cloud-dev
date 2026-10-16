/**
 * tests/ssr/test-lit-renderer.mjs
 * Unit tests verifying Lit SSR DSD extraction across all supported components.
 */

import test from 'node:test';
import assert from 'node:assert/strict';
import { renderComponentDSD } from '../../scripts/lib/lit-renderer.mjs';

test('Renders wa-button with authentic DSD template', () => {
  const { dsdTemplateNode, hostAttrs } = renderComponentDSD('wa-button', [
    { name: 'variant', value: 'primary' },
    { name: 'size', value: 'medium' },
  ]);

  assert.equal(dsdTemplateNode.tagName, 'template');
  const modeAttr = dsdTemplateNode.attrs.find(
    (a) => (a.name === 'shadowrootmode' || a.name === 'shadowroot') && a.value === 'open'
  );
  assert.ok(modeAttr, 'Expected shadowrootmode="open"');

  const content = dsdTemplateNode.content || dsdTemplateNode;
  assert.ok(content.childNodes.length > 0, 'Expected shadow DOM children');

  // Verify style tag in shadow root
  const hasStyle = content.childNodes.some((c) => c.tagName === 'style');
  assert.ok(hasStyle, 'Expected style element in shadow root');
});

test('Renders wa-card with authentic DSD template', () => {
  const { dsdTemplateNode } = renderComponentDSD('wa-card', [
    { name: 'appearance', value: 'elevated' },
  ]);
  assert.equal(dsdTemplateNode.tagName, 'template');
  assert.ok(dsdTemplateNode.attrs.some((a) => a.value === 'open'));
});

test('Renders wa-callout with authentic DSD template', () => {
  const { dsdTemplateNode } = renderComponentDSD('wa-callout', [
    { name: 'variant', value: 'brand' },
  ]);
  assert.equal(dsdTemplateNode.tagName, 'template');
  assert.ok(dsdTemplateNode.attrs.some((a) => a.value === 'open'));
});

test('Renders wa-icon with authentic DSD template', () => {
  const { dsdTemplateNode } = renderComponentDSD('wa-icon', [
    { name: 'name', value: 'rocket' },
    { name: 'style', value: 'solid' },
  ]);
  assert.equal(dsdTemplateNode.tagName, 'template');
  assert.ok(dsdTemplateNode.attrs.some((a) => a.value === 'open'));
});

test('Rejects unsupported component tag in renderer', () => {
  assert.throws(() => renderComponentDSD('wa-dialog', []), /Unsupported component/);
});
