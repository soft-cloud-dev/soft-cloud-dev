# Textarea `<wa-textarea>`

Collects text across several lines.

> “allows a user to enter data that is sent to a server for processing” — [Wikipedia: HTML form](wiki:HTML_form). This quote supplies general domain context, not an API definition.

**Category:** [Forms](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/v3.14.0/packages/webawesome/src/components/textarea/textarea.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/textarea/).

:::{note} Integration status

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Live preview

```{anywidget} ../../widgets/webawesome-demo.mjs
{
  "tree": {
    "tag": "wa-textarea",
    "attrs": {
      "label": "Notes",
      "rows": "3",
      "placeholder": "Describe the change"
    },
    "children": []
  }
}
```

## Markdown code snippet

```html
<wa-textarea label="Notes" rows="3" placeholder="Describe the change"></wa-textarea>
```

Use native MyST for documentation layout; interactive Web Awesome previews remain hosted through the existing `{anywidget}` integration when available. 
