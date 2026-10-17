# Button Group `<wa-button-group>`

Organizes multiple related button atoms into one control strip.

> “provides the user a simple way to trigger an event” — [Wikipedia: Button (computing)](wiki:Button_(computing)). This quote supplies general domain context, not an API definition.

**Category:** [Actions](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/v3.14.0/packages/webawesome/src/components/button-group/button-group.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/button-group/).

:::{wa-callout} Integration status
:variant: brand
:appearance: filled

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Atomic composition

Reuse: [Button](../actions/button.md). The full nested markup below remains independently usable.

## Live preview

```{anywidget} ../../widgets/webawesome-demo.mjs
{
  "tree": {
    "tag": "wa-button-group",
    "attrs": {
      "label": "Cluster controls"
    },
    "children": [
      {
        "tag": "wa-button",
        "attrs": {
          "variant": "brand"
        },
        "children": [
          "Start"
        ]
      },
      {
        "tag": "wa-button",
        "attrs": {
          "appearance": "outlined"
        },
        "children": [
          "Pause"
        ]
      },
      {
        "tag": "wa-button",
        "attrs": {
          "variant": "danger"
        },
        "children": [
          "Stop"
        ]
      }
    ]
  }
}
```

## Markdown code snippet

```html
<wa-button-group label="Cluster controls">
  <wa-button variant="brand">Start</wa-button>
  <wa-button appearance="outlined">Pause</wa-button>
  <wa-button variant="danger">Stop</wa-button>
</wa-button-group>
```

For direct MyST integration, place this trusted markup in a Markdown HTML block or use the corresponding built-in MyST directive/role when supported. 
