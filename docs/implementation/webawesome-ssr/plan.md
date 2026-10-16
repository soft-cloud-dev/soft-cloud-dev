# SoftCloud Web Awesome SSR — Full Engineering Specification

The complete Revision 7.0 specification is available as a Markdown document suitable for repository review and implementation.

Engineering & Integration Specification

18 sections · Approximately 5,100 words · Markdown

Download the full specification

The specification supersedes Revision 6 and addresses the confirmed incompatibilities. It uses Web Awesome 3.14.0 with Lit SSR 4.1.0, replaces unsupported MyST metadata properties with renderer-compatible AST nodes, defines an injection-resistant transformation process, and preserves the repository's multilingual build, narration, and CI contracts. The Web Awesome version change is necessary because SSR support was introduced after version 3.0.0.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://webawesome.com\&sz=32)

Web Awesome

+2



# SoftCloud Web Awesome SSR

## Phased Implementation Plan — Revision 7.0

**Status:** Ordered implementation plan — execution and acceptance required\
**Date:** October 16, 2026\
**Repository:** `soft-cloud-dev/soft-cloud-dev`\
**Target:** Production multilingual Jupyter Book / MyST website

## 1. Implementation principles

Implement the integration in dependency order. Do not enable production SSR until the isolated fixture, security, idempotence, browser, and repository-preservation checks pass.

The implementation must:

1. Pin the required Node dependencies and preserve the existing Python environment.
2. Add the MyST plugin using renderer-supported AST nodes.
3. Define one shared component and metadata contract.
4. Implement URL and attribute validation before rendering author-controlled values.
5. Transform completed HTML with `parse5` without serializing and reparsing existing content.
6. Generate authentic Lit SSR Declarative Shadow DOM.
7. Stage assets and locale helpers without changing the production TOC.
8. Integrate the transformation into the existing build only after fixture validation.
9. Add browser and CI verification before release.
10. Preserve rollback capability until all acceptance gates pass.

## 2. Phase overview

| Phase | Scope                                               | Depends on       |
| ----- | --------------------------------------------------- | ---------------- |
| 0     | Repository baseline and implementation branch       | None             |
| 1     | Dependency and runtime foundation                   | Phase 0          |
| 2     | Shared schemas, security policy, and test utilities | Phase 1          |
| 3     | MyST plugin and AST contract                        | Phases 1–2       |
| 4     | Python notebook API                                 | Phases 2–3       |
| 5     | HTML placeholder transformation                     | Phases 2–3       |
| 6     | Lit SSR and DSD integration                         | Phase 5          |
| 7     | Runtime assets, theme, and accessibility            | Phase 1, Phase 6 |
| 8     | Locale staging and production build integration     | Phases 4, 6, 7   |
| 9     | Fixtures, browser tests, and production validation  | Phases 3–8       |
| 10    | CI, release rehearsal, and packaging                | Phase 9          |
| 11    | Production rollout and rollback readiness           | Phase 10         |

---

## Phase 0 — Establish the repository baseline

### Objective

Create a reproducible starting point and document the existing build behavior before modifying repository files.

### Ordered tasks

1. Create an isolated implementation branch.
2. Record the current Git revision.
3. Inspect the existing:
   - `myst.yml`
   - `tools/check_profile.py`
   - `tools/build_locales.py`
   - `tools/build.sh`
   - `.github/workflows/deploy.yml`
   - Python lockfile and kernelspec configuration
   - existing test and validation scripts
4. Run the current repository validation and production build.
5. Save baseline logs and generated artifact metadata.
6. Confirm the current locale list, publication paths, SEO behavior, Thebe behavior, narration checks, and deployment artifact path.

### Responsible files

- Existing repository configuration and build files
- `requirements.lock`
- `tools/check_profile.py`
- `tools/build_locales.py`
- `tools/build.sh`
- `.github/workflows/deploy.yml`

### Validation commands

