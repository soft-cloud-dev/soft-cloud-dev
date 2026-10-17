# Card `<wa-card>`

Groups media, metadata, and actions into one surface.

> “the space where interactions between humans and machines occur” — [Wikipedia: User interface](wiki:User_interface). This quote supplies general domain context, not an API definition.

**Category:** [Layout](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/v3.14.0/packages/webawesome/src/components/card/card.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/card/).

:::{note} Integration status

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Live preview

### Static reference (works without JavaScript)

![Coffee cup photograph](../../assets/static/showcase/coffee.png)

The image and copyable HTML example below remain available if the interactive widget fails to initialize. The widget adds component behavior; it does not provide the only readable content.

```{anywidget} ../../widgets/webawesome-demo.mjs
{
  "tree": [
    {
      "tag": "wa-card",
      "attrs": {
        "appearance": "outlined"
      },
      "children": [
        {
          "tag": "img",
          "attrs": {
            "src": "showcase:coffee.png",
            "alt": "A white cup of coffee on a wooden table",
            "slot": "media",
            "loading": "lazy"
          },
          "children": []
        },
        {
          "tag": "strong",
          "attrs": {
            "slot": "header"
          },
          "children": [
            "Coffee sample"
          ]
        },
        {
          "tag": "p",
          "attrs": {},
          "children": [
            "A real bundled, CC0 photograph."
          ]
        },
        {
          "tag": "wa-button",
          "attrs": {
            "slot": "footer-actions",
            "appearance": "plain",
            "href": "/components/showcase-media"
          },
          "children": [
            "Media credits"
          ]
        }
      ]
    },
    {
      "tag": "wa-card",
      "attrs": {
        "appearance": "outlined"
      },
      "children": [
        {
          "tag": "video",
          "attrs": {
            "slot": "media",
            "controls": "",
            "preload": "metadata",
            "aria-label": "Short CC0 video of a flower"
          },
          "children": [
            {
              "tag": "source",
              "attrs": {
                "src": "https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4",
                "type": "video/mp4"
              },
              "children": []
            }
          ]
        },
        {
          "tag": "strong",
          "attrs": {
            "slot": "header"
          },
          "children": [
            "Motion media"
          ]
        },
        {
          "tag": "p",
          "attrs": {},
          "children": [
            "A CC0 video with browser-native playback controls."
          ]
        }
      ]
    }
  ]
}
```

## Markdown code snippet

```html
<wa-card appearance="outlined">
  <img slot="media" src="./images/coffee.png" alt="White cup of coffee on wood" loading="lazy">
  <strong slot="header">Coffee sample</strong>
  <p>A real bundled, CC0 photograph.</p>
  <wa-button slot="footer-actions" appearance="plain" href="/components/showcase-media">Media credits</wa-button>
</wa-card>

<wa-card appearance="outlined">
  <video slot="media" controls preload="metadata" aria-label="Short CC0 video of a flower">
    <source src="https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4" type="video/mp4">
  </video>
  <strong slot="header">Motion media</strong>
  <p>A CC0 video with browser-native playback controls.</p>
</wa-card>
```

## Usage and API notes

The photo is bundled locally; the short CC0 video is streamed from MDN and needs a network connection. `<wa-card>` supports media, headers, and action slots. Prefer the portable MyST `{card}` directive for ordinary documentation content; choose `<wa-card>` when Web Awesome slot semantics are needed. No Pro runtime is required for native HTML video.

Media sources: [Showcase media](../showcase-media.md).
