# Toast Item `<wa-toast-item>`

Represents one notification in a toast region.

> “Feedback is also a useful design principle for designing user interfaces.” — [Wikipedia: Feedback](wiki:Feedback). This quote supplies general domain context, not an API definition.

**Category:** [Feedback](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/next/packages/webawesome/src/components/toast-item/toast-item.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/toast-item/).

:::{wa-callout} Integration status
:variant: brand
:appearance: filled

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Atomic composition

Reuse: [Toast](../feedback/toast.md). The full nested markup below remains independently usable.

## Live preview

Live preview intentionally unavailable: this control requires external media, changes the entire page, or has only background behavior.

## Markdown code snippet

```html
<wa-toast>
  <wa-toast-item variant="success">Deployment queued</wa-toast-item>
</wa-toast>
```

For direct MyST integration, place this trusted markup in a Markdown HTML block or use the corresponding built-in MyST directive/role when supported. 
