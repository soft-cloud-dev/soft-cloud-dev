# Dialog `<wa-dialog>`

Presents a focused dialog surface above the document.

> “the space where interactions between humans and machines occur” — [Wikipedia: User interface](wiki:User_interface). This quote supplies general domain context, not an API definition.

**Category:** [Layout](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/next/packages/webawesome/src/components/dialog/dialog.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/dialog/).

:::{wa-callout} Integration status
:variant: brand
:appearance: soft

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Atomic composition

Reuse: [Button](../actions/button.md). The full nested markup below remains independently usable.

## Live preview

```{anywidget} ../../widgets/webawesome-demo.mjs
{
  "tree": [
    {
      "tag": "wa-button",
      "attrs": {
        "data-demo-target": "demo-dialog",
        "data-demo-action": "show"
      },
      "children": [
        "Open dialog"
      ]
    },
    {
      "tag": "wa-dialog",
      "attrs": {
        "id": "demo-dialog",
        "label": "Confirmation"
      },
      "children": [
        {
          "tag": "p",
          "attrs": {},
          "children": [
            "Proceed with deployment?"
          ]
        },
        {
          "tag": "wa-button",
          "attrs": {
            "slot": "footer",
            "data-demo-target": "demo-dialog",
            "data-demo-action": "hide"
          },
          "children": [
            "Close"
          ]
        }
      ]
    }
  ]
}
```

## Markdown code snippet

```html
<wa-button data-demo-target="demo-dialog" data-demo-action="show">Open dialog</wa-button>

<wa-dialog id="demo-dialog" label="Confirmation">
  <p>Proceed with deployment?</p>
  <wa-button slot="footer" data-demo-target="demo-dialog" data-demo-action="hide">Close</wa-button>
</wa-dialog>
```

For direct MyST integration, place this trusted markup in a Markdown HTML block or use the corresponding built-in MyST directive/role when supported. 
