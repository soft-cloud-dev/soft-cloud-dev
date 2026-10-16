#!/usr/bin/env node
/**
 * scripts/check-node-dependencies.mjs
 * Validates pinned Node dependencies, versions, and SSR entry points.
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(__dirname, '..');

const REQUIRED_VERSIONS = {
  '@awesome.me/webawesome': '3.14.0',
  '@lit-labs/ssr': '4.1.0',
  '@lit-labs/ssr-client': '1.1.8',
  'lit': '3.3.3',
  'parse5': '7.3.0',
  '@fortawesome/fontawesome-free': '6.5.2',
  '@playwright/test': '1.64.1',
};

// 1. Verify Node version
const nodeVersion = process.versions.node;
const [major] = nodeVersion.split('.').map(Number);
if (major < 20) {
  console.error(`[FAIL] Node 20+ required, current version is ${nodeVersion}`);
  process.exit(1);
}

// 2. Verify package versions from node_modules
for (const [pkgName, expectedVersion] of Object.entries(REQUIRED_VERSIONS)) {
  const pkgJsonPath = path.join(rootDir, 'node_modules', ...pkgName.split('/'), 'package.json');
  if (!fs.existsSync(pkgJsonPath)) {
    console.error(`[FAIL] Missing required package: ${pkgName}`);
    process.exit(1);
  }
  const pkg = JSON.parse(fs.readFileSync(pkgJsonPath, 'utf8'));
  if (pkg.version !== expectedVersion) {
    console.error(`[FAIL] Version mismatch for ${pkgName}: expected ${expectedVersion}, found ${pkg.version}`);
    process.exit(1);
  }
}

// 3. Verify module imports and exports
try {
  const { render } = await import('@lit-labs/ssr');
  if (typeof render !== 'function') throw new Error('@lit-labs/ssr render export missing');

  const { html, LitElement } = await import('lit');
  if (!html || !LitElement) throw new Error('lit html or LitElement export missing');

  const parse5 = await import('parse5');
  if (typeof parse5.parse !== 'function' || typeof parse5.serialize !== 'function') {
    throw new Error('parse5 parse/serialize export missing');
  }

  // Import components to register them in customElements registry
  await import('@awesome.me/webawesome/dist/components/button/button.js');
  await import('@awesome.me/webawesome/dist/components/callout/callout.js');
  await import('@awesome.me/webawesome/dist/components/card/card.js');
  await import('@awesome.me/webawesome/dist/components/icon/icon.js');

  // Verify static assets
  const ssrLoaderPath = path.join(rootDir, 'node_modules/@awesome.me/webawesome/dist/webawesome.ssr-loader.js');
  if (!fs.existsSync(ssrLoaderPath)) {
    throw new Error('Web Awesome SSR loader file missing at ' + ssrLoaderPath);
  }

  const faCssPath = path.join(rootDir, 'node_modules/@fortawesome/fontawesome-free/css/all.min.css');
  if (!fs.existsSync(faCssPath)) {
    throw new Error('Font Awesome CSS missing at ' + faCssPath);
  }

  const faWebfontsDir = path.join(rootDir, 'node_modules/@fortawesome/fontawesome-free/webfonts');
  if (!fs.existsSync(faWebfontsDir)) {
    throw new Error('Font Awesome webfonts directory missing at ' + faWebfontsDir);
  }

  const { test } = await import('@playwright/test');
  if (typeof test !== 'function') throw new Error('@playwright/test export missing');
} catch (err) {
  console.error(`[FAIL] Import/entry point verification failed:`, err);
  process.exit(1);
}

console.log(`[OK] All ${Object.keys(REQUIRED_VERSIONS).length} Node dependencies verified on Node ${nodeVersion}`);
