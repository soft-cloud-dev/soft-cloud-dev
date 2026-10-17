# Known Date `<wa-known-date>`

Splits an already-known date into day, month, and year parts.

> “allows a user to enter data that is sent to a server for processing” — [Wikipedia: HTML form](wiki:HTML_form). This quote supplies general domain context, not an API definition.

**Category:** [Forms](../index.md) · **Availability:** Core · **Maturity:** Experimental.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/v3.14.0/packages/webawesome/src/components/known-date/known-date.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/known-date/).

:::{note} Integration status

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Live preview

```{anywidget} ../../widgets/webawesome-demo.mjs
{
  "tree": {
    "tag": "wa-known-date",
    "attrs": {
      "label": "Start date"
    },
    "children": []
  }
}
```

## Markdown code snippet

```html
<wa-known-date label="Start date"></wa-known-date>
```

Use native MyST for documentation layout; interactive Web Awesome previews remain hosted through the existing `{anywidget}` integration when available. 
