---
description: Guidelines for authoring accessible, portable MyST documentation with Web Awesome interactive examples and Lit SSR primitives.
keywords:
  - MyST
  - Web Awesome
  - web components
  - authoring
  - progressive enhancement
tags:
  - contributing
  - documentation
  - web-components
edit_url: https://github.com/soft-cloud-dev/soft-cloud-dev/edit/main/components/authoring-guide.md
source_url: https://github.com/soft-cloud-dev/soft-cloud-dev/blob/main/components/authoring-guide.md
---

# Web Awesome + MyST Documentation Authoring Guide

## Design rule

**Use MyST built-ins for documentation layout. Use the existing typed Web Awesome directives for server-rendered button/card/callout/icon primitives. Use `{anywidget}` for client-side previews and stateful interaction that the typed SSR path does not cover.** A component demo may compose these primitives; do not add duplicate component frameworks or claim that a client-only widget has Lit SSR.

:::{admonition} Current implementation
:class: note

Versions come from the checked-in `package.json`, `package-lock.json`, and `requirements.lock`; the component inventory comes from `components/catalog.json`. Four typed primitives (`{wa-button}`, `{wa-card}`, `{wa-callout}`, and `{icon}` / `{fa}` for `wa-icon`) use genuine Lit SSR/Declarative Shadow DOM. Other licensed Core previews use the existing `{anywidget}` client runtime. Pro references do not load an unlicensed runtime.
:::

## Component selection policy

| Author intent | Prefer | Web Awesome only when |
| --- | --- | --- |
| Note, warning, hint, status prose | MyST `{note}`, `{warning}`, `{admonition}` | The callout is part of interactive app UI. |
| Static information tile | MyST `{card}` | Media slots and Web Awesome component behavior are required. |
| Responsive editorial grouping | MyST `{grid}`, `{grid-item}` | A runtime layout control is needed. |
| Alternative explanations or code samples | MyST `{tab-set}` / `{tab-item}` | Tabs are application controls with state and custom events. |
| Image/caption | MyST Markdown image or `{figure}` | Zoom, comparison, carousel, or motion controls are needed. |
| Links/paragraph/code tables | Native Markdown, roles, code fences | No Web Awesome replacement. |
| Static Web Awesome buttons, cards, callouts and icons | Typed `{wa-button}`, `{wa-card}`, `{wa-callout}` directives, `{icon}`/`{fa}` roles | Use the existing Lit SSR/DSD path instead of a widget for an ordinary static instance. |
| Interactive forms, menus, dialogs, toasts, sliders or bound state | Web Awesome in `{anywidget}` | Use the browser-hosted demo when a typed directive is unavailable or event/state handling is necessary. |
| Reused explanatory fragments | MyST `{include}` or `{embed}` | Reuse custom element atoms *inside* an interactive preview. |
| Executable research outputs | Jupyter notebook + MyST cross-references | Output must have a custom control. |

## Documentation page contract

