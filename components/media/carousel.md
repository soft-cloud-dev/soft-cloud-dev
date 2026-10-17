# Carousel `<wa-carousel>`

Coordinates a sequence of carousel item slides.

> “Multimedia is a form of communication that uses a combination of different content forms.” — [Wikipedia: Multimedia](wiki:Multimedia). This quote supplies general domain context, not an API definition.

**Category:** [Media](../index.md) · **Availability:** Core · **Maturity:** Experimental.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/v3.14.0/packages/webawesome/src/components/carousel/carousel.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/carousel/).

:::{wa-callout} Integration status
:variant: brand
:appearance: filled

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Atomic composition

Reuse: [Carousel Item](../media/carousel-item.md). The full nested markup below remains independently usable.

## Live preview

```{anywidget} ../../widgets/webawesome-demo.mjs
{
  "tree": {
    "tag": "wa-carousel",
    "attrs": {
      "pagination": "",
      "navigation": ""
    },
    "children": [
      {
        "tag": "wa-carousel-item",
        "attrs": {},
        "children": [
          {
            "tag": "p",
            "attrs": {},
            "children": [
              "First slide"
            ]
          }
        ]
      },
      {
        "tag": "wa-carousel-item",
        "attrs": {},
        "children": [
          {
            "tag": "p",
            "attrs": {},
            "children": [
              "Second slide"
            ]
          }
        ]
      }
    ]
  }
}
```

## Markdown code snippet

```html
<wa-carousel pagination="" navigation="">
  <wa-carousel-item>
    <p>First slide</p>
  </wa-carousel-item>
  <wa-carousel-item>
    <p>Second slide</p>
  </wa-carousel-item>
</wa-carousel>
```

For direct MyST integration, place this trusted markup in a Markdown HTML block or use the corresponding built-in MyST directive/role when supported. 
