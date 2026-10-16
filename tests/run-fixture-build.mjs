import { execSync } from 'node:child_process';
import { existsSync, mkdirSync, copyFileSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const rootDir = resolve(__dirname, '..');
const fixtureDir = resolve(rootDir, 'tests/fixtures/webawesome-book');
const fixtureBuildDir = resolve(fixtureDir, '_build/html');

console.log('[1/4] Building Jupyter Book fixture...');
const venvBin = resolve(rootDir, '.venv/bin');
const env = {
  ...process.env,
  PATH: `${venvBin}:${process.env.PATH || ''}`,
  PYTHONPATH: `${resolve(rootDir, 'assets/python')}:${process.env.PYTHONPATH || ''}`,
};

execSync(`"${resolve(venvBin, 'jupyter-book')}" build --html`, {
  cwd: fixtureDir,
  env,
  stdio: 'inherit',
});

// Ensure fixture assets (such as logo.svg) are in place
const fixtureImagesDir = resolve(fixtureBuildDir, 'images');
mkdirSync(fixtureImagesDir, { recursive: true });
const sourceLogo = resolve(rootDir, 'images/logo.svg');
if (existsSync(sourceLogo)) {
  copyFileSync(sourceLogo, resolve(fixtureImagesDir, 'logo.svg'));
}

console.log('[2/4] Staging runtime assets into fixture build...');
execSync(`node "${resolve(rootDir, 'scripts/stage-webawesome-assets.mjs')}" "${fixtureBuildDir}"`, {
  cwd: rootDir,
  env,
  stdio: 'inherit',
});

console.log('[3/4] Transforming placeholders to Lit SSR DSD...');
execSync(`node "${resolve(rootDir, 'scripts/lit-ssr-transform.mjs')}" "${fixtureBuildDir}" ""`, {
  cwd: rootDir,
  env,
  stdio: 'inherit',
});

console.log('[4/4] Validating fixture build...');
execSync(`"${resolve(venvBin, 'python')}" "${resolve(rootDir, 'scripts/validate-build.py')}" --verify-dir "${fixtureBuildDir}" --strict`, {
  cwd: rootDir,
  env,
  stdio: 'inherit',
});

console.log('[OK] Fixture build, SSR transformation, and validation completed successfully.');
