import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const source = readFileSync(new URL('../../widgets/webawesome-demo.mjs', import.meta.url), 'utf8');

test('preview resolves vendor assets for root, prefixed, and file deployments', () => {
  assert.match(source, /return new URL\('\.\.\/vendor\/webawesome\/', import\.meta\.url\)/);
  const cases = [
    ['https://cdn.example.com/build/preview.js', 'https://cdn.example.com/vendor/webawesome/'],
    ['https://domain.org/nested/subpath/build/preview.js', 'https://domain.org/nested/subpath/vendor/webawesome/'],
    ['file:///workspace/project/build/preview.js', 'file:///workspace/project/vendor/webawesome/']
  ];
  for (const [moduleUrl, expected] of cases) {
    const root = new URL('../vendor/webawesome/', moduleUrl);
    assert.equal(root.href, expected);
    assert.equal(new URL('components/button/button.js', root).href, expected + 'components/button/button.js');
  }
});

test('showcase media tokens resolve across root and prefixed deployments', async () => {
  const { resolveShowcaseMedia } = await import('../../widgets/webawesome-demo.mjs');
  for (const [moduleUrl, expected] of [
    ['https://domain.org/build/preview.js', 'https://domain.org/static/showcase/rocket.jpg'],
    ['https://domain.org/docs/build/preview.js', 'https://domain.org/docs/static/showcase/rocket.jpg'],
    ['file:///workspace/project/build/preview.js', 'file:///workspace/project/static/showcase/rocket.jpg']
  ]) {
    assert.equal(resolveShowcaseMedia('showcase:rocket.jpg', moduleUrl), expected);
  }
  assert.equal(resolveShowcaseMedia('showcase:../../escape.jpg'), 'showcase:../../escape.jpg');
});

test('preview does not depend on loader elements or currentScript', () => {
  const runtimeRoot = source.match(/function runtimeRoot\(\) \{([\s\S]*?)\n\}/)?.[1];
  assert.ok(runtimeRoot, 'runtimeRoot must exist');
  assert.doesNotMatch(runtimeRoot, /document|currentScript|querySelector/);
  assert.match(runtimeRoot, /import\.meta\.url/);
  assert.match(source, /async render\(\{ model, el \}\)/);
  assert.doesNotMatch(source, /document\.querySelector/);
});

test('preview restricts dynamic imports and clears failed promises', () => {
  const catalog = JSON.parse(readFileSync(new URL('../../components/catalog.json', import.meta.url), 'utf8'));
  const live = catalog.components.filter(c => c.live && !c.pro && !c.sourceOnly).map(c => c.slug);
  const match = source.match(/const allowedComponents = new Set\((\[[^;]+\])\);/);
  assert.ok(match, 'allowlist must be explicit');
  assert.deepEqual(JSON.parse(match[1]).slice().sort(), live.slice().sort());
  assert.ok(!live.includes('pro-datagrid'));
  assert.match(source, /if \(!allowedComponents\.has\(name\)\) throw new Error/);
  assert.match(source, /moduleImports\.delete\(name\)/);
  assert.match(source, /Failed to import Web Awesome component/);
});
