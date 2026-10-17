---
description: "Compact static SVG sparkline with source values in a MyST table."
keywords:
  - MyST
  - data visualization
  - Sparkline
tags:
  - portable-alternative
  - data-viz
  - accessible-documentation
---

# Sparkline: portable MyST alternative

:::{admonition} Portable Alternative (Non-Core)
:class: note

Web Awesome Pro components require a commercial license and are not bundled in this catalog. This page demonstrates portable, accessible alternatives using standard MyST markup and HTML5 semantics.
:::

**Former upstream Pro component:** `<wa-sparkline>`. **Category:** [Portable Alternatives](../portable-alternatives.md) · **Implementation:** MyST/SVG.

Use this documentation recipe without importing Web Awesome Pro code. The former component is named for compatibility and discovery only; the alternative is not API-equivalent.

## Portable example

Use a checked-in static SVG image and a MyST table. The figure requires no custom chart runtime; interactive filtering, tooltips and live recalculation are not provided.

:::{figure} ../../images/portable-charts/sparkline.svg
:alt: Seven-point trend: 8, 12, 10, 14, 16, 13 and 18 requests.
:label: fig-portable-sparkline

Static SVG example. The table below is the accessible source of the same illustrative data.
:::

:::{table} Sparkline source data
:label: tbl-portable-sparkline

| Sample | Requests |
| --- | ---: |
| 1 | 8 |
| 2 | 12 |
| 3 | 10 |
| 4 | 14 |
| 5 | 16 |
| 6 | 13 |
| 7 | 18 |
:::

## Accessibility and compatibility

The SVG has an accessible title and description, but the table contains the precise underlying values and remains usable in text and non-HTML exports. The example data are illustrative, not live operational measurements. No Web Awesome Pro elements, Pro imports or client-side chart libraries are used.

**References:** [MyST specification](https://mystmd.org/spec), [MyST figures](https://mystmd.org/guide/figures), [MyST tables](https://mystmd.org/guide/tables), [Web Awesome upstream reference](https://webawesome.com/docs/components/sparkline/).
