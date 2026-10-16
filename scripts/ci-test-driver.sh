#!/usr/bin/env bash
# scripts/ci-test-driver.sh
# Shared CI verification driver for PR validation and production deployment rehearsal.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

export PATH="$ROOT_DIR/.venv/bin:$PATH"
export PYTHONPATH="$ROOT_DIR/assets/python:${PYTHONPATH:-}"
export BASE_URL="${BASE_URL:-}"
export SOFTCLOUD_AUDIO_OFFLINE="${SOFTCLOUD_AUDIO_OFFLINE:-1}"

echo "=== [1/8] Verifying Node and Python runtime environment ==="
node --version
python -c "import sys; assert sys.version_info[:2] == (3, 12), sys.version"

python -m pip check
jupyter kernelspec list | grep -q "jb2-python"

echo "=== [2/8] Checking pinned Node dependencies ==="
node scripts/check-node-dependencies.mjs

echo "=== [3/8] Checking repository profile and MyST plugin permissions ==="
python tools/check_profile.py

echo "=== [4/8] Running security policy cross-language parity checks ==="
node scripts/check-security-parity.mjs

echo "=== [5/8] Running Python and Node unit test suites ==="
python -m unittest discover tests
node --test tests/**/*.mjs

echo "=== [6/8] Building Jupyter Book fixture and verifying Lit SSR ==="
node tests/run-fixture-build.mjs

echo "=== [7/8] Running Playwright browser test suite ==="
npx playwright test

echo "=== [8/8] Building and validating multilingual production site ==="
export BASE_URL="${BASE_URL:-}"
export SOFTCLOUD_AUDIO_OFFLINE="${SOFTCLOUD_AUDIO_OFFLINE:-1}"
bash tools/build.sh
python scripts/validate-build.py --verify-dir _build/html --strict

echo "=========================================================="
echo "🎉 CI VERIFICATION AND DEPLOYMENT REHEARSAL PASSED CLEANLY"
echo "=========================================================="
