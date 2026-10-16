# Popup `<wa-popup>`

Positions a floating element next to an anchor.

> “a sequence or set of instructions in a programming language” — [Wikipedia: Computer program](wiki:Computer_program). This quote supplies general domain context, not an API definition.

**Category:** [Helpers](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/next/packages/webawesome/src/components/popup/popup.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/popup/).

:::{wa-callout} Integration status
:variant: brand
:appearance: soft

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Live preview

Live preview intentionally unavailable: this control requires external media, changes the entire page, or has only background behavior.

## Markdown code snippet

```html
<span id="popup-anchor">Anchor</span>

<wa-popup anchor="popup-anchor" active="">Floating content</wa-popup>
```

For direct MyST integration, place this trusted markup in a Markdown HTML block or use the corresponding built-in MyST directive/role when supported. 
