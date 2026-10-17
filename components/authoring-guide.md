# Web Awesome + MyST Documentation Authoring Guide

## Design rule

**Keep Web Awesome for interactive component behavior using the existing `{anywidget}` integration; keep MyST built-ins for documentation layout and portable content.** Avoid new MyST component directives, new SSR shims, and duplicate card/tab/alert implementations.

:::{admonition} Current implementation
:class: note

The repository pins Web Awesome 3.14.0 and Jupyter Book 2.1.7. The 90-page catalog has client-side live previews for Core components that can be loaded safely, Pro references without unlicensed executables, and four legacy typed directives/roles with genuine Lit SSR/DSD. Do not conflate client-only anywidget previews with server-rendered output.
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
| Forms, inputs, menus, dialogs, toast, sliders | Web Awesome in `{anywidget}` | These require live browser interaction. |
| Reused explanatory fragments | MyST `{include}` or `{embed}` | Reuse custom element atoms *inside* an interactive preview. |
| Executable research outputs | Jupyter notebook + MyST cross-references | Output must have a custom control. |

## Documentation page contract

Follow the upstream [Tab Group](https://webawesome.com/docs/components/tab-group/) example: name, tag, version/availability, concise description, working example, usage variants, API (imports, slots, attributes/properties, events, CSS properties and parts, dependencies, SSR), accessibility, and source references. Distinguish **confirmed** APIs from planned enhancements; missing sections must not be invented. Individual atomic pages such as [`wa-tab`](navigation/tab.md) link to their parent group without duplicating the entire parent API.

Each component page should include: a descriptive heading with the actual tag, official documentation and GitHub source links (with MyST's transformer), an appropriately attributed Wikipedia context quotation where present, a Core/Pro availability marker, a live preview if licensed, a full copyable HTML snippet, a short MyST alternative where applicable, real example media with provenance, and inter-component dependencies.

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

Use native MyST documentation tabs for explanations and snippets. Do not replace these with `<wa-tab-group>` just to style source code:

::::{tab-set}
:::{tab-item} MyST note
```myst
:::{note}
Use this for publication notes.
:::
```
:::
:::{tab-item} Interactive app control
```html
<wa-tab-group active="media">
  <wa-tab panel="media">Media</wa-tab>
  <wa-tab-panel name="media">Interactive content</wa-tab-panel>
</wa-tab-group>
```
:::
::::

## Anywidget is the only catalog preview host

The existing `widgets/webawesome-demo.mjs` consumes structured JSON and creates allowlisted DOM elements using `document.createElement` and `document.createTextNode`. The model is **data**, never raw or trusted HTML; it must reject event-handler attributes and non-HTTPS/dangerous URL schemes. Runtime assets and component modules are self-hosted, and the loader must not be duplicated.

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

## Native documentation media and provenance

Use real self-hosted images with descriptive `alt` text, source credit and explicit licensing; prefer the shared [Showcase media](showcase-media.md) assets over text placeholders and externally hosted stock imagery. The actual sample photographs are reproducible inputs to screenshots and visual regression tests. The GIF and MP4 examples are documented external exceptions. Never present Pro components as executable without an installed Pro runtime.

## Build and SSR boundaries

1. MyST parses Markdown, grids, cards, tabs, notes, and anywidget directives in locale-specific builds.
2. Existing staging copies `assets/static/showcase` to `static/showcase` under the assembled HTML output. Anywidget resolves local component modules from the self-hosted Web Awesome distribution.
3. The existing Lit/parse5 post-processing pass handles the four typed Web Awesome SSR primitives; keep this contract stable and do not add SSR to all 90 catalog components.
4. Translation sources stay English-first; translations and narration must be regenerated through the existing per-locale workflows without translating JSON keys or HTML attribute names.
5. Verify the generated HTML for valid MyST layouts, loaded media, tab and carousel keyboard navigation, nonempty `alt` text, expected local asset paths, and no console/network failures.

## Practical composition recipes

The [practical pattern library](practical-patterns.md) adapts the **marketing, application UI, and ecommerce categories** shown in Tailwind Plus into original MyST-first patterns. It does not copy proprietary Tailwind Plus component source and does not add a CSS framework; its examples deliberately combine real credited media, native editorial layouts, and the existing Web Awesome anywidget primitives.

:::{note} Native authoring progress
The **90 catalog integration-status notices** have been migrated to MyST `{note}`/`{warning}` and the catalog index now uses `{note}`. The existing typed Web Awesome directives/roles still exist for opt-in functional use; this content migration does not remove their implementation. Upstream-grade API tables beyond the Tab Group exemplar remain phased work.
:::

## Migration and acceptance plan

| Phase | Deliverable | Acceptance |
| --- | --- | --- |
| P0 | Add real locally bundled photos and correct anywidget media support. | Carousel, cards, comparison, avatar, scroller, tabs and zoomable gallery render actual media; media files are present and credited. |
| P1 | Replace catalog-only status boxes with MyST native notes/warnings; use native tabs, cards and grids for editorial layout. | No new custom directive API, builds remain portable. |
| P2 | Expand individual 90 component pages with version-matched API tables from the installed 3.14.0 source and examples with real behavior, dependency links, slots, events, CSS parts/properties and SSR availability. | Every API claim is checked against upstream tag; Core/Pro boundaries are explicit. |
| P3 | Add browser, accessibility, visual regression, multilingual and media-asset checks to CI. | 5 locale builds pass, media previews are stable, no missing assets or unexpected remote dependencies. |

### Not in scope
No copying proprietary Web Awesome Pro code, not turning Markdown paragraphs into custom elements, no new client framework, no fake SSR for anywidget, no dynamic download of media during deterministic build.
