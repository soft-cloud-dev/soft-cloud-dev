# Format Bytes `<wa-format-bytes>`

Presents byte quantities with human-readable units.

> “a sequence or set of instructions in a programming language” — [Wikipedia: Computer program](wiki:Computer_program). This quote supplies general domain context, not an API definition.

**Category:** [Helpers](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/v3.14.0/packages/webawesome/src/components/format-bytes/format-bytes.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/format-bytes/).

:::{wa-callout} Integration status
:variant: brand
:appearance: filled

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Live preview

```{anywidget} ../../widgets/webawesome-demo.mjs
{
  "tree": {
    "tag": "wa-format-bytes",
    "attrs": {
      "value": "10485760"
    },
    "children": []
  }
}
```

## Markdown code snippet

```html
<wa-format-bytes value="10485760"></wa-format-bytes>
```

For direct MyST integration, place this trusted markup in a Markdown HTML block or use the corresponding built-in MyST directive/role when supported. 
