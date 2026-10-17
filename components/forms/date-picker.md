---
description: "Provide a platform-native date picker using an HTML5 date field alongside MyST fallback guidance."
keywords:
  - MyST
  - forms
  - Date Picker
tags:
  - portable-alternative
  - forms
  - accessible-documentation
---

# Date Picker: portable MyST alternative

:::{admonition} Portable Alternative (Non-Core)
:class: note

Web Awesome Pro components require a commercial license and are not bundled in this catalog. This page demonstrates portable, accessible alternatives using standard MyST markup and HTML5 semantics.
:::

**Former upstream Pro component:** `<wa-date-picker>`. **Category:** [Portable Alternatives](../portable-alternatives.md) · **Implementation:** MyST + HTML5.

Use this documentation recipe without importing Web Awesome Pro code. The former component is named for compatibility and discovery only; the alternative is not API-equivalent.

## Portable example

Browsers that support `<input type="date">` provide a platform date-selection UI. The exact calendar popover is not standardized visually; this is not a custom calendar implementation.

:::{table} Date Picker example values
:label: tbl-portable-date-picker

| Date | Meaning |
| --- | --- |
| 2026-10-17 | Earliest permitted selection |
| 2026-10-31 | Illustrative deadline |
:::

## Copyable HTML5 pattern

```html
<label for="review-deadline">Review deadline</label>
<input id="review-deadline" name="review-deadline"
       type="date" min="2026-10-17" required>
```

The HTML markup above is a code sample, not an active MyST form or a configured application endpoint.

## Accessibility and compatibility

The browser may expose a text-based fallback; do not promise a calendar popover on every platform. Apply server-side date constraints and communicate the accepted date format.

**References:** [MyST specification](https://mystmd.org/spec), [MyST tables](https://mystmd.org/guide/tables), [Web Awesome upstream reference](https://webawesome.com/docs/components/date-picker/).
