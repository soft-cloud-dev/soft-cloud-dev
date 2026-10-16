# Format Date `<wa-format-date>`

Formats timestamps using locale-aware date conventions.

> “a sequence or set of instructions in a programming language” — [Wikipedia: Computer program](wiki:Computer_program). This quote supplies general domain context, not an API definition.

**Category:** [Helpers](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/next/packages/webawesome/src/components/format-date/format-date.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/format-date/).

:::{wa-callout} Integration status
:variant: brand
:appearance: filled

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Live preview

```{anywidget} ../../widgets/webawesome-demo.mjs
{
  "tree": {
    "tag": "wa-format-date",
    "attrs": {
      "date": "2026-10-17T12:00:00Z",
      "month": "long",
      "day": "numeric",
      "year": "numeric"
    },
    "children": []
  }
}
```

## Markdown code snippet

```html
<wa-format-date date="2026-10-17T12:00:00Z" month="long" day="numeric" year="numeric"></wa-format-date>
```

For direct MyST integration, place this trusted markup in a Markdown HTML block or use the corresponding built-in MyST directive/role when supported. 
