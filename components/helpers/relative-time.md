# Relative Time `<wa-relative-time>`

Formats a timestamp relative to the current date.

> “a sequence or set of instructions in a programming language” — [Wikipedia: Computer program](wiki:Computer_program). This quote supplies general domain context, not an API definition.

**Category:** [Helpers](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/v3.14.0/packages/webawesome/src/components/relative-time/relative-time.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/relative-time/).

:::{wa-callout} Integration status
:variant: brand
:appearance: filled

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Live preview

```{anywidget} ../../widgets/webawesome-demo.mjs
{
  "tree": {
    "tag": "wa-relative-time",
    "attrs": {
      "date": "2026-10-16T12:00:00Z"
    },
    "children": []
  }
}
```

## Markdown code snippet

```html
<wa-relative-time date="2026-10-16T12:00:00Z"></wa-relative-time>
```

For direct MyST integration, place this trusted markup in a Markdown HTML block or use the corresponding built-in MyST directive/role when supported. 