```
git status --short
git rev-parse HEAD
python --version
node --version
python tools/check_profile.py
bash tools/build.sh
```

Use the repository’s existing documented commands if any of these entry points differ.

### Completion criteria

- The working tree is clean before implementation begins.
- The current build completes successfully.
- Baseline logs identify all existing validation stages.
- The five expected locales and their output paths are documented.
- No production behavior is changed in this phase.
- A rollback reference to the baseline Git revision is recorded.

---

## Phase 1 — Establish dependency and runtime foundations

### Objective

Add the exact Node dependency set while preserving the existing Python environment and kernelspec.

### Ordered tasks

1. Create or update `package.json`.
2. Pin:
   - Web Awesome `3.14.0`
   - Lit SSR `4.1.0`
   - Lit SSR Client `1.1.8`
   - Lit `3.3.3`
   - `parse5` `7.3.0`
   - Font Awesome Free `6.5.2`
   - Playwright Test `1.64.1`
3. Generate and commit `package-lock.json`.
4. Verify package exports and SSR entry points.
5. Confirm Node 20 compatibility.
6. Preserve `requirements.lock`, `.venv`, and the `jb2-python` kernelspec.
7. Add a minimal Node verification script that imports the required packages without modifying the production build.

### Responsible files

- `package.json`
- `package-lock.json`
- `scripts/check-node-dependencies.mjs`
- Existing Python environment files
- Existing kernelspec configuration

### Validation commands

```
node --version
npm ci
npm ls --depth=0
node scripts/check-node-dependencies.mjs
python -m pip check
jupyter kernelspec list
```

### Completion criteria

- `npm ci` succeeds on Node 20.
- The lockfile resolves the required versions.
- Web Awesome SSR, Lit SSR, `parse5`, Font Awesome, and Playwright imports succeed.
- No existing Python dependency or kernelspec is removed or changed unintentionally.
- The dependency check fails clearly when a required package or export is unavailable.
- G1 dependency requirements are satisfied.

---

## Phase 2 — Define shared schemas, security policy, and test utilities

### Objective

Create the canonical metadata, component-option, URL, attribute, and test contracts before implementing renderers.

### Ordered tasks

1. Define versioned metadata schemas for:
   - cards
   - callouts
   - buttons
   - icons
2. Define explicit allowlists for:
   - component names
   - callout variants
   - button variants
   - button appearances
   - button sizes
   - Font Awesome styles
   - optional Web Awesome icon families and variants
3. Define URL policies separately for links and media.
4. Implement rejection of:
   - control characters
   - backslashes
   - protocol-relative URLs
   - malformed authorities
   - credentials
   - unsupported schemes
   - unsafe media destinations
5. Define attribute policies for:
   - allowed attributes
   - event-handler rejection
   - `rel` handling
   - accessible labels
6. Create one JSON corpus containing valid and invalid URL cases.
7. Expose the same policy behavior to JavaScript and Python tests.
8. Define error codes or stable error messages for build diagnostics.

### Responsible files

Recommended files:

- `assets/shared/component-schema.json`
- `assets/shared/url-policy.json`
- `scripts/lib/schema.mjs`
- `scripts/lib/url-policy.mjs`
- `assets/python/softcloud_security.py`
- `tests/security/url-corpus.json`
- `tests/security/test-url-policy.mjs`
- `tests/security/test_url_policy.py`

### Validation commands

```
node --test tests/security/test-url-policy.mjs
pytest -q tests/security/test_url_policy.py
node scripts/check-security-parity.mjs
```

### Completion criteria

- JavaScript and Python accept and reject the same corpus entries.
- Relative references, fragments, query references, HTTP(S), and permitted `mailto:` links behave as specified.
- `mailto:` is rejected for media.
- Unsafe schemes and malformed destinations fail closed.
- Unknown component options and unsupported schema versions are rejected.
- Security tests include HTML-closing tags, event-handler payloads, and attribute-injection attempts.
- G3 security prerequisites are satisfied.

