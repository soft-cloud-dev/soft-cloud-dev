# Web Awesome SSR Fixture

This document exercises all Web Awesome directives and roles before SSR postprocessing.

```{wa-callout}
:variant: brand
:appearance: soft
:icon: info-circle
:title: Important Overview

This is an informational callout with a [documentation link](https://my.softcloud.dev/docs) and **bold** text.
```

```{wa-card} Card Header Title
:appearance: elevated
:image: /images/logo.svg
:image_alt: SoftCloud Logo

### Nested Heading in Card

Card body containing a list:
- First item with special chars: `<test>` & "quotes"
- Second item with a [nested link](https://my.softcloud.dev/about)

<!-- HTML comment inside card body -->
```

```{wa-button}
:variant: primary
:appearance: filled
:size: medium
:href: https://my.softcloud.dev/get-started
:target: _blank

Launch Console {fa}`brands github`
```

Inline icon test: Here is a rocket {icon}`classic solid rocket` and a terminal icon {fa}`solid terminal`.
