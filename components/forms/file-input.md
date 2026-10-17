---
description: "Describe a browser-native file upload input using HTML5 semantics and a MyST requirements note."
keywords:
  - MyST
  - forms
  - File Input
tags:
  - portable-alternative
  - forms
  - accessible-documentation
---

# File Input: portable MyST alternative

:::{admonition} Portable Alternative (Non-Core)
:class: note

Web Awesome Pro components require a commercial license and are not bundled in this catalog. This page demonstrates portable, accessible alternatives using standard MyST markup and HTML5 semantics.
:::

**Former upstream Pro component:** `<wa-file-input>`. **Category:** [Portable Alternatives](../portable-alternatives.md) · **Implementation:** MyST + HTML5.

Use this documentation recipe without importing Web Awesome Pro code. The former component is named for compatibility and discovery only; the alternative is not API-equivalent.

## Portable example

The HTML5 file input selects files without JavaScript. Upload handling requires a receiving service and is not supplied by MyST; the example does not submit or retain files.

:::{table} File Input example values
:label: tbl-portable-file-input

| Accepted type | Suggested maximum | Application obligation |
| --- | ---: | --- |
| PDF | 5 MB | Validate content, MIME type and size |
| PNG | 5 MB | Validate content, MIME type and size |
:::

## Copyable HTML5 pattern

```html
<label for="supporting-document">Supporting document</label>
<p id="file-rules">Choose a PDF or PNG; maximum allowed size: 5 MB.</p>
<input id="supporting-document" name="supporting-document" type="file"
       accept=".pdf,.png,application/pdf,image/png"
       aria-describedby="file-rules">
```

The HTML markup above is a code sample, not an active MyST form or a configured application endpoint.

## Accessibility and compatibility

`accept` is a chooser hint, not security enforcement. Server-side validation, scanning and upload storage are outside the MyST publishing runtime.

**References:** [MyST specification](https://mystmd.org/spec), [MyST tables](https://mystmd.org/guide/tables), [Web Awesome upstream reference](https://webawesome.com/docs/components/file-input/).
