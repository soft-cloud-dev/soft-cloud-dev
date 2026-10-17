# Step `<wa-step>`

Represents one stage inside a stepper.

> “the process of navigating a network of information resources” — [Wikipedia: Web navigation](wiki:Web_navigation). This quote supplies general domain context, not an API definition.

**Category:** [Navigation](../index.md) · **Availability:** Core · **Maturity:** Experimental.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/v3.14.0/packages/webawesome/src/components/step/step.ts#L1-L24) (MyST GitHub transformer); [official component directory](https://webawesome.com/docs/components) (not listed).

:::{warning} Integration status

Source-only experimental component: not currently listed in the public 3.14 directory; API and runtime availability are unverified.
:::

## Atomic composition

Reuse: [Stepper](../navigation/stepper.md). The full nested markup below remains independently usable.

## Live preview

Live preview intentionally unavailable: the component is not documented in the public 3.14 directory.

## Markdown code snippet

```html
<wa-stepper active="validate" label="Provisioning progress">
  <wa-step name="connect" completed>Connect</wa-step>
  <wa-step name="validate" active>Validate</wa-step>
</wa-stepper>
```

Use native MyST for documentation layout; interactive Web Awesome previews remain hosted through the existing `{anywidget}` integration when available. 
