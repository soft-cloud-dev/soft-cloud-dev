import { spawnSync } from 'node:child_process';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const rootDir = resolve(__dirname, '..');
const driverScript = resolve(__dirname, 'ci-test-driver.sh');

console.log('Starting shared CI verification driver via Node...');
const res = spawnSync('bash', [driverScript], {
  cwd: rootDir,
  env: process.env,
  stdio: 'inherit',
});

if (res.error) {
  console.error('Failed to run CI test driver:', res.error);
  process.exit(1);
}

process.exit(res.status ?? 0);
