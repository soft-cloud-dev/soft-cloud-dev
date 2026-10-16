# OTP Input `<wa-otp-input>`

Collects a fixed-length verification code.

> “allows a user to enter data that is sent to a server for processing” — [Wikipedia: HTML form](wiki:HTML_form). This quote supplies general domain context, not an API definition.

**Category:** [Forms](../index.md) · **Availability:** Core · **Maturity:** Experimental.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/next/packages/webawesome/src/components/otp-input/otp-input.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/otp-input/).

:::{wa-callout} Integration status
:variant: brand
:appearance: filled

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Live preview

```{anywidget} ../../widgets/webawesome-demo.mjs
{
  "tree": {
    "tag": "wa-otp-input",
    "attrs": {
      "label": "Security code",
      "length": "6"
    },
    "children": []
  }
}
```

## Markdown code snippet

```html
<wa-otp-input label="Security code" length="6"></wa-otp-input>
```

For direct MyST integration, place this trusted markup in a Markdown HTML block or use the corresponding built-in MyST directive/role when supported. 
