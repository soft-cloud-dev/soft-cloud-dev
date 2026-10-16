# Split Panel `<wa-split-panel>`

Separates two resizable adjacent regions.

> “the space where interactions between humans and machines occur” — [Wikipedia: User interface](wiki:User_interface). This quote supplies general domain context, not an API definition.

**Category:** [Layout](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/next/packages/webawesome/src/components/split-panel/split-panel.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/split-panel/).

:::{wa-callout} Integration status
:variant: brand
:appearance: filled

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

For direct MyST integration, place this trusted markup in a Markdown HTML block or use the corresponding built-in MyST directive/role when supported. 
