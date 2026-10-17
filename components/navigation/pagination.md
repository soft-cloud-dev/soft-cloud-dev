# Pagination `<wa-pagination>`

Moves among numbered pages of results.

> “the process of navigating a network of information resources” — [Wikipedia: Web navigation](wiki:Web_navigation). This quote supplies general domain context, not an API definition.

**Category:** [Navigation](../index.md) · **Availability:** Core · **Maturity:** Experimental.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/v3.14.0/packages/webawesome/src/components/pagination/pagination.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/pagination/).

:::{note} Integration status

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Live preview

```{anywidget} ../../widgets/webawesome-demo.mjs
{
  "tree": {
    "tag": "wa-pagination",
    "attrs": {
      "total": "237",
      "page-size": "10",
      "page": "3",
      "label": "Results pages"
    },
    "children": []
  }
}
```

## Markdown code snippet

```html
<wa-pagination total="237" page-size="10" page="3" label="Results pages"></wa-pagination>
```

Use native MyST for documentation layout; interactive Web Awesome previews remain hosted through the existing `{anywidget}` integration when available. 
