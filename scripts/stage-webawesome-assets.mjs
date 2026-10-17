#!/usr/bin/env node
/**
 * scripts/stage-webawesome-assets.mjs
 * Stages all Web Awesome, Font Awesome (including self-hosted SVGs),
 * and SoftCloud runtime static assets into the publication build directory.
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(__dirname, '..');

export function stageAssets(targetDir) {
  const destRoot = path.resolve(process.cwd(), targetDir);
  if (!fs.existsSync(destRoot)) {
    fs.mkdirSync(destRoot, { recursive: true });
  }

  // 1. Copy Web Awesome dist-cdn tree
  const waSrc = path.join(rootDir, 'node_modules/@awesome.me/webawesome/dist-cdn');
  const waDst = path.join(destRoot, 'vendor/webawesome');
  fs.mkdirSync(waDst, { recursive: true });
  fs.cpSync(waSrc, waDst, { recursive: true });

  // 2. Copy Font Awesome CSS and webfonts
  const faCssSrc = path.join(rootDir, 'node_modules/@fortawesome/fontawesome-free/css/all.min.css');
  const faWebfontsSrc = path.join(rootDir, 'node_modules/@fortawesome/fontawesome-free/webfonts');
  const faCssDst = path.join(destRoot, 'vendor/fontawesome/css/all.min.css');
  const faWebfontsDst = path.join(destRoot, 'vendor/fontawesome/webfonts');

  fs.mkdirSync(path.dirname(faCssDst), { recursive: true });
  fs.copyFileSync(faCssSrc, faCssDst);

  fs.mkdirSync(faWebfontsDst, { recursive: true });
  fs.cpSync(faWebfontsSrc, faWebfontsDst, { recursive: true });

  // 3. Copy Font Awesome SVGs (solid, regular, brands) for Web Awesome setIconPath() (WA-ICON-001)
  const faSvgsSrc = path.join(rootDir, 'node_modules/@fortawesome/fontawesome-free/svgs');
  const faSvgsDst = path.join(destRoot, 'vendor/fontawesome/svgs');
  fs.mkdirSync(faSvgsDst, { recursive: true });
  fs.cpSync(faSvgsSrc, faSvgsDst, { recursive: true });

  // Stage aliases for legacy icon names (e.g. info-circle -> circle-info)
  stageIconAliases(faSvgsDst);

  // 4. Copy SoftCloud static assets
  const staticSrc = path.join(rootDir, 'assets/static');
  const staticDst = path.join(destRoot, 'static');
  fs.mkdirSync(staticDst, { recursive: true });
  fs.cpSync(staticSrc, staticDst, { recursive: true });

  // Verification of key assets
  const expectedFiles = [
    path.join(destRoot, 'vendor/webawesome/webawesome.js'),
    path.join(destRoot, 'vendor/webawesome/webawesome.ssr-loader.js'),
    path.join(destRoot, 'vendor/webawesome/styles/webawesome.css'),
    path.join(destRoot, 'vendor/fontawesome/css/all.min.css'),
    path.join(destRoot, 'vendor/fontawesome/svgs/solid/server.svg'),
    path.join(destRoot, 'vendor/fontawesome/svgs/brands/github.svg'),
    path.join(destRoot, 'static/softcloud.css'),
    path.join(destRoot, 'static/softcloud-theme.js'),
    path.join(destRoot, 'static/softcloud-theme-init.js'),
    path.join(destRoot, 'static/softcloud-webawesome.mjs'),
  ];

  for (const f of expectedFiles) {
    if (!fs.existsSync(f)) {
      throw new Error(`Asset staging failed: missing expected file ${f}`);
    }
  }

  return { destRoot, stagedCount: expectedFiles.length };
}

function stageIconAliases(svgsDest) {
  const metaPath = path.join(rootDir, 'node_modules/@fortawesome/fontawesome-free/metadata/icon-families.json');
  if (!fs.existsSync(metaPath)) return;

  try {
    const data = JSON.parse(fs.readFileSync(metaPath, 'utf8'));
    const folders = ['solid', 'regular', 'brands'];

    for (const [canonical, info] of Object.entries(data)) {
      if (!info.aliases?.names) continue;

      for (const folder of folders) {
        const folderPath = path.join(svgsDest, folder);
        if (!fs.existsSync(folderPath)) continue;

        const canonicalFile = path.join(folderPath, `${canonical}.svg`);
        if (!fs.existsSync(canonicalFile)) continue;

        for (const alias of info.aliases.names) {
          const aliasFile = path.join(folderPath, `${alias}.svg`);
          if (!fs.existsSync(aliasFile)) {
            try {
              fs.copyFileSync(canonicalFile, aliasFile);
            } catch {
              // Ignore copy collision
            }
          }
        }
      }
    }
  } catch (err) {
    console.warn('[WARN] Staging icon aliases encountered warning:', err.message);
  }
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const target = process.argv[2] || '_build/html';
  try {
    const { destRoot } = stageAssets(target);
    console.log(`[OK] Runtime assets staged successfully to ${destRoot}`);
  } catch (err) {
    console.error(`[FAIL] Asset staging error:`, err);
    process.exit(1);
  }
}
