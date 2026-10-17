import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {join} from 'node:path';

const root = process.cwd();
const read = p => readFileSync(join(root,p), 'utf8');
const catalog = JSON.parse(read('components/catalog.json'));

test('90 component pages meet Core or portable-alternative contracts', () => {
  assert.equal(catalog.components.length, 90);
  const seen = new Set();
  for (const comp of catalog.components) {
    const path = 'components/' + comp.category + '/' + comp.slug + '.md';
    assert.ok(!seen.has(path), path);
    seen.add(path);
    const markdown = read(path);
    if (comp.pro) {
      assert.match(markdown, /Portable Alternative \(Non-Core\)/, path);
      assert.match(markdown, /description:/, path);
      assert.match(markdown, /tags:/, path);
      assert.doesNotMatch(markdown, /<wa-[a-z-]+\s/, path);
      assert.ok(!markdown.includes('\\`\\`\\`{anywidget}'), path);
      assert.ok(read('myst.yml').includes('file: ' + path), path + ' missing portable TOC');
      continue;
    }
    assert.match(markdown, /wiki:/);
    const sourceMatch = markdown.match(/^\*\*Source:\*\* \[[^\]]+\]\((https:\/\/[^)\s]+)\)/m);
    assert.ok(sourceMatch, path);
    assert.equal(new URL(sourceMatch[1]).hostname, 'github.com');
    assert.match(markdown, /## Markdown code snippet/);
    assert.ok(markdown.includes('<' + comp.tag), path);
    assert.match(markdown, /:::\{(?:note|warning)\} Integration status/);
    assert.ok(!markdown.includes(':::{wa-callout} Integration status'), path);
    if (comp.live) {
      assert.ok(markdown.includes('```{anywidget} ../../widgets/webawesome-demo.mjs'), path);
    } else {
      assert.ok(!markdown.includes('```{anywidget}'), path);
    }
    for (const dep of comp.deps) {
      assert.ok(markdown.includes('/' + dep + '.md)'), path + ' missing atom ' + dep);
    }
    assert.ok(read('myst.yml').includes('file: ' + path), path + ' missing TOC');
  }
});
test('widget uses only self-hosted modules and DOM constructors', () => {
  const code = read('widgets/webawesome-demo.mjs');
  assert.ok(code.includes('document.createElement'));
  assert.ok(code.includes('document.createTextNode'));
  assert.match(code, /new URL\('\.\.\/vendor\/webawesome\/', import\.meta\.url\)/);
  assert.doesNotMatch(code, /document\.querySelector\(['"]script\[src/);
  assert.ok(!code.includes('innerHTML'));
});
