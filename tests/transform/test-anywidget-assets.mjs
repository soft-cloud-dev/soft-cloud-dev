import test from 'node:test';
import assert from 'node:assert/strict';
import { transformAndRenderSSR } from '../../scripts/lit-ssr-transform.mjs';

test('anywidget-only component showcases receive self-hosted Web Awesome assets', () => {
  const source = '<!doctype html><html><head><title>Showcase</title></head>' +
    '<body><div data-widget="webawesome-demo.mjs"></div></body></html>';
  const { html, ssrCount } = transformAndRenderSSR(source, '/docs');

  assert.equal(ssrCount, 0, 'anywidget previews must not be misidentified as Lit SSR');
  assert.ok(html.includes('href="/docs/vendor/webawesome/styles/webawesome.css"'));
  assert.ok(html.includes('src="/docs/static/softcloud-webawesome.mjs"'));
  assert.ok(html.includes('src="/docs/static/softcloud-theme-init.js"'));
  assert.ok(html.includes('src="/docs/static/softcloud-theme.js"'));

  const again = transformAndRenderSSR(html, '/docs');
  assert.equal(again.html, html, 'asset injection must be idempotent');
  assert.equal(again.ssrCount, 0);
});

test('ordinary documents without Web Awesome content remain uninjected', () => {
  const source = '<!doctype html><html><head></head><body><p>Plain MyST content</p></body></html>';
  const { html, ssrCount } = transformAndRenderSSR(source);
  assert.equal(ssrCount, 0);
  assert.ok(!html.includes('softcloud-webawesome.mjs'));
});
