# Accordion Item `<wa-accordion-item>`

Defines one expandable section in an accordion.

> “the space where interactions between humans and machines occur” — [Wikipedia: User interface](wiki:User_interface). This quote supplies general domain context, not an API definition.

**Category:** [Layout](../index.md) · **Availability:** Core · **Maturity:** Experimental.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/next/packages/webawesome/src/components/accordion-item/accordion-item.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/accordion-item/).

:::{wa-callout} Integration status
:variant: brand
:appearance: filled

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Atomic composition

Reuse: [Accordion](../layout/accordion.md). The full nested markup below remains independently usable.

## Live preview

```{anywidget} ../../widgets/webawesome-demo.mjs
{
  "tree": {
    "tag": "wa-accordion",
    "attrs": {},
    "children": [
      {
        "tag": "wa-accordion-item",
        "attrs": {
          "label": "More information"
        },
        "children": [
          "Expand to read more."
        ]
      }
    ]
  }
}
```

## Markdown code snippet

```html
<wa-accordion>
  <wa-accordion-item label="More information">Expand to read more.</wa-accordion-item>
</wa-accordion>
```

For direct MyST integration, place this trusted markup in a Markdown HTML block or use the corresponding built-in MyST directive/role when supported. 
