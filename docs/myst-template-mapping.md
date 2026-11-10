# MyST & JTeX Architecture & Template Mapping Reference

This document provides a comprehensive architectural mapping of the **MyST Markdown** ecosystem, the **JTeX** (`jtex: v1`) templating engine, and their concrete implementation within the **SoftCloud** publishing pipeline (`soft-cloud-dev`).

---

## 1. Macro Architecture: The MyST 5-Phase Stack (`mystmd.org/guide/overview`)

The MyST build pipeline standardizes document authoring, transformation, and compilation into a five-phase lifecycle:

```text
  (1) Writing
      Raw ideas & computational narratives ──► .md, .ipynb, .tex
                                                      │
                                                      ▼
  (2) Parsing
      MyST Document Engine / Plugins ──────────► Raw MyST AST (mdast superset)
                                                      │
                                                      ▼
  (3) Resolving
      MyST Transformers ───────────────────────► Resolved / Processed AST
                                                 (Links, targets, metadata, validation)
                                                      │
                                                      ▼
  (4) Rendering
      MyST Renderers (HTML, DSD, React, TeX) ──► Renderable Component Trees
                                                      │
                                                      ▼
  (5) Theming & Templating
      JTeX / myst-theme (book-theme, Typst) ───► Final Publication Artifacts
```

### 1.1 Phase-by-Phase Implementation in SoftCloud

