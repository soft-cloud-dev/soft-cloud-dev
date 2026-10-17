"""scripts/create-webawesome-notebook.py
Generates the authoritative Web Awesome and Font Awesome reference & showcase notebook.
Focuses strictly on relevant components, tokens, utilities, and Font Awesome 6.5.2 icons
supported in SoftCloud, with zero external framework boilerplate or unsupported Pro features.
Integrates both native MyST Markdown directives/roles and the Python UI API.
"""

import json
from pathlib import Path

notebook = {
    "cells": [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# Web Awesome & Font Awesome Reference & Showcase\n",
                "\n",
                "This notebook serves as the interactive reference and live component showcase for **Web Awesome 3.14.0** and **Font Awesome Free 6.5.2** within the SoftCloud architecture.\n",
                "\n",
                "SoftCloud integrates Web Awesome via **authentic Lit SSR Declarative Shadow DOM (DSD)**. Components are rendered statically on the server during the build, minimizing cumulative layout shift (Page CLS <= 0.1, Component CLS <= 0.01) and hydrating seamlessly in the browser. Authors can create components either programmatically in Python notebooks using the `softcloud_ui.UI` API or declaratively in MyST Markdown using native directives and roles."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "import sys\n",
                "from pathlib import Path\n",
                "from IPython.display import display, HTML\n",
                "\n",
                "# Locate repository root and import assets/python/softcloud_ui\n",
                "root = Path.cwd().resolve()\n",
                "while root.name and root.name != 'soft-cloud-dev':\n",
                "    if (root / 'assets' / 'python').is_dir():\n",
                "        break\n",
                "    root = root.parent\n",
                "py_dir = root / 'assets' / 'python'\n",
                "if str(py_dir) not in sys.path:\n",
                "    sys.path.insert(0, str(py_dir))\n",
                "\n",
                "from softcloud_ui import UI, TrustedHTML\n",
                "print(\"✓ SoftCloud UI API & Web Awesome Lit SSR runtime initialized.\")"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "---\n",
                "## 1. Choosing Components by User Intent (`choosing-components`)\n",
                "\n",
                "When designing interactive technical documentation or laboratory notes, choose components based on **user intent** rather than visual styling alone:\n",
                "\n",
                "| User Intent | Recommended Component | Allowed Variants / Options | Primary Use Case |\n",
                "|---|---|---|---|\n",
                "| **System Status & Feedback** | `<wa-callout>` | `brand`, `neutral`, `success`, `warning`, `danger` | Operational status, warnings, configuration caveats, test outcomes |\n",
                "| **Command & Navigation** | `<wa-button>` | `brand`, `neutral`, `success`, `warning`, `danger` | Terminal actions, documentation links, script triggers, downloads |\n",
                "| **Structured Surface / Entity** | `<wa-card>` | `outlined`, `filled`, `accent`, `filled-outlined`, `plain` | Server node specs, service dashboards, media previews, metric summaries |\n",
                "| **Semantic Iconography** | `<wa-icon>` / Font Awesome | `solid`, `regular`, `brands` (FA 6.5.2) | Infrastructure icons, code symbols, security badges, brand logos |\n",
                "\n",
                "### Interface Parity: Python API vs. MyST Directives\n",
                "Authors can author the exact same component using either Python or MyST Markdown:\n",
                "\n",
                "| Component | Python Notebook API | MyST Markdown Syntax |\n",
                "|---|---|---|\n",
                "| **Callout** | `UI.callout_text(text,`<br/>`&nbsp;&nbsp;title=..., variant=...)` | ````{wa-callout} Title`<br/>`:variant: brand`<br/>`Content...`<br/>```` |\n",
                "| **Button** | `UI.button(label,`<br/>`&nbsp;&nbsp;href=..., variant=...)` | ````{wa-button} https://link`<br/>`:variant: brand`<br/>`Button Label`<br/>```` |\n",
                "| **Card** | `UI.card_text(text,`<br/>`&nbsp;&nbsp;header=..., appearance=...)` | ````{wa-card} Card Header`<br/>`:appearance: filled-outlined`<br/>`Content...`<br/>```` |\n",
                "| **Icon** | `UI.icon(name,`<br/>`&nbsp;&nbsp;family=..., variant=...)` | `{fa}` `solid server` or<br/>`{icon}` `rocket` |\n",
                "\n",
                "```{wa-callout} Component Selection Quick Start\n",
                ":variant: brand\n",
                ":appearance: filled-outlined\n",
                "Choose components based on author intent: callouts for alerts, buttons for actions, cards for surfaces, and icons for semantic cues.\n",
                "```"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Python API Callout verification\n",
                "display(UI.callout_text(\n",
                "    \"All Web Awesome components in this notebook are transformed with authentic Lit Declarative \"\n",
                "    \"Shadow DOM (DSD). They render immediately before client JavaScript executes, ensuring minimal layout shift (Component CLS <= 0.01).\",\n",
                "    title=\"SSR Architecture Active\",\n",
                "    variant=\"brand\",\n",
                "    appearance=\"filled-outlined\"\n",
                "))"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "---\n",
                "## 2. Web Awesome Core Component Reference (`components/`)\n",
                "\n",
                "SoftCloud provides first-class SSR support for four core Web Awesome custom elements. Below are their specifications, allowed attributes, and interactive showcases.\n",
                "\n",
                "### 2.1 Buttons (`<wa-button>`)\n",
                "Buttons trigger actions or navigate to resources. They support distinct semantic variants, surface appearances, sizes, and shape modifications:\n",
                "\n",
                "- **Variants**: `brand` (primary theme action), `neutral` (secondary action), `success` (confirmation/positive action), `warning` (cautionary action), `danger` (destructive action).\n",
                "- **Appearances**: `filled` (high contrast, default), `accent`, `outlined` (subtle border), `filled-outlined`, `plain` (ghost/flat button).\n",
                "- **Sizes**: `xs`, `s`, `m` (medium / default), `l`, `xl`. Compact size tokens ensure zero runtime console deprecations.\n",
                "- **Shapes & Modifiers**: `pill` (fully rounded caps), `circle` (equal aspect icon button), `disabled` (inaccessible state), `loading` (spinner state), `caret` (dropdown indicator).\n",
                "- **Navigation**: `href` (validated link URL) and `target` (`_blank`, `_self`; automatically enforces `rel=\"noopener noreferrer\"`).\n",
                "\n",
                "```{wa-button} https://my.softcloud.dev/\n",
                ":variant: brand\n",
                ":appearance: filled\n",
                ":size: m\n",
                "Documentation Home Portal\n",
                "```"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Button variants showcase\n",
                "variants = [\"brand\", \"neutral\", \"success\", \"warning\", \"danger\"]\n",
                "for var in variants:\n",
                "    display(UI.button(f\"{var.capitalize()} Action\", variant=var, size=\"m\"))"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Button sizes, appearances, and pill modifiers\n",
                "display(UI.button(\"Small Outlined\", variant=\"brand\", appearance=\"outlined\", size=\"s\"))\n",
                "display(UI.button(\"Medium Filled Pill\", variant=\"brand\", pill=True, size=\"m\"))\n",
                "display(UI.button(\"Large Success Action\", variant=\"success\", size=\"l\"))\n",
                "display(UI.button(\"External Documentation\", href=\"https://my.softcloud.dev/\", variant=\"neutral\", target=\"_blank\"))"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "### 2.2 Callouts (`<wa-callout>`)\n",
                "Callouts highlight important notes, warnings, prerequisites, and status updates inline within prose or computational workflows:\n",
                "\n",
                "- **Variants**:\n",
                "  - `brand`: General announcements, feature updates, architectural highlights.\n",
                "  - `neutral`: General notes, contextual background, tips.\n",
                "  - `success`: Completed operations, verified tests, system readiness.\n",
                "  - `warning`: Deprecations, prerequisites, resource constraints.\n",
                "  - `danger`: Critical errors, failure modes, security warnings.\n",
                "- **Appearances**: `accent`, `filled`, `outlined`, `filled-outlined`, `plain`.\n",
                "- **Title Slot**: Accessible header text announcing the callout purpose (rendered in default content slot).\n",
                "\n",
                "```{wa-callout} Operational Integrity Notice\n",
                ":variant: success\n",
                ":appearance: filled-outlined\n",
                "All node telemetry, security policies, and health probes pass continuously with minimal layout shift.\n",
                "```"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Callout variants showcase via Python UI helper\n",
                "display(UI.callout_text(\n",
                "    \"Production clusters use immutable OS images booted over ZFS root pools.\",\n",
                "    title=\"Architecture Notice\",\n",
                "    variant=\"brand\",\n",
                "    appearance=\"filled-outlined\"\n",
                "))\n",
                "display(UI.callout_text(\n",
                "    \"All unit, integration, and security test suites completed with 100% pass rate.\",\n",
                "    title=\"Verification Passed\",\n",
                "    variant=\"success\",\n",
                "    appearance=\"filled-outlined\"\n",
                "))\n",
                "display(UI.callout_text(\n",
                "    \"Rolling node restart requires migrating active KVM guests before draining.\",\n",
                "    title=\"Maintenance Prerequisite\",\n",
                "    variant=\"warning\",\n",
                "    appearance=\"filled-outlined\"\n",
                "))\n",
                "display(UI.callout_text(\n",
                "    \"Authentication failure: kerberos ticket expired. Renew credentials via kinit.\",\n",
                "    title=\"Security Alert\",\n",
                "    variant=\"danger\",\n",
                "    appearance=\"filled-outlined\"\n",
                "))\n",
                "display(UI.callout_text(\n",
                "    \"Configuration parameters can be tuned in /etc/softcloud/cluster.conf.\",\n",
                "    title=\"Operational Tip\",\n",
                "    variant=\"neutral\",\n",
                "    appearance=\"filled-outlined\"\n",
                "))"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "### 2.3 Cards (`<wa-card>`)\n",
                "Cards are flexible, structured containers for grouping related information, system nodes, metrics, or media:\n",
                "\n",
                "- **Appearances**: `outlined` (default, subtle 1px border), `accent`, `filled`, `filled-outlined`, `plain`.\n",
                "- **Named Slots**:\n",
                "  - `header`: Title or top action bar.\n",
                "  - `media`: Visual media (image or diagram) placed flush against top edge.\n",
                "  - `default`: Body content (paragraphs, metric lists, code).\n",
                "  - `footer`: Action buttons, metadata, or timestamps.\n",
                "\n",
                "```{wa-card} Infrastructure Overview\n",
                ":appearance: filled-outlined\n",
                ":header: Host Specification\n",
                ":footer: FreeIPA Kerberos SSO Enabled\n",
                "SoftCloud cluster hosts execute Linux and FreeBSD kernels with unified directory authentication and ZFS storage pools.\n",
                "```"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Card with header, structured body, and footer via Python UI helper\n",
                "display(UI.card_text(\n",
                "    \"SoftCloud nodes run FreeBSD and Rocky Linux kernels with unified FreeIPA authentication. \"\n",
                "    \"Telemetry is collected at 5-second intervals via OpenTelemetry collectors.\",\n",
                "    header=\"Compute Node: node-01.softcloud.dev\",\n",
                "    footer=\"Status: Healthy | CPU: 12% | Memory: 4.2 / 32 GB\",\n",
                "    appearance=\"filled-outlined\"\n",
                "))"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Card composed with TrustedHTML including nested status badges\n",
                "card_html = \"\"\"\n",
                "<div style=\"display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;\">\n",
                "  <span style=\"font-weight: 600; font-size: 1.1rem;\">Cluster Storage Pool (ZFS)</span>\n",
                "  <span class=\"sc-wa-telemetry-status online\">ONLINE</span>\n",
                "</div>\n",
                "<p style=\"margin: 0 0 0.75rem 0; color: var(--wa-color-text-quiet, #64748b);\">Pool <code>tank-nvme</code>: 8x 3.84TB NVMe SSDs in RAIDZ2. Scrub completed with zero checksum errors.</p>\n",
                "<div class=\"sc-wa-telemetry\">\n",
                "  Capacity: 18.2 TB / 30.7 TB (59% allocated) &bull; Free: 12.5 TB\n",
                "</div>\n",
                "\"\"\"\n",
                "display(UI.card_trusted_html(\n",
                "    TrustedHTML(card_html),\n",
                "    header=\"Storage Telemetry\",\n",
                "    appearance=\"outlined\"\n",
                "))"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "---\n",
                "## 3. Font Awesome 6.5.2 Icon Reference & Showcase\n",
                "\n",
                "SoftCloud includes **Font Awesome Free 6.5.2** self-hosted locally under `vendor/fontawesome/`. This provides over 2,000 vector icons across three core styles:\n",
                "\n",
                "- **`solid` (`fas`)**: High-contrast filled icons for infrastructure, actions, hardware, and system status.\n",
                "- **`regular` (`far`)**: Outlined icons for subtle indicators and secondary UI controls.\n",
                "- **`brands` (`fab`)**: Authentic brand and technology marks for open-source software, cloud platforms, and operating systems.\n",
                "\n",
                "### Icon Roles & Syntax\n",
                "Icons can be embedded in MyST Markdown or invoked via Python:\n",
                "- **MyST Font Awesome Role**: `{fa}` `solid server` or `{fa}` `brands github`\n",
                "- **MyST Web Awesome Icon Role**: `{icon}` `rocket`\n",
                "- **Python UI Helper**: `UI.icon(\"server\", family=\"classic\", variant=\"solid\", label=\"Compute Server\")` or `UI.icon_grid(items)`\n",
                "\n",
                "Inline examples in Markdown:\n",
                "- Server: {fa}`solid server`\n",
                "- Terminal: {fa}`solid terminal`\n",
                "- GitHub: {fa}`brands github`\n",
                "- Rocket: {icon}`rocket`"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Cloud & Systems Architecture Icons\n",
                "cloud_icons = [\n",
                "    (\"server\", \"Compute Server\"),\n",
                "    (\"cloud\", \"Cloud Network\"),\n",
                "    (\"database\", \"Database Instance\"),\n",
                "    (\"network-wired\", \"Ethernet / LAN\"),\n",
                "    (\"cubes\", \"Container Cluster\"),\n",
                "    (\"hard-drive\", \"ZFS Storage Pool\"),\n",
                "    (\"microchip\", \"CPU Cores\"),\n",
                "    (\"sitemap\", \"Network Topology\"),\n",
                "]\n",
                "\n",
                "print(\"Cloud & Infrastructure Icons (Font Awesome Free 6.5.2 Solid):\")\n",
                "display(UI.icon_grid(cloud_icons, family=\"classic\", variant=\"solid\"))\n"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# DevOps, Code & Terminal Icons\n",
                "devops_icons = [\n",
                "    (\"terminal\", \"CLI / Terminal\"),\n",
                "    (\"code\", \"Source Code\"),\n",
                "    (\"code-branch\", \"Git Branch\"),\n",
                "    (\"laptop-code\", \"Development Workstation\"),\n",
                "    (\"box-open\", \"Package Release\"),\n",
                "    (\"gears\", \"System Configuration\"),\n",
                "    (\"wrench\", \"Maintenance Tool\"),\n",
                "    (\"file-code\", \"Script / Manifest\"),\n",
                "]\n",
                "\n",
                "print(\"DevOps & Developer Tooling Icons:\")\n",
                "display(UI.icon_grid(devops_icons, family=\"classic\", variant=\"solid\"))\n"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Security, Authentication & Status Icons\n",
                "sec_icons = [\n",
                "    (\"shield-halved\", \"Firewall / Bastion\"),\n",
                "    (\"lock\", \"TLS / SSL Encrypted\"),\n",
                "    (\"key\", \"SSH / API Key\"),\n",
                "    (\"user-shield\", \"FreeIPA Identity\"),\n",
                "    (\"fingerprint\", \"Biometric Auth\"),\n",
                "    (\"vault\", \"Secrets Vault\"),\n",
                "    (\"circle-check\", \"Check Passed\"),\n",
                "    (\"triangle-exclamation\", \"Alert / Caution\"),\n",
                "]\n",
                "\n",
                "print(\"Security, Identity & Status Indicators:\")\n",
                "display(UI.icon_grid(sec_icons, family=\"classic\", variant=\"solid\"))\n"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Open Source, OS & Brand Icons (brands style)\n",
                "brand_icons = [\n",
                "    (\"github\", \"GitHub\"),\n",
                "    (\"linux\", \"Linux\"),\n",
                "    (\"python\", \"Python\"),\n",
                "    (\"docker\", \"Docker\"),\n",
                "    (\"rust\", \"Rust\"),\n",
                "    (\"freebsd\", \"FreeBSD\"),\n",
                "    (\"git-alt\", \"Git\"),\n",
                "    (\"markdown\", \"MyST Markdown\"),\n",
                "]\n",
                "\n",
                "print(\"Open Source Ecosystem Brands:\")\n",
                "display(UI.icon_grid(brand_icons, family=\"brands\"))\n"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "---\n",
                "## 4. Design Tokens & CSS Utilities Reference (`tokens/`, `utilities/`)\n",
                "\n",
                "Web Awesome is built on a design token architecture. CSS custom properties allow consistent spacing, color grading, shadows, and responsive typography across all components.\n",
                "\n",
                "### 4.1 Design Token Reference\n",
                "\n",
                "| Token Family | CSS Variable Pattern | Example Value | Description |\n",
                "|---|---|---|---|\n",
                "| **Brand Colors** | `--wa-color-brand-{05-95}` | `var(--wa-color-brand-60)` | Primary accent hue for interactive elements and brand accents |\n",
                "| **Neutral Grays** | `--wa-color-gray-{05-95}` | `var(--wa-color-gray-20)` | Surface backgrounds, borders, and structural dividers |\n",
                "| **Semantic Colors** | `--wa-color-{success\\|warning\\|danger}-{60}` | `var(--wa-color-success-60)` | State indicators for health, warnings, and errors |\n",
                "| **Text Contrast** | `--wa-color-text-{normal\\|quiet\\|loud}` | `var(--wa-color-text-normal)` | Accessible text contrast hierarchy |\n",
                "| **Spacing Scale** | `--wa-space-{3xs\\|2xs\\|xs\\|s\\|m\\|l\\|xl\\|2xl\\|3xl}` | `var(--wa-space-m)` (1.0rem) | Consistent margin, padding, and layout gap scale |\n",
                "| **Border Radius** | `--wa-border-radius-{xs\\|s\\|m\\|l\\|full}` | `var(--wa-border-radius-m)` (0.5rem) | Container corner rounding |\n",
                "| **Elevation / Shadow** | `--wa-shadow-{xs\\|sm\\|md\\|lg\\|xl}` | `var(--wa-shadow-md)` | Depth layers for cards, menus, and overlays |\n",
                "\n",
                "### 4.2 Utility CSS Classes\n",
                "Web Awesome provides lightweight utility classes in `styles/webawesome.css`:\n",
                "- **Typography**:\n",
                "  - `.wa-text-quiet`: Subdued secondary text for timestamps, descriptions, and labels.\n",
                "  - `.wa-text-normal`: Standard body copy contrast.\n",
                "  - `.wa-text-loud`: Emphasized high-contrast text.\n",
                "  - `.wa-prose`: Typographic formatting wrapper for markdown articles.\n",
                "- **Accessibility**:\n",
                "  - `.wa-visually-hidden`: Hides content visually while remaining fully accessible to screen readers.\n",
                "- **Rounding Utilities**:\n",
                "  - `.wa-rounded-sm`, `.wa-rounded-md`, `.wa-rounded-lg`, `.wa-rounded-full`."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Demonstrating Web Awesome design tokens and utilities in custom markup\n",
                "token_demo_html = \"\"\"\n",
                "<div style=\"border: 1px solid var(--wa-color-gray-25, #e2e8f0); border-radius: var(--wa-border-radius-l, 0.75rem); padding: var(--wa-space-l, 1.5rem); background: var(--wa-color-gray-05, #f8fafc); box-shadow: var(--wa-shadow-sm, 0 1px 2px rgba(0,0,0,0.05));\">\n",
                "  <div style=\"display: flex; gap: var(--wa-space-s, 0.75rem); align-items: center; margin-bottom: var(--wa-space-xs, 0.5rem);\">\n",
                "    <span style=\"display: inline-block; width: 0.75rem; height: 0.75rem; border-radius: 9999px; background: var(--wa-color-brand-60, #2563eb);\"></span>\n",
                "    <span class=\"wa-text-loud\" style=\"font-size: 1.1rem;\">Web Awesome Token Architecture</span>\n",
                "  </div>\n",
                "  <p class=\"wa-text-normal\" style=\"margin: 0 0 var(--wa-space-s, 0.75rem) 0;\">\n",
                "    Tokens provide consistent spacing (<code>--wa-space-*</code>), colors (<code>--wa-color-*</code>), and depth (<code>--wa-shadow-*</code>) that dynamically adapt between light and dark modes.\n",
                "  </p>\n",
                "  <div style=\"display: flex; gap: var(--wa-space-m, 1rem); flex-wrap: wrap;\">\n",
                "    <span class=\"wa-text-quiet\" style=\"font-size: 0.85rem;\">&bull; Border Radius: <code>var(--wa-border-radius-l)</code></span>\n",
                "    <span class=\"wa-text-quiet\" style=\"font-size: 0.85rem;\">&bull; Spacing: <code>var(--wa-space-l)</code></span>\n",
                "    <span class=\"wa-text-quiet\" style=\"font-size: 0.85rem;\">&bull; Shadow: <code>var(--wa-shadow-sm)</code></span>\n",
                "  </div>\n",
                "</div>\n",
                "\"\"\"\n",
                "display(UI.card_trusted_html(TrustedHTML(token_demo_html), appearance=\"plain\"))"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "---\n",
                "## 5. Usage Patterns, Themes & Architecture (`usage`, `themes`)\n",
                "\n",
                "### 5.1 Lit SSR & Declarative Shadow DOM (DSD) Lifecycle\n",
                "In SoftCloud, Web Awesome web components follow a modern three-stage lifecycle:\n",
                "\n",
                "1. **Build-Time Transformation (`scripts/lit-ssr-transform.mjs`)**:\n",
                "   During site compilation, HTML placeholders produced by MyST directives and Jupyter notebook outputs are parsed using `parse5`. The component render model generates custom elements and attaches `<template shadowroot=\"open\" shadowrootmode=\"open\">` containing the server-rendered template.\n",
                "2. **Instant Paint (Page CLS <= 0.1, Component CLS <= 0.01)**:\n",
                "   The browser immediately renders the component internals via native Declarative Shadow DOM before client-side scripts download or execute. There is no cumulative layout shift or flash of unstyled content.\n",
                "3. **Seamless Hydration (`webawesome.ssr-loader.js`)**:\n",
                "   The SSR autoloader adopts the existing shadow root without destroying or re-rendering the DOM tree, attaching event listeners and reactivity in place.\n",
                "\n",
                "### 5.2 Theme Synchronization\n",
                "SoftCloud's `softcloud-theme.js` automatically coordinates theme state:\n",
                "- Matches MyST book-theme light and dark mode toggles.\n",
                "- Applies `.wa-dark` / `.wa-light` classes to the `<html>` root element.\n",
                "- Design tokens automatically remap contrast ratios, backgrounds, and text shades for optimal readability.\n",
                "\n",
                "```{wa-callout} Theme Coordination Status\n",
                ":variant: brand\n",
                ":appearance: filled-outlined\n",
                "Theme synchronization operates synchronously via softcloud-theme.js without client hydration mismatch.\n",
                "```"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "display(UI.callout_text(\n",
                "    \"Theme synchronization operates synchronously via softcloud-theme.js. \"\n",
                "    \"Toggling between light and dark mode updates both MyST CSS variables and Web Awesome design tokens simultaneously.\",\n",
                "    title=\"Theme Synchronization Operational\",\n",
                "    variant=\"brand\",\n",
                "    appearance=\"filled-outlined\"\n",
                "))"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "---\n",
                "## 6. Real-World Composite Showcase\n",
                "\n",
                "Below are real-world composite UI patterns commonly used in SoftCloud laboratory and systems documentation.\n",
                "\n",
                "### 6.1 Cluster Node Specification Card\n",
                "A complete specification card combining icons, data metrics, status tags, and action buttons:"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "node_spec_html = \"\"\"\n",
                "<div style=\"display: flex; flex-direction: column; gap: 1rem;\">\n",
                "  <div style=\"display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--wa-color-gray-20, #e2e8f0); padding-bottom: 0.75rem;\">\n",
                "    <div>\n",
                "      <div style=\"font-weight: 700; font-size: 1.2rem;\">node-prod-04.infra.softcloud.dev</div>\n",
                "      <div class=\"wa-text-quiet\" style=\"font-size: 0.85rem;\">Rocky Linux 9.4 (Blue Onyx) &bull; Kernel 5.14.0-427</div>\n",
                "    </div>\n",
                "    <span class=\"sc-wa-telemetry-status online\">\n",
                "      ONLINE &bull; HEALTHY\n",
                "    </span>\n",
                "  </div>\n",
                "\n",
                "  <div style=\"display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem;\">\n",
                "    <div class=\"sc-wa-telemetry\">\n",
                "      <div class=\"wa-text-quiet\" style=\"font-size: 0.8rem; text-transform: uppercase;\">Compute</div>\n",
                "      <div style=\"font-weight: 700; font-size: 1.1rem; margin-top: 0.2rem;\">64 vCPUs (AMD EPYC)</div>\n",
                "      <div class=\"wa-text-quiet\" style=\"font-size: 0.8rem;\">Load: 0.42, 0.38, 0.35</div>\n",
                "    </div>\n",
                "    <div class=\"sc-wa-telemetry\">\n",
                "      <div class=\"wa-text-quiet\" style=\"font-size: 0.8rem; text-transform: uppercase;\">Memory</div>\n",
                "      <div style=\"font-weight: 700; font-size: 1.1rem; margin-top: 0.2rem;\">256 GB ECC DDR5</div>\n",
                "      <div class=\"wa-text-quiet\" style=\"font-size: 0.8rem;\">Allocated: 64.5 GB (25%)</div>\n",
                "    </div>\n",
                "    <div class=\"sc-wa-telemetry\">\n",
                "      <div class=\"wa-text-quiet\" style=\"font-size: 0.8rem; text-transform: uppercase;\">Network</div>\n",
                "      <div style=\"font-weight: 700; font-size: 1.1rem; margin-top: 0.2rem;\">2x 25 GbE LACP</div>\n",
                "      <div class=\"wa-text-quiet\" style=\"font-size: 0.8rem;\">RX: 1.2 Gbps &bull; TX: 850 Mbps</div>\n",
                "    </div>\n",
                "  </div>\n",
                "</div>\n",
                "\"\"\"\n",
                "display(UI.card_trusted_html(\n",
                "    TrustedHTML(node_spec_html),\n",
                "    header=\"System Telemetry & Resource Monitor\",\n",
                "    footer=\"Last telemetry refresh: 10 seconds ago via FreeIPA SSO\",\n",
                "    appearance=\"filled-outlined\"\n",
                "))"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "### 6.2 Maintenance & Incident Action Banner\n",
                "A high-priority alert callout paired with interactive action buttons:\n",
                "\n",
                "```{wa-callout} Scheduled Infrastructure Maintenance\n",
                ":variant: warning\n",
                "Scheduled kernel live-patching will commence at 02:00 UTC. Workloads on node-prod-04 will be live-migrated to standby capacity automatically.\n",
                "```\n",
                "\n",
                "```{wa-button} https://my.softcloud.dev/\n",
                ":variant: brand\n",
                ":size: m\n",
                "View Live Migration Runbook\n",
                "```"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "display(UI.callout_text(\n",
                "    \"Scheduled kernel live-patching will commence at 02:00 UTC. \"\n",
                "    \"Workloads on node-prod-04 will be live-migrated to standby capacity automatically.\",\n",
                "    title=\"Scheduled Infrastructure Maintenance\",\n",
                "    variant=\"warning\",\n",
                "    appearance=\"filled-outlined\"\n",
                "))\n",
                "display(UI.button(\"View Live Migration Runbook\", href=\"https://my.softcloud.dev/\", variant=\"brand\", size=\"m\"))"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "print(\"✓ Web Awesome & Font Awesome computational reference and showcase executed successfully.\")"
            ]
        }
    ],
    "metadata": {
        "kernelspec": {
            "display_name": "Python (JB2)",
            "language": "python",
            "name": "jb2-python"
        },
        "language_info": {
            "name": "python",
            "version": "3.12.14"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 5
}

for i, cell in enumerate(notebook["cells"]):
    cell["id"] = f"wa-docs-cell-{i+1:02d}"

target = Path("notebooks/webawesome-docs.ipynb")
target.write_text(json.dumps(notebook, indent=1), encoding="utf-8")
print(f"Generated {target} ({len(notebook['cells'])} cells)")