---

## Phase 3 — Implement the MyST plugin and AST contract

### Objective

Add the authorized MyST plugin using only AST structures supported by the installed React renderer.

### Ordered tasks

1. Create the plugin module.
2. Implement directives:
   - `{wa-card}`
   - `{wa-callout}`
   - `{wa-button}`
3. Implement roles:
   - `{icon}`
   - `{fa}`
4. Emit block wrappers as `div` nodes with:
   - `sc-wa-host`
   - component-specific marker classes
5. Emit inline icon wrappers as `span` nodes.
6. Add exactly one direct metadata `span` containing escaped JSON text.
7. Parse Markdown body content through `ctx.parseMyst()`.
8. Preserve nested Markdown, headings, links, comments, and child nodes.
9. Validate directive options against Phase 2 schemas.
10. Reject unsupported raw HTML, `hProperties`, disjoint HTML fragments, and unknown options.
11. Add a real Jupyter Book fixture that renders the plugin before postprocessing.

### Responsible files

- `assets/plugins/myst-webawesome.mjs`
- `assets/shared/component-schema.json`
- `tests/fixtures/webawesome-book/myst.yml`
- `tests/fixtures/webawesome-book/index.md`
- `tests/fixtures/webawesome-book/_toc.yml`
- `tests/myst/test-plugin-output.mjs`
- `tests/myst/test-plugin-output.py`

### Validation commands

```
node tests/myst/test-plugin-output.mjs
jupyter-book build tests/fixtures/webawesome-book
python tests/myst/inspect-pre-ssr-html.py tests/fixtures/webawesome-book/_build/html
```

### Completion criteria

- The fixture builds with the authorized plugin.
- Generated HTML contains the expected wrapper classes.
- Each supported placeholder contains exactly one direct metadata wrapper.
- Metadata is escaped text, not raw HTML.
- Nested Markdown, headings, links, comments, and special characters survive unchanged.
- The production TOC is not modified.
- G2 MyST compatibility requirements are satisfied.

---

## Phase 4 — Implement the Python notebook API

### Objective

Provide notebook helpers that emit the same placeholder contract as the MyST plugin.

### Ordered tasks

1. Create `TrustedHTML`.
2. Create the `UI` class.
3. Implement:
   - `UI.icon`
   - `UI.button`
   - `UI.card_text`
   - `UI.card_trusted_html`
   - `UI.callout_text`
   - `UI.callout_trusted_html`
4. Escape ordinary text and attribute values.
5. Permit body HTML only through explicit `TrustedHTML`.
6. Ensure titles are represented once in metadata.
7. Reuse the shared schema and URL policy.
8. Add an executable notebook fixture using the `jb2-python` kernel.
9. Verify that notebook output matches the MyST placeholder contract.

### Responsible files

- `assets/python/softcloud_ui.py`
- `assets/python/softcloud_security.py`
- `tests/fixtures/webawesome-book/notebooks/webawesome-api.ipynb`
- `tests/python/test_softcloud_ui.py`
- `tests/python/test_notebook_execution.py`

### Validation commands

```
pytest -q tests/python
jupyter nbconvert --to notebook --execute \
  tests/fixtures/webawesome-book/notebooks/webawesome-api.ipynb \
  --output /tmp/webawesome-api.executed.ipynb \
  --ExecutePreprocessor.kernel_name=jb2-python
```

### Completion criteria

- All required helper methods exist.
- Ordinary text cannot inject HTML.
- Only `TrustedHTML` contributes trusted body markup.
- Notebook execution succeeds with `jb2-python`.
- Generated placeholders are structurally identical to plugin placeholders.
- Titles are not duplicated.
- Locale staging can import the helper from `PYTHONPATH`.

---

## Phase 5 — Implement typed HTML placeholder transformation

### Objective

Convert validated placeholders into Web Awesome host elements while preserving existing HTML nodes and light-DOM content.

### Ordered tasks

