# Combobox `<wa-combobox>`

Provides searchable choices with free-form input.

> “allows a user to enter data that is sent to a server for processing” — [Wikipedia: HTML form](wiki:HTML_form). This quote supplies general domain context, not an API definition.

**Category:** [Forms](../index.md) · **Availability:** Pro · **Maturity:** Stable.

**Source:** [SoftCloud documentation Markdown](https://github.com/soft-cloud-dev/soft-cloud-dev/blob/main/components/forms/combobox.md#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/combobox/).

:::{warning} Integration status

Web Awesome Pro only: not installed in the existing Core runtime. No interactive preview or licensed code is distributed.
:::

## Atomic composition

Reuse: [Option](../forms/option.md). The full nested markup below remains independently usable.

## Live preview

Live preview intentionally unavailable: the Pro runtime is not licensed for this deployment.

## Markdown code snippet

```html
<wa-combobox label="Region">
  <wa-option value="eu">Europe</wa-option>
  <wa-option value="us">United States</wa-option>
</wa-combobox>
```

Use native MyST for documentation layout; interactive Web Awesome previews remain hosted through the existing `{anywidget}` integration when available. Chart/grid data and configuration must additionally be supplied through documented Pro JavaScript properties.
