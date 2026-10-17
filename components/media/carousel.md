# Carousel `<wa-carousel>`

Coordinates a sequence of carousel item slides.

> “Multimedia is a form of communication that uses a combination of different content forms.” — [Wikipedia: Multimedia](wiki:Multimedia). This quote supplies general domain context, not an API definition.

**Category:** [Media](../index.md) · **Availability:** Core · **Maturity:** Experimental.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/v3.14.0/packages/webawesome/src/components/carousel/carousel.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/carousel/).

:::{note} Integration status

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Atomic composition

Reuse: [Carousel Item](../media/carousel-item.md). The full nested markup below remains independently usable.

## Live preview

### Static reference (works without JavaScript)

![Falcon 9 launch photograph](../../assets/static/showcase/rocket.jpg)

The image and copyable HTML example below remain available if the interactive widget fails to initialize. The widget adds component behavior; it does not provide the only readable content.

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
              "src": "showcase:rocket.jpg",
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
              "src": "showcase:coffee.png",
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
              "src": "showcase:hubble-deep-field.jpg",
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
<wa-carousel pagination navigation loop mouse-dragging>
  <wa-carousel-item><img src="./images/rocket.jpg" alt="Falcon 9 rocket launch"></wa-carousel-item>
  <wa-carousel-item><img src="./images/coffee.png" alt="Cup of coffee" loading="lazy"></wa-carousel-item>
  <wa-carousel-item><img src="./images/hubble-deep-field.jpg" alt="Hubble deep field" loading="lazy"></wa-carousel-item>
</wa-carousel>
```

## Usage and API notes

`pagination` renders slide indicators, `navigation` provides previous/next controls, `loop` wraps the sequence, and `mouse-dragging` enables pointer navigation. The live slides use three bundled photographs, not placeholders. Provide meaningful `alt` text and ensure navigation works by keyboard.

Media licenses and canonical sources: [Showcase media](../showcase-media.md).
