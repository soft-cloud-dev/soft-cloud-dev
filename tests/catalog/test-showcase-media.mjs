import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync, statSync } from 'node:fs';
import { join } from 'node:path';

const ROOT = process.cwd();
const FENCE = String.fromCharCode(96).repeat(3);
const rootFile = relative => join(ROOT, relative);
const text = relative => readFileSync(rootFile(relative), 'utf8');
const binaryAssets = [
  ['rocket.jpg', Buffer.from([0xff, 0xd8, 0xff])],
  ['coffee.png', Buffer.from([0x89, 0x50, 0x4e, 0x47])],
  ['astronaut.png', Buffer.from([0x89, 0x50, 0x4e, 0x47])],
  ['hubble-deep-field.jpg', Buffer.from([0xff, 0xd8, 0xff])]
];
const pages = [
  'components/media/carousel.md',
  'components/media/carousel-item.md',
  'components/media/comparison.md',
  'components/media/avatar.md',
  'components/media/animated-image.md',
  'components/media/zoomable-frame.md',
  'components/layout/card.md',
  'components/layout/scroller.md',
  'components/navigation/tab-group.md',
  'components/navigation/tab.md',
  'components/navigation/tab-panel.md'
];
const remoteMedia = new Set([
  'https://shoelace.style/assets/images/walk.gif',
  'https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4'
]);

function parseLiveTree(markdown, file) {
  const marker = FENCE + '{anywidget} ../../widgets/webawesome-demo.mjs\n';
  const start = markdown.indexOf(marker);
  assert.ok(start >= 0, file + ' has no preview');
  const from = start + marker.length;
  const end = markdown.indexOf('\n' + FENCE, from);
  assert.ok(end > from, file + ' preview fence not closed');
  return JSON.parse(markdown.slice(from, end)).tree;
}

function visit(node, cb) {
  if (Array.isArray(node)) return node.forEach(child => visit(child, cb));
  if (typeof node === 'string' || !node) return;
  cb(node);
  for (const child of node.children || []) visit(child, cb);
}

test('real-media showcase assets are bundled and valid binary files', () => {
  const manifest = text('assets/static/showcase/README.md');
  for (const [name, magic] of binaryAssets) {
    const path = rootFile('assets/static/showcase/' + name);
    assert.ok(existsSync(path), path);
    assert.ok(statSync(path).size > 10000, path + ' is too small');
    const data = readFileSync(path);
    assert.ok(data.subarray(0, magic.length).equals(magic), name + ' has invalid file signature');
    assert.ok(manifest.includes(String.fromCharCode(96) + name + String.fromCharCode(96)), name + ' missing attribution');
  }
  const gallery = text('assets/static/showcase/gallery.html');
  assert.match(gallery, /default-src 'none'/);
  assert.doesNotMatch(gallery, /<script\b/i);
  for (const [name] of binaryAssets) assert.ok(gallery.includes('./' + name));
});

test('media documentation uses actual, attributable sources and safe anywidget trees', () => {
  let localCount = 0;
  let videos = 0;
  let gifCount = 0;
  for (const file of pages) {
    const md = text(file);
    const tree = parseLiveTree(md, file);
    const html = md.slice(md.indexOf('## Markdown code snippet'));
    let pageMediaCount = 0;
    visit(tree, node => {
      const attrs = node.attrs || {};
      if (node.tag === 'img') {
        assert.ok(typeof attrs.alt === 'string' && attrs.alt.length >= 8, file + ' img missing alt');
      }
      if (node.tag === 'wa-avatar' && attrs.image) {
        assert.ok(typeof attrs.label === 'string' && attrs.label.length > 0, file + ' avatar missing label');
      }
      if (node.tag === 'wa-zoomable-frame') {
        assert.ok(typeof attrs.label === 'string' && attrs.label.length > 0, file + ' frame missing label');
      }
      if (node.tag === 'video') {
        videos++;
        assert.equal(attrs.preload, 'metadata');
        assert.ok(Object.hasOwn(attrs, 'controls'));
        assert.ok(attrs['aria-label']);
      }
      for (const key of ['src', 'image']) {
        const value = attrs[key];
        if (typeof value !== 'string') continue;
        if (value.startsWith('/static/showcase/')) {
          const relative = 'assets' + value;
          assert.ok(existsSync(rootFile(relative)), file + ' references missing file ' + relative);
          const portable = './images/' + value.slice('/static/showcase/'.length);
          assert.ok(html.includes(value) || html.includes(portable), file + ' source and rendered snippet differ: ' + value);
          localCount++;
          pageMediaCount++;
        } else if (value.startsWith('https://')) {
          assert.ok(remoteMedia.has(value), file + ' uses an undocumented external media URL: ' + value);
          assert.ok(html.includes(value), file + ' source and rendered snippet differ: ' + value);
          if (value.endsWith('.gif')) gifCount++;
          pageMediaCount++;
        } else if (node.tag === 'img' || node.tag === 'video' || node.tag === 'source' || node.tag === 'wa-animated-image') {
          assert.fail(file + ' has an invalid or placeholder media URL: ' + value);
        }
      }
    });
    assert.ok(pageMediaCount > 0, file + ' contains no actual media');
  }
  assert.ok(localCount >= 20, 'expected substantial reuse of self-hosted photographs');
  assert.ok(videos >= 1, 'playable native video demo missing');
  assert.ok(gifCount >= 1, 'actual animated-image demo missing');
});

test('catalog widget supports safe media and required image layouts', () => {
  const s = text('widgets/webawesome-demo.mjs');
  for (const term of ["'video'", "'source'", "'loop'", "'mouse-dragging'", "'image'", "'loading'", "'zoom'"]) {
    assert.ok(s.includes(term), 'missing preview media support ' + term);
  }
  assert.ok(s.includes('document.createElement'));
  assert.ok(s.includes('document.createTextNode'));
  assert.ok(s.includes('validUrl.test'));
  assert.ok(s.includes('.sc-demo-grayscale'));
  assert.ok(!s.includes('innerHTML'));
});