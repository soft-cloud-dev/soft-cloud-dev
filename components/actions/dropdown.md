# Dropdown `<wa-dropdown>`

Combines a trigger button with reusable menu item controls.

> “provides the user a simple way to trigger an event” — [Wikipedia: Button (computing)](wiki:Button_(computing)). This quote supplies general domain context, not an API definition.

**Category:** [Actions](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/next/packages/webawesome/src/components/dropdown/dropdown.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/dropdown/).

:::{wa-callout} Integration status
:variant: brand
:appearance: filled

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Atomic composition

Reuse: [Button](../actions/button.md), [Dropdown Item](../actions/dropdown-item.md). The full nested markup below remains independently usable.

## Live preview

```{anywidget} ../../widgets/webawesome-demo.mjs
{
  "tree": {
    "tag": "wa-dropdown",
    "attrs": {},
    "children": [
      {
        "tag": "wa-button",
        "attrs": {
          "slot": "trigger",
          "with-caret": ""
        },
        "children": [
          "Actions"
        ]
      },
      {
        "tag": "wa-dropdown-item",
        "attrs": {
          "value": "inspect"
        },
        "children": [
          "Inspect"
        ]
      },
      {
        "tag": "wa-dropdown-item",
        "attrs": {
          "value": "restart"
        },
        "children": [
          "Restart"
        ]
      }
    ]
  }
}
```

## Markdown code snippet

```html
<wa-dropdown>
  <wa-button slot="trigger" with-caret="">Actions</wa-button>
  <wa-dropdown-item value="inspect">Inspect</wa-dropdown-item>
  <wa-dropdown-item value="restart">Restart</wa-dropdown-item>
</wa-dropdown>
```

For direct MyST integration, place this trusted markup in a Markdown HTML block or use the corresponding built-in MyST directive/role when supported. 
