# Implementation ledger — plan: docs/implementation/webawesome-ssr/plan.md

## Baseline and execution
- Baseline / rollback revision: `e62f3db005f8940f5242dd466bbd08187b19f9f4` (and ancestor commit `03bd544790ae7ea8017cac18c9cef43ed4ca6965`).
- Clean initial checkout; isolated implementation branch: `codex/webawesome-ssr`.
- Revision 7.0 plan is authoritative.
- Environment: Python 3.12.14, Node 20+, `requirements.lock` hash-enforced, `jb2-python` kernelspec registered.
- Baseline profile and verification: passed for all 5 source files across all 5 locales (`en`, `pl`, `de`, `es`, `fr`).

## Publication invariants
- English: `_build/html/index.html`; translations: `pl`, `de`, `es`, `fr` under their existing prefixes.
- `tools/build.sh` validates profile and translation freshness, builds locales, stages Web Awesome runtime assets, performs Lit SSR DSD transformation, copies CNAME and Thebe sourcemap, repairs SEO and Thebe, verifies narration and locales, and strictly validates output HTML via `scripts/validate-build.py`.
- Deployment artifact remains `./_build/html`; existing Python setup, hash enforcement, offline audio, and pinned actions remain preserved.
- Production TOC and translation provenance in `i18n/` are completely unchanged.

## Phase status
- [x] **Phase 0 — Repository baseline and implementation branch:** Completed. Baseline commit recorded, build and validation verified.
- [x] **Phase 1 — Dependency and runtime foundation:** Completed. Exact 7 npm packages pinned (`package.json` & `package-lock.json`), `scripts/check-node-dependencies.mjs` passes.
- [x] **Phase 2 — Shared schemas, security policy, and test utilities:** Completed. Canonical schemas in `assets/shared/component-schema.json`, URL policy in `assets/shared/url-policy.json`, 46-case `tests/security/url-corpus.json` with 100% JS/Python parity.
- [x] **Phase 3 — MyST plugin and AST contract:** Completed. `assets/plugins/myst-webawesome.mjs` implemented; tested on fixture book `tests/fixtures/webawesome-book`.
- [x] **Phase 4 — Python notebook API:** Completed. `assets/python/softcloud_ui.py` implemented (`TrustedHTML`, `UI.icon`, `UI.button`, `UI.card_text`, `UI.callout_text`, etc.) and tested with `jb2-python` kernel.
- [x] **Phase 5 — HTML placeholder transformation:** Completed. `scripts/lib/placeholder-transform.mjs`, `scripts/lib/parse5-tree.mjs`, `scripts/lib/component-render-model.mjs` implemented and passing idempotence tests.
- [x] **Phase 6 — Lit SSR and DSD integration:** Completed. `scripts/lib/lit-renderer.mjs`, `scripts/lib/dsd-validator.mjs`, and `scripts/lit-ssr-transform.mjs` implemented. Emits authentic `<template shadowroot="open" shadowrootmode="open">` with `did-ssr=""`.
- [x] **Phase 7 — Runtime assets, theme, and accessibility:** Completed. `assets/static/softcloud.css`, `assets/static/softcloud-theme.js` (supporting dual-way MyST and Web Awesome theme sync and MutationObserver placeholder restoration), `scripts/stage-webawesome-assets.mjs`.
- [x] **Phase 8 — Locale staging and production build integration:** Completed. `myst.yml` plugin registered, `tools/check_profile.py` updated, `tools/build_locales.py` staging updated, `tools/build.sh` pipeline integrated. 5-locale production build succeeds with code 0.
- [x] **Phase 9 — Production validation, fixtures, and browser verification:** Completed. `scripts/validate-build.py` implemented with strict validation; Playwright browser test suite (9/9 specs passing across hydration, DSD, accessibility, theme switching, no-JS readability).
- [x] **Phase 10 — CI, release rehearsal, and packaging:** Completed. Non-destructive update to `.github/workflows/deploy.yml` with SHA-pinned Node 20, new `.github/workflows/webawesome-pr.yml`, and shared CI test driver `scripts/ci-test-driver.sh` / `scripts/ci-test-driver.mjs`. Full release rehearsal passes code 0.
- [x] **Phase 11 — Final acceptance, packaging, rollout, and rollback readiness:** Completed. All release gates G1–G10 verified. Rollback procedures documented below.

## Release gates review (G1–G10)
- **G1 (Dependencies):** PASS. Web Awesome 3.14.0, Lit SSR 4.1.0, Lit SSR Client 1.1.8, Lit 3.3.3, parse5 7.3.0, Font Awesome Free 6.5.2, Playwright Test 1.64.1 pinned in `package.json` and committed in `package-lock.json`. `scripts/check-node-dependencies.mjs` passes.
- **G2 (Python & MyST Compatibility):** PASS. `requirements.lock` intact, `.venv` preserved, `jb2-python` kernelspec registered. MyST plugin runs cleanly without breaking AST or renderer.
- **G3 (Security Parity):** PASS. 100% agreement across all 46 test cases in `tests/security/url-corpus.json` between JS (`scripts/lib/url-policy.mjs`) and Python (`assets/python/softcloud_security.py`).
- **G4 (AST Placeholder Contract):** PASS. Plugins and Python helpers emit `.sc-wa-host` with marker class and exactly one direct `.sc-wa-meta` child containing escaped JSON text.
- **G5 (Idempotence):** PASS. Double transformation of transformed HTML produces byte-identical results; verified by `tests/transform/test-transform-idempotence.mjs`.
- **G6 (Authentic Lit SSR & DSD):** PASS. Valid `<template shadowroot="open" shadowrootmode="open">` attached to custom elements, host marked with `did-ssr=""`, light DOM preserved in exact slot positions.
- **G7 (Runtime Assets & Base Paths):** PASS. Self-hosted runtime assets staged under root `vendor/` and `static/`. Correct relative/absolute path resolution under root `""` and `/docs` base URLs.
- **G8 (Browser Acceptance & Multilingual Invariants):** PASS. 9/9 Playwright browser tests pass. No uncaught errors. 5-locale site (`en`, `pl`, `de`, `es`, `fr`) intact with 25 HTML pages, audio narration, SEO metadata, and Thebe sanitization.
- **G9 (CI & Reproducibility):** PASS. `scripts/ci-test-driver.sh` runs all 8 verification stages cleanly on a clean checkout. Both PR and deployment workflows configured with SHA-pinned actions.
- **G10 (Rollback Readiness):** PASS. Rollback revision recorded and documented below. Zero uncommitted artifacts or repository pollution.

## Rollback procedure
If a rollback is required, revert the branch or commit to `03bd544790ae7ea8017cac18c9cef43ed4ca6965` or baseline `e62f3db005f8940f5242dd466bbd08187b19f9f4`:
1. `git checkout main` (or checkout baseline commit `e62f3db005f8940f5242dd466bbd08187b19f9f4`).
2. Alternatively, disable the feature selectively without full git revert:
   - Remove `assets/plugins/myst-webawesome.mjs` from `myst.yml` plugins list.
   - Revert lines added to `tools/build.sh` (stages 1, 2, 3 calling `stage-webawesome-assets.mjs`, `lit-ssr-transform.mjs`, and `validate-build.py`).
   - Run `bash tools/build.sh` to produce a standard baseline build without SSR transformation.
