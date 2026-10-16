# QR Code `<wa-qr-code>`

Generates a QR code for a string or URL.

> “Multimedia is a form of communication that uses a combination of different content forms.” — [Wikipedia: Multimedia](wiki:Multimedia). This quote supplies general domain context, not an API definition.

**Category:** [Media](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/next/packages/webawesome/src/components/qr-code/qr-code.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/qr-code/).

:::{wa-callout} Integration status
:variant: brand
:appearance: filled

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Live preview

```{anywidget} ../../widgets/webawesome-demo.mjs
{
  "tree": {
    "tag": "wa-qr-code",
    "attrs": {
      "value": "https://my.softcloud.dev/",
      "size": "160",
      "label": "SoftCloud"
    },
    "children": []
  }
}
```

## Markdown code snippet

```html
<wa-qr-code value="https://my.softcloud.dev/" size="160" label="SoftCloud"></wa-qr-code>
```

For direct MyST integration, place this trusted markup in a Markdown HTML block or use the corresponding built-in MyST directive/role when supported. 
