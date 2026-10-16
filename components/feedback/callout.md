# Callout `<wa-callout>`

Displays a contextual warning, note, or operational status.

> “Feedback is also a useful design principle for designing user interfaces.” — [Wikipedia: Feedback](wiki:Feedback). This quote supplies general domain context, not an API definition.

**Category:** [Feedback](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/next/packages/webawesome/src/components/callout/callout.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/callout/).

:::{wa-callout} Integration status
:variant: brand
:appearance: soft

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Live preview

```{anywidget} ../../widgets/webawesome-demo.mjs
{
  "tree": {
    "tag": "wa-callout",
    "attrs": {
      "variant": "warning",
      "appearance": "soft"
    },
    "children": [
      {
        "tag": "strong",
        "attrs": {
          "slot": "title"
        },
        "children": [
          "Notice"
        ]
      },
      {
        "tag": "p",
        "attrs": {},
        "children": [
          "Maintenance is scheduled."
        ]
      }
    ]
  }
}
```

## Markdown code snippet

```html
<wa-callout variant="warning" appearance="soft">
  <strong slot="title">Notice</strong>
  <p>Maintenance is scheduled.</p>
</wa-callout>
```

For direct MyST integration, place this trusted markup in a Markdown HTML block or use the corresponding built-in MyST directive/role when supported. 
