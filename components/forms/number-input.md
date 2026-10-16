# Number Input `<wa-number-input>`

Collects bounded numeric values with step controls.

> “allows a user to enter data that is sent to a server for processing” — [Wikipedia: HTML form](wiki:HTML_form). This quote supplies general domain context, not an API definition.

**Category:** [Forms](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/next/packages/webawesome/src/components/number-input/number-input.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/number-input/).

:::{wa-callout} Integration status
:variant: brand
:appearance: filled

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Live preview

```{anywidget} ../../widgets/webawesome-demo.mjs
{
  "tree": {
    "tag": "wa-number-input",
    "attrs": {
      "label": "Replicas",
      "min": "1",
      "max": "20",
      "value": "3"
    },
    "children": []
  }
}
```

## Markdown code snippet

```html
<wa-number-input label="Replicas" min="1" max="20" value="3"></wa-number-input>
```

For direct MyST integration, place this trusted markup in a Markdown HTML block or use the corresponding built-in MyST directive/role when supported. 
