# Random Content `<wa-random-content>`

Chooses one or more child fragments at random.

> “a sequence or set of instructions in a programming language” — [Wikipedia: Computer program](wiki:Computer_program). This quote supplies general domain context, not an API definition.

**Category:** [Helpers](../index.md) · **Availability:** Core · **Maturity:** Experimental.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/next/packages/webawesome/src/components/random-content/random-content.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/random-content/).

:::{wa-callout} Integration status
:variant: brand
:appearance: filled

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Live preview

```{anywidget} ../../widgets/webawesome-demo.mjs
{
  "tree": {
    "tag": "wa-random-content",
    "attrs": {},
    "children": [
      {
        "tag": "span",
        "attrs": {},
        "children": [
          "Verify builds"
        ]
      },
      {
        "tag": "span",
        "attrs": {},
        "children": [
          "Pin dependencies"
        ]
      }
    ]
  }
}
```

## Markdown code snippet

```html
<wa-random-content>
  <span>Verify builds</span>
  <span>Pin dependencies</span>
</wa-random-content>
```

For direct MyST integration, place this trusted markup in a Markdown HTML block or use the corresponding built-in MyST directive/role when supported. 
