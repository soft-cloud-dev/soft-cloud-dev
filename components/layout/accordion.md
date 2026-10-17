# Accordion `<wa-accordion>`

Organizes expandable accordion items.

> “the space where interactions between humans and machines occur” — [Wikipedia: User interface](wiki:User_interface). This quote supplies general domain context, not an API definition.

**Category:** [Layout](../index.md) · **Availability:** Core · **Maturity:** Experimental.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/v3.14.0/packages/webawesome/src/components/accordion/accordion.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/accordion/).

:::{note} Integration status

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Atomic composition

Reuse: [Accordion Item](../layout/accordion-item.md). The full nested markup below remains independently usable.

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
          "label": "Prerequisites"
        },
        "children": [
          "Install dependencies."
        ]
      },
      {
        "tag": "wa-accordion-item",
        "attrs": {
          "label": "Verification"
        },
        "children": [
          "Run the tests."
        ]
      }
    ]
  }
}
```

## Markdown code snippet

```html
<wa-accordion>
  <wa-accordion-item label="Prerequisites">Install dependencies.</wa-accordion-item>
  <wa-accordion-item label="Verification">Run the tests.</wa-accordion-item>
</wa-accordion>
```

Use native MyST for documentation layout; interactive Web Awesome previews remain hosted through the existing `{anywidget}` integration when available. 
