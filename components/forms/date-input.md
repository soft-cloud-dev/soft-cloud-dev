---
description: "Document date entry with the native HTML5 date input and a portable MyST constraint table."
keywords:
  - MyST
  - forms
  - Date Input
tags:
  - portable-alternative
  - forms
  - accessible-documentation
---

# Date Input: portable MyST alternative

:::{admonition} Portable Alternative (Non-Core)
:class: note

Web Awesome Pro components require a commercial license and are not bundled in this catalog. This page demonstrates portable, accessible alternatives using standard MyST markup and HTML5 semantics.
:::

**Former upstream Pro component:** `<wa-date-input>`. **Category:** [Portable Alternatives](../portable-alternatives.md) · **Implementation:** MyST + HTML5.

Use this documentation recipe without importing Web Awesome Pro code. The former component is named for compatibility and discovery only; the alternative is not API-equivalent.

## Portable example

Use `<input type="date">` for browser-native date entry. Its submitted value uses the ISO `YYYY-MM-DD` format; the visible picker varies by browser and locale.

:::{table} Date Input example values
:label: tbl-portable-date-input

| Field | Example | Constraint |
| --- | --- | --- |
| Deployment date | 2026-10-17 | Between 2026-01-01 and 2027-12-31 |
| Submitted format | 2026-10-17 | ISO 8601 calendar date |
:::

## Copyable HTML5 pattern

```html
<label for="deployment-date">Deployment date</label>
<input id="deployment-date" name="deployment-date" type="date"
       min="2026-01-01" max="2027-12-31" required>
```

The HTML markup above is a code sample, not an active MyST form or a configured application endpoint.

## Accessibility and compatibility

Provide a visible label and validate dates server-side. A date input is an application control, while the MyST table remains readable in non-HTML exports.

**References:** [MyST specification](https://mystmd.org/spec), [MyST tables](https://mystmd.org/guide/tables), [Web Awesome upstream reference](https://webawesome.com/docs/components/date-input/).
