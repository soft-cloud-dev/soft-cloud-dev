# Divider `<wa-divider>`

Visually separates adjacent sections or controls.

> “the space where interactions between humans and machines occur” — [Wikipedia: User interface](wiki:User_interface). This quote supplies general domain context, not an API definition.

**Category:** [Layout](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/v3.14.0/packages/webawesome/src/components/divider/divider.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/divider/).

:::{note} Integration status

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Live preview

```{anywidget} ../../widgets/webawesome-demo.mjs
{
  "tree": {
    "tag": "div",
    "attrs": {},
    "children": [
      {
        "tag": "p",
        "attrs": {},
        "children": [
          "Staging"
        ]
      },
      {
        "tag": "wa-divider",
        "attrs": {},
        "children": []
      },
      {
        "tag": "p",
        "attrs": {},
        "children": [
          "Production"
        ]
      }
    ]
  }
}
```

## Markdown code snippet

```html
<div>
  <p>Staging</p>
  <wa-divider></wa-divider>
  <p>Production</p>
</div>
```

Use native MyST for documentation layout; interactive Web Awesome previews remain hosted through the existing `{anywidget}` integration when available. 
