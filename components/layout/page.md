# Page `<wa-page>`

Arranges header, navigation, main, and footer slots.

> “the space where interactions between humans and machines occur” — [Wikipedia: User interface](wiki:User_interface). This quote supplies general domain context, not an API definition.

**Category:** [Layout](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/next/packages/webawesome/src/components/page/page.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/page/).

:::{wa-callout} Integration status
:variant: brand
:appearance: filled

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Live preview

Live preview intentionally unavailable: this control requires external media, changes the entire page, or has only background behavior.

## Markdown code snippet

```html
<wa-page>
  <div slot="header">Header</div>
  <div slot="navigation">Navigation</div>
  <div slot="main">Content</div>
  <div slot="footer">Footer</div>
</wa-page>
```

For direct MyST integration, place this trusted markup in a Markdown HTML block or use the corresponding built-in MyST directive/role when supported. 
