---
description: "Static SVG radar diagram with per-axis service health scores and a table."
keywords:
  - MyST
  - data visualization
  - Radar Chart
tags:
  - portable-alternative
  - data-viz
  - accessible-documentation
---

# Radar Chart: portable MyST alternative

:::{admonition} Portable Alternative (Non-Core)
:class: note

Web Awesome Pro components require a commercial license and are not bundled in this catalog. This page demonstrates portable, accessible alternatives using standard MyST markup and HTML5 semantics.
:::

**Former upstream Pro component:** `<wa-radar-chart>`. **Category:** [Portable Alternatives](../portable-alternatives.md) · **Implementation:** MyST/SVG.

Use this documentation recipe without importing Web Awesome Pro code. The former component is named for compatibility and discovery only; the alternative is not API-equivalent.

## Portable example

Use a checked-in static SVG image and a MyST table. The figure requires no custom chart runtime; interactive filtering, tooltips and live recalculation are not provided.

:::{figure} ../../images/portable-charts/radar-chart.svg
:alt: Radar polygon for availability 90, latency score 70, reliability 85, capacity 60.
:label: fig-portable-radar-chart

Static SVG example. The table below is the accessible source of the same illustrative data.
:::

:::{table} Radar Chart source data
:label: tbl-portable-radar-chart

| Dimension | Score (0-100) |
| --- | ---: |
| Availability | 90 |
| Latency score | 70 |
| Reliability | 85 |
| Capacity | 60 |
:::

## Accessibility and compatibility

The SVG has an accessible title and description, but the table contains the precise underlying values and remains usable in text and non-HTML exports. The example data are illustrative, not live operational measurements. No Web Awesome Pro elements, Pro imports or client-side chart libraries are used.

**References:** [MyST specification](https://mystmd.org/spec), [MyST figures](https://mystmd.org/guide/figures), [MyST tables](https://mystmd.org/guide/tables), [Web Awesome upstream reference](https://webawesome.com/docs/components/radar-chart/).
