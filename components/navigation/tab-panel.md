# Tab Panel `<wa-tab-panel>`

Contains content selected by a matching tab.

> “the process of navigating a network of information resources” — [Wikipedia: Web navigation](wiki:Web_navigation). This quote supplies general domain context, not an API definition.

**Category:** [Navigation](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/v3.14.0/packages/webawesome/src/components/tab-panel/tab-panel.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/tab-panel/).

:::{wa-callout} Integration status
:variant: brand
:appearance: filled

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Atomic composition

Reuse: [Tab Group](../navigation/tab-group.md), [Tab](../navigation/tab.md). The full nested markup below remains independently usable.

## Live preview

```{anywidget} ../../widgets/webawesome-demo.mjs
{
  "tree": {
    "tag": "wa-tab-group",
    "attrs": {
      "active": "usage"
    },
    "children": [
      {
        "tag": "wa-tab",
        "attrs": {
          "panel": "usage"
        },
        "children": [
          "Usage"
        ]
      },
      {
        "tag": "wa-tab-panel",
        "attrs": {
          "name": "usage"
        },
        "children": [
          "Resource consumption"
        ]
      }
    ]
  }
}
```

## Markdown code snippet

```html
<wa-tab-group active="usage">
  <wa-tab panel="usage">Usage</wa-tab>
  <wa-tab-panel name="usage">Resource consumption</wa-tab-panel>
</wa-tab-group>
```

For direct MyST integration, place this trusted markup in a Markdown HTML block or use the corresponding built-in MyST directive/role when supported. 
