# Format Date `<wa-format-date>`

Formats timestamps using locale-aware date conventions.

> “a sequence or set of instructions in a programming language” — [Wikipedia: Computer program](wiki:Computer_program). This quote supplies general domain context, not an API definition.

**Category:** [Helpers](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/v3.14.0/packages/webawesome/src/components/format-date/format-date.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/format-date/).

:::{note} Integration status

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

Use native MyST for documentation layout; interactive Web Awesome previews remain hosted through the existing `{anywidget}` integration when available. 
