# Tab `<wa-tab>`

Names and activates a matching tab panel.

> “the process of navigating a network of information resources” — [Wikipedia: Web navigation](wiki:Web_navigation). This quote supplies general domain context, not an API definition.

**Category:** [Navigation](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/next/packages/webawesome/src/components/tab/tab.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/tab/).

:::{wa-callout} Integration status
:variant: brand
:appearance: filled

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Atomic composition

Reuse: [Tab Group](../navigation/tab-group.md), [Tab Panel](../navigation/tab-panel.md). The full nested markup below remains independently usable.

## Live preview

```{anywidget} ../../widgets/webawesome-demo.mjs
{
  "tree": {
    "tag": "wa-tab-group",
    "attrs": {
      "active": "network"
    },
    "children": [
      {
        "tag": "wa-tab",
        "attrs": {
          "panel": "network"
        },
        "children": [
          "Network"
        ]
      },
      {
        "tag": "wa-tab-panel",
        "attrs": {
          "name": "network"
        },
        "children": [
          "Network settings"
        ]
      }
    ]
  }
}
```

## Markdown code snippet

```html
<wa-tab-group active="network">
  <wa-tab panel="network">Network</wa-tab>
  <wa-tab-panel name="network">Network settings</wa-tab-panel>
</wa-tab-group>
```

For direct MyST integration, place this trusted markup in a Markdown HTML block or use the corresponding built-in MyST directive/role when supported. 
