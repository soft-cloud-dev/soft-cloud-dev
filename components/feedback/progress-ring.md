# Progress Ring `<wa-progress-ring>`

Shows task completion as a circular measure.

> “Feedback is also a useful design principle for designing user interfaces.” — [Wikipedia: Feedback](wiki:Feedback). This quote supplies general domain context, not an API definition.

**Category:** [Feedback](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/next/packages/webawesome/src/components/progress-ring/progress-ring.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/progress-ring/).

:::{wa-callout} Integration status
:variant: brand
:appearance: filled

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Live preview

```{anywidget} ../../widgets/webawesome-demo.mjs
{
  "tree": {
    "tag": "wa-progress-ring",
    "attrs": {
      "value": "64",
      "label": "Deployment progress"
    },
    "children": [
      "64%"
    ]
  }
}
```

## Markdown code snippet

```html
<wa-progress-ring value="64" label="Deployment progress">64%</wa-progress-ring>
```

For direct MyST integration, place this trusted markup in a Markdown HTML block or use the corresponding built-in MyST directive/role when supported. 
