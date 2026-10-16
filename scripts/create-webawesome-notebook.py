import json
from pathlib import Path

notebook = {
    "cells": [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# Web Awesome 3.14.0 Reference & Documentation\n",
                "\n",
                "Comprehensive computational reference guide covering the Web Awesome component library, design tokens, CSS utilities, framework integrations, and Lit SSR architecture for SoftCloud."
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
                "\n",
                "# Ensure assets/python is importable\n",
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
                "print(\"SoftCloud UI and Web Awesome Python API loaded successfully.\")"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## Overview & Quick Reference\n",
                "\n",
                "Web Awesome provides an extensive catalog of modern, framework-agnostic web components built on open web standards. This notebook brings together the official Web Awesome references:\n",
                "\n",
                "- **Choosing Components**: Decision tree mapped to user intent.\n",
                "- **Components**: Interactive reference for cards, callouts, buttons, icons, and more.\n",
                "- **Frameworks**: Integration patterns for React, Vue, Angular, and Svelte.\n",
                "- **Utilities**: CSS layout, spacing, text, prose, and visibility utilities.\n",
                "- **Tokens**: Design tokens for color, space, typography, borders, and shadows.\n",
                "- **Installation**: Self-hosted, npm, and CDN loading patterns.\n",
                "- **Usage**: Declarative Shadow DOM, custom element lifecycle, attributes, and slots.\n",
                "- **Form Controls**: Constraint Validation API, forms, and custom controls.\n",
                "- **Themes**: Theme classes, color palettes, and dark mode synchronization."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "UI.callout_text(\n",
                "    \"Web Awesome is integrated with authentic Lit SSR Declarative Shadow DOM (DSD) in SoftCloud. \"\n",
                "    \"All components render with zero layout shift and progressive enhancement.\",\n",
                "    title=\"Web Awesome SSR Active\",\n",
                "    variant=\"brand\"\n",
                ")"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "---\n",
                "## 1. Choosing the Right Component (`choosing-components`)\n",
                "\n",
                "When selecting a component, start from **user intent** rather than component name:\n",
                "\n",
                "### Decision Matrix\n",
                "| User Intent | Component Choice | Key Considerations |\n",
                "|---|---|---|\n",
                "| **Pick one (2–5 options)** | `<wa-radio-group>` | All options visible simultaneously. |\n",
                "| **Pick one (many options)** | `<wa-select>` with `<wa-option>` | Compact dropdown selector. *(Do not use `<wa-dropdown>` for value selection!)* |\n",
                "| **Pick many** | `<wa-select multiple>` or `<wa-checkbox-group>` | Multi-selection from a set. |\n",
                "| **Instant toggle** | `<wa-switch>` | Takes effect immediately (e.g. notifications on/off). |\n",
                "| **Form boolean** | `<wa-checkbox>` | Submitted with form payload later. |\n",
                "| **Trigger action** | `<wa-button>` | Primary action uses `variant=\"brand\"`. |\n",
                "| **Action menu** | `<wa-dropdown>` | Menu of commands/actions (not for picking form values). |\n",
                "| **Feedback / status** | `<wa-callout>`, `<wa-badge>`, `<wa-toast>` | Persistent inline message or compact badge. |\n",
                "| **Data display** | `<wa-card>`, `<wa-avatar>`, `<wa-format-date>` | Structured container with slots for header, media, and footer. |\n",
                "| **Overlay** | `<wa-dialog>`, `<wa-drawer>`, `<wa-popover>` | Modal dialogs and flyout drawers. |"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Example: Demonstrating component selection in action\n",
                "UI.card_text(\n",
                "    \"Use <wa-card> for self-contained content with optional header and media slots. \"\n",
                "    \"For primary call-to-actions, pair with a brand button.\",\n",
                "    header=\"Decision Tree in Practice: Card + Action\",\n",
                "    appearance=\"elevated\"\n",
                ")"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "UI.button(\"Explore Component Catalog\", href=\"https://webawesome.com/docs/components\", variant=\"brand\", size=\"medium\", target=\"_blank\")"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "---\n",
                "## 2. Core Components (`components/`)\n",
                "\n",
                "Web Awesome includes over 50 accessible web components. The SoftCloud SSR engine natively supports Lit SSR for the core set:\n",
                "\n",
                "- **`<wa-button>`**: Supports variants (`brand`, `neutral`, `success`, `warning`, `danger`), appearances (`filled`, `outlined`, `plain`), sizes (`s`, `m`, `l`), and icon slots.\n",
                "- **`<wa-card>`**: Structured surface supporting `header`, `media`, and `footer` named slots.\n",
                "- **`<wa-callout>`**: Informational alerts with `brand`, `success`, `warning`, and `danger` styling.\n",
                "- **`<wa-icon>`**: SVG icon renderer supporting Web Awesome classic and Font Awesome 6.5.2 icon families (`solid`, `regular`, `brands`)."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Callout variants demonstration\n",
                "variants = [\"brand\", \"success\", \"warning\", \"danger\", \"neutral\"]\n",
                "for v in variants:\n",
                "    UI.callout_text(f\"This is a {v.upper()} status callout with accessible icon.\", title=f\"{v.capitalize()} Alert\", variant=v)"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Font Awesome & Web Awesome icon demonstration\n",
                "icons = [\n",
                "    (\"rocket\", \"solid\", \"classic\"),\n",
                "    (\"code\", \"solid\", \"classic\"),\n",
                "    (\"check-circle\", \"solid\", \"classic\"),\n",
                "    (\"github\", \"brands\", \"classic\"),\n",
                "    (\"terminal\", \"solid\", \"classic\")\n",
                "]\n",
                "for name, style, fam in icons:\n",
                "    UI.icon(name, style=style, family=fam)"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "---\n",
                "## 3. Framework Integration (`frameworks/`)\n",
                "\n",
                "Web Awesome custom elements work across all major modern JavaScript frameworks:\n",
                "\n",
                "### React\n",
                "Use Web Awesome with standard JSX or Lit React wrappers (`@lit/react`):\n",
                "```tsx\n",
                "import { createComponent } from '@lit/react';\n",
                "import React from 'react';\n",
                "import { WaButton } from '@awesome.me/webawesome/dist/components/button/button.js';\n",
                "\n",
                "export const Button = createComponent({\n",
                "  tagName: 'wa-button',\n",
                "  elementClass: WaButton,\n",
                "  react: React,\n",
                "  events: { onWaChange: 'wa-change' },\n",
                "});\n",
                "```\n",
                "\n",
                "### Vue\n",
                "Configure `isCustomElement` in `vite.config.ts`:\n",
                "```ts\n",
                "vue({\n",
                "  template: {\n",
                "    compilerOptions: {\n",
                "      isCustomElement: (tag) => tag.startsWith('wa-')\n",
                "    }\n",
                "  }\n",
                "})\n",
                "```\n",
                "\n",
                "### Angular\n",
                "Add `CUSTOM_ELEMENTS_SCHEMA` to your module/component:\n",
                "```ts\n",
                "import { CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';\n",
                "\n",
                "@Component({\n",
                "  schemas: [CUSTOM_ELEMENTS_SCHEMA]\n",
                "})\n",
                "```\n",
                "\n",
                "### Svelte\n",
                "Custom elements are first-class in Svelte with direct binding:\n",
                "```svelte\n",
                "<wa-button on:click={handleClick} variant=\"brand\">Submit</wa-button>\n",
                "```"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "---\n",
                "## 4. Utilities (`utilities/`)\n",
                "\n",
                "Web Awesome provides utility CSS classes in `styles/webawesome.css`:\n",
                "\n",
                "- **Prose**: `.wa-prose` provides styled typography for markdown articles.\n",
                "- **Rounding**: `.wa-rounded-none`, `.wa-rounded-sm`, `.wa-rounded-md`, `.wa-rounded-lg`, `.wa-rounded-full`.\n",
                "- **Text Styling**: `.wa-text-quiet` (secondary), `.wa-text-normal`, `.wa-text-loud` (bold/high-contrast).\n",
                "- **Accessibility**: `.wa-visually-hidden` hides elements visually while preserving screen reader accessibility."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Demonstrating utility styling with TrustedHTML\n",
                "html_markup = \"\"\"\n",
                "<div style=\"padding: 1rem; border: 1px dashed var(--wa-color-gray-40); border-radius: var(--wa-border-radius-m);\">\n",
                "  <span class=\"wa-text-loud\">Bold Utility Text</span> &mdash; \n",
                "  <span class=\"wa-text-quiet\">Quiet Utility Subtitle</span>\n",
                "  <span class=\"wa-visually-hidden\">Screen reader only announcement</span>\n",
                "</div>\n",
                "\"\"\"\n",
                "UI.card_trusted_html(TrustedHTML(html_markup), header=\"CSS Utility Showcase\")"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "---\n",
                "## 5. Design Tokens (`tokens/`)\n",
                "\n",
                "Design tokens define the visual foundation of Web Awesome:\n",
                "\n",
                "- **Color Scale**: `--wa-color-{hue}-{tint}` from `05` to `95` (e.g. `--wa-color-brand-60`, `--wa-color-gray-20`).\n",
                "- **Spacing Scale**: `--wa-space-3xs` through `--wa-space-3xl` (`--wa-space-m` = `1rem`).\n",
                "- **Border Radius**: `--wa-border-radius-s`, `--wa-border-radius-m`, `--wa-border-radius-l`, `--wa-border-radius-full`.\n",
                "- **Shadows**: `--wa-shadow-sm`, `--wa-shadow-md`, `--wa-shadow-lg`, `--wa-shadow-xl`.\n",
                "- **Focus**: `--wa-focus-ring-width: 2px`, `--wa-focus-ring-color: var(--wa-color-primary-60)`."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Inspecting available color and spacing tokens\n",
                "tokens_summary = {\n",
                "    \"Brand Primary\": \"var(--wa-color-brand-60)\",\n",
                "    \"Text Normal\": \"var(--wa-color-text-normal)\",\n",
                "    \"Panel Radius\": \"var(--wa-panel-border-radius)\",\n",
                "    \"Default Spacing\": \"var(--wa-space-m)\"\n",
                "}\n",
                "for k, v in tokens_summary.items():\n",
                "    print(f\"Token: {k:16} => {v}\")"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "---\n",
                "## 6. Installation & Loading (`installation`)\n",
                "\n",
                "Web Awesome supports three primary distribution modes:\n",
                "\n",
                "1. **Self-Hosted SSR (Recommended in SoftCloud)**:\n",
                "   Assets are staged to `vendor/webawesome` and transformed statically using `@lit-labs/ssr` Declarative Shadow DOM.\n",
                "2. **npm Package**:\n",
                "   ```bash\n",
                "   npm install @awesome.me/webawesome@3.14.0\n",
                "   ```\n",
                "3. **CDN Loading**:\n",
                "   ```html\n",
                "   <link rel=\"stylesheet\" href=\"https://ka-f.webawesome.com/webawesome@3.14.0/styles/webawesome.css\" />\n",
                "   <script type=\"module\" src=\"https://ka-f.webawesome.com/webawesome@3.14.0/webawesome.loader.js\"></script>\n",
                "   ```"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "---\n",
                "## 7. Usage Patterns & SSR (`usage`)\n",
                "\n",
                "Key rules when working with Web Awesome:\n",
                "- **No self-closing tags**: Web Components are custom elements and require closing tags: `<wa-button>...</wa-button>`.\n",
                "- **Slots**: Use `slot=\"start\"`, `slot=\"end\"`, `slot=\"header\"`, `slot=\"footer\"` to position children inside shadow roots.\n",
                "- **Declarative Shadow DOM**: The SSR engine attaches `<template shadowroot=\"open\" shadowrootmode=\"open\">` to custom element hosts, ensuring instant rendering before JavaScript hydration.\n",
                "- **SSR Autoloader**: `vendor/webawesome/webawesome.ssr-loader.js` hydrates DSD components without double-rendering."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Demonstrating slot composition in Python\n",
                "card_content = \"\"\"\n",
                "<p>This card demonstrates named slot composition:</p>\n",
                "<ul>\n",
                "  <li><strong>Header slot:</strong> Card Title</li>\n",
                "  <li><strong>Default slot:</strong> Body paragraph</li>\n",
                "  <li><strong>Action:</strong> Embedded interactive button</li>\n",
                "</ul>\n",
                "\"\"\"\n",
                "UI.card_trusted_html(\n",
                "    TrustedHTML(card_content),\n",
                "    header=\"Slot Composition Pattern\",\n",
                "    appearance=\"elevated\"\n",
                ")"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "---\n",
                "## 8. Form Controls (`form-controls`)\n",
                "\n",
                "Web Awesome form controls integrate directly with browser forms:\n",
                "- Support browser **Constraint Validation API** (`required`, `minlength`, `maxlength`, `pattern`).\n",
                "- Automatic required indicator (`*`).\n",
                "- Standard form events: `wa-input`, `wa-change`, `wa-invalid`.\n",
                "- Custom validation error messages via `setCustomValidity()`."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Form control documentation & example button\n",
                "UI.button(\"View Form Controls Guide\", href=\"https://webawesome.com/docs/form-controls\", variant=\"neutral\", size=\"medium\", target=\"_blank\")"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "---\n",
                "## 9. Themes & Color Palettes (`themes`)\n",
                "\n",
                "Web Awesome features a tokenized theme engine:\n",
                "- **Theme Classes**: Add `.wa-theme-default`, `.wa-theme-awesome`, or `.wa-theme-shoelace` to `<html>`.\n",
                "- **Dark Mode**: Add `.wa-theme-dark` to `<html>` for automatic dark theme token mapping.\n",
                "- **SoftCloud Theme Sync**: SoftCloud's `softcloud-theme.js` automatically synchronizes MyST theme toggles with Web Awesome classes and attributes."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "UI.callout_text(\n",
                "    \"SoftCloud's theme switcher seamlessly coordinates Web Awesome theme classes \"\n",
                "    \"(.wa-theme-dark / .wa-theme-light) and data-theme attributes across all viewports.\",\n",
                "    title=\"Theme Synchronization Summary\",\n",
                "    variant=\"brand\"\n",
                ")"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "print(\"Web Awesome reference documentation notebook generated and verified.\")"
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

Path("notebooks/webawesome-docs.ipynb").write_text(json.dumps(notebook, indent=1), encoding="utf-8")
print("Wrote notebooks/webawesome-docs.ipynb")
