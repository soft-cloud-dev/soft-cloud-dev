# Comparison `<wa-comparison>`

Compares two images with an adjustable split.

> “Multimedia is a form of communication that uses a combination of different content forms.” — [Wikipedia: Multimedia](wiki:Multimedia). This quote supplies general domain context, not an API definition.

**Category:** [Media](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/next/packages/webawesome/src/components/comparison/comparison.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/comparison/).

:::{wa-callout} Integration status
:variant: brand
:appearance: filled

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Live preview

```{anywidget} ../../widgets/webawesome-demo.mjs
{
  "tree": {
    "tag": "wa-comparison",
    "attrs": {},
    "children": [
      {
        "tag": "img",
        "attrs": {
          "slot": "before",
          "src": "/images/logo.svg",
          "alt": "Light logo"
        },
        "children": []
      },
      {
        "tag": "img",
        "attrs": {
          "slot": "after",
          "src": "/images/logo-dark.svg",
          "alt": "Dark logo"
        },
        "children": []
      }
    ]
  }
}
```

## Markdown code snippet

```html
<wa-comparison>
  <img slot="before" src="/images/logo.svg" alt="Light logo"></img>
  <img slot="after" src="/images/logo-dark.svg" alt="Dark logo"></img>
</wa-comparison>
```

For direct MyST integration, place this trusted markup in a Markdown HTML block or use the corresponding built-in MyST directive/role when supported. 
