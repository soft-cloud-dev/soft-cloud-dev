# Split Panel `<wa-split-panel>`

Separates two resizable adjacent regions.

> “the space where interactions between humans and machines occur” — [Wikipedia: User interface](wiki:User_interface). This quote supplies general domain context, not an API definition.

**Category:** [Layout](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/v3.14.0/packages/webawesome/src/components/split-panel/split-panel.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/split-panel/).

:::{note} Integration status

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Live preview

```{anywidget} ../../widgets/webawesome-demo.mjs
{
  "tree": {
    "tag": "wa-split-panel",
    "attrs": {
      "position": "40"
    },
    "children": [
      {
        "tag": "div",
        "attrs": {
          "slot": "start"
        },
        "children": [
          "Configuration"
        ]
      },
      {
        "tag": "div",
        "attrs": {
          "slot": "end"
        },
        "children": [
          "Telemetry"
        ]
      }
    ]
  }
}
```

## Markdown code snippet

```html
<wa-split-panel position="40">
  <div slot="start">Configuration</div>
  <div slot="end">Telemetry</div>
</wa-split-panel>
```

Use native MyST for documentation layout; interactive Web Awesome previews remain hosted through the existing `{anywidget}` integration when available. 
