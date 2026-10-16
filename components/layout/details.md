# Details `<wa-details>`

Reveals or hides supplemental content on demand.

> “the space where interactions between humans and machines occur” — [Wikipedia: User interface](wiki:User_interface). This quote supplies general domain context, not an API definition.

**Category:** [Layout](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/next/packages/webawesome/src/components/details/details.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/details/).

:::{wa-callout} Integration status
:variant: brand
:appearance: filled

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Live preview

```{anywidget} ../../widgets/webawesome-demo.mjs
{
  "tree": {
    "tag": "wa-details",
    "attrs": {
      "summary": "Advanced options"
    },
    "children": [
      "Enable additional diagnostics."
    ]
  }
}
```

## Markdown code snippet

```html
<wa-details summary="Advanced options">Enable additional diagnostics.</wa-details>
```

For direct MyST integration, place this trusted markup in a Markdown HTML block or use the corresponding built-in MyST directive/role when supported. 
