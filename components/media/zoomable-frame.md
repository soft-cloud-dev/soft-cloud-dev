# Zoomable Frame `<wa-zoomable-frame>`

Embeds a pan-and-zoom frame.

> “Multimedia is a form of communication that uses a combination of different content forms.” — [Wikipedia: Multimedia](wiki:Multimedia). This quote supplies general domain context, not an API definition.

**Category:** [Media](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/v3.14.0/packages/webawesome/src/components/zoomable-frame/zoomable-frame.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/zoomable-frame/).

:::{note} Integration status

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Live preview

```{anywidget} ../../widgets/webawesome-demo.mjs
{
  "tree": {
    "tag": "wa-zoomable-frame",
    "attrs": {
      "src": "/static/showcase/gallery.html",
      "label": "SoftCloud photo gallery",
      "zoom": "0.75"
    },
    "children": []
  }
}
```

## Markdown code snippet

```html
<wa-zoomable-frame src="/static/showcase/gallery.html" label="SoftCloud photo gallery" zoom="0.75"></wa-zoomable-frame>
```

## Usage and API notes

This zoomable frame loads a same-origin, script-free page containing actual photographs. `label` provides the accessible frame name. When using untrusted destinations, configure `sandbox` and `allow` appropriately.

Media licenses and canonical sources: [Showcase media](../showcase-media.md).
