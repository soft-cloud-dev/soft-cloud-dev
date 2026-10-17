# Option `<wa-option>`

Represents one value and visible label in a Select.

> “allows a user to enter data that is sent to a server for processing” — [Wikipedia: HTML form](wiki:HTML_form). This quote supplies general domain context, not an API definition.

**Category:** [Forms](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/v3.14.0/packages/webawesome/src/components/option/option.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/option/).

:::{wa-callout} Integration status
:variant: brand
:appearance: filled

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Atomic composition

Reuse: [Select](../forms/select.md). The full nested markup below remains independently usable.

## Live preview

```{anywidget} ../../widgets/webawesome-demo.mjs
{
  "tree": {
    "tag": "wa-select",
    "attrs": {
      "label": "Platform",
      "value": "linux"
    },
    "children": [
      {
        "tag": "wa-option",
        "attrs": {
          "value": "linux"
        },
        "children": [
          "Linux"
        ]
      },
      {
        "tag": "wa-option",
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
<wa-select label="Platform" value="linux">
  <wa-option value="linux">Linux</wa-option>
  <wa-option value="freebsd">FreeBSD</wa-option>
</wa-select>
```

For direct MyST integration, place this trusted markup in a Markdown HTML block or use the corresponding built-in MyST directive/role when supported. 
