# Carousel Item `<wa-carousel-item>`

Represents one slide inside a carousel.

> “Multimedia is a form of communication that uses a combination of different content forms.” — [Wikipedia: Multimedia](wiki:Multimedia). This quote supplies general domain context, not an API definition.

**Category:** [Media](../index.md) · **Availability:** Core · **Maturity:** Experimental.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/v3.14.0/packages/webawesome/src/components/carousel-item/carousel-item.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/carousel-item/).

:::{note} Integration status

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Atomic composition

Reuse: [Carousel](../media/carousel.md). The full nested markup below remains independently usable.

## Live preview

```{anywidget} ../../widgets/webawesome-demo.mjs
{
  "tree": {
    "tag": "wa-carousel",
    "attrs": {
      "pagination": "",
      "navigation": "",
      "loop": "",
      "mouse-dragging": ""
    },
    "children": [
      {
        "tag": "wa-carousel-item",
        "attrs": {},
        "children": [
          {
            "tag": "img",
            "attrs": {
              "src": "/static/showcase/rocket.jpg",
              "alt": "Falcon 9 carrying DSCOVR launching from Cape Canaveral"
            },
            "children": []
          }
        ]
      },
      {
        "tag": "wa-carousel-item",
        "attrs": {},
        "children": [
          {
            "tag": "img",
            "attrs": {
              "src": "/static/showcase/coffee.png",
              "alt": "White cup of coffee on a wooden table",
              "loading": "lazy"
            },
            "children": []
          }
        ]
      },
      {
        "tag": "wa-carousel-item",
        "attrs": {},
        "children": [
          {
            "tag": "img",
            "attrs": {
              "src": "/static/showcase/hubble-deep-field.jpg",
              "alt": "Hubble eXtreme Deep Field containing thousands of galaxies",
              "loading": "lazy"
            },
            "children": []
          }
        ]
      }
    ]
  }
}
```

## Markdown code snippet

```html
<wa-carousel pagination navigation>
  <wa-carousel-item><img src="/static/showcase/rocket.jpg" alt="Falcon 9 rocket launch"></wa-carousel-item>
  <wa-carousel-item><img src="/static/showcase/coffee.png" alt="Cup of coffee"></wa-carousel-item>
  <wa-carousel-item><img src="/static/showcase/hubble-deep-field.jpg" alt="Hubble deep field"></wa-carousel-item>
</wa-carousel>
```

## Usage and API notes

This atomic element must be nested in `<wa-carousel>`. Use meaningful, descriptive media in each slide. The parent handles pagination, transitions, and navigation.

Media licenses and canonical sources: [Showcase media](../showcase-media.md).
