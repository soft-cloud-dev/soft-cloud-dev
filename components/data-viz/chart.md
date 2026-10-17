# Chart: MyST alternative

**Category:** [data-viz](../index.md) · **Implementation:** MyST-first · **Former reference:** Web Awesome Pro `<wa-chart>`.

MyST is a publication format, not a drop-in interactive form or charting runtime. These examples provide accessible, portable documentation alternatives without shipping Web Awesome Pro.

## Portable example

Use a MyST table as the canonical accessible representation of quantitative values. For a static chart, generate an image in the publication build and include it with the MyST `{figure}` directive, including alt text and a source table. The MyST specification does not supply an interactive equivalent of this chart type.

| Period | Requests |
| --- | ---: |
| Week 1 | 42 |
| Week 2 | 57 |
| Week 3 | 51 |

````myst
:::{figure} ./figures/chart.svg
:alt: Chart visualizing weekly request counts

Chart based on the table above. Generate this file during the build before enabling the figure.
:::
````

## Accessibility and compatibility

Preserve labels, units, descriptions, and a readable non-JavaScript representation. This page intentionally contains no Pro custom elements, Pro imports, or Pro API claims. See the [MyST specification](https://mystmd.org/spec) for supported markup and AST nodes.
