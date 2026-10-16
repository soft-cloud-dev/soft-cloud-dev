# Select `<wa-select>`

Presents a compact list of reusable option atoms.

> “allows a user to enter data that is sent to a server for processing” — [Wikipedia: HTML form](wiki:HTML_form). This quote supplies general domain context, not an API definition.

**Category:** [Forms](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/next/packages/webawesome/src/components/select/select.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/select/).

:::{wa-callout} Integration status
:variant: brand
:appearance: filled

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

For direct MyST integration, place this trusted markup in a Markdown HTML block or use the corresponding built-in MyST directive/role when supported. 
