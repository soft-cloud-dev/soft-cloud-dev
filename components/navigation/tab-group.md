# Tab Group `<wa-tab-group>`

Coordinates tab buttons and their corresponding panels.

> “the process of navigating a network of information resources” — [Wikipedia: Web navigation](wiki:Web_navigation). This quote supplies general domain context, not an API definition.

**Category:** [Navigation](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/next/packages/webawesome/src/components/tab-group/tab-group.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/tab-group/).

:::{wa-callout} Integration status
:variant: brand
:appearance: filled

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Atomic composition

Reuse: [Tab](../navigation/tab.md), [Tab Panel](../navigation/tab-panel.md). The full nested markup below remains independently usable.

## Live preview

```{anywidget} ../../widgets/webawesome-demo.mjs
{
  "tree": {
    "tag": "wa-tab-group",
    "attrs": {
      "active": "overview"
    },
    "children": [
      {
        "tag": "wa-tab",
        "attrs": {
          "panel": "overview"
        },
        "children": [
          "Overview"
        ]
      },
      {
        "tag": "wa-tab",
        "attrs": {
          "panel": "metrics"
        },
        "children": [
          "Metrics"
        ]
      },
      {
        "tag": "wa-tab-panel",
        "attrs": {
          "name": "overview"
        },
        "children": [
          "System overview"
        ]
      },
      {
        "tag": "wa-tab-panel",
        "attrs": {
          "name": "metrics"
        },
        "children": [
          "CPU and memory"
        ]
      }
    ]
  }
}
```

## Markdown code snippet

```html
<wa-tab-group active="overview">
  <wa-tab panel="overview">Overview</wa-tab>
  <wa-tab panel="metrics">Metrics</wa-tab>
  <wa-tab-panel name="overview">System overview</wa-tab-panel>
  <wa-tab-panel name="metrics">CPU and memory</wa-tab-panel>
</wa-tab-group>
```

For direct MyST integration, place this trusted markup in a Markdown HTML block or use the corresponding built-in MyST directive/role when supported. 
