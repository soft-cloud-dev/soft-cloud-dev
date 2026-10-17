import { execSync } from 'node:child_process';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { existsSync } from 'node:fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const rootDir = resolve(__dirname, '..');
const venvBin = resolve(rootDir, '.venv/bin');
const env = {
  ...process.env,
  PATH: `${venvBin}:${process.env.PATH || ''}`,
  PYTHONPATH: `${resolve(rootDir, 'assets/python')}:${process.env.PYTHONPATH || ''}`,
};

function runStep(label, cmd) {
  console.log(`\n=== [RUNNING] ${label} ===`);
  execSync(cmd, {
    cwd: rootDir,
    env,
    stdio: 'inherit',
  });
  console.log(`=== [PASSED] ${label} ===`);
}

try {
  runStep('Node Dependency Checks', `node "${resolve(rootDir, 'scripts/check-node-dependencies.mjs')}"`);
  runStep('Security Parity Checks', `node "${resolve(rootDir, 'scripts/check-security-parity.mjs')}"`);
  runStep('Python Unit & Parity Tests', `"${resolve(venvBin, 'python')}" -m unittest discover tests`);
  runStep(
    'Node Unit Tests',
    `node --test "${resolve(rootDir, 'tests/myst/test-*.mjs')}" "${resolve(rootDir, 'tests/transform/test-*.mjs')}" "${resolve(rootDir, 'tests/ssr/test-*.mjs')}" "${resolve(rootDir, 'tests/security/test-*.mjs')}" "${resolve(rootDir, 'tests/assets/test-*.mjs')}" "${resolve(rootDir, 'tests/catalog/test-*.mjs')}"`
  );
  runStep('Fixture Build & Lit SSR', `node "${resolve(rootDir, 'tests/run-fixture-build.mjs')}"`);
  runStep('Playwright Browser Tests', `npx playwright test`);

  if (existsSync(resolve(rootDir, '_build/html/index.html'))) {
    runStep('Production Build Validation', `"${resolve(venvBin, 'python')}" "${resolve(rootDir, 'scripts/validate-build.py')}" --verify-dir "${resolve(rootDir, '_build/html')}" --strict`);
  }

  console.log('\n=============================================');
  console.log('🎉 ALL TEST SUITES PASSED CLEANLY');
  console.log('=============================================\n');
} catch (err) {
  console.error('\n❌ Test suite failed:', err.message);
  process.exit(1);
}
