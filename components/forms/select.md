# Select `<wa-select>`

Presents a compact list of reusable option atoms.

> “allows a user to enter data that is sent to a server for processing” — [Wikipedia: HTML form](wiki:HTML_form). This quote supplies general domain context, not an API definition.

**Category:** [Forms](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/v3.14.0/packages/webawesome/src/components/select/select.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/select/).

:::{note} Integration status

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Atomic composition

Reuse: [Option](../forms/option.md). The full nested markup below remains independently usable.

## Live preview

```{anywidget} ../../widgets/webawesome-demo.mjs
{
  "tree": {
    "tag": "wa-select",
    "attrs": {
      "label": "Role",
      "value": "worker"
    },
    "children": [
      {
        "tag": "wa-option",
        "attrs": {
          "value": "worker"
        },
        "children": [
          "Worker"
        ]
      },
      {
        "tag": "wa-option",
        "attrs": {
          "value": "control"
        },
        "children": [
          "Control plane"
        ]
      }
    ]
  }
}
```

## Markdown code snippet

```html
<wa-select label="Role" value="worker">
  <wa-option value="worker">Worker</wa-option>
  <wa-option value="control">Control plane</wa-option>
</wa-select>
```

Use native MyST for documentation layout; interactive Web Awesome previews remain hosted through the existing `{anywidget}` integration when available. 
