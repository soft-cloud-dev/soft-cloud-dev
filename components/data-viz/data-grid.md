---
description: "Accessible sortable-data-grid alternative presented as a static MyST table."
keywords:
  - MyST
  - data visualization
  - Data Grid
tags:
  - portable-alternative
  - data-viz
  - accessible-documentation
---

# Data Grid: portable MyST alternative

:::{admonition} Portable Alternative (Non-Core)
:class: note

Web Awesome Pro components require a commercial license and are not bundled in this catalog. This page demonstrates portable, accessible alternatives using standard MyST markup and HTML5 semantics.
:::

**Former upstream Pro component:** `<wa-data-grid>`. **Category:** [Portable Alternatives](../portable-alternatives.md) · **Implementation:** MyST/SVG.

Use this documentation recipe without importing Web Awesome Pro code. The former component is named for compatibility and discovery only; the alternative is not API-equivalent.

## Portable example

A MyST table provides a readable, printable data grid without JavaScript. Virtualization, editing, sorting and filtering require a separate interactive application.

:::{table} Data Grid source data
:label: tbl-portable-data-grid

| Region | Requests | Status |
| --- | ---: | --- |
| Europe | 120 | Healthy |
| North America | 95 | Healthy |
| Asia | 82 | Monitoring |
:::

## Accessibility and compatibility

Use explicit column headers, stable row order and textual status. The example data are illustrative, not live operational measurements. No Web Awesome Pro elements, Pro imports or client-side chart libraries are used.

**References:** [MyST specification](https://mystmd.org/spec), [MyST figures](https://mystmd.org/guide/figures), [MyST tables](https://mystmd.org/guide/tables), [Web Awesome upstream reference](https://webawesome.com/docs/components/data-grid/).
