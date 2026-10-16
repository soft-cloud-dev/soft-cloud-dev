# Color Picker `<wa-color-picker>`

Presents a palette and a field for specifying a color.

> “allows a user to enter data that is sent to a server for processing” — [Wikipedia: HTML form](wiki:HTML_form). This quote supplies general domain context, not an API definition.

**Category:** [Forms](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/next/packages/webawesome/src/components/color-picker/color-picker.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/color-picker/).

:::{wa-callout} Integration status
:variant: brand
:appearance: soft

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Live preview

```{anywidget} ../../widgets/webawesome-demo.mjs
{
  "tree": {
    "tag": "wa-color-picker",
    "attrs": {
      "label": "Accent",
      "value": "#2563eb"
    },
    "children": []
  }
}
```

## Markdown code snippet

```html
<wa-color-picker label="Accent" value="#2563eb"></wa-color-picker>
```

For direct MyST integration, place this trusted markup in a Markdown HTML block or use the corresponding built-in MyST directive/role when supported. 
