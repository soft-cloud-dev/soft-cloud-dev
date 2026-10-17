---
description: "Replace a proprietary video playlist with a MyST ordered list and native HTML5 video controls."
keywords:
  - MyST
  - media
  - Video Playlist
tags:
  - portable-alternative
  - media
  - accessible-documentation
---

# Video Playlist: portable MyST alternative

:::{admonition} Portable Alternative (Non-Core)
:class: note

Web Awesome Pro components require a commercial license and are not bundled in this catalog. This page demonstrates portable, accessible alternatives using standard MyST markup and HTML5 semantics.
:::

**Former upstream Pro component:** `<wa-video-playlist>`. **Category:** [Portable Alternatives](../portable-alternatives.md) · **Implementation:** MyST + HTML5.

Use this documentation recipe without importing Web Awesome Pro code. The former component is named for compatibility and discovery only; the alternative is not API-equivalent.

## Portable example

A portable playlist is a semantic ordered list of recordings with descriptions and transcripts. Playback sequencing, persistence and synchronized playlist controls require additional application logic.

## Copyable HTML5 pattern

```html
<ol aria-label="Recorded demonstrations">
  <li>
    <h3>Flower time-lapse</h3>
    <video controls preload="metadata" aria-label="Flower time-lapse">
      <source src="https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4"
              type="video/mp4">
      <track kind="captions" src="CAPTIONS_URL" srclang="en" label="English">
      Your browser does not support HTML5 video.
    </video>
  </li>
</ol>
```

1. [Flower time-lapse, CC0 example (MP4)](https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4) — A flower opens over time.

**Caption asset contract:** replace `CAPTIONS_URL` with a real application-hosted WebVTT file before using the HTML snippet. Do not claim this static list automatically changes videos or controls autoplay.

## Accessibility and compatibility

Provide a title and written context for each recording. Keep each video's controls independent and include captions and transcripts where needed. The example does not perform JavaScript playlist playback.

**References:** [MyST specification](https://mystmd.org/spec), [MyST videos](https://mystmd.org/guide/figures), [Web Awesome upstream reference](https://webawesome.com/docs/components/video-playlist/).
