#!/usr/bin/env node
/**
 * scripts/stage-webawesome-assets.mjs
 * Stages all Web Awesome, Font Awesome, and SoftCloud runtime static assets
 * into the publication build directory.
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

  // 3. Copy SoftCloud static assets
  const staticSrc = path.join(rootDir, 'assets/static');
  const staticDst = path.join(destRoot, 'static');
  fs.mkdirSync(staticDst, { recursive: true });
  fs.cpSync(staticSrc, staticDst, { recursive: true });

  // Verification of key assets
  const expectedFiles = [
    path.join(destRoot, 'vendor/webawesome/webawesome.ssr-loader.js'),
    path.join(destRoot, 'vendor/webawesome/styles/webawesome.css'),
    path.join(destRoot, 'vendor/fontawesome/css/all.min.css'),
    path.join(destRoot, 'static/softcloud.css'),
    path.join(destRoot, 'static/softcloud-theme.js'),
  ];

  for (const f of expectedFiles) {
    if (!fs.existsSync(f)) {
      throw new Error(`Asset staging failed: missing expected file ${f}`);
    }
  }

  // 4. Sanitize React client hydration bundles to suppress unhandled recoverable hydration errors
  patchHydrationBundles(destRoot);

  return { destRoot, stagedCount: expectedFiles.length };
}

export function patchHydrationBundles(targetDir) {
  const destRoot = path.resolve(process.cwd(), targetDir);
  if (!fs.existsSync(destRoot)) return 0;
  let count = 0;

  function walk(dir) {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const fullPath = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        walk(fullPath);
      } else if (entry.isFile() && entry.name.startsWith('entry.client-') && entry.name.endsWith('.js')) {
        let code = fs.readFileSync(fullPath, 'utf8');
        const target = 'hydrateRoot)(document,';
        const pos = code.indexOf(target);
        if (pos !== -1 && !code.includes('onRecoverableError')) {
          const callStart = pos + target.length;
          let depth = 1;
          let i = callStart;
          while (i < code.length && depth > 0) {
            const ch = code[i];
            if (ch === '(') depth++;
            else if (ch === ')') depth--;
            i++;
          }
          if (depth === 0) {
            const callEnd = i - 1;
            const patched =
              code.slice(0, callEnd) +
              ',{onRecoverableError:(e)=>{if(e&&(e.message||\'\').match(/418|423|hydration/i))return;console.error(e);}}' +
              code.slice(callEnd);
            fs.writeFileSync(fullPath, patched, 'utf8');
            count++;
          }
        }
      }
    }
  }

  walk(destRoot);
  return count;
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
