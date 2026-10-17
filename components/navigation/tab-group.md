# Tab Group `<wa-tab-group>`

Coordinates tab buttons and their corresponding panels.

> “the process of navigating a network of information resources” — [Wikipedia: Web navigation](wiki:Web_navigation). This quote supplies general domain context, not an API definition.

**Category:** [Navigation](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/v3.14.0/packages/webawesome/src/components/tab-group/tab-group.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/tab-group/).

:::{note} Integration status

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Atomic composition

Reuse: [Tab](../navigation/tab.md), [Tab Panel](../navigation/tab-panel.md). The full nested markup below remains independently usable.

## Live preview

```{anywidget} ../../widgets/webawesome-demo.mjs
{
  "tree": {
    "tag": "wa-tab-group",
    "attrs": {
      "active": "launch"
    },
    "children": [
      {
        "tag": "wa-tab",
        "attrs": {
          "panel": "launch"
        },
        "children": [
          "Launch"
        ]
      },
      {
        "tag": "wa-tab",
        "attrs": {
          "panel": "galaxies"
        },
        "children": [
          "Galaxies"
        ]
      },
      {
        "tag": "wa-tab-panel",
        "attrs": {
          "name": "launch"
        },
        "children": [
          {
            "tag": "img",
            "attrs": {
              "src": "/static/showcase/rocket.jpg",
              "alt": "Falcon 9 launch"
            },
            "children": []
          },
          {
            "tag": "p",
            "attrs": {},
            "children": [
              "Falcon 9 carrying the DSCOVR spacecraft."
            ]
          }
        ]
      },
      {
        "tag": "wa-tab-panel",
        "attrs": {
          "name": "galaxies"
        },
        "children": [
          {
            "tag": "img",
            "attrs": {
              "src": "/static/showcase/hubble-deep-field.jpg",
              "alt": "Hubble eXtreme Deep Field"
            },
            "children": []
          },
          {
            "tag": "p",
            "attrs": {},
            "children": [
              "Distant galaxies captured by Hubble."
            ]
          }
        ]
      }
    ]
  }
}
```

## Markdown code snippet

```html
<wa-tab-group active="launch">
  <wa-tab panel="launch">Launch</wa-tab>
  <wa-tab panel="galaxies">Galaxies</wa-tab>
  <wa-tab-panel name="launch">
    <img src="/static/showcase/rocket.jpg" alt="Falcon 9 launch">
    <p>Falcon 9 carrying the DSCOVR spacecraft.</p>
  </wa-tab-panel>
  <wa-tab-panel name="galaxies">
    <img src="/static/showcase/hubble-deep-field.jpg" alt="Hubble eXtreme Deep Field">
    <p>Distant galaxies captured by Hubble.</p>
  </wa-tab-panel>
</wa-tab-group>
```

## Usage and API notes

Each `wa-tab[panel]` targets a unique `wa-tab-panel[name]`. `wa-tab-group[active]` chooses the initial panel. Actual photographs make switching panels observable. Use the MyST `{tab-set}` and `{tab-item}` directives when the task is organizing prose or alternative code listings, and Web Awesome only for application-like tabs.

Media sources: [Showcase media](../showcase-media.md).


## Examples: placement and keyboard activation

Use the `placement` attribute to choose `top` (default), `bottom`, `start`, or `end`. Set `activation="manual"` when moving keyboard focus should *not* immediately switch the active panel; in that mode, arrow keys navigate between tabs and Space/Enter selects the focused tab.

```html
<wa-tab-group active="launch" placement="start" activation="manual">
  <wa-tab panel="launch">Launch</wa-tab>
  <wa-tab panel="gallery">Gallery</wa-tab>
  <wa-tab panel="unavailable" disabled>Unavailable</wa-tab>
  <wa-tab-panel name="launch">
    <img src="/static/showcase/rocket.jpg" alt="Falcon 9 launch">
  </wa-tab-panel>
  <wa-tab-panel name="gallery">
    <img src="/static/showcase/hubble-deep-field.jpg" alt="Hubble deep field">
  </wa-tab-panel>
  <wa-tab-panel name="unavailable">This panel is disabled.</wa-tab-panel>
</wa-tab-group>
```

## Verified API: Web Awesome 3.14.0

| Attribute / property | Values / default | Usage |
| --- | --- | --- |
| `active` | Name of a panel, default empty | Sets which tab and panel are selected |
| `placement` | `top` (default), `bottom`, `start`, `end` | Horizontal or vertical tab arrangement |
| `activation` | `auto` (default), `manual` | Whether keyboard focus also changes the visible panel |
| `without-scroll-controls` | Boolean, default false | Hides scroll arrow controls if tabs overflow |

| Slot | Accepted content |
| --- | --- |
| Default | `<wa-tab-panel>` children |
| `nav` | `<wa-tab>` children (tabs assign their `nav` slot automatically) |

| Event | Emission |
| --- | --- |
| `wa-tab-show` | A tab becomes visible |
| `wa-tab-hide` | A tab is hidden |

The component exposes `--indicator-color`, `--track-color`, and `--track-width` CSS custom properties. Publicly documented parts include `tab-group`, `nav`, `tabs`, `body`, `scroll-button`, `scroll-button-start`, `scroll-button-end`, and `scroll-button__base`. The obsolete `base` part is deprecated. Other documented dependencies include `wa-button`, `wa-icon`, `wa-spinner`, `wa-tab` and `wa-tab-panel`.

:::{note} Server rendering is a different integration path
The live example on this page uses browser-side MyST `{anywidget}`. The official upstream SSR guidance for `wa-tab-group` is to mark the chosen child `<wa-tab>` **and** `<wa-tab-panel>` with `active` as well, because the group cannot inspect its children during SSR. Do not claim that the existing four-primitive SoftCloud Lit SSR transformer also renders tab groups.
:::

## Portable MyST equivalent

When tabs only separate documentation snippets or language-specific explanations, use the built-in MyST `{tab-set}` and `{tab-item}` instead of initializing Web Awesome:

::::{tab-set}
:::{tab-item} List pods
```sh
kubectl get pods -A
```
:::
:::{tab-item} List nodes
```sh
kubectl get nodes -o wide
```
:::
::::

Use Web Awesome tab groups for actual application state, dynamic user interaction, custom placement, or tab-specific events. For source-of-truth API details see [upstream version-pinned reference](https://github.com/shoelace-style/webawesome/blob/v3.14.0/packages/webawesome/docs/docs/components/tab-group.md) and the [official API page](https://webawesome.com/docs/components/tab-group/). Refer to the [SoftCloud authoring guide](../authoring-guide.md) for the page-standard checklist.