1. Create a `parse5` document parser and tree adapter utility.
2. Identify only approved placeholder classes.
3. Require exactly one direct metadata child.
4. Decode metadata from text content.
5. Validate metadata against the shared schemas.
6. Reject:
   - duplicate metadata
   - unknown fields
   - unsupported schema versions
   - invalid attributes
   - unsafe URLs
   - malformed placeholder structure
7. Construct custom-element hosts through the tree adapter.
8. Create header, footer, media, icon, and label nodes as typed nodes.
9. Insert author-controlled values only as text nodes or validated attributes.
10. Move existing Markdown children into the correct light-DOM position.
11. Update parent references for moved nodes.
12. Remove synthetic metadata wrappers and marker classes.
13. Preserve comments, nested elements, and original text.
14. Add deterministic serialization.
15. Add a second-pass idempotence check.

### Responsible files

- `scripts/lib/parse5-tree.mjs`
- `scripts/lib/placeholder-transform.mjs`
- `scripts/lib/component-render-model.mjs`
- `tests/transform/test-placeholder-transform.mjs`
- `tests/transform/test-transform-security.mjs`
- `tests/transform/test-transform-idempotence.mjs`

### Validation commands

```
node --test tests/transform/test-placeholder-transform.mjs
node --test tests/transform/test-transform-security.mjs
node --test tests/transform/test-transform-idempotence.mjs
```

### Completion criteria

- Valid placeholders become correctly structured custom-element hosts.
- Existing light-DOM content is preserved byte-for-byte where required.
- No author-controlled value is interpolated into an HTML string.
- Invalid metadata fails the build.
- Unsafe URLs fail the build.
- Duplicate or malformed markers fail the build.
- A second transformation pass produces identical output bytes.
- The transformer is safe to run on pages containing zero components.

---

## Phase 6 — Integrate Lit SSR and Declarative Shadow DOM

### Objective

Generate authentic Web Awesome SSR output and attach valid DSD to transformed hosts.

### Ordered tasks

1. Import the Lit SSR Node shim.
2. Register supported Web Awesome component modules.
3. Define trusted Lit templates using validated properties.
4. Render each supported component through Lit’s high-level SSR API.
5. Parse the rendered result with `parse5`.
6. Locate the matching custom-element host.
7. Extract exactly one direct:
   - `template[shadowrootmode="open"]`
8. Reject missing, duplicate, or malformed DSD.
9. Prepend the DSD template to the original host.
10. Preserve original light-DOM children after the template.
11. Preserve nested templates, styles, and hydration markers.
12. Add `did-ssr` only after successful validation.
13. Treat an existing `did-ssr` without valid DSD as an error.
14. Traverse nested custom elements in sequential awaited depth-first post-order.
15. Add a standalone transform CLI.

### Responsible files

- `scripts/lit-ssr-transform.mjs`
- `scripts/lib/lit-renderer.mjs`
- `scripts/lib/dsd-validator.mjs`
- `tests/ssr/test-lit-renderer.mjs`
- `tests/ssr/test-dsd-structure.mjs`
- `tests/ssr/test-nested-components.mjs`

### Validation commands

```
node scripts/lit-ssr-transform.mjs \
  tests/fixtures/webawesome-book/_build/html \
  ""

node --test tests/ssr/test-lit-renderer.mjs
node --test tests/ssr/test-dsd-structure.mjs
node --test tests/ssr/test-nested-components.mjs
```

### Completion criteria

- Every supported fixture component receives authentic DSD.
- Each host has exactly one valid direct open DSD template.
- `did-ssr` is present only on successfully transformed hosts.
- Nested components are processed in deterministic post-order.
- Original light-DOM content remains after the DSD template.
- Invalid SSR output fails the build.
- Repeated SSR transformation is byte-identical.
- G4 Lit SSR and G5 idempotence requirements are satisfied.

---

## Phase 7 — Publish runtime assets and implement theme/accessibility behavior

### Objective

