# Tree Item `<wa-tree-item>`

Represents one hierarchical node in a tree.

> “the process of navigating a network of information resources” — [Wikipedia: Web navigation](wiki:Web_navigation). This quote supplies general domain context, not an API definition.

**Category:** [Navigation](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/v3.14.0/packages/webawesome/src/components/tree-item/tree-item.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/tree-item/).

:::{note} Integration status

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Atomic composition

Reuse: [Tree](../navigation/tree.md). The full nested markup below remains independently usable.

## Live preview

```{anywidget} ../../widgets/webawesome-demo.mjs
{
  "tree": {
    "tag": "wa-tree",
    "attrs": {},
    "children": [
      {
        "tag": "wa-tree-item",
        "attrs": {},
        "children": [
          "Cluster",
          {
            "tag": "wa-tree-item",
            "attrs": {},
            "children": [
              "Control plane"
            ]
          },
          {
            "tag": "wa-tree-item",
            "attrs": {},
            "children": [
              "Workers"
            ]
          }
        ]
      }
    ]
  }
}
```

## Markdown code snippet

```html
<wa-tree>
  <wa-tree-item>
    Cluster
    <wa-tree-item>Control plane</wa-tree-item>
    <wa-tree-item>Workers</wa-tree-item>
  </wa-tree-item>
</wa-tree>
```

Use native MyST for documentation layout; interactive Web Awesome previews remain hosted through the existing `{anywidget}` integration when available. 
