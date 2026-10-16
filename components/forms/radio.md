# Radio `<wa-radio>`

Represents one mutually exclusive choice in a group.

> “allows a user to enter data that is sent to a server for processing” — [Wikipedia: HTML form](wiki:HTML_form). This quote supplies general domain context, not an API definition.

**Category:** [Forms](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/v3.14.0/packages/webawesome/src/components/radio/radio.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/radio/).

:::{wa-callout} Integration status
:variant: brand
:appearance: filled

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Atomic composition

Reuse: [Radio Group](../forms/radio-group.md). The full nested markup below remains independently usable.

## Live preview

```{anywidget} ../../widgets/webawesome-demo.mjs
{
  "tree": {
    "tag": "wa-radio-group",
    "attrs": {
      "label": "System",
      "value": "linux"
    },
    "children": [
      {
        "tag": "wa-radio",
        "attrs": {
          "value": "linux"
        },
        "children": [
          "Linux"
        ]
      },
      {
        "tag": "wa-radio",
        "attrs": {
          "value": "freebsd"
        },
        "children": [
          "FreeBSD"
        ]
      }
    ]
  }
}
```

## Markdown code snippet

```html
<wa-radio-group label="System" value="linux">
  <wa-radio value="linux">Linux</wa-radio>
  <wa-radio value="freebsd">FreeBSD</wa-radio>
</wa-radio-group>
```

For direct MyST integration, place this trusted markup in a Markdown HTML block or use the corresponding built-in MyST directive/role when supported. 