Self-host all required runtime assets and preserve theme, accessibility, and pre-hydration behavior.

### Ordered tasks

1. Create the asset staging script.
2. Copy the pinned Web Awesome `dist-cdn` tree.
3. Copy Font Awesome CSS and matching webfonts.
4. Publish:
   - `softcloud.css`
   - `softcloud-theme.js`
   - Web Awesome SSR loader
5. Implement base-path-aware URL generation.
6. Inject each required stylesheet and script exactly once.
7. Prevent loading both standard and SSR autoloaders.
8. Implement theme synchronization with MyST `html.dark` and `html.light`.
9. Preserve MyST theme classes.
10. Avoid repeated theme mutations.
11. Support system preference when no explicit theme is selected.
12. Verify accessible labels, focus behavior, image alternatives, responsive layout, and readable pre-hydration content.
13. Document that DSD does not provide JavaScript-free interactivity.

### Responsible files

- `scripts/stage-webawesome-assets.mjs`
- `assets/static/softcloud.css`
- `assets/static/softcloud-theme.js`
- `assets/static/`
- `scripts/lib/asset-injection.mjs`
- `tests/assets/test-asset-staging.mjs`
- `tests/assets/test-base-paths.mjs`
- `tests/browser/theme.spec.ts`
- `tests/browser/accessibility.spec.ts`

### Validation commands

```
node scripts/stage-webawesome-assets.mjs tests/fixtures/webawesome-book/_build/html
node --test tests/assets/test-asset-staging.mjs
node --test tests/assets/test-base-paths.mjs
```

### Completion criteria

- All required local assets exist in the expected paths.
- Root and `/docs` base paths generate correct URLs.
- Translated pages use shared site-root assets without locale duplication.
- Each required asset reference appears exactly once per document.
- Theme synchronization does not mutate MyST state incorrectly.
- Accessibility and pre-hydration requirements are covered by tests.
- G7 base-path prerequisites are satisfied.

---

## Phase 8 — Integrate locale staging and the production build

### Objective

Add the feature to the real multilingual build without changing existing publication behavior.

### Ordered tasks

1. Register the authorized plugin in `myst.yml`.
2. Update `tools/check_profile.py` to allow only the approved plugin path.
3. Extend `stage_locale_workspace(...)` in `tools/build_locales.py`.
4. Stage:
   - `assets/plugins`
   - `assets/static`
   - `assets/python`
5. Set `PYTHONPATH` to the absolute staged Python helper directory.
6. Preserve existing images, widgets, sourcemaps, audio, TOC pruning, and publication assembly.
7. Add the three required commands to `tools/build.sh` immediately after locale building:
   1. `node scripts/stage-webawesome-assets.mjs _build/html`
   2. `node scripts/lit-ssr-transform.mjs _build/html "$BASE_URL"`
   3. `python scripts/validate-build.py --verify-dir _build/html`
8. Preserve all existing positional arguments and checks.
9. Confirm English and translated output paths.
10. Ensure a zero-component production build remains valid.

### Responsible files

- `myst.yml`
- `tools/check_profile.py`
- `tools/build_locales.py`
- `tools/build.sh`
- `scripts/stage-webawesome-assets.mjs`
- `scripts/lit-ssr-transform.mjs`
- `scripts/validate-build.py`

### Validation commands

```
python tools/check_profile.py
bash tools/build.sh
find _build/html -name '*.html' -print
test -f _build/html/index.html
```

Run the repository’s existing locale and publication verification commands as part of `tools/build.sh`.

### Completion criteria

- The production profile accepts exactly the authorized plugin.
- Locale workspaces contain the staged plugin, static assets, and Python helpers.
- Notebook helpers import successfully in locale builds.
- The full five-locale offline build succeeds.
- English remains at `_build/html/index.html`.
- Polish, German, Spanish, and French remain under their existing prefixes.
- Existing SEO, Thebe, narration, sourcemap, CNAME, and publication checks pass.
- No production TOC or translation provenance is changed.
- G6 repository preservation requirements are satisfied.

