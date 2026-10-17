# Component documentation verification contract (PR 2 baseline)

This document is the pre-migration contract for all 90 catalog entries. PR 1 fixes rendering defects and installs focused regression checks; PR 2 enforces the complete contract before broad content migration. No second MyST or SSR pipeline is permitted.

| Gate | Source of truth | Acceptance |
| --- | --- | --- |
| Inventory | components/catalog.json | Exactly 90 unique entries, every entry mapped to a Markdown file and MyST TOC |
| Availability | catalog.json and installed package | No Pro preview unless licensed; Core and source-only status explicit |
| API | package-lock.json exact @awesome.me/webawesome version | Inspect installed dist/custom-elements.json and validate shape/coverage; generate and compare API references, fail on missing supported Core APIs |
| Frontmatter | docs/verification/page-frontmatter.schema.json | Validate description, keywords, slug, source link; no handwritten version-dependent counts |
| Page structure | catalog.json | Title/tag, source link, availability, preview or portable alternative, static readable fallback, copyable example, accessibility, API, dependencies |
| MyST | tools/build.sh | Real Jupyter Book 2 strict build, zero errors and parsed code fences |
| Accessibility | tests/doc-browser | axe-core serious/critical count zero on representative routes |
| Keyboard | tests/doc-browser | Playwright Tab/Enter/Space/Arrow keys for applicable interactive components |
| No-JS mock | deterministic server HTML fixture and Playwright with JavaScript disabled | Verify semantic fallback text, media URLs, copyable code, typed SSR hosts and DSD without screenshots or pixel thresholds; separately simulate widget initialization failure with JavaScript enabled |
| Links | assembled _build/html | Internal href/src resolve for root and prefixed locales; zero broken internal links |
| Remote media | assets/static/showcase/README.md | Only shoelace.style/assets/images/walk.gif and interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4 |
| Coverage | manifest and CI reports | One finding-to-regression mapping for all 15 findings; never claim unverified completion |

**Progressive enhancement:** Every browser-only preview must have semantic static text or media and a copyable example *outside* anywidget. Both must remain with JS disabled and when component loading fails after JS starts. A noscript-only fallback fails the contract. The four typed primitives continue to use genuine Lit SSR/DSD.

**Build provenance:** English sources are copied into isolated _build/locales/en/workspace and translations into locale workspaces before Jupyter Book renders them. Edit URLs must point to original GitHub paths. Existing asset staging copies assets/static/showcase to static/showcase; anywidget resolves showcase: tokens from the module URL.

**Rollout:** PR 1 fixes nested fences, edit links, media URLs and static fallback; PR 2 adds schema, API, accessibility, keyboard, links, No-JS mock checks and inventory gates; PR 3 improves metadata, navigation and attribution.
