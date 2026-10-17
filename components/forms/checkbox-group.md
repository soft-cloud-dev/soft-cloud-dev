# Checkbox Group `<wa-checkbox-group>`

Organizes independent checkboxes under one accessible label.

> “allows a user to enter data that is sent to a server for processing” — [Wikipedia: HTML form](wiki:HTML_form). This quote supplies general domain context, not an API definition.

**Category:** [Forms](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/v3.14.0/packages/webawesome/src/components/checkbox-group/checkbox-group.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/checkbox-group/).

:::{note} Integration status

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Atomic composition

Reuse: [Checkbox](../forms/checkbox.md). The full nested markup below remains independently usable.

## Live preview

```{anywidget} ../../widgets/webawesome-demo.mjs
{
  "tree": {
    "tag": "wa-checkbox-group",
    "attrs": {
      "label": "Features"
    },
    "children": [
      {
        "tag": "wa-checkbox",
        "attrs": {
          "value": "monitor",
          "checked": ""
        },
        "children": [
          "Monitoring"
        ]
      },
      {
        "tag": "wa-checkbox",
        "attrs": {
          "value": "logs"
        },
        "children": [
          "Logs"
        ]
      }
    ]
  }
}
```

## Markdown code snippet

```html
<wa-checkbox-group label="Features">
  <wa-checkbox value="monitor" checked="">Monitoring</wa-checkbox>
  <wa-checkbox value="logs">Logs</wa-checkbox>
</wa-checkbox-group>
```

Use native MyST for documentation layout; interactive Web Awesome previews remain hosted through the existing `{anywidget}` integration when available. 
