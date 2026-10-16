# Skeleton `<wa-skeleton>`

Reserves space for content not yet available.

> “Feedback is also a useful design principle for designing user interfaces.” — [Wikipedia: Feedback](wiki:Feedback). This quote supplies general domain context, not an API definition.

**Category:** [Feedback](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/next/packages/webawesome/src/components/skeleton/skeleton.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/skeleton/).

:::{wa-callout} Integration status
:variant: brand
:appearance: filled

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Live preview

```{anywidget} ../../widgets/webawesome-demo.mjs
{
  "tree": {
    "tag": "div",
    "attrs": {},
    "children": [
      {
        "tag": "wa-skeleton",
        "attrs": {
          "effect": "pulse"
        },
        "children": []
      },
      {
        "tag": "wa-skeleton",
        "attrs": {
          "effect": "pulse"
        },
        "children": []
      }
    ]
  }
}
```

## Markdown code snippet

```html
<div>
  <wa-skeleton effect="pulse"></wa-skeleton>
  <wa-skeleton effect="pulse"></wa-skeleton>
</div>
```

For direct MyST integration, place this trusted markup in a Markdown HTML block or use the corresponding built-in MyST directive/role when supported. 
