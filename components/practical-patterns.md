# Practical UI Patterns: MyST + Web Awesome

This is a pattern library for building publication pages and interactive examples. It draws on the **categories** in [Tailwind Plus UI Blocks](https://tailwindcss.com/plus/ui-blocks) (marketing sections, application UI, and e-commerce patterns), **not** on proprietary Tailwind Plus markup or code. The components below are original SoftCloud examples; they run on the existing MyST / Web Awesome stack **without introducing a Tailwind dependency**.

:::{note} Rendering contract
Use MyST `{grid}`, `{card}`, `{tab-set}`, `{tab-item}`, and `{note}` for publication structure. Use self-hosted Web Awesome in the existing `{anywidget}` integration only where application-like interaction is required. The four typed Web Awesome directives/roles remain supported for their separately tested Lit SSR/Declarative Shadow DOM use cases.
:::

## 1. Marketing hero and feature story

A landing page needs a strong hierarchy, real imagery, a descriptive call to action, and responsive layout; it does **not** need a JavaScript component to position content. Use a native MyST grid and a normal link.

::::{grid} 1 1 2 2
:::{grid-item}
### Publish reproducible infrastructure research

Document architecture, publish computational evidence, and maintain multilingual reference material in a deterministic build.

[Explore the component catalog](index.md) · [Review the publishing platform](../README.md)

:::
:::{grid-item}
:::{card} Research in context

![Falcon 9 carrying the DSCOVR spacecraft into flight](../assets/static/showcase/rocket.jpg)

**Credit:** SpaceX / DSCOVR launch photograph (distributed through scikit-image). **License:** public-domain designation recorded in the [media manifest](../assets/static/showcase/README.md); original rights confirmation remains pending.
:::
::::

**Why MyST:** portable reading order, working Markdown links, normal image fallback, and responsive columns without custom components. A Web Awesome `<wa-carousel>` is appropriate only if multiple slides and navigation are actually necessary.

## 2. Bento-like capability grid

Tailwind Plus catalogs bento grids, feature sections, and statistics layouts. A MyST grid with cards expresses the same information architecture while remaining suitable for other MyST outputs.

::::{grid} 1 1 2 3
:::{card} Reproducibility

Lock dependencies, verify build inputs, and preserve source provenance.

[Architecture reference](../architecture.md)
:::
:::{card} Interactive controls

Use Web Awesome `wa-button`, `wa-dialog`, `wa-copy-button`, and form controls through the self-hosted widget integration.

[Button](actions/button.md) · [Copy Button](actions/copy-button.md)
:::
:::{card} Actual media

Images, comparisons, and carousels use real, credited media. Ordinary figures remain native MyST.

[Real-media gallery](showcase-media.md)
:::
::::

**Do not** use utility classes as a substitute for semantic elements or use decorative badges for data that should be text. A dense application bento may add project-scoped CSS once the native layout becomes insufficient.

## 3. Application UI: an actionable operations tile

A dashboard can combine a native explanatory card with a Web Awesome action, without converting the entire documentation page to web components.

:::{card} Diagnostics reference
This example is a demonstration, **not a live infrastructure status**. The button copies a reproducible diagnostic command.
:::

```{anywidget} ../widgets/webawesome-demo.mjs
{
  "tree": [
    {
      "tag": "wa-button",
      "attrs": {
        "variant": "brand",
        "appearance": "filled",
        "href": "https://my.softcloud.dev/"
      },
      "children": ["Open SoftCloud"]
    },
    {
      "tag": "wa-copy-button",
      "attrs": {
        "value": "kubectl get nodes -o wide",
        "copy-label": "Copy diagnostic command",
        "label": "Copy kubectl command"
      },
      "children": []
    }
  ]
}
```

**Atomic reuse:** [`wa-button`](actions/button.md) provides navigation; [`wa-copy-button`](actions/copy-button.md) handles clipboard interaction. The MyST `{card}` above provides the document context. Never register a second button, card, or copy-button implementation for the same need.

## 4. Documentation tabs versus application tabs

Use native MyST tabs for alternative explanations and code listings.

::::{tab-set}
:::{tab-item} Shell
```sh
kubectl get nodes -o wide
```
:::
:::{tab-item} API
```http
GET /api/v1/nodes
```
:::
::::

Use a Web Awesome `<wa-tab-group>` for application state, custom tab placement, dynamic panel selection, or event-driven interaction. The [Tab Group](navigation/tab-group.md), [Tab](navigation/tab.md), and [Tab Panel](navigation/tab-panel.md) pages demonstrate that interaction with **actual photographs**. Do not restyle MyST documentation tabs as Web Awesome just because the visual treatment is similar.

## 5. Photo cards, galleries, and comparison views

Media is part of a realistic component recipe, not a text-only placeholder.

::::{grid} 1 1 2 2
:::{card} Space exploration

![Hubble eXtreme Deep Field showing distant galaxies](../assets/static/showcase/hubble-deep-field.jpg)

**Credit:** NASA / Hubble eXtreme Deep Field. **License:** public domain ([media manifest](../assets/static/showcase/README.md)). Use native MyST cards and images for editorial content.
:::
:::{card} Coffee and texture

![White porcelain coffee cup photographed on a wooden table](../assets/static/showcase/coffee.png)

**Credit:** Rachel Michetti / Pikolo Espresso Bar. **License:** CC0 ([media manifest](../assets/static/showcase/README.md)). Use image captions and alternate text even in promotional layouts.
:::
::::

For interaction, use [Carousel](media/carousel.md) for controlled slides, [Comparison](media/comparison.md) for a draggable synchronized split, [Zoomable Frame](media/zoomable-frame.md) for a bounded page preview, and [Animated Image](media/animated-image.md) for motion playback controls. These are **not** MyST card replacements.

## 6. Tailwind utility classes as an optional supplement

An application that already compiles Tailwind may use its **utility vocabulary** for responsive spacing, widths, and alignment, while leaving behavior to Web Awesome. This snippet is a conceptual frontend integration example, **not executed by this Jupyter Book site**:

```html
<section class="mx-auto grid max-w-6xl grid-cols-1 gap-6 p-6 lg:grid-cols-3">
  <article class="rounded-xl border p-6">
    <h2 class="text-xl font-semibold">Reproducible builds</h2>
    <p>Validate configuration before publishing.</p>
    <wa-button variant="brand" href="/architecture">Architecture</wa-button>
  </article>
</section>
```

**Do not add a Tailwind runtime solely for these examples.** Without a separately built Tailwind stylesheet, utility classes in that block have no styling effect. Where the output must remain portable to PDF, print, JATS, or non-HTML MyST renderers, prefer MyST's native structural directives. When custom CSS is necessary, use scoped classes and Web Awesome design tokens rather than relying on undocumented internal Shadow DOM.

## Component selection matrix

| Tailwind-style pattern | MyST-first implementation | Add Web Awesome when |
| --- | --- | --- |
| Hero, features, bento, logo cloud, statistics | Headings, grid, cards, images | An action, carousel, or dynamic display is required |
| FAQ, notice, release notes | Admonition, heading, list, native tabs | Details need stateful disclosure or application-specific behavior |
| Pricing or feature comparison | Tables, grids, cards | User-selectable configuration affects the content |
| Application dashboard | Grid, tables, figures, cards | Filters, tabs, sorting, dialogs, copy actions, or forms are required |
| Gallery / media story | Images, figures, captions, grid | Controlled carousel, comparison slider, or pan/zoom behavior is required |
| Forms / application shell | Narrative structure in MyST | Actual controls, validation, and events must execute in the browser |

## Accessibility and verification

Every recipe must remain understandable with JavaScript unavailable (static text and images survive); use real, provenance-recorded media; give interactive controls discernible labels; preserve keyboard focus and logical reading order; test responsive widths and reduced-motion behavior where relevant; and validate local asset URLs under both root and prefixed deployments. The Web Awesome `{anywidget}` previews hydrate on the client; they are **not** automatically Lit SSR output.

Further reading: [Authoring standard](authoring-guide.md), [Migration plan](authoring-guide.md#migration-and-acceptance-plan), [Real-media sources](showcase-media.md), [Tailwind Plus categories](https://tailwindcss.com/plus/ui-blocks), and [MyST grid/card/tab syntax](https://mystmd.org/guide/dropdowns-cards-and-tabs).
