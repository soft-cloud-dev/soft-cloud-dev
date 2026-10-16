# Progress Bar `<wa-progress-bar>`

Shows task completion as a linear measure.

> “Feedback is also a useful design principle for designing user interfaces.” — [Wikipedia: Feedback](wiki:Feedback). This quote supplies general domain context, not an API definition.

**Category:** [Feedback](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/v3.14.0/packages/webawesome/src/components/progress-bar/progress-bar.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/progress-bar/).

:::{wa-callout} Integration status
:variant: brand
:appearance: filled

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Live preview

```{anywidget} ../../widgets/webawesome-demo.mjs
{
  "tree": {
    "tag": "wa-progress-bar",
    "attrs": {
      "value": "64",
      "label": "Deployment progress"
    },
    "children": []
  }
}
```

## Markdown code snippet

```html
<wa-progress-bar value="64" label="Deployment progress"></wa-progress-bar>
```

For direct MyST integration, place this trusted markup in a Markdown HTML block or use the corresponding built-in MyST directive/role when supported. 
