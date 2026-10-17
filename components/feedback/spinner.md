# Spinner `<wa-spinner>`

Indicates activity with unknown remaining duration.

> “Feedback is also a useful design principle for designing user interfaces.” — [Wikipedia: Feedback](wiki:Feedback). This quote supplies general domain context, not an API definition.

**Category:** [Feedback](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/v3.14.0/packages/webawesome/src/components/spinner/spinner.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/spinner/).

:::{wa-callout} Integration status
:variant: brand
:appearance: filled

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Live preview

```{anywidget} ../../widgets/webawesome-demo.mjs
{
  "tree": {
    "tag": "wa-spinner",
    "attrs": {
      "aria-label": "Loading"
    },
    "children": []
  }
}
```

## Markdown code snippet

```html
<wa-spinner aria-label="Loading"></wa-spinner>
```

For direct MyST integration, place this trusted markup in a Markdown HTML block or use the corresponding built-in MyST directive/role when supported. 
