# Tab Group `<wa-tab-group>`

Coordinates tab buttons and their corresponding panels.

> “the process of navigating a network of information resources” — [Wikipedia: Web navigation](wiki:Web_navigation). This quote supplies general domain context, not an API definition.

**Category:** [Navigation](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/v3.14.0/packages/webawesome/src/components/tab-group/tab-group.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/tab-group/).

:::{wa-callout} Integration status
:variant: brand
:appearance: filled

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