Follow the upstream [Tab Group](https://webawesome.com/docs/components/tab-group/) example: name, tag, version/availability, concise description, working example, usage variants, API (imports, slots, attributes/properties, events, CSS properties and parts, dependencies, SSR), accessibility, and source references. Distinguish **confirmed** APIs from planned enhancements; missing sections must not be invented. Individual atomic pages such as [`wa-tab`](navigation/tab.md) link to their parent group without duplicating the entire parent API.

Each component page should include: a descriptive heading with the actual tag, official documentation and GitHub source links (with MyST's transformer), an optional relevant background citation (not a mandatory generic Wikipedia definition), a Core/Pro availability marker, a live preview if licensed, a full copyable HTML snippet, a short MyST alternative where applicable, real example media with provenance, and inter-component dependencies.

## Portable MyST layout first

:::::{grid} 1 1 2 2
:::{card} Native documentation card
No JavaScript or additional plugin API is needed for this card.
:::
::::{card} Native documentation warning
:::{warning}
The example data is not a live service status.
:::
::::
:::::

Use native MyST tabs for editorial explanations and snippet alternatives. The inner directive below is *example source*, shielded by a four-backtick code fence; the outer directives have distinct 5/4-colon delimiters.

:::::{tab-set}
::::{tab-item} MyST note
````myst
:::{note}
Use this for publication notes.
:::
````
::::
::::{tab-item} Interactive app control
```html
<wa-tab-group active="media">
  <wa-tab panel="media">Media</wa-tab>
  <wa-tab-panel name="media">Interactive content</wa-tab-panel>
</wa-tab-group>
```
::::
:::::

Typed SSR/DSD and browser widgets have separate roles. Prefer this supported typed primitive for a server-rendered call to action:

````myst
:::{wa-button}
:variant: brand
:href: https://my.softcloud.dev/
Open SoftCloud
:::
````

Use a widget for an interactive form or a live demonstration requiring browser-side state. The rendered documentation must remain legible when the preview cannot execute.
## Browser-only component preview host: `{anywidget}`

The existing `widgets/webawesome-demo.mjs` consumes structured JSON and creates allowlisted DOM elements using `document.createElement` and `document.createTextNode`. The model is **data**, never raw or trusted HTML; it must reject event-handler attributes and non-HTTPS/dangerous URL schemes. Runtime assets and component modules are self-hosted, and the loader must not be duplicated. **The `/static/showcase/...` URL in the executable model below is a site-specific runtime asset, not a portable Markdown or HTML snippet.** For published images use MyST relative image references; in reusable HTML examples use an application-supplied relative asset URL.

Example reusable atomic composition:

```{anywidget} ../widgets/webawesome-demo.mjs
{
  "tree": {
    "tag": "wa-tab-group",
    "attrs": { "active": "sample" },
    "children": [
      { "tag": "wa-tab", "attrs": { "panel": "sample" }, "children": ["Photo"] },
      { "tag": "wa-tab-panel", "attrs": { "name": "sample" },
        "children": [
          { "tag": "img", "attrs": { "src": "/static/showcase/rocket.jpg", "alt": "Falcon 9 rocket launch" } }
        ]
      }
    ]
  }
}
```

## Copyable media markup and provenance

For standalone HTML, substitute a file shipped with the consuming application rather than copying the SoftCloud-only `/static/showcase/` asset URL:

```html
<img src="./images/rocket.jpg" alt="Falcon 9 rocket launch">
```

## Native documentation media and provenance

Use real self-hosted images with descriptive `alt` text, source credit and explicit licensing; prefer the shared [Showcase media](showcase-media.md) assets over text placeholders and externally hosted stock imagery. The actual sample photographs are reproducible inputs to screenshots and visual regression tests. The only allowlisted remote showcase media are `https://shoelace.style/assets/images/walk.gif` (animated-image example) and `https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4` (native video example). CI must reject other remote media dependencies unless reviewed and added to this allowlist. Never present Pro components as executable without an installed Pro runtime.

## Build and SSR boundaries

1. MyST parses Markdown, grids, cards, tabs, notes, and anywidget directives in locale-specific builds.
2. Existing staging copies `assets/static/showcase` to `static/showcase` under the assembled HTML output. Anywidget resolves local component modules from the self-hosted Web Awesome distribution.
3. The existing Lit/parse5 post-processing pass handles the four typed Web Awesome SSR primitives; keep this contract stable and do not add SSR to all 90 catalog components.
4. Translation sources stay English-first; translations and narration must be regenerated through the existing per-locale workflows without translating JSON keys or HTML attribute names.
5. Verify the generated HTML for valid MyST layouts, loaded media, tab and carousel keyboard navigation, nonempty `alt` text, expected local asset paths, and no console/network failures.

## Practical composition recipes

The [practical pattern library](practical-patterns.md) adapts the **marketing, application UI, and ecommerce categories** shown in Tailwind Plus into original MyST-first patterns. It does not copy proprietary Tailwind Plus component source and does not add a CSS framework; its examples deliberately combine real credited media, native editorial layouts, and the existing Web Awesome anywidget primitives.

:::{note} Native authoring progress
The **component-catalog integration-status notices** have been migrated to MyST `{note}`/`{warning}` and the catalog index now uses `{note}`. The existing typed Web Awesome directives/roles still exist for opt-in functional use; this content migration does not remove their implementation. Upstream-grade API tables beyond the Tab Group exemplar remain phased work.
:::

## Migration and acceptance plan

Source-of-truth versions: `package.json` for Web Awesome, `requirements.lock` for MyST/Jupyter Book, and `components/catalog.json` for component counts. This avoids stale numbers in prose. Status indicates implementation observed in source, not a claim that the deployed site has passed all gates.

| Phase | Status | Deliverable | Measurable acceptance |
| --- | --- | --- | --- |
| P0 | Implemented; rendered regression pending | Bundle and credit real media, with live anywidget examples. | Every local media URL resolves in a built site; the manifest records credit/license for every file; rendered examples contain real images. |
| P1 | Implemented; regression pending | Use MyST native notes, tabs, cards and grids for documentation prose. | Catalog status blocks use native directives, no duplicate layout API, no escaped example fences in output. |
| P2 | In progress | Generate version-matched API sections from the installed Web Awesome Custom Elements Manifest (CEM), with explicit Core/Pro/source-only boundaries. | Every supported Core tag has a CEM-matched attributes/events/slots/CSS-parts section or a documented manifest gap; generated sections are checked for drift in CI. |
| P3 | Partial | Strict locale builds, accessibility, link checking, browser, visual, and no-JS checks. | All enabled locales pass `jupyter book build --html --strict`; axe reports zero serious/critical violations on tested routes; link checks have zero broken required links; asset and no-JS tests pass; remote media requests are restricted to the documented GIF and MDN MP4 allowlist. |

### No-JavaScript requirements

Client-only `{anywidget}` previews may not render without JavaScript. Every preview page must preserve readable text and a copyable source example outside the widget, plus a static semantic fallback where essential content would otherwise be unavailable. The existing typed SSR primitives retain their own tested DSD/no-JS path.
### Not in scope
No copying proprietary Web Awesome Pro code, not turning Markdown paragraphs into custom elements, no new client framework, no fake SSR for anywidget, no dynamic download of media during deterministic build.
