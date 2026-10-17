# Breadcrumb `<wa-breadcrumb>`

Assembles breadcrumb item atoms into a navigation trail.

> “the process of navigating a network of information resources” — [Wikipedia: Web navigation](wiki:Web_navigation). This quote supplies general domain context, not an API definition.

**Category:** [Navigation](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/v3.14.0/packages/webawesome/src/components/breadcrumb/breadcrumb.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/breadcrumb/).

:::{wa-callout} Integration status
:variant: brand
:appearance: filled

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Atomic composition

Reuse: [Breadcrumb Item](../navigation/breadcrumb-item.md). The full nested markup below remains independently usable.

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
        "attrs": {
          "href": "/architecture"
        },
        "children": [
          "Architecture"
        ]
      },
      {
        "tag": "wa-breadcrumb-item",
        "attrs": {},
        "children": [
          "Components"
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
  <wa-breadcrumb-item href="/architecture">Architecture</wa-breadcrumb-item>
  <wa-breadcrumb-item>Components</wa-breadcrumb-item>
</wa-breadcrumb>
```

For direct MyST integration, place this trusted markup in a Markdown HTML block or use the corresponding built-in MyST directive/role when supported. 
