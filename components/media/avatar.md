# Avatar `<wa-avatar>`

Shows a compact representation of an entity or user.

> “Multimedia is a form of communication that uses a combination of different content forms.” — [Wikipedia: Multimedia](wiki:Multimedia). This quote supplies general domain context, not an API definition.

**Category:** [Media](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/next/packages/webawesome/src/components/avatar/avatar.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/avatar/).

:::{wa-callout} Integration status
:variant: brand
:appearance: filled

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Live preview

```{anywidget} ../../widgets/webawesome-demo.mjs
{
  "tree": {
    "tag": "wa-avatar",
    "attrs": {
      "initials": "SC",
      "label": "SoftCloud"
    },
    "children": []
  }
}
```

## Markdown code snippet

```html
<wa-avatar initials="SC" label="SoftCloud"></wa-avatar>
```

For direct MyST integration, place this trusted markup in a Markdown HTML block or use the corresponding built-in MyST directive/role when supported. 