| Lifecycle Phase | MyST Specification Standard | Concrete Implementation in `soft-cloud-dev` | Key Project Assets |
| :--- | :--- | :--- | :--- |
| **1. Writing** | Authors compose technical content using MyST Markdown and Jupyter Notebooks with directives, roles, and math blocks. | Markdown documentation, systems architecture notes, and CPython 3.12.14 computational notebooks. Components authored via typed Web Awesome directives. | [`README.md`](file:///Users/user/data/Projects/soft-cloud-dev/README.md), [`architecture.md`](file:///Users/user/data/Projects/soft-cloud-dev/architecture.md), [`notebooks/experiment.ipynb`](file:///Users/user/data/Projects/soft-cloud-dev/notebooks/experiment.ipynb), [`components/**/*.md`](file:///Users/user/data/Projects/soft-cloud-dev/components) |
| **2. Parsing** | MyST Document Engine parses source files into a unified MyST AST conforming to the `mdast` superset specification. | JavaScript plugin (`myst-webawesome.mjs`) registers 3 directives (`wa-card`, `wa-callout`, `wa-button`) and 2 roles (`icon`, `fa`), emitting strict JSON metadata spans and placeholder hosts. | [`assets/plugins/myst-webawesome.mjs`](file:///Users/user/data/Projects/soft-cloud-dev/assets/plugins/myst-webawesome.mjs), [`assets/shared/component-schema.json`](file:///Users/user/data/Projects/soft-cloud-dev/assets/shared/component-schema.json) |
| **3. Resolving** | Transformers traverse AST nodes to link targets, enrich metadata, and resolve cross-references. | AST transformation pipeline walks DOM trees, validates JSON schema constraints, enforces strict URL safety policies, and prepares nodes for server-side hydration. | [`scripts/lib/placeholder-transform.mjs`](file:///Users/user/data/Projects/soft-cloud-dev/scripts/lib/placeholder-transform.mjs), [`scripts/lib/schema.mjs`](file:///Users/user/data/Projects/soft-cloud-dev/scripts/lib/schema.mjs), [`scripts/lib/url-policy.mjs`](file:///Users/user/data/Projects/soft-cloud-dev/scripts/lib/url-policy.mjs) |
| **4. Rendering** | Renderers convert AST elements into target runtime markup, web components, or LaTeX fragments. | Lit SSR pipeline (`@lit-labs/ssr`, Lit 3.3.3) renders custom elements with Declarative Shadow DOM templates (`<template shadowrootmode="open">`) stamped with `did-ssr`, ensuring zero-JS readability. | [`scripts/lit-ssr-transform.mjs`](file:///Users/user/data/Projects/soft-cloud-dev/scripts/lit-ssr-transform.mjs), [`scripts/lib/lit-renderer.mjs`](file:///Users/user/data/Projects/soft-cloud-dev/scripts/lib/lit-renderer.mjs), [`scripts/lib/dsd-validator.mjs`](file:///Users/user/data/Projects/soft-cloud-dev/scripts/lib/dsd-validator.mjs) |
| **5. Theming** | Themes and templates assemble rendered components into finalized, distributable artifacts. | Book Theme website compilation across 5 locales (`en`, `pl`, `de`, `es`, `fr`), self-hosted Web Awesome asset distribution, and reciprocal multilingual SEO generation. | [`myst.yml`](file:///Users/user/data/Projects/soft-cloud-dev/myst.yml), [`scripts/stage-webawesome-assets.mjs`](file:///Users/user/data/Projects/soft-cloud-dev/scripts/stage-webawesome-assets.mjs), [`tools/build_locales.py`](file:///Users/user/data/Projects/soft-cloud-dev/tools/build_locales.py), [`tools/fix_seo_artifacts.py`](file:///Users/user/data/Projects/soft-cloud-dev/tools/fix_seo_artifacts.py) |

### 1.2 Jupyter Book 2 & Computational Runtime Relationship

- **Jupyter Book 2 Distribution**: Jupyter Book 2 is the opinionated distribution of the MyST Document Engine. `soft-cloud-dev` runs pinned `jupyter-book==2.1.7` governed by cryptographic hash verification (`requirements.lock`).
- **Computational Determinism**: Notebooks execute under the canonical `jb2-python` kernelspec bound to CPython 3.12.14, eliminating environment drift.
- **Verification Gates**: Preflight validation (`tools/check_profile.py`), unit/SSR suites (`npm test`), Python tests (`unittest`), and Playwright browser specs guarantee production integrity.

---

## 2. JTeX Templating Engine & Delimiter Rules (`mystmd.org/jtex`)

`jtex` is the data-driven templating engine and command-line utility used by MyST Markdown to render publications into static export formats (LaTeX, Typst, PDF) and web themes.

### 2.1 Syntax Delimiters (Adapted Nunjucks/Jinja2)

To coexist seamlessly with LaTeX backslashes and Typst markup without escaping conflicts, JTeX customizes Jinja2 delimiters:

| Template Construct | Standard Jinja2 | JTeX Delimiter | Usage / Example |
| :--- | :--- | :--- | :--- |
| **Statements** | `{% ... %}` | `[# ... #]` | `[# if doc.title #] \title{[- doc.title -]} [# endif #]` |
| **Expressions** | `{{ ... }}` | `[- ... -]` | `[- doc.title -]` |
| **Comments** | `{# ... #}` | `%# ... #%` | `%# Internal template note #%` |
| **Line Comments** | `##` | `%%` | `%% Single line comment` |
| **Whitespace Trimming** | `{%- -%}` | `[#- -#]`, `[-- --]` | Strips leading/trailing whitespace |

### 2.2 Global Template Variables

- **`doc`**: Frontmatter attributes (`title`, `short_title`, `description`, `authors`, `affiliations`, `keywords`, `date.day|month|year`).
- **`options`**: User-configured variables declared in `template.yml` and passed via `myst.yml` `site.options` or document frontmatter.
- **`parts`**: Modular document segments outside the main content body (`abstract`, `acknowledgments`, `footer`, `navbar_end`).
- **`[- CONTENT -]`**: Injects primary parsed document body.
- **`[- IMPORTS -]`**: Injects required macro definitions and packages.

---

## 3. Template Schema Specification (`template.yml` / `jtex: v1`)

Every JTeX / MyST template is formally declared using a `template.yml` manifest conforming to schema `jtex: v1`.

```yaml
jtex: v1
title: Book Theme
description: Multi-page documentation and computational notebook theme
version: 1.0.0
license: MIT
source: https://github.com/jupyter-book/myst-theme
thumbnail: ./thumbnail.png
authors:
  - name: SoftCloud Contributors
    website: https://my.softcloud.dev
tags:
  - book
  - documentation

options:
  - id: internal_domains
    type: string
    description: Domains treated as internal links (wildcards supported, e.g. *.softcloud.dev)
  - id: logo
    type: file
    description: Path to site logo
  - id: logo_dark
    type: file
    description: Path to dark-mode site logo
  - id: logo_text
    type: string
    description: Display text next to logo
  - id: logo_url
    type: string
    description: Target destination for logo link
  - id: favicon
    type: file
    description: Favicon icon file
  - id: folders
    type: boolean
    description: Respect nested folder structure in URL paths

parts:
  - id: footer
    description: Site-wide custom footer content
  - id: primary_sidebar_footer
    description: Replaces default sidebar footer
  - id: navbar_end
    description: Custom content injected into right edge of navigation bar
```

### 3.1 Schema Anatomy & Validation Rules

1. **`options`**: Typed inputs (`boolean`, `string`, `number`, `choice`, `file`) with validation constraints (`choices`, `min`/`max`, `required`, conditional dependencies `condition: { id, value }`).
2. **`doc`**: Frontmatter attributes required or consumed by the template.
3. **`parts`**: Modular structural components rendered conditionally (`[# if parts.abstract #]`).
4. **`files`**: Strict whitelist of files and assets copied to target build artifacts.
5. **`packages`**: Pre-declared LaTeX/Typst packages to prevent redundant import declarations.

---

## 4. Web Theme Layouts & Slots (`mystmd.org/guide/website-templates`)

MyST website templates convert documents and notebooks into accessible, responsive HTML static sites.

### 4.1 Bundled Themes Comparison

| Theme | Best Suited For | Primary Layout Features |
| :--- | :--- | :--- |
| **`book-theme`** (Default) | Multi-page documentation, systems hubs, manuals, computational books. | Hierarchical primary TOC sidebar, nested navigation, in-page outline sidebar, multi-locale routing. |
| **`article-theme`** | Scientific research papers, stand-alone computational studies with supporting notebooks. | Single primary narrative document, banner hero block, author affiliation modals/cards, supporting notebook appendices. |

### 4.2 Website Layout Regions & Slots

```text
┌──────────────────────────────────────────────────────────────────┐
│ Banner (site.parts.banner)                                       │
├──────────────────────────────────────────────────────────────────┤
│ Header: Logo, Title (logo_text), Navigation (site.nav), Actions  │
├───────────────────────┬──────────────────────────┬───────────────┤
│ Primary Sidebar       │ Content Window           │ Secondary     │
│ (TOC navigation)      │ Main article content     │ Sidebar       │
│                       │ & page metadata          │ (In-page      │
│ [site.parts.          │                          │  outline)     │
│  primary_sidebar_     │                          │               │
│  footer]              │                          │               │
├───────────────────────┴──────────────────────────┴───────────────┤
│ Footer (site.parts.footer)                                       │
└──────────────────────────────────────────────────────────────────┘
```

### 4.3 Full Site Options Reference (`site.options`)

| Option | Type | Description |
| :--- | :--- | :--- |
| `logo` | `file` | Light theme brand logo. |
| `logo_dark` | `file` | Dark theme brand logo. |
| `logo_text` | `string` | Text displayed alongside logo in header. |
| `logo_url` | `string` | Custom link destination for logo (defaults to `/`). |
| `logo_alt` | `string` | Accessible text alternative for logo. |
| `favicon` | `file` | Path to browser favicon. |
| `internal_domains` | `string` | Wildcard domain patterns treated as native internal links (`*.softcloud.dev`). |
| `folders` | `boolean` | Preserves folder directory structure in URL paths. |
| `hide_toc` | `boolean` | Suppresses primary TOC sidebar globally or per page. |
| `hide_outline` | `boolean` | Suppresses right-hand heading outline sidebar. |
| `hide_footer_links`| `boolean` | Hides previous/next pagination links. |
| `hide_title_block` | `boolean` | Suppresses auto-rendered page title block. |
| `hide_authors` | `boolean` | Suppresses page authors block. |
| `hide_search` | `boolean` | Disables client-side search indexing modal. |
| `outline_maxdepth` | `number` | Heading level threshold (1–6) for the outline. |
| `numbered_references` | `boolean` | Renders numerical citation references. |
| `style` | `file` | Path to custom stylesheet for site-wide injection. |

### 4.4 Top-Level Site Navigation & Actions

- **`site.nav`**: Multi-page navigation bar links and dropdown menus.
- **`site.actions`**: Prominent call-to-action buttons in header (e.g. GitHub repo link, primary artifact downloads).
- **`site.parts`**: Custom markdown injection slots (`banner`, `primary_sidebar_footer`, `footer`).

### 4.5 Per-Page Overrides

Any site option can be customized on a per-document basis directly in the markdown page frontmatter:

```markdown
---
title: Custom Landing Page
site:
  hide_toc: true
  hide_outline: true
---
```

---

## 5. Website Metadata & Data Layer (`mystmd.org/guide/website-metadata`)

MyST generates dual layers of metadata for all published web pages: a human-facing presentation layer and a machine-readable data layer.

### 5.1 Presentation & SEO Metadata

| Frontmatter Field | Behavior / Scope | Rendered Target |
| :--- | :--- | :--- |
| `title` | Page & Project | HTML `<title>`, Open Graph `og:title`, Twitter `twitter:title`, search snippets. |
| `description` | Page & Project | HTML `<meta name="description">`, `og:description`, `twitter:description`. |
| `thumbnail` | Page & Project | Open Graph image `og:image`, `twitter:image`, social card previews. |
| `keywords` / `tags` | Page & Project | `<meta name="keywords">`, document taxonomy, and in-site topic categorization. |
| `authors` | Page can override Project | Rendered author block, indexing metadata, and citation attribution. |
| `license` | Page can override Project | Machine-readable SPDX license link and footer/article licensing notice. |
| `github` | Project | "Edit this page" repository source links and revision provenance. |

### 5.2 Machine-Readable Data Layer

1. **JSON Data URLs (`.json`)**:
   - Every rendered HTML page produces a companion `.json` file containing its complete AST, metadata, structure, and AST tokens.
   - For standard sites: `https://domain.com/page` -> `https://domain.com/page.json`.
   - For folder-structured sites (`folders: true`): `https://domain.com/section/page/` -> `https://domain.com/section.page.json`.
2. **Cross-Reference Registry (`myst.xref.json`)**:
   - Served at the root (`/myst.xref.json`), cataloging every page, heading, figure, code cell, and equation identifier across the project.
   - Enables federated inter-project referencing (`External References`) without hardcoded URLs.
3. **Robots & Sitemaps**:
   - Automated `robots.txt` declaring crawler policy and referencing the root `sitemap.xml`.
   - `sitemap.xml` paired with `sitemap_style.xsl` for styled human and crawler discoverability.
   - Multilingual canonical and reciprocal `hreflang` annotations for internationalized routing.

---

## 6. Implementation Blueprint in SoftCloud (`myst.yml`)

The SoftCloud repository aligns its configuration with the MyST and JTeX template architecture:

```yaml
version: 1
project:
  id: hub
  title: SoftCloud — Systems Documentation and Laboratories
  short_title: SoftCloud Hub
  description: Project documentation, architecture notes, and laboratory resources for SoftCloud systems.
  github: https://github.com/soft-cloud-dev/soft-cloud-dev
  license: BSD-2-Clause
  authors:
    - name: SoftCloud Systems Team
      website: https://my.softcloud.dev/
      github: soft-cloud-dev
  thumbnail: images/logo.png
  keywords:
    - SoftCloud
    - Cloud Infrastructure
    - FreeBSD
    - Linux
    - FreeIPA
    - Systems Architecture
  plugins:
    - assets/plugins/myst-webawesome.mjs

site:
  template: book-theme
  nav:
    - title: Hub
      url: https://my.softcloud.dev/
    - title: Node Linux
      url: https://linux.softcloud.dev/
    - title: FreeIPA
      url: https://freeipa.softcloud.dev/
    - title: GitHub
      url: https://github.com/soft-cloud-dev
  actions:
    - title: GitHub
      url: https://github.com/soft-cloud-dev/soft-cloud-dev
  options:
    favicon: images/favicon.ico
    logo: images/logo.svg
    logo_dark: images/logo-dark.svg
    logo_alt: SoftCloud
    logo_text: SoftCloud
    logo_url: https://my.softcloud.dev/
    internal_domains: "*.softcloud.dev"
```

### Key Architectural Decisions:
1. **Intra-Network Domain Mapping**: `internal_domains: "*.softcloud.dev"` ensures seamless cross-subdomain navigation without external link decorations.
2. **Consistent Identity Lockup**: Pinned `logo_text` and `logo_url` maintain unified header identity across all devices.
3. **Machine-Readable Metadata**: Complete project frontmatter (`license`, `authors`, `thumbnail`) generates compliant Open Graph, Twitter Cards, and AST JSON representations across all 5 compiled locales.
