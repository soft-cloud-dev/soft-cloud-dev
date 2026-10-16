/**
 * tests/assets/test-base-paths.mjs
 * Unit tests verifying base-path-aware URL generation and exactly-once asset injection.
 */

import test from 'node:test';
import assert from 'node:assert/strict';
import { parse, serialize } from 'parse5';

import { injectRuntimeAssets, normalizeBaseUrl } from '../../scripts/lib/asset-injection.mjs';

test('normalizeBaseUrl formats paths correctly', () => {
  assert.equal(normalizeBaseUrl(''), '');
  assert.equal(normalizeBaseUrl('/'), '');
  assert.equal(normalizeBaseUrl('/docs'), '/docs');
  assert.equal(normalizeBaseUrl('/docs/'), '/docs');
  assert.equal(normalizeBaseUrl('docs/'), '/docs');
});

test('Injects assets exactly once with root base URL', () => {
  const doc = `<!DOCTYPE html><html><head><title>Root Base</title></head><body><p>Hello</p></body></html>`;
  const ast = parse(doc);

  const res1 = injectRuntimeAssets(ast, '');
  assert.equal(res1.injectedStylesheets.length, 3);
  assert.equal(res1.injectedScripts.length, 2);

  const html1 = serialize(ast);
  assert.ok(html1.includes('href="/vendor/webawesome/styles/webawesome.css"'));
  assert.ok(html1.includes('src="/vendor/webawesome/webawesome.ssr-loader.js"'));

  // Second injection pass on the same AST should inject 0 new assets (exactly-once)
  const res2 = injectRuntimeAssets(ast, '');
  assert.equal(res2.injectedStylesheets.length, 0);
  assert.equal(res2.injectedScripts.length, 0);

  const html2 = serialize(ast);
  assert.equal(html2, html1);
});

test('Injects assets correctly with /docs prefix', () => {
  const doc = `<!DOCTYPE html><html><head><title>Prefix</title></head><body></body></html>`;
  const ast = parse(doc);

  injectRuntimeAssets(ast, '/docs');
  const html = serialize(ast);

  assert.ok(html.includes('href="/docs/vendor/webawesome/styles/webawesome.css"'));
  assert.ok(html.includes('href="/docs/vendor/fontawesome/css/all.min.css"'));
  assert.ok(html.includes('href="/docs/static/softcloud.css"'));
  assert.ok(html.includes('src="/docs/vendor/webawesome/webawesome.ssr-loader.js"'));
  assert.ok(html.includes('src="/docs/static/softcloud-theme.js"'));
});

test('Prevents loading both standard and SSR autoloaders', () => {
  const docWithStandard = `<!DOCTYPE html><html><head><script src="/vendor/webawesome/webawesome.loader.js"></script></head><body></body></html>`;
  const ast = parse(docWithStandard);

  injectRuntimeAssets(ast, '');
  const html = serialize(ast);

  assert.ok(html.includes('webawesome.ssr-loader.js'));
  assert.ok(!html.includes('webawesome.loader.js'), 'Standard autoloader must be removed');
});
