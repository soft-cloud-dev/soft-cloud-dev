#!/bin/sh
set -eu
export JB_ALLOW_NODEENV=0
command -v node
command -v npm
node --version
npm --version
python --version
python -m pip --version
python tools/check_profile.py
python tools/generate_audio.py --page introduction.md
jupyter book --version
jupyter book clean --all --execute -y
jupyter book build --html --strict --execute
if [ -f CNAME ]; then
  cp CNAME _build/html/CNAME
fi
if [ -f tools/fix_seo_artifacts.py ]; then
  python tools/fix_seo_artifacts.py "https://my.softcloud.dev" _build/html
fi
python tools/generate_audio.py --page introduction.md --check-only --verify-build-dir _build/html
test -s _build/html/index.html
