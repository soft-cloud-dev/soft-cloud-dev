# Video Playlist `<wa-video-playlist>`

Coordinates several video elements.

> “Multimedia is a form of communication that uses a combination of different content forms.” — [Wikipedia: Multimedia](wiki:Multimedia). This quote supplies general domain context, not an API definition.

**Category:** [Media](../index.md) · **Availability:** Pro · **Maturity:** Experimental.

**Source:** [SoftCloud documentation Markdown](https://github.com/soft-cloud-dev/soft-cloud-dev/blob/main/components/media/video-playlist.md#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/video-playlist/).

:::{warning} Integration status

Web Awesome Pro only: not installed in the existing Core runtime. No interactive preview or licensed code is distributed.
:::

## Atomic composition

Reuse: [Video](../media/video.md). The full nested markup below remains independently usable.

## Live preview

Live preview intentionally unavailable: the Pro runtime is not licensed for this deployment.

## Markdown code snippet

```html
<wa-video-playlist>
  <wa-video src="https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4"></wa-video>
  <wa-video src="https://uploads.webawesome.com/dog-with-glasses.mp4"></wa-video>
</wa-video-playlist>
```

These are **real media source URLs** (MDN CC0 flower clip and a Web Awesome-hosted dog clip). The playlist is intentionally *reference-only* because Pro is not installed. Sources must be reachable before examples can play in a licensed environment.

Use native MyST for documentation layout; interactive Web Awesome previews remain hosted through the existing `{anywidget}` integration when available. Chart/grid data and configuration must additionally be supplied through documented Pro JavaScript properties.
