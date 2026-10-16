/**
 * tests/assets/test-asset-staging.mjs
 * Unit tests verifying self-hosted runtime asset staging.
 */

import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import { stageAssets } from '../../scripts/stage-webawesome-assets.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const tmpStageDir = path.resolve(__dirname, '../../_build/test-staging');

test('Stages Web Awesome dist-cdn, Font Awesome, and SoftCloud assets', () => {
  if (fs.existsSync(tmpStageDir)) {
    fs.rmSync(tmpStageDir, { recursive: true, force: true });
  }

  const { destRoot, stagedCount } = stageAssets(tmpStageDir);
  assert.equal(destRoot, tmpStageDir);
  assert.equal(stagedCount, 5);

  const filesToCheck = [
    'vendor/webawesome/webawesome.ssr-loader.js',
    'vendor/webawesome/styles/webawesome.css',
    'vendor/fontawesome/css/all.min.css',
    'vendor/fontawesome/webfonts/fa-solid-900.woff2',
    'static/softcloud.css',
    'static/softcloud-theme.js',
  ];

  for (const rel of filesToCheck) {
    const p = path.join(tmpStageDir, rel);
    assert.ok(fs.existsSync(p), `Missing staged file: ${rel}`);
    assert.ok(fs.statSync(p).size > 0, `Staged file is empty: ${rel}`);
  }

  // Cleanup
  fs.rmSync(tmpStageDir, { recursive: true, force: true });
});
