# Breadcrumb Item `<wa-breadcrumb-item>`

Represents one level in a navigation trail.

> “the process of navigating a network of information resources” — [Wikipedia: Web navigation](wiki:Web_navigation). This quote supplies general domain context, not an API definition.

**Category:** [Navigation](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/next/packages/webawesome/src/components/breadcrumb-item/breadcrumb-item.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/breadcrumb-item/).

:::{wa-callout} Integration status
:variant: brand
:appearance: soft

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Atomic composition

Reuse: [Breadcrumb](../navigation/breadcrumb.md). The full nested markup below remains independently usable.

## Live preview

```{anywidget} ../../widgets/webawesome-demo.mjs
{
  "tree": {
    "tag": "wa-breadcrumb",
    "attrs": {},
    "children": [
      {
        "tag": "wa-breadcrumb-item",
        "attrs": {
          "href": "/"
        },
        "children": [
          "Home"
        ]
      },
      {
        "tag": "wa-breadcrumb-item",
        "attrs": {},
        "children": [
          "Current section"
        ]
      }
    ]
  }
}
```

## Markdown code snippet

```html
<wa-breadcrumb>
  <wa-breadcrumb-item href="/">Home</wa-breadcrumb-item>
  <wa-breadcrumb-item>Current section</wa-breadcrumb-item>
</wa-breadcrumb>
```

For direct MyST integration, place this trusted markup in a Markdown HTML block or use the corresponding built-in MyST directive/role when supported. 
