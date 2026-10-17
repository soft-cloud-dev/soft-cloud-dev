# Time Input `<wa-time-input>`

Provides a segmented field for choosing time.

> “allows a user to enter data that is sent to a server for processing” — [Wikipedia: HTML form](wiki:HTML_form). This quote supplies general domain context, not an API definition.

**Category:** [Forms](../index.md) · **Availability:** Core · **Maturity:** Experimental.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/v3.14.0/packages/webawesome/src/components/time-input/time-input.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/time-input/).

:::{wa-callout} Integration status
:variant: brand
:appearance: filled

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Live preview

```{anywidget} ../../widgets/webawesome-demo.mjs
{
  "tree": {
    "tag": "wa-time-input",
    "attrs": {
      "label": "Window",
      "value": "14:30"
    },
    "children": []
  }
}
```

## Markdown code snippet

```html
<wa-time-input label="Window" value="14:30"></wa-time-input>
```

For direct MyST integration, place this trusted markup in a Markdown HTML block or use the corresponding built-in MyST directive/role when supported. 
