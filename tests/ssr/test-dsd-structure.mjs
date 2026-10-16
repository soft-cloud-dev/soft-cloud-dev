/**
 * tests/ssr/test-dsd-structure.mjs
 * Validates DSD structure, did-ssr consistency, and light-DOM preservation.
 */

import test from 'node:test';
import assert from 'node:assert/strict';
import { parse } from 'parse5';
import { transformAndRenderSSR } from '../../scripts/lit-ssr-transform.mjs';
import { validateHostDSD, validateDocumentDSD } from '../../scripts/lib/dsd-validator.mjs';

test('Transforms document, attaches DSD, adds did-ssr and preserves light DOM', () => {
  const doc = `<!DOCTYPE html>
<html>
<head><title>DSD Test</title></head>
<body>
  <div class="sc-wa-host sc-wa-button">
    <span class="sc-wa-meta">{"schema_version":"1.0.0","component":"wa-button","variant":"primary","href":"/docs"}</span>
    <span class="custom-label">Read Documentation</span>
  </div>
</body>
</html>`;

  const { html, transformedCount, ssrCount } = transformAndRenderSSR(doc);
  assert.equal(transformedCount, 1);
  assert.equal(ssrCount, 1);

  // Assert DSD template attached and did-ssr present
  assert.ok(html.includes('<wa-button'));
  assert.ok(html.includes('did-ssr=""') || html.includes('did-ssr'));
  assert.ok(html.includes('shadowrootmode="open"'));
  assert.ok(html.includes('<span class="custom-label">Read Documentation</span>'));

  // Validate AST structure with dsd-validator
  const ast = parse(html);
  const docRes = validateDocumentDSD(ast);
  assert.equal(docRes.valid, true, `Errors: ${docRes.errors.join('; ')}`);
  assert.equal(docRes.totalHosts, 1);
  assert.equal(docRes.dsdCount, 1);
});

test('Rejects host having did-ssr without DSD template', () => {
  const malformed = `<!DOCTYPE html><html><body><wa-button did-ssr>No template</wa-button></body></html>`;
  const ast = parse(malformed);
  const docRes = validateDocumentDSD(ast);
  assert.equal(docRes.valid, false);
  assert.ok(docRes.errors[0].includes("missing a valid DSD template"));
});

test('Rejects host having multiple direct DSD templates', () => {
  const doubleTpl = `<!DOCTYPE html><html><body>
<wa-button did-ssr>
  <template shadowrootmode="open"><style></style></template>
  <template shadowrootmode="open"><style></style></template>
</wa-button>
</body></html>`;
  const ast = parse(doubleTpl);
  const docRes = validateDocumentDSD(ast);
  assert.equal(docRes.valid, false);
  assert.ok(docRes.errors[0].includes("multiple direct DSD templates"));
});