---

## Phase 9 — Implement production validation, fixtures, and browser verification

### Objective

Create blocking validation for generated output and verify client hydration in a real browser.

### Ordered tasks

1. Create the isolated fixture site under `tests/fixtures/webawesome-book/`.
2. Add:
   - nested cards
   - callouts
   - buttons
   - both icon roles
   - special HTML characters
   - relative and absolute links
   - comments
   - headings
   - executable notebook content
3. Add adversarial fixtures for:
   - HTML-closing tags
   - event-handler payloads
   - unsupported protocols
   - malicious URLs
   - malformed JSON
   - duplicate markers
   - invalid options
4. Implement `scripts/validate-build.py`.
5. Validate:
   - build directory existence
   - nonempty HTML
   - no unresolved placeholders
   - valid DSD
   - no duplicate direct DSD templates
   - consistent `did-ssr`
   - safe attributes and destinations
   - local runtime resources
   - no duplicate injected assets
6. Produce a verification report with:
   - page count
   - component count
   - DSD count
   - locale count
   - diagnostics
7. Add Playwright tests for:
   - DSD attachment
   - hydration
   - content preservation
   - link navigation
   - focus behavior
   - responsive layout
   - theme switching
   - reduced motion
   - root and `/docs` base paths
   - local JavaScript, CSS, fonts, icons, and chunks
8. Capture uncaught browser errors and Lit hydration warnings.
9. Disable JavaScript and verify readable document text only.

### Responsible files

- `tests/fixtures/webawesome-book/`
- `scripts/validate-build.py`
- `tests/browser/*.spec.ts`
- `playwright.config.ts`
- `tests/run-fixture-build.mjs`
- `tests/run-all.mjs`

### Validation commands

```
python scripts/validate-build.py --verify-dir _build/html
npm exec playwright test
npm test
```

### Completion criteria

- The fixture contains nonzero supported components.
- The fixture passes pre-SSR, post-transform, and browser checks.
- Production validation rejects every required malformed case.
- Browser tests pass without uncaught errors or Lit hydration warnings.
- Hydration does not duplicate or remove content unexpectedly.
- JavaScript-disabled pages remain readable.
- G8 browser requirements are satisfied.
- The validator produces a reviewable report.

---

## Phase 10 — Add CI verification and release rehearsal

### Objective

Make the implementation reproducible and blocking in pull requests and deployment workflows.

### Ordered tasks

1. Extend `.github/workflows/deploy.yml` non-destructively.
2. Add SHA-pinned Node 20 setup.
3. Enable npm caching.
4. Run `npm ci`.
5. Run dependency and repository profile checks before production build.
6. Preserve:
   - pinned actions
   - Python setup
   - `.venv`
   - hash-enforced installation
   - `pip check`
   - kernelspec registration
   - offline audio
   - Pages upload path
   - deployment permissions
7. Create a separate pull-request workflow without deployment permissions or production secrets.
8. Create a shared test driver used by both workflows.
9. Run:
   - MyST fixture tests
   - URL-policy parity tests
   - SSR tests
   - idempotence tests
   - browser tests
   - full five-locale offline build
10. Perform a deployment rehearsal without publishing.
11. Store logs, transformed HTML samples, reports, and browser traces without secrets.

### Responsible files

- `.github/workflows/deploy.yml`
- `.github/workflows/webawesome-pr.yml`
- `scripts/ci-test-driver.mjs`
- `scripts/ci-test-driver.sh`
- `package.json`
- `package-lock.json`

### Validation commands

```
npm ci
npm run verify
bash scripts/ci-test-driver.sh
python tools/check_profile.py
bash tools/build.sh
```

Use a local workflow runner if available to validate GitHub Actions syntax and step ordering.

### Completion criteria

