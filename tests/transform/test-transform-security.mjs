/**
 * tests/transform/test-transform-security.mjs
 * Security tests for placeholder transformation (duplicate markers, unsafe URLs, injection).
 */

import test from 'node:test';
import assert from 'node:assert/strict';
import { transformPlaceholders } from '../../scripts/lib/placeholder-transform.mjs';

test('Rejects missing metadata span', () => {
  const input = `<div class="sc-wa-host sc-wa-card"><p>No metadata</p></div>`;
  assert.throws(() => transformPlaceholders(input, { isFragment: true }), /missing metadata span/);
});

test('Rejects duplicate metadata spans', () => {
  const input = `
<div class="sc-wa-host sc-wa-card">
  <span class="sc-wa-meta">{"schema_version":"1.0.0","component":"wa-card"}</span>
  <span class="sc-wa-meta">{"schema_version":"1.0.0","component":"wa-card"}</span>
</div>`;
  assert.throws(() => transformPlaceholders(input, { isFragment: true }), /duplicate metadata spans/);
});

test('Rejects malformed JSON in metadata span', () => {
  const input = `<div class="sc-wa-host sc-wa-card"><span class="sc-wa-meta">{bad_json}</span></div>`;
  assert.throws(() => transformPlaceholders(input, { isFragment: true }), /invalid JSON in metadata span/);
});

test('Rejects missing component marker class', () => {
  const input = `<div class="sc-wa-host"><span class="sc-wa-meta">{"schema_version":"1.0.0","component":"wa-card"}</span></div>`;
  assert.throws(() => transformPlaceholders(input, { isFragment: true }), /missing component marker class/);
});

test('Rejects marker class and metadata component mismatch', () => {
  const input = `<div class="sc-wa-host sc-wa-callout"><span class="sc-wa-meta">{"schema_version":"1.0.0","component":"wa-card"}</span></div>`;
  assert.throws(() => transformPlaceholders(input, { isFragment: true }), /Component mismatch/);
});

test('Rejects unsafe javascript href in button', () => {
  const input = `
<div class="sc-wa-host sc-wa-button">
  <span class="sc-wa-meta">{"schema_version":"1.0.0","component":"wa-button","href":"javascript:alert(1)"}</span>
  Click
</div>`;
  assert.throws(() => transformPlaceholders(input, { isFragment: true }), /violates URL policy/);
});

test('Rejects unknown fields in metadata', () => {
  const input = `
<div class="sc-wa-host sc-wa-card">
  <span class="sc-wa-meta">{"schema_version":"1.0.0","component":"wa-card","unauthorized_field":"dangerous"}</span>
</div>`;
  assert.throws(() => transformPlaceholders(input, { isFragment: true }), /Unknown field 'unauthorized_field'/);
});
