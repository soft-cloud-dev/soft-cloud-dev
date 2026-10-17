---
description: "Use standard HTML5 video with captions and a MyST transcript fallback instead of Web Awesome Pro video."
keywords:
  - MyST
  - media
  - Video
tags:
  - portable-alternative
  - media
  - accessible-documentation
---

# Video: portable MyST alternative

:::{admonition} Portable Alternative (Non-Core)
:class: note

Web Awesome Pro components require a commercial license and are not bundled in this catalog. This page demonstrates portable, accessible alternatives using standard MyST markup and HTML5 semantics.
:::

**Former upstream Pro component:** `<wa-video>`. **Category:** [Portable Alternatives](../portable-alternatives.md) · **Implementation:** MyST + HTML5.

Use this documentation recipe without importing Web Awesome Pro code. The former component is named for compatibility and discovery only; the alternative is not API-equivalent.

## Portable example

For HTML output, use native `<video controls>` and a semantic `<track kind="captions">`. MyST also supports publishing a video as a figure when the media is intentionally included in the project, but this recipe keeps the remote MDN demo as an explicit external exception.

## Copyable HTML5 pattern

```html
<video controls preload="metadata" aria-label="Flower opening time-lapse">
  <source src="https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4"
          type="video/mp4">
  <track kind="captions" src="CAPTIONS_URL" srclang="en" label="English">
  Your browser does not support HTML5 video.
</video>
```

**Caption asset contract:** `CAPTIONS_URL` is a required substitution for an application-hosted, accurate WebVTT file. It is intentionally not a link in the published page. The MDN clip is external and may be unavailable offline.

[Open the original CC0 flower video](https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4).

:::{note} Text alternative
The clip shows a flower opening in a time-lapse. This summary is descriptive context, not a time-synchronized caption file.
:::

## Accessibility and compatibility

Keep controls discoverable; provide accurate synchronized captions for dialogue or informative audio, and a transcript or descriptive equivalent. Video embeds are HTML-specific; source links and written descriptions remain portable.

**References:** [MyST specification](https://mystmd.org/spec), [MyST videos](https://mystmd.org/guide/figures), [Web Awesome upstream reference](https://webawesome.com/docs/components/video/).
