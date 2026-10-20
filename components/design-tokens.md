---
description: Visual reference for Web Awesome colors, typography, spacing, radius, shadows, and themed components in SoftCloud.
keywords:
  - design tokens
  - style preview
  - Web Awesome
  - MyST
  - dark mode
edit_url: https://github.com/soft-cloud-dev/soft-cloud-dev/edit/main/components/design-tokens.md
source_url: https://github.com/soft-cloud-dev/soft-cloud-dev/blob/main/components/design-tokens.md
---

# Design Tokens & Style Preview

This page visualizes the **self-hosted Web Awesome 3.14.0 design tokens** used by the SoftCloud documentation theme. Every color, spacing measurement, radius, and shadow below is drawn from a CSS custom property, not a separate palette of fixed sample colors.

The visual samples are **illustrative UI**, not live infrastructure telemetry. The color and layout previews render as ordinary HTML/CSS without JavaScript; the examples of `wa-button`, `wa-card`, and `wa-callout` use the existing typed Lit SSR directives.

[Back to the Web Awesome notebook](../notebooks/webawesome-docs.ipynb) · [Component catalog](index.md) · [Official Web Awesome design tokens](https://webawesome.com/docs/tokens/)

## 1. Themed interface previews

The two samples explicitly scope `wa-light` and `wa-dark` to **individual sections**. They appear side by side regardless of the reader's currently selected site theme and do not modify the global MyST theme.

<div class="sc-token-preview-grid">
<section class="sc-token-panel wa-light" aria-label="Light theme example">
  <div class="sc-token-panel-heading"><span class="sc-token-panel-name">Light theme</span><span class="sc-token-panel-mode">Illustrative interface</span></div>
  <div class="sc-token-panel-card">
    <div class="sc-token-panel-topline"><span class="sc-token-panel-appmark" aria-hidden="true">S</span><div><strong>SoftCloud UI</strong><small>Design system preview</small></div><span class="sc-token-panel-indicator">Sample</span></div>
    <div class="sc-token-panel-split">
      <div><small>Surface hierarchy</small><strong>Readable by default</strong><span>Uses semantic background and text tokens</span></div>
      <div class="sc-token-panel-signal"><span aria-hidden="true">✓</span><strong>Success</strong><small>Semantic status</small></div>
    </div>
    <div class="sc-token-panel-actionrow"><a class="sc-token-panel-link" href="https://webawesome.com/docs/tokens/">Explore tokens</a><span>Theme: light</span></div>
  </div>
</section>
<section class="sc-token-panel wa-dark" aria-label="Dark theme example">
  <div class="sc-token-panel-heading"><span class="sc-token-panel-name">Dark theme</span><span class="sc-token-panel-mode">Illustrative interface</span></div>
  <div class="sc-token-panel-card">
    <div class="sc-token-panel-topline"><span class="sc-token-panel-appmark" aria-hidden="true">S</span><div><strong>SoftCloud UI</strong><small>Design system preview</small></div><span class="sc-token-panel-indicator">Sample</span></div>
    <div class="sc-token-panel-split">
      <div><small>Surface hierarchy</small><strong>Readable by default</strong><span>Uses semantic background and text tokens</span></div>
      <div class="sc-token-panel-signal"><span aria-hidden="true">✓</span><strong>Success</strong><small>Semantic status</small></div>
    </div>
    <div class="sc-token-panel-actionrow"><a class="sc-token-panel-link" href="https://webawesome.com/docs/tokens/">Explore tokens</a><span>Theme: dark</span></div>
  </div>
</section>
</div>

## 2. Semantic color variants

Web Awesome defines five semantic variants. The color patch uses the matched core color and its `-on` foreground token, so the swatch label is readable even when a hue is changed by the theme.

<div class="sc-token-colors" role="group" aria-label="Web Awesome semantic color samples">
  <div class="sc-token-color sc-token-brand">
    <div class="sc-token-color-paint" aria-hidden="true">Aa</div>
    <strong>Brand</strong>
    <span>Primary actions</span>
    <code>--wa-color-brand</code>
  </div>
  <div class="sc-token-color sc-token-neutral">
    <div class="sc-token-color-paint" aria-hidden="true">Aa</div>
    <strong>Neutral</strong>
    <span>Secondary UI</span>
    <code>--wa-color-neutral</code>
  </div>
  <div class="sc-token-color sc-token-success">
    <div class="sc-token-color-paint" aria-hidden="true">Aa</div>
    <strong>Success</strong>
    <span>Confirmed outcomes</span>
    <code>--wa-color-success</code>
  </div>
  <div class="sc-token-color sc-token-warning">
    <div class="sc-token-color-paint" aria-hidden="true">Aa</div>
    <strong>Warning</strong>
    <span>Caution</span>
    <code>--wa-color-warning</code>
  </div>
  <div class="sc-token-color sc-token-danger">
    <div class="sc-token-color-paint" aria-hidden="true">Aa</div>
    <strong>Danger</strong>
    <span>Errors and risk</span>
    <code>--wa-color-danger</code>
  </div>
</div>

### Brand tint ramp

The ramp below uses `--wa-color-brand-20` through `--wa-color-brand-95`. Numeric tint names identify tokens, **not** measured contrast ratios.

<div class="sc-token-ramp" role="group" aria-label="Brand color tint samples">
  <div class="sc-token-ramp-item sc-token-brand-20"><div aria-hidden="true" class="sc-token-ramp-paint"></div><code>20</code></div>
  <div class="sc-token-ramp-item sc-token-brand-40"><div aria-hidden="true" class="sc-token-ramp-paint"></div><code>40</code></div>
  <div class="sc-token-ramp-item sc-token-brand-60"><div aria-hidden="true" class="sc-token-ramp-paint"></div><code>60</code></div>
  <div class="sc-token-ramp-item sc-token-brand-80"><div aria-hidden="true" class="sc-token-ramp-paint"></div><code>80</code></div>
  <div class="sc-token-ramp-item sc-token-brand-95"><div aria-hidden="true" class="sc-token-ramp-paint"></div><code>95</code></div>
</div>

The available numeric tints are `05`, `10`, `20`, `30`, `40`, `50`, `60`, `70`, `80`, `90`, and `95`. The current palette and theme determine the rendered color.

## 3. Typography

Text samples inherit the installed Web Awesome font families, sizes, weights, and line heights. A publication's MyST typography can differ from a Web Awesome component's typography; this is a reference for the latter.

<div class="sc-token-types" aria-label="Typography scale">
  <div><span class="sc-token-type sc-token-type-3xl">Interface heading</span><code>--wa-font-size-3xl</code></div>
  <div><span class="sc-token-type sc-token-type-2xl">Section heading</span><code>--wa-font-size-2xl</code></div>
  <div><span class="sc-token-type sc-token-type-l">Supporting heading</span><code>--wa-font-size-l</code></div>
  <div><span class="sc-token-type sc-token-type-m">Body copy — Sphinx of black quartz, judge my vow.</span><code>--wa-font-size-m</code></div>
  <div><span class="sc-token-type sc-token-type-s">Secondary labels and supporting details</span><code>--wa-font-size-s</code></div>
  <div><span class="sc-token-type sc-token-type-code">kubectl get nodes -o wide</span><code>--wa-font-family-code</code></div>
</div>

## 4. Spacing

Each bar is exactly three times the named spacing token so the progression is visible; its width updates automatically if `--wa-space-scale` changes.

<div class="sc-token-spaces" aria-label="Spacing scale examples">
  <div class="sc-token-space sc-token-space-2xs"><code>--wa-space-2xs</code><span class="sc-token-space-bar" aria-hidden="true"></span></div>
  <div class="sc-token-space sc-token-space-xs"><code>--wa-space-xs</code><span class="sc-token-space-bar" aria-hidden="true"></span></div>
  <div class="sc-token-space sc-token-space-s"><code>--wa-space-s</code><span class="sc-token-space-bar" aria-hidden="true"></span></div>
  <div class="sc-token-space sc-token-space-m"><code>--wa-space-m</code><span class="sc-token-space-bar" aria-hidden="true"></span></div>
  <div class="sc-token-space sc-token-space-l"><code>--wa-space-l</code><span class="sc-token-space-bar" aria-hidden="true"></span></div>
  <div class="sc-token-space sc-token-space-xl"><code>--wa-space-xl</code><span class="sc-token-space-bar" aria-hidden="true"></span></div>
  <div class="sc-token-space sc-token-space-2xl"><code>--wa-space-2xl</code><span class="sc-token-space-bar" aria-hidden="true"></span></div>
</div>

## 5. Border radii and shadows

:::::{grid} 1 1 2 2
::::{grid-item}
### Radius

<div class="sc-token-shapes">
  <div class="sc-token-radius sc-token-radius-s"><div class="sc-token-radius-shape" aria-hidden="true"></div><strong>Small</strong><code>--wa-border-radius-s</code></div>
  <div class="sc-token-radius sc-token-radius-m"><div class="sc-token-radius-shape" aria-hidden="true"></div><strong>Medium</strong><code>--wa-border-radius-m</code></div>
  <div class="sc-token-radius sc-token-radius-l"><div class="sc-token-radius-shape" aria-hidden="true"></div><strong>Large</strong><code>--wa-border-radius-l</code></div>
  <div class="sc-token-radius sc-token-radius-pill"><div class="sc-token-radius-shape" aria-hidden="true"></div><strong>Pill</strong><code>--wa-border-radius-pill</code></div>
</div>
::::
::::{grid-item}
### Elevation

<div class="sc-token-shapes">
  <div class="sc-token-shadow sc-token-shadow-s"><div class="sc-token-shadow-shape" aria-hidden="true"></div><strong>Small</strong><code>--wa-shadow-s</code></div>
  <div class="sc-token-shadow sc-token-shadow-m"><div class="sc-token-shadow-shape" aria-hidden="true"></div><strong>Medium</strong><code>--wa-shadow-m</code></div>
  <div class="sc-token-shadow sc-token-shadow-l"><div class="sc-token-shadow-shape" aria-hidden="true"></div><strong>Large</strong><code>--wa-shadow-l</code></div>
</div>
::::
:::::

## 6. Components with real Web Awesome styling

These are the **existing typed SSR primitives**, not synthetic CSS reproductions of Web Awesome components. The explanatory content and copyable code remain available without client JavaScript.

:::::{grid} 1 1 2 2
::::{grid-item}
:::{wa-card} Token-aware surface
:appearance: outlined

Card contents inherit the active theme and use the existing `wa-card` slot and elevation rules.

[Card reference](layout/card.md)
:::
::::
::::{grid-item}
:::{wa-callout} Example confirmation
:variant: success
:appearance: filled-outlined

Illustrative success state. Status meaning is also conveyed in words, not only by color.
:::
::::
:::::

:::{wa-button}
:variant: brand
:appearance: filled
:href: https://webawesome.com/docs/tokens/
Open token reference
:::

:::{wa-button}
:variant: neutral
:appearance: outlined
:href: https://webawesome.com/docs/customizing/
Read theming guide
:::

## 7. Reusable source snippet

The following is **standalone example markup**. It uses Web Awesome's public CSS custom properties and does not depend on Shadow DOM internals, JavaScript, Tailwind, or absolute deployment paths.

~~~html
<section class="wa-light" aria-label="Example status card">
  <div class="token-example">
    <strong>Documented surface</strong>
    <p>Theme-responsive content with semantic colors.</p>
  </div>
</section>
~~~

~~~css
.token-example {
  padding: var(--wa-space-l);
  border: var(--wa-border-width-s) var(--wa-border-style) var(--wa-color-surface-border);
  border-radius: var(--wa-border-radius-l);
  box-shadow: var(--wa-shadow-s);
  background: var(--wa-color-surface-raised);
  color: var(--wa-color-text-normal);
  font: var(--wa-font-weight-body) var(--wa-font-size-m) / var(--wa-line-height-normal)
    var(--wa-font-family-body);
}
~~~

## Accessibility, rendering and source of truth

- The essential samples are static HTML and CSS; they remain readable with JavaScript disabled and in printed or exported text form.
- Never rely on color alone for state; pair each variant with a name or other visible text. Use `--wa-color-{variant}-on` for foreground text on the corresponding core fill rather than guessing a contrasting hex value.
- Theme previews use local `wa-light`/`wa-dark` scopes; they must not update the `<html>` element or write browser storage.
- The project pins the Web Awesome version in [package.json](https://github.com/soft-cloud-dev/soft-cloud-dev/blob/main/package.json). Styles are supplied through the existing self-hosted build pipeline, including prefixed locale routes.
- For canonical definitions, see Web Awesome's [colors](https://webawesome.com/docs/tokens/color/), [typography](https://webawesome.com/docs/tokens/typography/), [space](https://webawesome.com/docs/tokens/space/), [borders](https://webawesome.com/docs/tokens/borders/), and [shadows](https://webawesome.com/docs/tokens/shadows/) references.
