# Scroller `<wa-scroller>`

Provides a bounded scroll area with overflow hints.

> “the space where interactions between humans and machines occur” — [Wikipedia: User interface](wiki:User_interface). This quote supplies general domain context, not an API definition.

**Category:** [Layout](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/next/packages/webawesome/src/components/scroller/scroller.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/scroller/).

:::{wa-callout} Integration status
:variant: brand
:appearance: filled

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Live preview

```{anywidget} ../../widgets/webawesome-demo.mjs
{
  "tree": {
    "tag": "wa-scroller",
    "attrs": {},
    "children": [
      {
        "tag": "div",
        "attrs": {
          "class": "wa-cluster"
        },
        "children": [
          "First item",
          {
            "tag": "wa-button",
            "attrs": {},
            "children": [
              "One"
            ]
          },
          {
            "tag": "wa-button",
            "attrs": {},
            "children": [
              "Two"
            ]
          },
          {
            "tag": "wa-button",
            "attrs": {},
            "children": [
              "Three"
            ]
          },
          {
            "tag": "wa-button",
            "attrs": {},
            "children": [
              "Four"
            ]
          }
        ]
      }
    ]
  }
}
```

## Markdown code snippet

```html
<wa-scroller>
  <div class="wa-cluster">
    First item
    <wa-button>One</wa-button>
    <wa-button>Two</wa-button>
    <wa-button>Three</wa-button>
    <wa-button>Four</wa-button>
  </div>
</wa-scroller>
```

For direct MyST integration, place this trusted markup in a Markdown HTML block or use the corresponding built-in MyST directive/role when supported. 
