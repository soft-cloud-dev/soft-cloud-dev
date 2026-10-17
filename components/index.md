---
slug: components
description: Web Awesome component catalog with live examples, source references, and MyST alternatives.
keywords:
  - Web Awesome
  - web components
  - MyST
  - component catalog
---

# Web Awesome — Component Catalog

The complete component catalog is split into one self-contained MyST Markdown file per component. It covers **87 components listed in the official public directory** plus three source-only experimental components (`wa-stepper`, `wa-step`, `wa-tag-input`). The installed Web Awesome version is pinned in `package.json`; the inventory is maintained in `components/catalog.json`.

:::{note} Rendering strategy

The existing four typed MyST Web Awesome integrations (`wa-button`, `wa-card`, `wa-callout`, `wa-icon`) retain genuine Lit SSR and Declarative Shadow DOM. Other available Core components use the existing MyST `{anywidget}` integration to load self-hosted Web Awesome modules. The 17 former Pro component pages are now portable MyST/HTML5 recipes; no Pro runtime is bundled.
:::

## Documentation and real-media examples

- [Authoring and migration guide](authoring-guide.md) — choose MyST built-ins for prose and layout, retain anywidget for interactive Web Awesome components, and follow the phased API documentation plan.
- [Practical UI patterns](practical-patterns.md) — original Tailwind-inspired marketing and application-UI recipes using native MyST grids/cards/tabs with Web Awesome interactive atoms.
- [Real media showcase](showcase-media.md) — bundled public-domain/CC0 photographs, photographic carousel, comparison, avatar, photo tabs, zoomable frame, and native video.

For this catalog, an interactive preview is **client-rendered by anywidget**; it must not be mistaken for the genuine Lit SSR path used by four existing typed primitives. Core media previews use site-local `/static/showcase/` runtime assets. Standalone HTML snippets should instead use host-provided relative media URLs. The 17 Pro alternatives are documented as non-Core recipes without licensed Pro executables.

## Portable alternatives

All 17 non-Core recipes are grouped in [Portable Alternatives](portable-alternatives.md), with static MyST/SVG charts and HTML5 form and media examples. They are not replacements for the full interactive Web Awesome Pro APIs.

## Component categories

### Actions

[Button](actions/button.md) · [Button Group](actions/button-group.md) · [Copy Button](actions/copy-button.md) · [Dropdown](actions/dropdown.md) · [Dropdown Item](actions/dropdown-item.md).

### Forms

[Checkbox](forms/checkbox.md) · [Checkbox Group](forms/checkbox-group.md) · [Color Picker](forms/color-picker.md) · [Combobox](forms/combobox.md) (portable recipe) · [Date Input](forms/date-input.md) (portable recipe) · [Date Picker](forms/date-picker.md) (portable recipe) · [File Input](forms/file-input.md) (portable recipe) · [Input](forms/input.md) · [Known Date](forms/known-date.md) · [Number Input](forms/number-input.md) · [OTP Input](forms/otp-input.md) · [Radio Group](forms/radio-group.md) · [Radio](forms/radio.md) · [Rating](forms/rating.md) · [Select](forms/select.md) · [Option](forms/option.md) · [Slider](forms/slider.md) · [Switch](forms/switch.md) · [Tag Input](forms/tag-input.md) (source-only) · [Textarea](forms/textarea.md) · [Time Input](forms/time-input.md).

### Layout

[Accordion](layout/accordion.md) · [Accordion Item](layout/accordion-item.md) · [Card](layout/card.md) · [Details](layout/details.md) · [Dialog](layout/dialog.md) · [Divider](layout/divider.md) · [Drawer](layout/drawer.md) · [Page](layout/page.md) · [Scroller](layout/scroller.md) · [Split Panel](layout/split-panel.md).

### Navigation

[Breadcrumb](navigation/breadcrumb.md) · [Breadcrumb Item](navigation/breadcrumb-item.md) · [Pagination](navigation/pagination.md) · [Stepper](navigation/stepper.md) (source-only) · [Step](navigation/step.md) (source-only) · [Tab Group](navigation/tab-group.md) · [Tab](navigation/tab.md) · [Tab Panel](navigation/tab-panel.md) · [Tree](navigation/tree.md) · [Tree Item](navigation/tree-item.md).

### Feedback

[Badge](feedback/badge.md) · [Callout](feedback/callout.md) · [Progress Bar](feedback/progress-bar.md) · [Progress Ring](feedback/progress-ring.md) · [Skeleton](feedback/skeleton.md) · [Spinner](feedback/spinner.md) · [Tag](feedback/tag.md) · [Toast](feedback/toast.md) · [Toast Item](feedback/toast-item.md) · [Tooltip](feedback/tooltip.md).

### Media

[Animated Image](media/animated-image.md) · [Avatar](media/avatar.md) · [Carousel](media/carousel.md) · [Carousel Item](media/carousel-item.md) · [Comparison](media/comparison.md) · [Icon](media/icon.md) · [Markdown](media/markdown.md) · [QR Code](media/qr-code.md) · [Video](media/video.md) (portable recipe) · [Video Playlist](media/video-playlist.md) (portable recipe) · [Zoomable Frame](media/zoomable-frame.md).

### Data Visualization

[Bar Chart](data-viz/bar-chart.md) (portable) · [Bubble Chart](data-viz/bubble-chart.md) (portable) · [Chart](data-viz/chart.md) (portable) · [Data Grid](data-viz/data-grid.md) (portable) · [Doughnut Chart](data-viz/doughnut-chart.md) (portable) · [Line Chart](data-viz/line-chart.md) (portable) · [Pie Chart](data-viz/pie-chart.md) (portable) · [Polar Area Chart](data-viz/polar-area-chart.md) (portable) · [Radar Chart](data-viz/radar-chart.md) (portable) · [Scatter Chart](data-viz/scatter-chart.md) (portable) · [Sparkline](data-viz/sparkline.md) (portable).

### Helpers

[Animation](helpers/animation.md) · [Format Bytes](helpers/format-bytes.md) · [Format Date](helpers/format-date.md) · [Format Number](helpers/format-number.md) · [Include](helpers/include.md) · [Intersection Observer](helpers/intersection-observer.md) · [Mutation Observer](helpers/mutation-observer.md) · [Popover](helpers/popover.md) · [Popup](helpers/popup.md) · [Random Content](helpers/random-content.md) · [Relative Time](helpers/relative-time.md) · [Resize Observer](helpers/resize-observer.md).


## Architecture

Complex examples reuse atomic custom elements including Button, Dropdown Item, Checkbox, Option, Radio, Accordion Item, Breadcrumb Item, Tab, Tab Panel, Tree Item, Carousel Item, and Toast Item. Every Markdown page includes its expanded HTML snippet so it is usable independently of the catalog index. Individual pages cite an upstream GitHub source file through MyST's GitHub transformer (or a SoftCloud documentation source for private Pro components) and an attributed Wikipedia excerpt using the native `wiki:` link transformer.

The existing [Web Awesome notebook](../notebooks/webawesome-docs.ipynb) and [SoftCloud MyST integration source](https://github.com/soft-cloud-dev/soft-cloud-dev/blob/main/assets/plugins/myst-webawesome.mjs#L1-L24) remain the canonical documentation of the four server-rendered primitives. See [the official Web Awesome component directory](https://webawesome.com/docs/components) for public availability and supported APIs.
