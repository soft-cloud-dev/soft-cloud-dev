# Scroller `<wa-scroller>`

Provides a bounded scroll area with overflow hints.

> “the space where interactions between humans and machines occur” — [Wikipedia: User interface](wiki:User_interface). This quote supplies general domain context, not an API definition.

**Category:** [Layout](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/v3.14.0/packages/webawesome/src/components/scroller/scroller.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/scroller/).

:::{note} Integration status

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Live preview

### Static reference (works without JavaScript)

![Falcon 9 launch photograph](../../assets/static/showcase/rocket.jpg)

The image and copyable HTML example below remain available if the interactive widget fails to initialize. The widget adds component behavior; it does not provide the only readable content.

```{anywidget} ../../widgets/webawesome-demo.mjs
{
  "tree": {
    "tag": "wa-scroller",
    "attrs": {},
    "children": [
      {
        "tag": "div",
        "attrs": {
          "class": "sc-demo-thumb-row"
        },
        "children": [
          {
            "tag": "img",
            "attrs": {
              "src": "showcase:rocket.jpg",
              "alt": "Rocket launch thumbnail",
              "loading": "lazy"
            },
            "children": []
          },
          {
            "tag": "img",
            "attrs": {
              "src": "showcase:coffee.png",
              "alt": "Coffee cup thumbnail",
              "loading": "lazy"
            },
            "children": []
          },
          {
            "tag": "img",
            "attrs": {
              "src": "showcase:hubble-deep-field.jpg",
              "alt": "Hubble deep field thumbnail",
              "loading": "lazy"
            },
            "children": []
          },
          {
            "tag": "img",
            "attrs": {
              "src": "showcase:astronaut.png",
              "alt": "Astronaut Eileen Collins thumbnail",
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
<wa-scroller>
  <div class="sc-demo-thumb-row">
    <img src="./images/rocket.jpg" alt="Rocket launch thumbnail">
    <img src="./images/coffee.png" alt="Cup of coffee thumbnail">
    <img src="./images/hubble-deep-field.jpg" alt="Hubble deep field thumbnail">
    <img src="./images/astronaut.png" alt="Astronaut Eileen Collins thumbnail">
  </div>
</wa-scroller>
<style>
  .sc-demo-thumb-row { display:flex; gap:0.75rem; width:max-content; }
  .sc-demo-thumb-row img { width:180px; aspect-ratio:16/9; object-fit:cover; }
</style>
```

## Usage and API notes

This is a real photo thumbnail strip illustrating scroll overflow. The images use the same bundled assets as the carousel and comparison. Prefer MyST `{grid}` for static columns rather than recreating a non-interactive grid as a widget.

Media sources: [Showcase media](../showcase-media.md).
