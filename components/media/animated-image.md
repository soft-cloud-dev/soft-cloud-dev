# Animated Image `<wa-animated-image>`

Offers playback controls for animated imagery.

> “Multimedia is a form of communication that uses a combination of different content forms.” — [Wikipedia: Multimedia](wiki:Multimedia). This quote supplies general domain context, not an API definition.

**Category:** [Media](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/v3.14.0/packages/webawesome/src/components/animated-image/animated-image.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/animated-image/).

:::{note} Integration status

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Live preview

### Static reference (works without JavaScript)

![Animated shoe demonstration](https://shoelace.style/assets/images/walk.gif)

The image and copyable HTML example below remain available if the interactive widget fails to initialize. The widget adds component behavior; it does not provide the only readable content.

```{anywidget} ../../widgets/webawesome-demo.mjs
{
  "tree": {
    "tag": "wa-animated-image",
    "attrs": {
      "src": "https://shoelace.style/assets/images/walk.gif",
      "alt": "Animated image of untied shoes walking on pavement"
    },
    "children": []
  }
}
```

## Markdown code snippet

```html
<wa-animated-image src="https://shoelace.style/assets/images/walk.gif" alt="Animated image of untied shoes walking on pavement"></wa-animated-image>
```

## Usage and API notes

Uses the real animated GIF from Web Awesome's official example. Unlike the bundled photographs, this demo remains externally hosted and needs network access; Web Awesome's canvas-based pause/freeze may be subject to cross-origin restrictions. The image must provide meaningful alternative text.

Media licenses and canonical sources: [Showcase media](../showcase-media.md).
