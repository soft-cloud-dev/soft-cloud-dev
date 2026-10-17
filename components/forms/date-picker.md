# Date Picker: MyST alternative

**Category:** [forms](../index.md) · **Implementation:** MyST-first · **Former reference:** Web Awesome Pro `<wa-date-picker>`.

MyST is a publication format, not a drop-in interactive form or charting runtime. These examples provide accessible, portable documentation alternatives without shipping Web Awesome Pro.

## Portable example

Use a MyST table for reference dates and constraints. An actual date-entry or date-picker interaction requires an application form.

| Field | Example | Constraint |
| --- | --- | --- |
| Start date | 2026-10-17 | ISO 8601 date |
| End date | 2026-10-31 | Not earlier than start date |

## Accessibility and compatibility

Preserve labels, units, descriptions, and a readable non-JavaScript representation. This page intentionally contains no Pro custom elements, Pro imports, or Pro API claims. See the [MyST specification](https://mystmd.org/spec) for supported markup and AST nodes.
