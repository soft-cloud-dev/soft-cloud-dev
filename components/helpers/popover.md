# Popover `<wa-popover>`

Displays contextual floating content anchored to a trigger.

> “a sequence or set of instructions in a programming language” — [Wikipedia: Computer program](wiki:Computer_program). This quote supplies general domain context, not an API definition.

**Category:** [Helpers](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/next/packages/webawesome/src/components/popover/popover.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/popover/).

:::{wa-callout} Integration status
:variant: brand
:appearance: filled

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Atomic composition

Reuse: [Button](../actions/button.md). The full nested markup below remains independently usable.

## Live preview

Live preview intentionally unavailable: this control requires external media, changes the entire page, or has only background behavior.

## Markdown code snippet

```html
<wa-button id="popover-anchor">More context</wa-button>

<wa-popover for="popover-anchor">
  <p>Contextual help</p>
</wa-popover>
```

For direct MyST integration, place this trusted markup in a Markdown HTML block or use the corresponding built-in MyST directive/role when supported. 
