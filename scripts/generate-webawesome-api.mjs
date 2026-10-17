import { readFileSync, existsSync, mkdirSync, writeFileSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const root = resolve(import.meta.dirname, '..');
const pkg = require('@awesome.me/webawesome/package.json');
const manifestPath = resolve(root, 'node_modules/@awesome.me/webawesome/custom-elements.json');
const catalog = JSON.parse(readFileSync(resolve(root, 'components/catalog.json'), 'utf8'));
if (!existsSync(manifestPath)) throw new Error('Missing installed Web Awesome custom-elements.json; do not synthesize API data');
const manifest = JSON.parse(readFileSync(manifestPath, 'utf8'));
const declarations = manifest.modules.flatMap(m => m.declarations || []).filter(d => d.customElement && d.tagName);
const byTag = new Map(declarations.map(d => [d.tagName, d]));
const cell = x => String(x ?? '').replaceAll('|', '\\|').replaceAll('\n', ' ').trim() || '—';
const section = (title, columns, rows) => [
  '### ' + title, '',
  '| ' + columns.join(' | ') + ' |',
  '| ' + columns.map(() => '---').join(' | ') + ' |',
  ...rows.map(row => '| ' + row.map(cell).join(' | ') + ' |'), ''
].join('\n');
const generated = [];
for (const component of catalog.components) {
  const decl = byTag.get(component.tag);
  if (!decl) {
    if (component.availability === 'Core' || component.availability === 'core') throw new Error('Missing Core component CEM entry: ' + component.tag);
    continue;
  }
  const out = [
    '# Generated API: `' + component.tag + '`', '',
    '> Generated from the installed Web Awesome ' + pkg.version + ' Custom Elements Manifest. Do not edit by hand.', '',
    section('Attributes', ['Attribute', 'Type', 'Default', 'Description'], (decl.attributes || []).map(a => [a.name, a.type?.text, a.default, a.description])),
    section('Events', ['Event', 'Type', 'Description'], (decl.events || []).map(a => [a.name, a.type?.text, a.description])),
    section('Slots', ['Slot', 'Description'], (decl.slots || []).map(a => [a.name || '(default)', a.description])),
    section('CSS properties', ['Property', 'Description'], (decl.cssProperties || []).map(a => [a.name, a.description])),
    section('CSS parts', ['Part', 'Description'], (decl.cssParts || []).map(a => [a.name, a.description]))
  ].join('\n');
  const path = resolve(root, 'components/generated-api', component.category, component.slug + '.md');
  generated.push([path, out]);
}
const check = process.argv.includes('--check');
let stale = 0;
for (const [path, body] of generated) {
  if (check) { if (!existsSync(path) || readFileSync(path, 'utf8') !== body) { console.error('Stale generated API: ' + path); stale++; } }
  else { mkdirSync(dirname(path), {recursive: true}); writeFileSync(path, body); }
}
console.log('Web Awesome ' + pkg.version + ': ' + generated.length + ' CEM-backed API files');
if (stale) process.exitCode = 1;
