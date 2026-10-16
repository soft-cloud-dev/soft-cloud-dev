# Copy Button `<wa-copy-button>`

Copies a configured value to the clipboard with result feedback.

> “provides the user a simple way to trigger an event” — [Wikipedia: Button (computing)](wiki:Button_(computing)). This quote supplies general domain context, not an API definition.

**Category:** [Actions](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/next/packages/webawesome/src/components/copy-button/copy-button.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/copy-button/).

:::{wa-callout} Integration status
:variant: brand
:appearance: soft

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Live preview

```{anywidget} ../../widgets/webawesome-demo.mjs
{
  "tree": {
    "tag": "wa-copy-button",
    "attrs": {
      "value": "kubectl get nodes"
    },
    "children": []
  }
}
```

## Markdown code snippet

```html
<wa-copy-button value="kubectl get nodes"></wa-copy-button>
```

For direct MyST integration, place this trusted markup in a Markdown HTML block or use the corresponding built-in MyST directive/role when supported. 
