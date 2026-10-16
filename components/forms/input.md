# Input `<wa-input>`

Collects one line of text in a form.

> “allows a user to enter data that is sent to a server for processing” — [Wikipedia: HTML form](wiki:HTML_form). This quote supplies general domain context, not an API definition.

**Category:** [Forms](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/v3.14.0/packages/webawesome/src/components/input/input.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/input/).

:::{wa-callout} Integration status
:variant: brand
:appearance: filled

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Live preview

```{anywidget} ../../widgets/webawesome-demo.mjs
{
  "tree": {
    "tag": "wa-input",
    "attrs": {
      "label": "Hostname",
      "placeholder": "node.example.org"
    },
    "children": []
  }
}
```

## Markdown code snippet

```html
<wa-input label="Hostname" placeholder="node.example.org"></wa-input>
```

For direct MyST integration, place this trusted markup in a Markdown HTML block or use the corresponding built-in MyST directive/role when supported. 
