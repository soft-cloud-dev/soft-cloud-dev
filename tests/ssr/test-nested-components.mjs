/**
 * tests/ssr/test-nested-components.mjs
 * Validates post-order rendering of nested components and repeated transformation idempotence.
 */

import test from 'node:test';
import assert from 'node:assert/strict';
import { transformAndRenderSSR } from '../../scripts/lit-ssr-transform.mjs';
import { parse } from 'parse5';
import { validateDocumentDSD } from '../../scripts/lib/dsd-validator.mjs';

test('Processes deeply nested components in post-order attaching DSD to all', () => {
  const doc = `<!DOCTYPE html>
<html>
<head><title>Nested Test</title></head>
<body>
  <div class="sc-wa-host sc-wa-card">
    <span class="sc-wa-meta">{"schema_version":"1.0.0","component":"wa-card","header":"Outer Card"}</span>
    <p>Card intro</p>
    <div class="sc-wa-host sc-wa-callout">
      <span class="sc-wa-meta">{"schema_version":"1.0.0","component":"wa-callout","variant":"brand","title":"Nested Callout"}</span>
      <p>Inside callout:</p>
      <div class="sc-wa-host sc-wa-button">
        <span class="sc-wa-meta">{"schema_version":"1.0.0","component":"wa-button","variant":"success","href":"/nested"}</span>
        Button with <span class="sc-wa-host sc-wa-icon"><span class="sc-wa-meta">{"schema_version":"1.0.0","component":"wa-icon","name":"rocket"}</span></span>
      </div>
    </div>
  </div>
</body>
</html>`;

  const { html, transformedCount, ssrCount } = transformAndRenderSSR(doc);
  assert.equal(transformedCount, 4, 'Expected 4 placeholders transformed');
  assert.equal(ssrCount, 4, 'Expected 4 components received DSD');

  // Validate AST
  const ast = parse(html);
  const docRes = validateDocumentDSD(ast);
  assert.equal(docRes.valid, true, `Errors: ${docRes.errors.join('; ')}`);
  assert.equal(docRes.totalHosts, 4);
  assert.equal(docRes.dsdCount, 4);

  // Assert nesting hierarchy preserved
  assert.ok(html.includes('<wa-card'));
  assert.ok(html.includes('<wa-callout'));
  assert.ok(html.includes('<wa-button'));
  assert.ok(html.includes('<wa-icon'));
});

test('Repeated transformation is byte-identical (idempotence gate G5)', () => {
  const doc = `<!DOCTYPE html>
<html>
<head><title>Idempotence Test</title></head>
<body>
  <div class="sc-wa-host sc-wa-card">
    <span class="sc-wa-meta">{"schema_version":"1.0.0","component":"wa-card","header":"Test"}</span>
    <p>Card content</p>
  </div>
  <div class="sc-wa-host sc-wa-button">
    <span class="sc-wa-meta">{"schema_version":"1.0.0","component":"wa-button","variant":"primary"}</span>
    Click
  </div>
</body>
</html>`;

  // First pass
  const pass1 = transformAndRenderSSR(doc);
  assert.equal(pass1.transformedCount, 2);
  assert.equal(pass1.ssrCount, 2);

  // Second pass on pass1 output
  const pass2 = transformAndRenderSSR(pass1.html);
  assert.equal(pass2.transformedCount, 0, 'No remaining placeholders to transform');
  assert.equal(pass2.ssrCount, 0, 'No un-SSR hosts to render');
  assert.equal(pass2.html, pass1.html, 'Second pass must be byte-identical');

  // Third pass
  const pass3 = transformAndRenderSSR(pass2.html);
  assert.equal(pass3.html, pass1.html, 'Third pass must be byte-identical');
});
