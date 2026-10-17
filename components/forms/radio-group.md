# Radio Group `<wa-radio-group>`

Enforces one active value among related radio atoms.

> “allows a user to enter data that is sent to a server for processing” — [Wikipedia: HTML form](wiki:HTML_form). This quote supplies general domain context, not an API definition.

**Category:** [Forms](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/v3.14.0/packages/webawesome/src/components/radio-group/radio-group.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/radio-group/).

:::{note} Integration status

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Atomic composition

Reuse: [Radio](../forms/radio.md). The full nested markup below remains independently usable.

## Live preview

```{anywidget} ../../widgets/webawesome-demo.mjs
{
  "tree": {
    "tag": "wa-radio-group",
    "attrs": {
      "label": "Channel",
      "value": "stable"
    },
    "children": [
      {
        "tag": "wa-radio",
        "attrs": {
          "value": "stable"
        },
        "children": [
          "Stable"
        ]
      },
      {
        "tag": "wa-radio",
        "attrs": {
          "value": "preview"
        },
        "children": [
          "Preview"
        ]
      }
    ]
  }
}
```

## Markdown code snippet

```html
<wa-radio-group label="Channel" value="stable">
  <wa-radio value="stable">Stable</wa-radio>
  <wa-radio value="preview">Preview</wa-radio>
</wa-radio-group>
```

Use native MyST for documentation layout; interactive Web Awesome previews remain hosted through the existing `{anywidget}` integration when available. 
