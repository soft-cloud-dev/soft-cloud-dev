import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const original = readFileSync(new URL('../../assets/static/silhouette-pink-original.svg', import.meta.url), 'utf8');
const animated = readFileSync(new URL('../../assets/static/softcloud-campaign.svg', import.meta.url), 'utf8');
const introduction = readFileSync(new URL('../../introduction.md', import.meta.url), 'utf8');

test('SoftCloud animation preserves the supplied original silhouette and cords', () => {
  const originalSilhouette = original.match(/<path id="sil"[^>]*d="([^"]+)"/)?.[1];
  const originalCords = original.match(/<g id="cords"[\s\S]*?<\/g>/)?.[0];
  assert.ok(originalSilhouette, 'source silhouette path must exist');
  assert.ok(originalCords, 'source cord paths must exist');
  assert.ok(animated.includes(originalSilhouette), 'original silhouette path changed');
  assert.ok(animated.includes(originalCords), 'original headphone cord paths changed');
});

test('SoftCloud animation has branding, accessibility and reduced motion', () => {
  assert.match(animated, /@keyframes dance/);
  assert.match(animated, /prefers-reduced-motion/);
  assert.match(animated, /role="img"/);
  assert.match(animated, /aria-labelledby="campaign-title campaign-desc"/);
  assert.match(animated, /softcloud\.dev/);
  assert.match(animated, /Build\./);
  assert.match(animated, /Deploy\./);
  assert.match(animated, /Scale\./);
  assert.doesNotMatch(animated, /<script\b|\bonload\s*=|javascript:/i);
  assert.doesNotMatch(animated, /<c2pa:manifest>/);
});

test('Introduction campaign is mounted only by its widget without altering narrated Markdown', () => {
  const widget = readFileSync(new URL('../../widgets/voice-player.mjs', import.meta.url), 'utf8');
  assert.match(introduction, /\{anywidget\} \.\/widgets\/voice-player\.mjs/);
  assert.doesNotMatch(introduction, /softcloud-campaign\.svg/);
  assert.match(widget, /model\.get\("page"\) === "introduction"/);
  assert.match(widget, /campaignImage\.src = "\/assets\/static\/softcloud-campaign\.svg"/);
  assert.match(widget, /campaignImage\.alt = "/);
  assert.match(widget, /campaignFigure\?\.remove\(\)/);
});
