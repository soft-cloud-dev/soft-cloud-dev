# Animation `<wa-animation>`

Runs declaratively configured visual effects.

> “a sequence or set of instructions in a programming language” — [Wikipedia: Computer program](wiki:Computer_program). This quote supplies general domain context, not an API definition.

**Category:** [Helpers](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/v3.14.0/packages/webawesome/src/components/animation/animation.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/animation/).

:::{note} Integration status

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Live preview

```{anywidget} ../../widgets/webawesome-demo.mjs
{
  "tree": {
    "tag": "wa-animation",
    "attrs": {
      "name": "fadeIn",
      "play": ""
    },
    "children": [
      {
        "tag": "strong",
        "attrs": {},
        "children": [
          "Animated status"
        ]
      }
    ]
  }
}
```

## Markdown code snippet

```html
<wa-animation name="fadeIn" play="">
  <strong>Animated status</strong>
</wa-animation>
```

Use native MyST for documentation layout; interactive Web Awesome previews remain hosted through the existing `{anywidget}` integration when available. 
