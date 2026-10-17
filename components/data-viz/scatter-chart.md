---
description: "Static SVG scatter chart with explicitly tabulated x/y observations."
keywords:
  - MyST
  - data visualization
  - Scatter Chart
tags:
  - portable-alternative
  - data-viz
  - accessible-documentation
---

# Scatter Chart: portable MyST alternative

:::{admonition} Portable Alternative (Non-Core)
:class: note

Web Awesome Pro components require a commercial license and are not bundled in this catalog. This page demonstrates portable, accessible alternatives using standard MyST markup and HTML5 semantics.
:::

**Former upstream Pro component:** `<wa-scatter-chart>`. **Category:** [Portable Alternatives](../portable-alternatives.md) · **Implementation:** MyST/SVG.

Use this documentation recipe without importing Web Awesome Pro code. The former component is named for compatibility and discovery only; the alternative is not API-equivalent.

## Portable example

Use a checked-in static SVG image and a MyST table. The figure requires no custom chart runtime; interactive filtering, tooltips and live recalculation are not provided.

:::{figure} ../../images/portable-charts/scatter-chart.svg
:alt: Four points: A (1,2), B (2,3), C (3,2), D (4,5).
:label: fig-portable-scatter-chart

Static SVG example. The table below is the accessible source of the same illustrative data.
:::

:::{table} Scatter Chart source data
:label: tbl-portable-scatter-chart

| Observation | X | Y |
| --- | ---: | ---: |
| A | 1 | 2 |
| B | 2 | 3 |
| C | 3 | 2 |
| D | 4 | 5 |
:::

## Accessibility and compatibility

The SVG has an accessible title and description, but the table contains the precise underlying values and remains usable in text and non-HTML exports. The example data are illustrative, not live operational measurements. No Web Awesome Pro elements, Pro imports or client-side chart libraries are used.

**References:** [MyST specification](https://mystmd.org/spec), [MyST figures](https://mystmd.org/guide/figures), [MyST tables](https://mystmd.org/guide/tables), [Web Awesome upstream reference](https://webawesome.com/docs/components/scatter-chart/).
