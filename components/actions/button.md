---
description: Web Awesome button component for navigation, actions, and accessible calls to action.
keywords:
  - Web Awesome
  - button
  - wa-button
  - actions
---

# Button `<wa-button>`

Triggers a command, submits a choice, or navigates to another page.

> “provides the user a simple way to trigger an event” — [Wikipedia: Button (computing)](wiki:Button_(computing)). This quote supplies general domain context, not an API definition.

**Category:** [Actions](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/v3.14.0/packages/webawesome/src/components/button/button.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/button/).

:::{note} Integration status

The catalog's interactive demonstration uses anywidget. For a static server-rendered button, use the existing typed `{wa-button}` directive with genuine Lit SSR/DSD; do not require anywidget for this case.
:::

## Live preview

```{anywidget} ../../widgets/webawesome-demo.mjs
{
  "tree": {
    "tag": "wa-button",
    "attrs": {
      "variant": "brand"
    },
    "children": [
      "Run health check"
    ]
  }
}
```

## Markdown code snippet

```html
<wa-button variant="brand">Run health check</wa-button>
```

Use native MyST for documentation layout; interactive Web Awesome previews remain hosted through the existing `{anywidget}` integration when available. 
