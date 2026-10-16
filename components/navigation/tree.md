# Tree `<wa-tree>`

Represents an expandable tree of nested item atoms.

> “the process of navigating a network of information resources” — [Wikipedia: Web navigation](wiki:Web_navigation). This quote supplies general domain context, not an API definition.

**Category:** [Navigation](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/next/packages/webawesome/src/components/tree/tree.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/tree/).

:::{wa-callout} Integration status
:variant: brand
:appearance: filled

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Atomic composition

Reuse: [Tree Item](../navigation/tree-item.md). The full nested markup below remains independently usable.

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
          "Infrastructure",
          {
            "tag": "wa-tree-item",
            "attrs": {},
            "children": [
              "Compute"
            ]
          },
          {
            "tag": "wa-tree-item",
            "attrs": {},
            "children": [
              "Storage"
            ]
          }
        ]
      },
      {
        "tag": "wa-tree-item",
        "attrs": {},
        "children": [
          "Apps"
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
    Infrastructure
    <wa-tree-item>Compute</wa-tree-item>
    <wa-tree-item>Storage</wa-tree-item>
  </wa-tree-item>
  <wa-tree-item>Apps</wa-tree-item>
</wa-tree>
```

For direct MyST integration, place this trusted markup in a Markdown HTML block or use the corresponding built-in MyST directive/role when supported. 
