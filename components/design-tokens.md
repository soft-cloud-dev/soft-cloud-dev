---
description: >-
  Live reference for Web Awesome design tokens in SoftCloud: colors, type, space, borders, shadows, focus, motion, and component groups.
keywords:
  - Web Awesome
  - design tokens
  - CSS custom properties
  - accessibility
  - MyST
---

# Design Tokens

Design tokens are Web Awesome's theme-aware CSS custom properties. They control the visual language shared by components and ordinary HTML: **color, typography, space, borders, shadows, focus, transitions, and component groups**. This page illustrates the eight families from Web Awesome **3.14.0**, the version pinned by SoftCloud, using the existing site stylesheet and MyST documentation primitives.

**Source:** [Web Awesome design token index](https://webawesome.com/docs/tokens/) · [Theming documentation](https://webawesome.com/docs/theming/) · [Component catalog](index.md).

:::{note} How to read the previews
The samples resolve actual `--wa-*` variables from the active Web Awesome theme; they do not hard-code token values. Switch the site's light/dark theme to compare. Static token names, native controls, and the source snippets remain readable with JavaScript disabled. Web Awesome form previews use the existing anywidget integration only for interactive behavior.
:::

::::{grid} 1 1 2 4
:::{card} [Color](#color)
Palettes, variants, themed surfaces, and foregrounds.
:::
:::{card} [Typography](#typography)
Font families, type scale, weights, and line height.
:::
:::{card} [Space](#space)
Consistent spacing from 3xs to 5xl.
:::
:::{card} [Borders](#borders)
Border strokes, radii, and shape.
:::
:::{card} [Shadows](#shadows)
Elevation, offsets, blur, and spread.
:::
:::{card} [Focus](#focus)
Keyboard focus outlines and offset.
:::
:::{card} [Transitions](#transitions)
Durations, easing, and reduced-motion support.
:::
:::{card} [Component Groups](#component-groups)
Shared form, button, panel, and tooltip styling.
:::
::::

## Color

Web Awesome separates its 10-hue palette, five semantic variants, and role-based surface/content colors. Each hue has 11 tints: `95`, `90`, `80`, `70`, `60`, `50`, `40`, `30`, `20`, `10`, `05`. For text on core fills, always pair a core token with its matching `-on` token rather than assuming black or white.

### Core palette colors

<div class="sc-tokens__swatches" role="group" aria-label="Web Awesome core color hues">
<figure class="sc-tokens__swatch sc-tokens__swatch--red"><div class="sc-tokens__patch" aria-hidden="true">Aa</div><figcaption>Red<code>--wa-color-red</code></figcaption></figure>
<figure class="sc-tokens__swatch sc-tokens__swatch--orange"><div class="sc-tokens__patch" aria-hidden="true">Aa</div><figcaption>Orange<code>--wa-color-orange</code></figcaption></figure>
<figure class="sc-tokens__swatch sc-tokens__swatch--yellow"><div class="sc-tokens__patch" aria-hidden="true">Aa</div><figcaption>Yellow<code>--wa-color-yellow</code></figcaption></figure>
<figure class="sc-tokens__swatch sc-tokens__swatch--green"><div class="sc-tokens__patch" aria-hidden="true">Aa</div><figcaption>Green<code>--wa-color-green</code></figcaption></figure>
<figure class="sc-tokens__swatch sc-tokens__swatch--cyan"><div class="sc-tokens__patch" aria-hidden="true">Aa</div><figcaption>Cyan<code>--wa-color-cyan</code></figcaption></figure>
<figure class="sc-tokens__swatch sc-tokens__swatch--blue"><div class="sc-tokens__patch" aria-hidden="true">Aa</div><figcaption>Blue<code>--wa-color-blue</code></figcaption></figure>
<figure class="sc-tokens__swatch sc-tokens__swatch--indigo"><div class="sc-tokens__patch" aria-hidden="true">Aa</div><figcaption>Indigo<code>--wa-color-indigo</code></figcaption></figure>
<figure class="sc-tokens__swatch sc-tokens__swatch--purple"><div class="sc-tokens__patch" aria-hidden="true">Aa</div><figcaption>Purple<code>--wa-color-purple</code></figcaption></figure>
<figure class="sc-tokens__swatch sc-tokens__swatch--pink"><div class="sc-tokens__patch" aria-hidden="true">Aa</div><figcaption>Pink<code>--wa-color-pink</code></figcaption></figure>
<figure class="sc-tokens__swatch sc-tokens__swatch--gray"><div class="sc-tokens__patch" aria-hidden="true">Aa</div><figcaption>Gray<code>--wa-color-gray</code></figcaption></figure>
</div>

### Semantic variants

<div class="sc-tokens__swatches" role="group" aria-label="Web Awesome semantic colors">
<figure class="sc-tokens__swatch sc-tokens__swatch--brand"><div class="sc-tokens__patch" aria-hidden="true">Aa</div><figcaption>Brand<code>--wa-color-brand</code></figcaption></figure>
<figure class="sc-tokens__swatch sc-tokens__swatch--neutral"><div class="sc-tokens__patch" aria-hidden="true">Aa</div><figcaption>Neutral<code>--wa-color-neutral</code></figcaption></figure>
<figure class="sc-tokens__swatch sc-tokens__swatch--success"><div class="sc-tokens__patch" aria-hidden="true">Aa</div><figcaption>Success<code>--wa-color-success</code></figcaption></figure>
<figure class="sc-tokens__swatch sc-tokens__swatch--warning"><div class="sc-tokens__patch" aria-hidden="true">Aa</div><figcaption>Warning<code>--wa-color-warning</code></figcaption></figure>
<figure class="sc-tokens__swatch sc-tokens__swatch--danger"><div class="sc-tokens__patch" aria-hidden="true">Aa</div><figcaption>Danger<code>--wa-color-danger</code></figcaption></figure>
</div>

### Color token reference

| Token or pattern | Purpose |
| --- | --- |
| `--wa-color-{hue}-{tint}` | 10 hues × 11 tints, `95` (lightest) through `05` (darkest). |
| `--wa-color-{hue}` / `--wa-color-{hue}-on` | Core hue and its readable foreground. |
| `--wa-color-{variant}-{tint}` | Semantic palettes: brand, neutral, success, warning, danger. |
| `--wa-color-{variant}` / `--wa-color-{variant}-on` | Core variant and its paired foreground. |
| `--wa-color-{variant}-{fill|border|on}-{quiet|normal|loud}` | Semantic component roles and attention levels. |
| `--wa-color-surface-raised` / `--wa-color-surface-default` / `--wa-color-surface-lowered` | Surface elevation levels. |
| `--wa-color-surface-border` | Surface boundaries. |
| `--wa-color-text-normal` / `--wa-color-text-quiet` / `--wa-color-text-link` | Text hierarchy and links. |
| `--wa-color-overlay-modal` / `--wa-color-overlay-inline` | Backdrops and inline overlays. |
| `--wa-color-shadow` / `--wa-color-focus` | Shadow tint and focus-ring color. |
| `--wa-color-mix-hover` / `--wa-color-mix-active` | Hover/pressed color mixtures. |

The `wa-brand-{hue}` and related `wa-{variant}-{hue}` classes on the document root select a palette hue for a semantic variant. Accessible contrast depends on the resolved pair, not merely the hue name.

```css
.status-success {
  background: var(--wa-color-success-fill-normal);
  color: var(--wa-color-success-on-normal);
  border: var(--wa-border-width-s) var(--wa-border-style)
    var(--wa-color-success-border-normal);
}
```

**Upstream:** [Color token reference](https://webawesome.com/docs/tokens/color/).

## Typography

Typography tokens cover role-specific font families, a responsive-friendly size scale, line heights, weights, and link decoration. Font-size tokens are based on `rem` and scale through `--wa-font-size-scale`; component previews therefore reflect the current theme rather than a fixed pixel chart.

<div class="sc-tokens__type-samples" role="group" aria-label="Theme font-family examples">
  <p class="sc-tokens__font sc-tokens__font--body"><strong>Body</strong> — Sphinx of black quartz, judge my vow.</p>
  <p class="sc-tokens__font sc-tokens__font--heading"><strong>Heading</strong> — Sphinx of black quartz, judge my vow.</p>
  <p class="sc-tokens__font sc-tokens__font--code"><strong>Code</strong> — Sphinx of black quartz, judge my vow.</p>
  <p class="sc-tokens__font sc-tokens__font--longform"><strong>Longform</strong> — Sphinx of black quartz, judge my vow.</p>
</div>

| Group | Available properties |
| --- | --- |
| Font family | `--wa-font-family-body`, `--wa-font-family-heading`, `--wa-font-family-code`, `--wa-font-family-longform` |
| Font size | `--wa-font-size-scale`, `--wa-font-size-3xs`, `--wa-font-size-2xs`, `--wa-font-size-xs`, `--wa-font-size-s`, `--wa-font-size-m`, `--wa-font-size-l`, `--wa-font-size-xl`, `--wa-font-size-2xl`, `--wa-font-size-3xl`, `--wa-font-size-4xl`, `--wa-font-size-5xl`, `--wa-font-size-smaller`, `--wa-font-size-larger` |
| Font weight | `--wa-font-weight-light`, `--wa-font-weight-normal`, `--wa-font-weight-semibold`, `--wa-font-weight-bold`, `--wa-font-weight-body`, `--wa-font-weight-heading`, `--wa-font-weight-code`, `--wa-font-weight-longform`, `--wa-font-weight-action` |
| Line height | `--wa-line-height-condensed`, `--wa-line-height-normal`, `--wa-line-height-expanded` |
| Link decoration | `--wa-link-decoration-default`, `--wa-link-decoration-hover` |

For long-form text, choose an appropriate font family and `--wa-line-height-normal` (or `expanded`); do not reduce paragraph leading just to fit a sample.

```css
.documentation-lead {
  font-family: var(--wa-font-family-longform);
  font-size: var(--wa-font-size-l);
  line-height: var(--wa-line-height-expanded);
  color: var(--wa-color-text-normal);
}
```

**Upstream:** [Typography token reference](https://webawesome.com/docs/tokens/typography/).

## Space

The space scale uses `rem` units and the multiplier `--wa-space-scale`. Bars below take their lengths from the active tokens; the smallest tokens may render as narrow marks on dense displays.

<div class="sc-tokens__space-scale" role="group" aria-label="Resolved Web Awesome space scale">
<div class="sc-tokens__space-row"><code>--wa-space-3xs</code><span class="sc-tokens__space-track" aria-hidden="true"><span class="sc-tokens__space-bar sc-tokens__space-bar--3xs"></span></span></div>
<div class="sc-tokens__space-row"><code>--wa-space-2xs</code><span class="sc-tokens__space-track" aria-hidden="true"><span class="sc-tokens__space-bar sc-tokens__space-bar--2xs"></span></span></div>
<div class="sc-tokens__space-row"><code>--wa-space-xs</code><span class="sc-tokens__space-track" aria-hidden="true"><span class="sc-tokens__space-bar sc-tokens__space-bar--xs"></span></span></div>
<div class="sc-tokens__space-row"><code>--wa-space-s</code><span class="sc-tokens__space-track" aria-hidden="true"><span class="sc-tokens__space-bar sc-tokens__space-bar--s"></span></span></div>
<div class="sc-tokens__space-row"><code>--wa-space-m</code><span class="sc-tokens__space-track" aria-hidden="true"><span class="sc-tokens__space-bar sc-tokens__space-bar--m"></span></span></div>
<div class="sc-tokens__space-row"><code>--wa-space-l</code><span class="sc-tokens__space-track" aria-hidden="true"><span class="sc-tokens__space-bar sc-tokens__space-bar--l"></span></span></div>
<div class="sc-tokens__space-row"><code>--wa-space-xl</code><span class="sc-tokens__space-track" aria-hidden="true"><span class="sc-tokens__space-bar sc-tokens__space-bar--xl"></span></span></div>
<div class="sc-tokens__space-row"><code>--wa-space-2xl</code><span class="sc-tokens__space-track" aria-hidden="true"><span class="sc-tokens__space-bar sc-tokens__space-bar--2xl"></span></span></div>
<div class="sc-tokens__space-row"><code>--wa-space-3xl</code><span class="sc-tokens__space-track" aria-hidden="true"><span class="sc-tokens__space-bar sc-tokens__space-bar--3xl"></span></span></div>
<div class="sc-tokens__space-row"><code>--wa-space-4xl</code><span class="sc-tokens__space-track" aria-hidden="true"><span class="sc-tokens__space-bar sc-tokens__space-bar--4xl"></span></span></div>
<div class="sc-tokens__space-row"><code>--wa-space-5xl</code><span class="sc-tokens__space-track" aria-hidden="true"><span class="sc-tokens__space-bar sc-tokens__space-bar--5xl"></span></span></div>
</div>

`--wa-content-spacing` is the semantic default spacing between top-level content blocks. Prefer semantic layout relationships instead of applying a single arbitrary gap everywhere.

```css
.card-stack {
  display: grid;
  gap: var(--wa-space-l);
  padding: var(--wa-space-m);
}
```

**Upstream:** [Space token reference](https://webawesome.com/docs/tokens/space/).

## Borders

Borders use scale-controlled stroke widths and radii, plus fixed shape aliases for pills, circles, and squares. These examples use the token values directly.

<div class="sc-tokens__samples" role="group" aria-label="Border size examples">
  <div class="sc-tokens__edge sc-tokens__edge--s">Small</div>
  <div class="sc-tokens__edge sc-tokens__edge--m">Medium</div>
  <div class="sc-tokens__edge sc-tokens__edge--l">Large</div>
  <div class="sc-tokens__edge sc-tokens__edge--pill">Pill</div>
</div>

| Token | Purpose |
| --- | --- |
| `--wa-border-style` | Default border line style. |
| `--wa-border-width-scale` | Global border thickness multiplier. |
| `--wa-border-width-s` / `--wa-border-width-m` / `--wa-border-width-l` | Small, medium, and large stroke widths. |
| `--wa-border-radius-scale` | Global corner rounding multiplier. |
| `--wa-border-radius-s` / `--wa-border-radius-m` / `--wa-border-radius-l` | Size-based corner rounding. |
| `--wa-border-radius-pill` / `--wa-border-radius-circle` / `--wa-border-radius-square` | Fixed shape tokens; circle requires square dimensions. |

`--wa-border-width-scale` and `--wa-border-radius-scale` can adjust component appearance globally. Shape tokens (such as `pill`) are not scaled like size-based radii.

**Upstream:** [Borders token reference](https://webawesome.com/docs/tokens/borders/).

## Shadows

Three ready-to-use shadows are composed from smaller offset, blur, and spread variables plus `--wa-color-shadow`. Use shadow tokens for elevation; do not invent a separate page-specific shadow scale.

<div class="sc-tokens__samples" role="group" aria-label="Shadow size examples">
  <div class="sc-tokens__shadow sc-tokens__shadow--s">Small</div>
  <div class="sc-tokens__shadow sc-tokens__shadow--m">Medium</div>
  <div class="sc-tokens__shadow sc-tokens__shadow--l">Large</div>
</div>

| Token | Purpose |
| --- | --- |
| `--wa-shadow-s` / `--wa-shadow-m` / `--wa-shadow-l` | Ready-to-use small, medium, large shadows. |
| `--wa-shadow-offset-x-scale` / `--wa-shadow-offset-x-{s|m|l}` | Horizontal-offset multiplier and three size tokens. |
| `--wa-shadow-offset-y-scale` / `--wa-shadow-offset-y-{s|m|l}` | Vertical-offset multiplier and three size tokens. |
| `--wa-shadow-blur-scale` / `--wa-shadow-blur-{s|m|l}` | Blur multiplier and three size tokens. |
| `--wa-shadow-spread-scale` / `--wa-shadow-spread-{s|m|l}` | Spread multiplier and three size tokens. |
| `--wa-color-shadow` | Shared shadow color. |

The shadow shorthand can be inset: `box-shadow: inset var(--wa-shadow-s);`. Larger effects may be less appropriate in dense documentation layouts.

**Upstream:** [Shadows token reference](https://webawesome.com/docs/tokens/shadows/).

## Focus

Keyboard focus must remain visible in both light and dark themes. Web Awesome composes its focus-ring style, width, and `--wa-color-focus` into a reusable shorthand. Use `Tab` to focus the native controls below; this preview works without JavaScript.

<div class="sc-tokens__focus-example">
  <label for="sc-tokens-name">Example label</label>
  <input id="sc-tokens-name" name="token-example" type="text" placeholder="Tab to focus this field">
  <button type="button">Focusable button</button>
</div>

| Token | Purpose |
| --- | --- |
| `--wa-focus-ring-style` | Outline line style. |
| `--wa-focus-ring-width` | Outline stroke width. |
| `--wa-focus-ring` | Complete outline shorthand. |
| `--wa-focus-ring-offset` | Gap between control and ring. |
| `--wa-color-focus` | Theme-specific focus-ring color. |

```css
.custom-control:focus-visible {
  outline: var(--wa-focus-ring);
  outline-offset: var(--wa-focus-ring-offset);
}
```

Do not remove a focus outline without providing an equivalent high-contrast alternative.

**Upstream:** [Focus token reference](https://webawesome.com/docs/tokens/focus/).

## Transitions

Transition duration tokens are `--wa-transition-fast`, `--wa-transition-normal`, and `--wa-transition-slow`. `--wa-transition-easing` specifies the shared timing function. Hover **or keyboard-focus** each button to compare its response; when reduced motion is requested, the animation is disabled.

<div class="sc-tokens__motion-samples" role="group" aria-label="Transition duration examples">
  <button type="button" class="sc-tokens__motion sc-tokens__motion--fast">Fast <span aria-hidden="true"></span></button>
  <button type="button" class="sc-tokens__motion sc-tokens__motion--normal">Normal <span aria-hidden="true"></span></button>
  <button type="button" class="sc-tokens__motion sc-tokens__motion--slow">Slow <span aria-hidden="true"></span></button>
</div>

```css
.interactive-surface {
  transition: background-color var(--wa-transition-normal)
    var(--wa-transition-easing);
}
@media (prefers-reduced-motion: reduce) {
  .interactive-surface { transition: none; }
}
```

**Upstream:** [Transitions token reference](https://webawesome.com/docs/tokens/transitions/).

## Component Groups

Group-level variables share visual decisions across related components. Unlike individual `wa-*` component-specific CSS properties, these act on a family of controls without duplicating overrides. Not every form control consumes every form-control token.

| Group | Properties |
| --- | --- |
| Form controls (surface) | `--wa-form-control-background-color`, `--wa-form-control-border-color`, `--wa-form-control-border-style`, `--wa-form-control-border-width`, `--wa-form-control-border-radius`, `--wa-form-control-activated-color` |
| Form controls (text) | `--wa-form-control-label-color`, `--wa-form-control-label-font-weight`, `--wa-form-control-label-line-height`, `--wa-form-control-value-color`, `--wa-form-control-value-font-weight`, `--wa-form-control-value-line-height`, `--wa-form-control-hint-color`, `--wa-form-control-hint-font-weight`, `--wa-form-control-hint-line-height`, `--wa-form-control-placeholder-color` |
| Form controls (required & sizing) | `--wa-form-control-required-content`, `--wa-form-control-required-content-color`, `--wa-form-control-required-content-offset`, `--wa-form-control-padding-block`, `--wa-form-control-padding-inline`, `--wa-form-control-height`, `--wa-form-control-toggle-size` |
| Buttons | `--wa-button-transform-hover`, `--wa-button-transform-active` |
| Panels | `--wa-panel-border-style`, `--wa-panel-border-width`, `--wa-panel-border-radius` |
| Tooltips | `--wa-tooltip-arrow-size`, `--wa-tooltip-background-color`, `--wa-tooltip-border-color`, `--wa-tooltip-border-style`, `--wa-tooltip-border-width`, `--wa-tooltip-border-radius`, `--wa-tooltip-content-color`, `--wa-tooltip-font-size`, `--wa-tooltip-line-height` |

### SSR panel and button atoms

These use SoftCloud's existing typed `{wa-card}`, `{wa-callout}`, and `{wa-button}` MyST directives (real Lit SSR/Declarative Shadow DOM), not a second component renderer:

:::{wa-card} Panel example
:appearance: outlined
This card inherits shared panel border and radius tokens.
:::

:::{wa-callout} Theme-aware callout
:variant: brand
:appearance: outlined
The callout shares panel styling with the card.
:::

:::{wa-button}
:variant: brand
:appearance: filled
Token-aware action
:::

### Interactive form controls

The native fieldset is the no-JavaScript reference; the Web Awesome preview beneath it enhances the example when its self-hosted modules load.

<fieldset class="sc-tokens__native-form">
  <legend>Native form reference</legend>
  <label for="sc-tokens-email">Email</label>
  <input id="sc-tokens-email" type="email" placeholder="person@example.org">
  <label><input type="checkbox"> Receive updates</label>
</fieldset>

```{anywidget} ../widgets/webawesome-demo.mjs
{
  "tree": [
    {"tag": "wa-input", "attrs": {"label": "Email", "type": "email", "placeholder": "person@example.org"}},
    {"tag": "wa-select", "attrs": {"label": "Environment", "value": "production"}, "children": [
      {"tag": "wa-option", "attrs": {"value": "development"}, "children": ["Development"]},
      {"tag": "wa-option", "attrs": {"value": "production"}, "children": ["Production"]}
    ]},
    {"tag": "wa-checkbox", "children": ["Receive updates"]},
    {"tag": "wa-button", "attrs": {"variant": "brand"}, "children": ["Submit"]}
  ]
}
```

Copyable HTML using the same existing atomic components:

```html
<wa-input label="Email" type="email" placeholder="person@example.org"></wa-input>
<wa-select label="Environment" value="production">
  <wa-option value="development">Development</wa-option>
  <wa-option value="production">Production</wa-option>
</wa-select>
<wa-checkbox>Receive updates</wa-checkbox>
<wa-button variant="brand">Submit</wa-button>
```

Related catalog pages: [Input](forms/input.md), [Select](forms/select.md), [Checkbox](forms/checkbox.md), [Button](actions/button.md), [Card](layout/card.md), and [Callout](feedback/callout.md).

**Upstream:** [Component group tokens](https://webawesome.com/docs/tokens/component-groups/).

## Putting tokens together

A single portable CSS rule can use several families without redefining their values:

```css
.feature-panel {
  background: var(--wa-color-surface-raised);
  color: var(--wa-color-text-normal);
  border: var(--wa-border-width-s) var(--wa-border-style)
    var(--wa-color-surface-border);
  border-radius: var(--wa-border-radius-l);
  box-shadow: var(--wa-shadow-s);
  padding: var(--wa-space-l);
  font-family: var(--wa-font-family-body);
  line-height: var(--wa-line-height-normal);
  transition: box-shadow var(--wa-transition-normal)
    var(--wa-transition-easing);
}
@media (prefers-reduced-motion: reduce) {
  .feature-panel { transition: none; }
}
```

MyST `{grid}`, `{card}`, and standard Markdown remain the default for documentation structure. Reuse typed SSR directives for the four integrated Web Awesome primitives; use the existing `{anywidget}` when genuine interaction is required. Every preview must retain readable content when scripts are unavailable.

Token names and intent were checked against the [official Web Awesome 3.x reference](https://webawesome.com/docs/tokens/). Exact computed values are theme-dependent; use browser developer tools to inspect your chosen theme instead of copying a screenshot's numeric colors.
