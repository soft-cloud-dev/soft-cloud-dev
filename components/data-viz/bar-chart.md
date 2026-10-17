---
description: "Static SVG bar chart with a MyST figure and accessible weekly request table."
keywords:
  - MyST
  - data visualization
  - Bar Chart
tags:
  - portable-alternative
  - data-viz
  - accessible-documentation
---

# Bar Chart: portable MyST alternative

:::{admonition} Portable Alternative (Non-Core)
:class: note

Web Awesome Pro components require a commercial license and are not bundled in this catalog. This page demonstrates portable, accessible alternatives using standard MyST markup and HTML5 semantics.
:::

**Former upstream Pro component:** `<wa-bar-chart>`. **Category:** [Portable Alternatives](../portable-alternatives.md) · **Implementation:** MyST/SVG.

Use this documentation recipe without importing Web Awesome Pro code. The former component is named for compatibility and discovery only; the alternative is not API-equivalent.

## Portable example

Use a checked-in static SVG image and a MyST table. The figure requires no custom chart runtime; interactive filtering, tooltips and live recalculation are not provided.

:::{figure} ../../images/portable-charts/bar-chart.svg
:alt: Bars for weekly requests: Week 1 42, Week 2 57, Week 3 51.
:label: fig-portable-bar-chart

Static SVG example. The table below is the accessible source of the same illustrative data.
:::

:::{table} Bar Chart source data
:label: tbl-portable-bar-chart

| Period | Requests |
| --- | ---: |
| Week 1 | 42 |
| Week 2 | 57 |
| Week 3 | 51 |
:::

## Accessibility and compatibility

The SVG has an accessible title and description, but the table contains the precise underlying values and remains usable in text and non-HTML exports. The example data are illustrative, not live operational measurements. No Web Awesome Pro elements, Pro imports or client-side chart libraries are used.

**References:** [MyST specification](https://mystmd.org/spec), [MyST figures](https://mystmd.org/guide/figures), [MyST tables](https://mystmd.org/guide/tables), [Web Awesome upstream reference](https://webawesome.com/docs/components/bar-chart/).
