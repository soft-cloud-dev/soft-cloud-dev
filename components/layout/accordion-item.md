# Accordion Item `<wa-accordion-item>`

Defines one expandable section in an accordion.

> “the space where interactions between humans and machines occur” — [Wikipedia: User interface](wiki:User_interface). This quote supplies general domain context, not an API definition.

**Category:** [Layout](../index.md) · **Availability:** Core · **Maturity:** Experimental.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/v3.14.0/packages/webawesome/src/components/accordion-item/accordion-item.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/accordion-item/).

:::{note} Integration status

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

Use native MyST for documentation layout; interactive Web Awesome previews remain hosted through the existing `{anywidget}` integration when available. 
