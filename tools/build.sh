#!/bin/sh
set -eu
export JB_ALLOW_NODEENV=0
export BASE_URL="${BASE_URL:-}"
command -v node
command -v npm
node --version
npm --version
python --version
python -m pip --version
python tools/check_profile.py
python tools/translate_sources.py --check-only --progressive
jupyter book --version
python tools/build_locales.py
if [ -f CNAME ]; then
  cp CNAME _build/html/CNAME
fi
if [ -f thebe-core.min.js.map ]; then
  cp thebe-core.min.js.map _build/html/thebe-core.min.js.map
fi
if [ -f tools/fix_seo_artifacts.py ]; then
  python tools/fix_seo_artifacts.py "https://my.softcloud.dev" _build/html
fi
if [ -f tools/fix_thebe.py ]; then
  python tools/fix_thebe.py _build/html
fi
node scripts/stage-webawesome-assets.mjs _build/html
node scripts/lit-ssr-transform.mjs _build/html "$BASE_URL"
python tools/generate_audio.py --all-locales --narrated-only --check-only --verify-build-dir _build/html
python tools/verify_locales.py --verify-build-dir _build/html --progressive
python scripts/validate-build.py --verify-dir _build/html
test -s _build/html/index.html
test -s _build/html/pl/index.html
test -s _build/html/de/index.html
test -s _build/html/es/index.html
test -s _build/html/fr/index.html