- Pull requests run all required checks without deployment permissions.
- Deployment workflow retains its existing permissions and publication path.
- Both workflows use the same verification driver.
- CI passes on a clean checkout.
- No production secrets are required for PR verification.
- G9 CI requirements are satisfied.

---

## Phase 11 — Final acceptance, packaging, rollout, and rollback readiness

### Objective

Complete all release gates and prepare a controlled production rollout.

### Ordered tasks

1. Review all release gates G1–G10.
2. Run the complete clean-checkout verification.
3. Confirm exact dependency versions and lockfile integrity.
4. Confirm the production build and fixture build are both valid.
5. Confirm all five locales and all existing repository checks pass.
6. Review generated HTML for:
   - valid DSD
   - preserved light DOM
   - correct asset URLs
   - no unresolved placeholders
   - no unsafe attributes
7. Review browser traces and console output.
8. If a Skill archive is required:
   - create `SKILL.md`
   - create `agents/openai.yaml`
   - include only required scripts and assets
   - exclude `node_modules`, `.venv`, caches, deployment output, credentials, and restricted fonts
   - validate before creating `skill.zip`
9. Tag or record the release candidate revision.
10. Rehearse rollback by identifying the exact changes to:
    - plugin registration
    - build hooks
    - runtime injection
11. Deploy only after all gates pass.
12. Monitor the published artifact and retain verification evidence.

### Responsible files

- All implementation files
- `SKILL.md`, if required
- `agents/openai.yaml`, if required
- `skill.zip`, if required
- Release and verification artifacts

### Validation commands

```
npm run verify
bash scripts/ci-test-driver.sh
python tools/check_profile.py
bash tools/build.sh
python scripts/validate-build.py --verify-dir _build/html
npm exec playwright test
```

If packaging is required:

```
python scripts/validate-skill.py
python scripts/create-skill-zip.py
python scripts/validate-skill-zip.py skill.zip
```

### Completion criteria

- G1 through G10 all pass.
- The final multilingual artifact is complete and internally referenced.
- No deployment occurs from a partially transformed build.
- Rollback steps are documented and tested.
- Required implementation documentation is complete.
- Any Skill archive passes validation and size restrictions.
- Production deployment is approved by repository owners.

## 3. Cross-phase dependency rules

The following rules are blocking:

1. Do not implement Lit SSR before the metadata and URL schemas are stable.
2. Do not enable the production MyST plugin before the real fixture proves renderer compatibility.
3. Do not accept trusted HTML without explicit `TrustedHTML` construction.
4. Do not serialize author-controlled values into HTML fragments.
5. Do not integrate the transformer into `tools/build.sh` before idempotence passes.
6. Do not modify locale staging until the Python helper executes in the fixture kernel.
7. Do not enable deployment CI before the PR workflow passes.
8. Do not publish if `validate-build.py` reports any error.
9. Do not treat DSD as proof of JavaScript-free interactivity.
10. Do not package a Skill archive before validating its contents.

## 4. Final release checklist

- Baseline build recorded.
- Node 20 dependency installation passes.
- Required package versions and exports verified.
- Python lockfile and `jb2-python` preserved.
- Shared schemas and URL policies pass parity tests.
- MyST plugin passes a real Jupyter Book fixture.
- Python notebook helpers execute successfully.
- Placeholder transformation preserves content.
- Lit SSR produces valid DSD.
- Transformation is byte-idempotent.
- Runtime assets are self-hosted and base-path-correct.
- Theme and accessibility tests pass.
- Locale staging and five-locale build pass.
- Production validator passes.
- Browser hydration tests pass without console errors.
- PR CI passes without deployment permissions.
- Deployment workflow preserves existing safeguards.
- Skill archive is validated, if required.
- Rollback procedure is documented.
- Production release is approved.

**Completion status:** This document defines the ordered implementation plan. It does not claim that any phase has been completed. Production acceptance requires every phase completion criterion and every release gate to pass.

Scope of completion: The specification file was created and verified. The repository itself was not modified, and no build, pull request, or deployment was executed.