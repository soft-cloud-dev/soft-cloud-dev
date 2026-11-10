# MyST Markdown Complete Guide & Implementation Reference

This document serves as the authoritative, comprehensive technical reference and authoring specification for the **MyST Markdown** ecosystem, covering the 24 official guides across six functional pillars and detailing their concrete mapping into the **SoftCloud** publishing pipeline ([`soft-cloud-dev`](file:///Users/user/data/Projects/soft-cloud-dev)).

---

## 1. Executive Architecture & Taxonomy

MyST (Markedly Structured Text) is an extensible, scientific dialect of CommonMark designed for technical publishing, computational notebooks, and documentation hubs. It combines the simplicity of Markdown with the semantic richness of reStructuredText (roles and directives) and native Jupyter execution.

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                            MyST Document Engine                              │
├───────────────────────────────┬──────────────────────────────────────────────┤
│ 1. Content & Scientific Markup│ • CommonMark Syntax       • Typography       │
│                               │ • Admonitions & Callouts  • Figures & Media  │
│                               │ • Math & Equations        • Structured Tables│
│                               │ • Code & Executable Cells • Cross-References │
│                               │ • External References     • Embed Directives │
│                               │ • Citations (BibTeX)      • Proofs/Theorems  │
│                               │ • Mermaid/Graphviz        • Asides & Margins │
│                               │ • Dropdowns, Cards, Tabs  • Layout Grids     │
├───────────────────────────────┼──────────────────────────────────────────────┤
│ 2. Navigation & Theming       │ • Project TOC Hierarchy   • Top Navbar       │
│                               │ • Action Buttons          • Internal Domains │
│                               │ • Book Theme vs. Article  • Part Slots       │
├───────────────────────────────┼──────────────────────────────────────────────┤
│ 3. Metadata, SEO & Style      │ • Frontmatter Data Layer  • Open Graph / Card│
│                               │ • Robots & Sitemaps       • Custom CSS & Vars│
│                               │ • WCAG A11y Standards     • Lit SSR / DSD    │
├───────────────────────────────┼──────────────────────────────────────────────┤
│ 4. Analytics & Downloads      │ • Privacy Analytics       • Multi-Format PDF │
│                               │ • Notebook Downloads      • Word Docx / JATS │
├───────────────────────────────┼──────────────────────────────────────────────┤
│ 5. CI/CD Deployment           │ • GitHub Actions Pipeline • Static Artifacts │
│                               │ • Zero-JS Fallbacks       • Custom CNAME     │
├───────────────────────────────┼──────────────────────────────────────────────┤
│ 6. Landing Pages              │ • Uncluttered Hero Canvas • Action Catalogs  │
│                               │ • Feature Matrices        • Responsive Grids │
└───────────────────────────────┴──────────────────────────────────────────────┘
```

---

## Group 1: Core Content & Scientific Markup Specification

### 1. CommonMark Foundations (`guide/commonmark`)
MyST conforms strictly to the **CommonMark specification** for all baseline prose elements:
- **Headings**: `# H1` through `###### H6`. MyST automatically slugifies heading text into anchor identifiers (e.g. `## Network Topologies` yields `#network-topologies`).
- **Paragraphs & Line Breaks**: Standard Markdown whitespace rules apply. A blank line separates paragraphs. Two trailing spaces or a backslash `\` produce a hard line break `<br />`.
- **Inline Formatting**:
  - `*italic*` or `_italic_` for emphasis.
  - `**bold**` or `__bold__` for strong importance.
  - `` `inline code` `` for identifiers, file paths, and syntax fragments.
  - `[Hyperlink](https://my.softcloud.dev)` for web targets.
- **Block Elements**:
  - Unordered lists (`- `, `* `, `+ `) and ordered lists (`1. `). Nested sub-lists must indent by 2 or 4 spaces.
  - Blockquotes (`> `) for editorial citations and quotations.
  - Thematic breaks / horizontal rules (`---` or `***`).
- **HTML Ingestion**: Safe, sanitized HTML tags (such as `<div>`, `<span>`, `<kbd>`, `<samp>`) pass through to the HTML renderer while preserving document safety.

### 2. Typography & Text Ensembles (`guide/typography`)
MyST enables typographically refined publishing features:
- **Smart Typography**: Automatic conversion of straight quotes (`"..."` and `'...'`) into directional typographic quotes (“...” and ‘...’), and consecutive periods (`...`) into ellipses (`…`).
- **Dashes**:
  - En-dash: `--` renders `–` (used for numerical and date ranges: `1984–2026`).
  - Em-dash: `---` renders `—` (used for editorial breaks and syntactic clauses).
- **Subscript & Superscript**:
  - Native syntax: `H~2~O` yields H₂O; `E = mc^2^` yields E = mc².
  - Semantic roles: `{sub}`2`` and `{sup}`2``.
- **Inline Delimiters & Text Styling**:
  - Strikethrough: `~~deprecated parameter~~` renders with a strikethrough line.
  - Underline: `{u}`underlined text`` role.
  - Abbreviations: `{abbr}`BGP (Border Gateway Protocol)`` renders an accessible tooltip with definition expansion.
- **Literal Escaping**: Special characters (such as `$`, `{`, `}`, `_`, `*`) are escaped using a preceding backslash `\$`.

### 3. Admonitions & Callouts (`guide/admonitions`)
Admonitions highlight vital contextual guidance, status notices, and operational risks:
- **Standard Directives**:
  ```markdown
  :::{note}
  Informational guidance or background context.
  :::

  :::{tip}
  Actionable advice or performance optimization technique.
  :::

  :::{warning}
  Operational warning regarding configuration drift or deprecation.
  :::

  :::{caution}
  High-risk notice regarding data loss, security boundaries, or failover events.
  :::

  :::{important}
  Required prerequisite or mandatory design contract.
  :::

  :::{danger}
  Destructive system operation notice.
  :::
  ```
- **Generic Admonitions with Custom Titles & Classes**:
  ```markdown
  :::{admonition} Operational SLA Verification
  :class: note
  The production FreeIPA replica fleet guarantees a 99.99% authentication SLA.
  :::
  ```
- **Collapsible / Dropdown Admonitions**:
  ```markdown
  :::{admonition} Historical Changelog
  :class: dropdown, tip
  Expanded details available on demand for archival inspection.
  :::
  ```
- **SoftCloud Implementation Rule**: Use native MyST admonitions for publication prose. Use `{wa-callout}` with Lit SSR only when rendering application UI mockups or interactive component showcases.

### 4. Figures & Media (`guide/figures`)
MyST provides first-class support for numbered, caption-bearing figures and media assets:
- **Directive Syntax**:
  ```markdown
  (fig-network-topology)=
  :::{figure} images/topology-edge.svg
  :alt: SoftCloud BGP Edge Routing Topology
  :width: 85%
  :align: center
  :name: fig-network-topology

  High-availability dual-homed BGP edge routing architecture.
  :::
  ```
- **Figure Anatomy**:
  - Target Anchor `(fig-network-topology)=` allows direct cross-referencing.
  - `:alt:` guarantees accessible screen-reader interpretation.
  - `:width:` / `:height:` enforce layout bounding boxes, preventing Cumulative Layout Shift (CLS).
  - The block body serves as the rich Markdown caption.
- **Subfigures**: Group multiple nested `{figure}` directives inside a parent container or grid to generate automatically indexed sub-labels (e.g., Figure 1(a), Figure 1(b)).

### 5. Mathematical Equations & Expressions (`guide/math`)
MyST renders mathematical notations deterministically using KaTeX in web distributions and native LaTeX in PDF builds:
- **Inline Equations**: `$P(A|B) = \frac{P(B|A)P(A)}{P(B)}\$`
- **Display Block Equations**:
  ```markdown
  $$
  \nabla \times \mathbf{E} = -\frac{\partial \mathbf{B}}{\partial t}
  $$ (eq:maxwell-faraday)
  ```
- **The `{math}` Directive**:
  ```markdown
  ```{math}
  :label: eq-navier-stokes
  \rho \left( \frac{\partial \mathbf{u}}{\partial t} + \mathbf{u} \cdot \nabla \mathbf{u} \right) = -\nabla p + \mu \nabla^2 \mathbf{u} + \mathbf{f}
  ```
  ```
- **AMS Environments**: Multi-line aligned systems using `\begin{align} ... \end{align}` or `\begin{cases} ... \end{cases}`.
- **Global Macro Definitions**: Configure project-wide or page-wide LaTeX macros in frontmatter:
  ```yaml
  math:
    \RR: "\\mathbb{R}"
    \vx: "\\mathbf{x}"
    \norm: "\\left\\| #1 \\right\\|"
  ```

### 6. Tables & Structured Data (`guide/tables`)
MyST supports both concise Markdown tables and complex, rich `{list-table}` definitions:
- **CommonMark Pipe Tables**:
  ```markdown
  | Protocol | Port | Transport | Purpose |
  | :--- | :---: | :--- | :--- |
  | HTTPS | 443 | TCP / QUIC | Secure API Gateway |
  | DNS | 53 | UDP / TCP | Split-Horizon Resolution |
  | Kerberos | 88 | TCP / UDP | FreeIPA Identity Ticket Granting |
  ```
- **The `{list-table}` Directive**: Ideal for multiline text, nested code, or explicit column ratios:
  ```markdown
  (table-firewall-rules)=
  ```{list-table} Edge Firewall Ingress Policy
  :header-rows: 1
  :widths: 20 15 25 40
  :name: table-firewall-rules

  * - Source CIDR
    - Port Range
    - Target Node
    - Security Justification
  * - `10.240.0.0/16`
    - `22/tcp`
    - Bastion Fleet
    - WireGuard VPN authenticated administrative access.
  * - `0.0.0.0/0`
    - `443/tcp`
    - Edge Load Balancer
    - Public egress gateway with TLS 1.3 termination.
  ```
  ```

### 7. Code Blocks & Executable Snippets (`guide/code`)
MyST code blocks provide syntax highlighting, line numbering, line emphasizing, and file transclusion:
- **Highlighted Code Fence**:
  ````markdown
  ```python
  :linenos:
  :emphasize-lines: 3, 5-7
  :caption: TLS Configuration Generator
  :name: code-tls-gen

  import ssl
  context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
  context.minimum_version = ssl.TLSVersion.TLSv1_3
  context.load_cert_chain(certfile="server.crt", keyfile="server.key")
  ```
  ````
- **Code Transclusion (`{literalinclude}`)**: Ingest raw source files directly from the repository, avoiding copy-paste discrepancies:
  ```markdown
  ```{literalinclude} ../scripts/stage-webawesome-assets.mjs
  :language: javascript
  :linenos:
  :lines: 1-25
  :caption: Web Awesome CDN Asset Staging Logic
  ```
  ```

### 8. Cross-References & Internal Linking (`guide/cross-references`)
MyST features an unambiguous cross-referencing model based on explicit target anchors:
- **Target Anchor Declaration**: Placed immediately above any heading, figure, table, equation, or code block:
  ```markdown
  (sec-cluster-storage)=
  ### Distributed Cluster Storage Architecture
  ```
- **Referencing Targets**:
  - Automatic Title Ingestion: `[](sec-cluster-storage)` resolves automatically to the heading title `"Distributed Cluster Storage Architecture"`.
  - Custom Link Text: `[Storage Architecture](sec-cluster-storage)`.
  - Explicit Roles:
    - `{ref}`sec-cluster-storage``
    - `{numref}`Figure %s <fig-network-topology>`` resolves to `"Figure 1"` or the localized number.
    - `{eq}`eq-maxwell-faraday`` generates a hyperlinked equation callout `(1)`.

### 9. External References & Intersphinx Registry (`guide/external-references`)
MyST projects can seamlessly reference external documentation sets without hardcoding URLs:
- **Configuring External Inventories (`myst.yml`)**:
  ```yaml
  project:
    references:
      python: https://docs.python.org/3/objects.inv
      lit: https://lit.dev/objects.inv
      cloud_core: https://my.softcloud.dev/myst.xref.json
  ```
- **Referencing External Symbols**:
  - `{doc}`python:library/asyncio``
  - `{term}`python:coroutine``
  - `[](cloud_core:sec-cluster-storage)` links directly into the resolved cross-project anchor.

### 10. Embedding Content & Computational Cells (`guide/embed`)
The `{embed}` directive enables transclusion of specific Jupyter Notebook cells, outputs, or Markdown fragments:
- **Directive Syntax**:
  ```markdown
  ```{embed} notebooks/experiment.ipynb#latency-boxplot
  :remove-input: true
  ```
  ```
- **Use Case**: Authors run a computational analysis in a `.ipynb` notebook, tag the visualization cell `latency-boxplot`, and embed only the generated chart directly into an executive architecture brief without duplicating the code.

### 11. Citations & Bibliographies (`guide/citations`)
MyST provides academic citation management powered by BibTeX:
- **Configuration**:
  ```yaml
  project:
    bibliography:
      - references.bib
  ```
- **In-Text Citations**:
  - Inline author-year: `[@lamport1994latex]` or `{cite}`lamport1994latex``.
  - Parenthetical citation: `{cite:p}`lamport1994latex; knuth1984literate``.
- **Rendering the Reference List**:
  ```markdown
  ### References
  ```{bibliography}
  :filter: docname in docnames
  ```
  ```

### 12. Proofs, Theorems, & Mathematical Statements (`guide/proofs-and-theorems`)
MyST includes native formal directives for theoretical, mathematical, and algorithmic literature:
- **Directives Available**: `{proof:theorem}`, `{proof:lemma}`, `{proof:definition}`, `{proof:corollary}`, `{proof:remark}`, `{proof:algorithm}`, `{proof:proof}`.
- **Example Usage**:
  ```markdown
  ```{proof:theorem} CAP Theorem
  :label: thm-cap
  It is impossible for a distributed data store to simultaneously provide more than two out of three guarantees: Consistency, Availability, and Partition Tolerance.
  ```

  ```{proof:proof}
  Follows by reduction to asynchronous network partitions as shown in [](thm-cap).
  ```
  ```

### 13. Diagrams & Visual Workflows (`guide/diagrams`)
MyST parses and renders diagrams natively as responsive vector graphics (SVGs):
- **Mermaid Directives**:
  ````markdown
  ```{mermaid}
  flowchart TD
    Client[Client Request] --> ALB[AWS ALB / Edge Gateway]
    ALB --> PodA[FreeIPA Node A]
    ALB --> PodB[FreeIPA Node B]
    PodA <-->|389/tcp Directory Sync| PodB
  ```
  ````
- **Graphviz Directives**:
  ````markdown
  ```{graphviz}
  digraph G {
    rankdir=LR;
    node [shape=box];
    Master -> Replica1;
    Master -> Replica2;
  }
  ```
  ````

### 14. Asides, Sidebars, & Margins (`guide/asides`)
Directives for editorial side content without interrupting narrative flow:
- **`{margin}`**: Content rendered on the outer desktop margin adjacent to the surrounding paragraph.
- **`{sidebar}`**: Floating sidebar block with an optional title that text wraps around.
- **`{aside}`**: Semantic aside for non-critical commentary.
  ```markdown
  ```{margin}
  **Security Note**: FreeIPA replication passwords rotate automatically via HashiCorp Vault every 30 days.
  ```
  ```

### 15. Dropdowns, Cards, & Tab Sets (`guide/dropdowns-cards-and-tabs`)
MyST provides built-in interactive layout blocks that require no external component libraries:
- **Dropdown Accordions**:
  ```markdown
  ```{dropdown} Production Rollout Checklist
  :open: false
  1. Verify BGP route convergence.
  2. Confirm DNS split-horizon records.
  3. Validate TLS cert expiry on SAN domains.
  ```
  ```
- **Editorial Cards**:
  ```markdown
  :::{card} Node Linux Architecture
  :header: Enterprise Linux Foundation
  Detailed kernel tuning parameters for high-throughput packet processing.
  ^^^
  Middle card segment.
  +++
  [Explore Node Linux Specs](projects/linux.md)
  :::
  ```
- **Tab Sets (`{tab-set}`)**:
  ````markdown
  ::::{tab-set}
  :::{tab-item} FreeBSD
  ```sh
  pkg install -y freeipa-client wireguard-tools
  ```
  :::
  :::{tab-item} Ubuntu / Debian
  ```sh
  apt-get update && apt-get install -y freeipa-client wireguard
  ```
  :::
  ::::
  ````
- **Responsive Layout Grids (`{grid}`)**:
  ```markdown
  ::::{grid} 1 2 2 3
  :gutter: 3

  :::{grid-item-card} High Availability
  Multi-region master-master replication.
  :::
  :::{grid-item-card} Zero Trust
  mTLS and Kerberos identity brokering.
  :::
  :::{grid-item-card} Observability
  Prometheus metrics and eBPF tracing.
  :::
  ::::
  ```

---

## Group 2: Website Structure, Navigation, & Templating

### 16. Website Navigation Architecture (`guide/website-navigation`)
Site hierarchy is governed by `project.toc` and `site.nav` in [`myst.yml`](file:///Users/user/data/Projects/soft-cloud-dev/myst.yml):
- **Table of Contents (`toc`) Structure**:
  ```yaml
  project:
    toc:
      - file: README.md
      - file: introduction.md
      - file: architecture.md
      - title: Systems & Infrastructure
        children:
          - file: projects/linux.md
          - file: projects/freebsd.md
      - title: Contributor Guide
        children:
          - file: components/authoring-guide.md
  ```
- **Top Navigation Bar (`site.nav`)**:
  ```yaml
  site:
    nav:
      - title: Hub
        url: https://my.softcloud.dev/
      - title: Node Linux
        url: https://linux.softcloud.dev/
      - title: FreeIPA
        url: https://freeipa.softcloud.dev/
      - title: Ecosystem
        children:
          - title: Web Awesome Docs
            url: /components/
          - title: Notebook Labs
            url: /notebooks/experiment
  ```
- **Header Actions (`site.actions`)**:
  ```yaml
  site:
    actions:
      - title: GitHub
        url: https://github.com/soft-cloud-dev/soft-cloud-dev
        icon: github
  ```
- **Internal Domains Configuration**:
  ```yaml
  site:
    options:
      internal_domains: "*.softcloud.dev"
  ```
  *Ensures links between `linux.softcloud.dev` and `my.softcloud.dev` are treated as internal routes without external link warning decorators.*

### 17. Website Templates & Layout Engine (`guide/website-templates`)
MyST websites compile via `@myst-theme` engines:
- **`book-theme`**: The default layout in SoftCloud, tailored for multi-page documentation hubs, hierarchical sidebars, and computational notebooks.
- **`article-theme`**: Tailored for single-document scientific preprints, standalone papers, and research presentations.
- **Structural Slots & Parts**:
  - `site.parts.banner`: Announcements or deprecation notices fixed at the top of every page.
  - `site.parts.primary_sidebar_footer`: Custom widgets or copyright tags pinned below the left TOC navigation tree.
  - `site.parts.footer`: Site-wide copyright notices and footer links.
  - `site.parts.navbar_end`: Additional status indicators or locale switchers in the top navigation bar.
- **Global & Page Options Reference**:
  ```yaml
  site:
    options:
      hide_toc: false          # Suppress primary left sidebar
      hide_outline: false      # Suppress secondary right heading outline
      hide_footer_links: false  # Hide Prev/Next pagination links
      folders: true            # Preserve nested URL directory paths
      outline_maxdepth: 3      # Maximum heading level rendered in outline
  ```

---

## Group 3: Website Metadata, SEO, Styling, Performance, & Accessibility

### 18. Website Metadata & Data Ecosystem (`guide/website-metadata`)
MyST standardizes document frontmatter into a dual presentation and data layer:
- **Frontmatter Schema**:
  ```yaml
  ---
  title: Production Cluster Architecture
  short_title: Architecture
  description: High-availability distributed edge computing and identity fabric.
  authors:
    - name: SoftCloud Systems Team
      email: systems@softcloud.dev
      affiliations:
        - SoftCloud Engineering
  license: BSD-2-Clause
  keywords: [BGP, FreeIPA, Linux, FreeBSD]
  thumbnail: images/logo.png
  ---
  ```
- **Machine-Readable Exports**:
  - **Companion JSON (`.json`)**: Every page generates a companion `.json` file (`/architecture.json`) containing its serialized AST and execution tokens.
  - **Cross-Reference Registry (`myst.xref.json`)**: Root catalog indexing all project targets, equations, headings, and figures for external federated linking.

### 19. SEO & Social Sharing Mechanics (`guide/seo-and-social`)
- **Open Graph & Twitter Cards**: MyST auto-generates `<meta property="og:title">`, `og:description`, `og:image`, and `<meta name="twitter:card" content="summary_large_image">` from the document title, description, and thumbnail.
- **Sitemap & Robots**:
  - Automatic `sitemap.xml` generated with `sitemap_style.xsl` for search engine crawlers.
  - Standard `robots.txt` declaring crawler rules and sitemap location.
- **Multilingual SEO**: In SoftCloud, [`tools/fix_seo_artifacts.py`](file:///Users/user/data/Projects/soft-cloud-dev/tools/fix_seo_artifacts.py) verifies reciprocal `hreflang` links across all 5 compiled locales (`en`, `pl`, `de`, `es`, `fr`), preventing duplicate content penalties.

### 20. Website Styling & Custom CSS (`guide/website-style`)
Custom visual styling is injected via `site.options.style`:
- **Theme Variables Override**:
  ```css
  :root {
    --myst-color-primary: #0284c7;
    --myst-color-primary-dark: #0369a1;
    --myst-font-family-body: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    --myst-font-family-mono: "JetBrains Mono", ui-monospace, monospace;
    --myst-max-width-content: 840px;
  }

  /* Dark mode overrides */
  .dark {
    --myst-color-primary: #38bdf8;
  }
  ```

### 21. Accessibility & Performance Benchmarks (`guide/accessibility-and-performance`)
- **WCAG 2.1 AA Standards**:
  - High-contrast text colors in both light and dark modes.
  - Semantic HTML5 landmarks: `<nav>`, `<main>`, `<header>`, `<footer>`, `<aside>`.
  - Accessible keyboard navigation across all interactive tabs, accordions, and dropdowns.
- **Zero-JS Lit SSR / Declarative Shadow DOM**:
  - SoftCloud's Web Awesome elements (`wa-card`, `wa-callout`, `wa-button`) are server-rendered with `<template shadowrootmode="open">` stamped with `did-ssr`.
  - Documents remain 100% readable and structurally complete when JavaScript is disabled or delayed.

---

## Group 4: Analytics & Publication Distribution

### 22. Web Analytics Integration (`guide/analytics`)
MyST supports privacy-friendly and enterprise analytics configured in `site.options`:
```yaml
site:
  options:
    analytics:
      plausible: my.softcloud.dev     # Privacy-focused, cookie-free analytics
      google: G-XXXXXXXXXX            # Google Analytics 4 Measurement ID
      fathom: ABCDEF                  # Fathom Analytics Site ID
```

### 23. Website Downloads & Artifact Export (`guide/website-downloads`)
MyST sites can provide direct download actions for published narratives in multiple compiled formats:
- **Site & Document Downloads Configuration**:
  ```yaml
  site:
    options:
      downloads:
        - id: pdf
          title: Compiled PDF (Typst / LaTeX)
        - id: ipynb
          title: Executable Jupyter Notebook
        - id: docx
          title: Word Document
        - id: md
          title: Markdown Source
  ```
- Readers access downloads directly through the page header action dropdown.

---

## Group 5: Continuous Integration & Deployment

### 24. GitHub Pages Deployment Lifecycle (`guide/deployment-github-pages`)
SoftCloud automates multi-locale build and deployment via [`.github/workflows/deploy.yml`](file:///Users/user/data/Projects/soft-cloud-dev/.github/workflows/deploy.yml):
1. **Runner Environment**: Runs on Ubuntu 24.04 with pinned Python 3.12 (`requirements.lock`) and Node.js 20 (`package-lock.json`).
2. **Preflight Checks**:
   - `scripts/check-node-dependencies.mjs` verifies asset consistency.
   - `scripts/check-security-parity.mjs` enforces URL safety policies and CSP constraints.
3. **Multilingual Compilation**:
   - `tools/build.sh` invokes Jupyter Book 2 across all locales.
   - Post-build transforms run Declarative Shadow DOM stamps and SEO sitemap generation.
4. **Publishing Artifact**:
   - `actions/upload-pages-artifact@v3` packages `_build/html`.
   - `actions/deploy-pages@v4` publishes the final artifact with custom domain routing ([`CNAME`](file:///Users/user/data/Projects/soft-cloud-dev/CNAME) -> `my.softcloud.dev`).

---

## Group 6: Presentation & High-Impact Landing Pages

### 25. High-Impact Website Landing Pages (`guide/website-landing-pages`)
A landing page presents a clean, distraction-free entry point into a documentation ecosystem:
- **Frontmatter Layout Suppression**:
  ```yaml
  ---
  title: SoftCloud Systems Documentation
  site:
    hide_toc: true           # Suppresses left navigation tree
    hide_outline: true       # Suppresses right-hand outline
    hide_title_block: true   # Replaces default header with custom hero
  ---
  ```
- **Hero & Action Banner Architecture**:
  ```markdown
  # SoftCloud Engineering & Systems Laboratory

  > Modern cloud infrastructure, FreeBSD/Linux systems architecture, and identity federations.

  ::::{grid} 1 2 3 3
  :gutter: 3

  :::{grid-item-card} 🚀 Node Linux
  Enterprise Linux configuration profiles, kernel tuning, and automated deployment.
  +++
  [View Node Linux Docs](projects/linux.md)
  :::

  :::{grid-item-card} 🔒 FreeIPA Identity
  Centralized identity management, Kerberos, DNS, and mTLS trust fabric.
  +++
  [View FreeIPA Architecture](architecture.md)
  :::

  :::{grid-item-card} 📊 Computational Labs
  Reproducible experiments and telemetry analysis notebooks.
  +++
  [Explore Notebooks](notebooks/experiment.ipynb)
  :::
  ::::
  ```

---

## Implementation Comparison: MyST Built-ins vs. SoftCloud Lit SSR

| Requirement | Native MyST Directive | SoftCloud Web Awesome (Lit SSR / DSD) | Selection Policy |
| :--- | :--- | :--- | :--- |
| **Callout / Admonition** | `:::{note}`, `:::{warning}` | `:::{wa-callout}` (`variant="neutral"`) | Prefer MyST for all prose; use `wa-callout` for UI component specs. |
| **Card / Tile** | `:::{card}` | `:::{wa-card}` | Prefer MyST `{card}` for documentation; use `wa-card` when demonstrating Web Awesome slots. |
| **Call to Action** | CommonMark `[Button](url)` | `:::{wa-button}` (`variant="brand"`) | Use `wa-button` with SSR for primary hero CTA buttons. |
| **Tabs / Variant Code** | `::::{tab-set}` | `<wa-tab-group>` (Client-only) | **Always** use `tab-set` for documentation; client element is for live app demos only. |
| **Icons** | Unicode / SVG images | `{icon}` / `{fa}` roles | Use `{icon}` / `{fa}` roles to render self-hosted SVG font icons. |
| **Interactive Demos** | Jupyter Notebook output | `{anywidget}` / `widgets/webawesome-demo.mjs` | Use `{anywidget}` with data JSON for interactive client demos with static fallbacks. |

---

## Related Project Artifacts

- Architecture & JTeX Template Specification: [`docs/myst-template-mapping.md`](file:///Users/user/data/Projects/soft-cloud-dev/docs/myst-template-mapping.md)
- Web Awesome Authoring Guide: [`components/authoring-guide.md`](file:///Users/user/data/Projects/soft-cloud-dev/components/authoring-guide.md)
- Component Documentation Contract: [`docs/verification/component-documentation-contract.md`](file:///Users/user/data/Projects/soft-cloud-dev/docs/verification/component-documentation-contract.md)
- Project Configuration Manifest: [`myst.yml`](file:///Users/user/data/Projects/soft-cloud-dev/myst.yml)
- Deployment Pipeline: [`.github/workflows/deploy.yml`](file:///Users/user/data/Projects/soft-cloud-dev/.github/workflows/deploy.yml)
