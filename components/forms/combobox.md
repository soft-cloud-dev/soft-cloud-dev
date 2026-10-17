---
description: "Accessible text suggestions using an HTML5 datalist, with MyST documentation and validation guidance."
keywords:
  - MyST
  - forms
  - Combobox
tags:
  - portable-alternative
  - forms
  - accessible-documentation
---

# Combobox: portable MyST alternative

:::{admonition} Portable Alternative (Non-Core)
:class: note

Web Awesome Pro components require a commercial license and are not bundled in this catalog. This page demonstrates portable, accessible alternatives using standard MyST markup and HTML5 semantics.
:::

**Former upstream Pro component:** `<wa-combobox>`. **Category:** [Portable Alternatives](../portable-alternatives.md) · **Implementation:** MyST + HTML5.

Use this documentation recipe without importing Web Awesome Pro code. The former component is named for compatibility and discovery only; the alternative is not API-equivalent.

## Portable example

The HTML5 `datalist` element supplies browser-managed suggestions without JavaScript. It is not a feature-equivalent replacement for a searchable Web Awesome Pro combobox: free-text input remains possible and screen-reader support varies.

:::{table} Combobox example values
:label: tbl-portable-combobox

| Suggested value | Meaning |
| --- | --- |
| Development | Local integration |
| Staging | Preproduction validation |
| Production | Live workloads |
:::

## Copyable HTML5 pattern

```html
<label for="environment">Deployment environment</label>
<p id="environment-help">Choose a suggestion or enter another environment.</p>
<input id="environment" name="environment" list="environments"
       aria-describedby="environment-help" autocomplete="off">
<datalist id="environments">
  <option value="Development"></option>
  <option value="Staging"></option>
  <option value="Production"></option>
</datalist>
```

The HTML markup above is a code sample, not an active MyST form or a configured application endpoint.

## Accessibility and compatibility

Validate allowed values at the receiving application; `<datalist>` does not restrict input to listed choices. For richer keyboard, filtering, and announcement behavior, select a separate accessible client-side control.

**References:** [MyST specification](https://mystmd.org/spec), [MyST tables](https://mystmd.org/guide/tables), [Web Awesome upstream reference](https://webawesome.com/docs/components/combobox/).
