# Showcase media provenance

These are **real photographs** used in the Web Awesome + MyST demonstrations. All four raster files are copied byte-for-byte from `scikit-image/scikit-image` (Git blob SHA preserved) and staged as `/static/showcase/*` by the existing SoftCloud asset-copy process. They are not synthetic placeholder illustrations.

| File | Upstream sample path | Git blob SHA | Rights and original credit |
| --- | --- | --- | --- |
| `rocket.jpg` | `src/_skimage2/data/rocket.jpg` | `32bdd33960c60d012fc71b5fd80a7ccc24d3b906` | SpaceX Falcon 9 DSCOVR launch photograph; released into the public domain. |
| `coffee.png` | `src/_skimage2/data/coffee.png` | `f8350bf7e6e22734667f8c86fd230a741370fbcb` | Rachel Michetti, courtesy Pikolo Espresso Bar; CC0. |
| `astronaut.png` | `src/_skimage2/data/astronaut.png` | `834cda0012478c5edc8d43bade96d315dedeaab4` | NASA portrait of Eileen Collins; public domain. |
| `hubble-deep-field.jpg` | `src/_skimage2/data/hubble_deep_field.jpg` | `50c1b81aea1d565d78741387b5279bbed0ba4ce8` | NASA Hubble eXtreme Deep Field; public domain. |

Canonical source and license evidence: [scikit-image data module](https://github.com/scikit-image/scikit-image/blob/main/src/_skimage2/data/_fetchers.py) (`astronaut`, `coffee`, `hubble_deep_field`, and `rocket` docstrings). Sample source files are in the same directory.

External, not vendored:

- Animated shoes GIF: `https://shoelace.style/assets/images/walk.gif`, the [upstream Web Awesome animated-image demo](https://webawesome.com/docs/components/animated-image/). Its canvas-based pause control depends on cross-origin image permissions.
- Flower MP4: `https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4`, MDN's public CC0 HTML media sample. Only the browser fetches it, with native controls and `preload=metadata`.

Production media rules: reuse bundled photographs; do not introduce new placeholder image paths; record upstream authorship and licenses before vendoring; provide nonempty `alt`/accessible labels and media alternatives; favor media with known intrinsic dimensions; do not autoplay video by default; keep external media as an explicitly marked exception.
