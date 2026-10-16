# Tag `<wa-tag>`

Displays a compact category or selection label.

> “Feedback is also a useful design principle for designing user interfaces.” — [Wikipedia: Feedback](wiki:Feedback). This quote supplies general domain context, not an API definition.

**Category:** [Feedback](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/next/packages/webawesome/src/components/tag/tag.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/tag/).

:::{wa-callout} Integration status
:variant: brand
:appearance: soft

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Live preview

```{anywidget} ../../widgets/webawesome-demo.mjs
{
  "tree": {
    "tag": "wa-tag",
    "attrs": {
      "variant": "brand"
    },
    "children": [
      "In review"
    ]
  }
}
```

## Markdown code snippet

```html
<wa-tag variant="brand">In review</wa-tag>
```

For direct MyST integration, place this trusted markup in a Markdown HTML block or use the corresponding built-in MyST directive/role when supported. 
