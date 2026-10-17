# Real Media Showcase

Web Awesome's interactive media components are rendered by the existing MyST `{anywidget}` integration. Ordinary illustrations, photo collections, captions, grids, and documentation tabs remain native MyST blocks. All still photographs shown below are bundled in the repository and therefore do not require external image services.

:::{note} Runtime boundary
Jupyter Book and MyST render this page as normal publication content. The **component preview** runs in anywidget's browser-side Shadow DOM; it is not claimed to have Lit SSR. The separate legacy SSR pipeline continues to support the four typed Web Awesome components.
:::

## Bundled photographs

::::{grid} 1 1 2 2
:::{card} SpaceX launch
![Falcon 9 carrying DSCOVR lifts off](../assets/static/showcase/rocket.jpg)
**Source:** SpaceX Falcon 9 DSCOVR launch photograph, distributed via scikit-image. **License:** public-domain designation recorded in scikit-image; independent confirmation of the original SpaceX release remains pending. See the [media provenance manifest](https://github.com/soft-cloud-dev/soft-cloud-dev/blob/main/assets/static/showcase/README.md).
:::
:::{card} Coffee cup
![White cup of coffee on a wooden table](../assets/static/showcase/coffee.png)
**Credit:** Rachel Michetti / Pikolo Espresso Bar. **License:** CC0. See the [media provenance manifest](https://github.com/soft-cloud-dev/soft-cloud-dev/blob/main/assets/static/showcase/README.md).
:::
:::{card} Deep field
![Hubble eXtreme Deep Field](../assets/static/showcase/hubble-deep-field.jpg)
**Credit:** NASA / Hubble eXtreme Deep Field. **License:** public domain. See the [media provenance manifest](https://github.com/soft-cloud-dev/soft-cloud-dev/blob/main/assets/static/showcase/README.md).
:::
:::{card} Astronaut portrait
![NASA portrait of Eileen Collins](../assets/static/showcase/astronaut.png)
**Credit:** NASA / Eileen Collins portrait. **License:** public domain. See the [media provenance manifest](https://github.com/soft-cloud-dev/soft-cloud-dev/blob/main/assets/static/showcase/README.md).
:::
::::

## Interactive Web Awesome showcases

These component pages reuse exactly the same local assets. Each page includes a working anywidget preview and a complete HTML snippet:

- [Carousel](media/carousel.md) and [Carousel Item](media/carousel-item.md) — real photographic slides.
- [Comparison](media/comparison.md) — same photograph before/after grayscale filtering.
- [Avatar](media/avatar.md) — NASA portrait rather than placeholder initials.
- [Card](layout/card.md) — photo in the media slot and playable CC0 video.
- [Scroller](layout/scroller.md) — a horizontally scrollable photo strip.
- [Tab Group](navigation/tab-group.md), [Tab](navigation/tab.md), and [Tab Panel](navigation/tab-panel.md) — tabs containing photographs.
- [Zoomable Frame](media/zoomable-frame.md) — a same-origin, script-free gallery.
- [Animated Image](media/animated-image.md) — a real animated Web Awesome example GIF (external).

## Native browser video

Web Awesome `wa-video` and `wa-video-playlist` are Pro components and remain reference-only. Use browser-native HTML video when Pro is unavailable. For example:

```html
<video controls preload="metadata" aria-label="Time-lapse of a flower opening">
  <source src="https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4" type="video/mp4">
  Your browser does not support HTML video.
</video>
```

The MP4 is an actual public CC0 demo clip hosted by MDN. It requires network access; audio/video material should include captions or a text equivalent where meaningful. The [Card](layout/card.md) page provides a playable live preview. No Pro code is shipped.

## Provenance and deterministic staging

The self-hosted samples were copied byte-for-byte from [scikit-image](https://github.com/scikit-image/scikit-image) and have recorded Git blob hashes, original credits, and claimed public-domain or CC0 license status in [the media manifest](https://github.com/soft-cloud-dev/soft-cloud-dev/blob/main/assets/static/showcase/README.md). Existing asset staging copies `assets/static/showcase` to `_build/html/static/showcase`, including locale builds. Animated GIF and MDN MP4 are the only intentionally external showcase assets.
