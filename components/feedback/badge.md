# Badge `<wa-badge>`

Shows a small count, label, or status indicator.

> “Feedback is also a useful design principle for designing user interfaces.” — [Wikipedia: Feedback](wiki:Feedback). This quote supplies general domain context, not an API definition.

**Category:** [Feedback](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/v3.14.0/packages/webawesome/src/components/badge/badge.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/badge/).

:::{note} Integration status

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Live preview

```{anywidget} ../../widgets/webawesome-demo.mjs
{
  "tree": {
    "tag": "wa-badge",
    "attrs": {
      "variant": "success",
      "pill": ""
    },
    "children": [
      "Healthy"
    ]
  }
}
```

## Markdown code snippet

```html
<wa-badge variant="success" pill="">Healthy</wa-badge>
```

Use native MyST for documentation layout; interactive Web Awesome previews remain hosted through the existing `{anywidget}` integration when available. 
