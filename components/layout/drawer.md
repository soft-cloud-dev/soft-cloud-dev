# Drawer `<wa-drawer>`

Opens a dismissible panel at the viewport edge.

> “the space where interactions between humans and machines occur” — [Wikipedia: User interface](wiki:User_interface). This quote supplies general domain context, not an API definition.

**Category:** [Layout](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/next/packages/webawesome/src/components/drawer/drawer.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/drawer/).

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
        "data-demo-target": "demo-drawer",
        "data-demo-action": "show"
      },
      "children": [
        "Open drawer"
      ]
    },
    {
      "tag": "wa-drawer",
      "attrs": {
        "id": "demo-drawer",
        "label": "Settings"
      },
      "children": [
        {
          "tag": "p",
          "attrs": {},
          "children": [
            "Node settings"
          ]
        },
        {
          "tag": "wa-button",
          "attrs": {
            "slot": "footer",
            "data-demo-target": "demo-drawer",
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
<wa-button data-demo-target="demo-drawer" data-demo-action="show">Open drawer</wa-button>

<wa-drawer id="demo-drawer" label="Settings">
  <p>Node settings</p>
  <wa-button slot="footer" data-demo-target="demo-drawer" data-demo-action="hide">Close</wa-button>
</wa-drawer>
```

For direct MyST integration, place this trusted markup in a Markdown HTML block or use the corresponding built-in MyST directive/role when supported. 
