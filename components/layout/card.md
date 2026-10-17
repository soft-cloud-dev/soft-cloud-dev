# Card `<wa-card>`

Groups media, metadata, and actions into one surface.

> “the space where interactions between humans and machines occur” — [Wikipedia: User interface](wiki:User_interface). This quote supplies general domain context, not an API definition.

**Category:** [Layout](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/v3.14.0/packages/webawesome/src/components/card/card.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/card/).

:::{wa-callout} Integration status
:variant: brand
:appearance: filled

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Live preview

```{anywidget} ../../widgets/webawesome-demo.mjs
{
  "tree": {
    "tag": "wa-card",
    "attrs": {
      "appearance": "outlined"
    },
    "children": [
      {
        "tag": "strong",
        "attrs": {
          "slot": "header"
        },
        "children": [
          "Service status"
        ]
      },
      {
        "tag": "p",
        "attrs": {},
        "children": [
          "All probes healthy."
        ]
      },
      {
        "tag": "wa-button",
        "attrs": {},
        "children": [
          "View details"
        ]
      }
    ]
  }
}
```

## Markdown code snippet

```html
<wa-card appearance="outlined">
  <strong slot="header">Service status</strong>
  <p>All probes healthy.</p>
  <wa-button>View details</wa-button>
</wa-card>
```

For direct MyST integration, place this trusted markup in a Markdown HTML block or use the corresponding built-in MyST directive/role when supported. 
