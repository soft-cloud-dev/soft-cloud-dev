# Avatar `<wa-avatar>`

Shows a compact representation of an entity or user.

> “Multimedia is a form of communication that uses a combination of different content forms.” — [Wikipedia: Multimedia](wiki:Multimedia). This quote supplies general domain context, not an API definition.

**Category:** [Media](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/v3.14.0/packages/webawesome/src/components/avatar/avatar.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/avatar/).

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
      "image": "/static/showcase/astronaut.png",
      "label": "NASA portrait of astronaut Eileen Collins",
      "shape": "circle",
      "loading": "lazy"
    },
    "children": []
  }
}
```

## Markdown code snippet

```html
<wa-avatar image="/static/showcase/astronaut.png" label="NASA portrait of astronaut Eileen Collins" shape="circle" loading="lazy"></wa-avatar>
```

## Usage and API notes

The image is an actual NASA public-domain portrait, not initials. Use `image` and a meaningful accessible `label`. `shape` accepts `circle`, `rounded`, or `square`.

Media licenses and canonical sources: [Showcase media](../showcase-media.md).
