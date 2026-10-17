---
description: "Static SVG doughnut chart with labeled proportions and a MyST source table."
keywords:
  - MyST
  - data visualization
  - Doughnut Chart
tags:
  - portable-alternative
  - data-viz
  - accessible-documentation
---

# Doughnut Chart: portable MyST alternative

:::{admonition} Portable Alternative (Non-Core)
:class: note

Web Awesome Pro components require a commercial license and are not bundled in this catalog. This page demonstrates portable, accessible alternatives using standard MyST markup and HTML5 semantics.
:::

**Former upstream Pro component:** `<wa-doughnut-chart>`. **Category:** [Portable Alternatives](../portable-alternatives.md) · **Implementation:** MyST/SVG.

Use this documentation recipe without importing Web Awesome Pro code. The former component is named for compatibility and discovery only; the alternative is not API-equivalent.

## Portable example

Use a checked-in static SVG image and a MyST table. The figure requires no custom chart runtime; interactive filtering, tooltips and live recalculation are not provided.

:::{figure} ../../images/portable-charts/doughnut-chart.svg
:alt: Doughnut chart: Compute 50 percent, Storage 30 percent, Network 20 percent.
:label: fig-portable-doughnut-chart

Static SVG example. The table below is the accessible source of the same illustrative data.
:::

:::{table} Doughnut Chart source data
:label: tbl-portable-doughnut-chart

| Service | Share (%) |
| --- | ---: |
| Compute | 50 |
| Storage | 30 |
| Network | 20 |
:::

## Accessibility and compatibility

The SVG has an accessible title and description, but the table contains the precise underlying values and remains usable in text and non-HTML exports. The example data are illustrative, not live operational measurements. No Web Awesome Pro elements, Pro imports or client-side chart libraries are used.

**References:** [MyST specification](https://mystmd.org/spec), [MyST figures](https://mystmd.org/guide/figures), [MyST tables](https://mystmd.org/guide/tables), [Web Awesome upstream reference](https://webawesome.com/docs/components/doughnut-chart/).
