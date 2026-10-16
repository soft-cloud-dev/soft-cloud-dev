/**
 * tests/transform/test-transform-idempotence.mjs
 * Tests idempotence of placeholder transformation.
 */

import test from 'node:test';
import assert from 'node:assert/strict';
import { transformPlaceholders } from '../../scripts/lib/placeholder-transform.mjs';

test('Second pass on transformed HTML produces identical output (idempotence)', () => {
  const fullDocument = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Test Page</title>
</head>
<body>
  <h1>Page Title</h1>
  <div class="sc-wa-host sc-wa-card">
    <span class="sc-wa-meta">{"schema_version":"1.0.0","component":"wa-card","header":"Card 1"}</span>
    <p>Card body with <span class="sc-wa-host sc-wa-icon"><span class="sc-wa-meta">{"schema_version":"1.0.0","component":"wa-icon","name":"star"}</span></span> icon.</p>
  </div>
  <div class="sc-wa-host sc-wa-button">
    <span class="sc-wa-meta">{"schema_version":"1.0.0","component":"wa-button","variant":"primary","href":"/docs"}</span>
    Documentation
  </div>
</body>
</html>`;

  // First pass: transforms placeholders into custom elements
  const pass1 = transformPlaceholders(fullDocument);
  assert.equal(pass1.transformedCount, 3);
  assert.ok(!pass1.html.includes('sc-wa-host'));

  // Second pass: should find 0 placeholders and produce identical bytes
  const pass2 = transformPlaceholders(pass1.html);
  assert.equal(pass2.transformedCount, 0);
  assert.equal(pass2.html, pass1.html);
});

test('Safe to run on documents with zero components', () => {
  const plainHtml = `<!DOCTYPE html><html><head><title>No Components</title></head><body><p>Hello World</p></body></html>`;
  const res = transformPlaceholders(plainHtml);
  assert.equal(res.transformedCount, 0);
  // Re-parsing and serializing plain HTML is stable
  const res2 = transformPlaceholders(res.html);
  assert.equal(res2.html, res.html);
});
