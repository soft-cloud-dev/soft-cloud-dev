# Markdown `<wa-markdown>`

Renders a fragment of Markdown client-side.

> “Multimedia is a form of communication that uses a combination of different content forms.” — [Wikipedia: Multimedia](wiki:Multimedia). This quote supplies general domain context, not an API definition.

**Category:** [Media](../index.md) · **Availability:** Core · **Maturity:** Experimental.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/next/packages/webawesome/src/components/markdown/markdown.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/markdown/).

:::{wa-callout} Integration status
:variant: brand
:appearance: filled

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Live preview

Reference-only: rendering requires a `script[type="text/markdown"]` child and runs exclusively client-side. Executable script children are intentionally disallowed in the generic demo renderer to keep previews safe.

## Markdown code snippet

```html
<wa-markdown>
  <script type="text/markdown">
    **Bold** and `code` from Markdown.
  </script>
</wa-markdown>
```

For direct MyST integration, place this trusted markup in a Markdown HTML block or use the corresponding built-in MyST directive/role when supported. 
