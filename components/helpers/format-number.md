# Format Number `<wa-format-number>`

Formats a number using locale settings.

> “a sequence or set of instructions in a programming language” — [Wikipedia: Computer program](wiki:Computer_program). This quote supplies general domain context, not an API definition.

**Category:** [Helpers](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/next/packages/webawesome/src/components/format-number/format-number.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/format-number/).

:::{wa-callout} Integration status
:variant: brand
:appearance: soft

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Live preview

```{anywidget} ../../widgets/webawesome-demo.mjs
{
  "tree": {
    "tag": "wa-format-number",
    "attrs": {
      "value": "0.975",
      "type": "percent"
    },
    "children": []
  }
}
```

## Markdown code snippet

```html
<wa-format-number value="0.975" type="percent"></wa-format-number>
```

For direct MyST integration, place this trusted markup in a Markdown HTML block or use the corresponding built-in MyST directive/role when supported. 
