# Comparison `<wa-comparison>`

Compares two images with an adjustable split.

> “Multimedia is a form of communication that uses a combination of different content forms.” — [Wikipedia: Multimedia](wiki:Multimedia). This quote supplies general domain context, not an API definition.

**Category:** [Media](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/v3.14.0/packages/webawesome/src/components/comparison/comparison.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/comparison/).

:::{note} Integration status

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Live preview

```{anywidget} ../../widgets/webawesome-demo.mjs
{
  "tree": {
    "tag": "wa-comparison",
    "attrs": {
      "position": "50"
    },
    "children": [
      {
        "tag": "img",
        "attrs": {
          "src": "/static/showcase/rocket.jpg",
          "alt": "Grayscale Falcon 9 rocket launch",
          "slot": "before",
          "class": "sc-demo-grayscale"
        },
        "children": []
      },
      {
        "tag": "img",
        "attrs": {
          "src": "/static/showcase/rocket.jpg",
          "alt": "Color Falcon 9 rocket launch",
          "slot": "after"
        },
        "children": []
      }
    ]
  }
}
```

## Markdown code snippet

```html
<wa-comparison position="50">
  <img slot="before" class="sc-demo-grayscale" src="/static/showcase/rocket.jpg" alt="Grayscale Falcon 9 launch">
  <img slot="after" src="/static/showcase/rocket.jpg" alt="Color Falcon 9 launch">
</wa-comparison>
<style>
  .sc-demo-grayscale { filter: grayscale(1); }
</style>
```

## Usage and API notes

The views use the exact **same local photograph**; a CSS grayscale filter guarantees aligned before/after content. The comparison handle is keyboard accessible. `position` sets the initial split, from 0 through 100.

Media licenses and canonical sources: [Showcase media](../showcase-media.md).
