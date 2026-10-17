# Button `<wa-button>`

Triggers a command, submits a choice, or navigates to another page.

> “provides the user a simple way to trigger an event” — [Wikipedia: Button (computing)](wiki:Button_(computing)). This quote supplies general domain context, not an API definition.

**Category:** [Actions](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/v3.14.0/packages/webawesome/src/components/button/button.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/button/).

:::{note} Integration status

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Live preview

```{anywidget} ../../widgets/webawesome-demo.mjs
{
  "tree": {
    "tag": "wa-button",
    "attrs": {
      "variant": "brand"
    },
    "children": [
      "Run health check"
    ]
  }
}
```

## Markdown code snippet

```html
<wa-button variant="brand">Run health check</wa-button>
```

Use native MyST for documentation layout; interactive Web Awesome previews remain hosted through the existing `{anywidget}` integration when available. 
