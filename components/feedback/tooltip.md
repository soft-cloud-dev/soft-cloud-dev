# Tooltip `<wa-tooltip>`

Explains an action through brief contextual text.

> “Feedback is also a useful design principle for designing user interfaces.” — [Wikipedia: Feedback](wiki:Feedback). This quote supplies general domain context, not an API definition.

**Category:** [Feedback](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/v3.14.0/packages/webawesome/src/components/tooltip/tooltip.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/tooltip/).

:::{note} Integration status

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Atomic composition

Reuse: [Button](../actions/button.md). The full nested markup below remains independently usable.

## Live preview

```{anywidget} ../../widgets/webawesome-demo.mjs
{
  "tree": [
    {
      "tag": "wa-button",
      "attrs": {
        "id": "node-tooltip-trigger"
      },
      "children": [
        "Hover for help"
      ]
    },
    {
      "tag": "wa-tooltip",
      "attrs": {
        "for": "node-tooltip-trigger"
      },
      "children": [
        "Node health"
      ]
    }
  ]
}
```

## Markdown code snippet

```html
<wa-button id="node-tooltip-trigger">Hover for help</wa-button>

<wa-tooltip for="node-tooltip-trigger">Node health</wa-tooltip>
```

Use native MyST for documentation layout; interactive Web Awesome previews remain hosted through the existing `{anywidget}` integration when available. 
