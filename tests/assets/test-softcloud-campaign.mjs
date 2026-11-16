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

test('Introduction references the checked-in animated SVG via a MyST figure', () => {
  assert.match(introduction, /:::\{figure\} assets\/static\/softcloud-campaign\.svg/);
  assert.match(introduction, /:alt: Animated Software Cloud advertisement/);
  assert.match(introduction, /:width: 100%/);
});
