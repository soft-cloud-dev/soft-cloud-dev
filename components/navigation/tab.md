# Tab `<wa-tab>`

Names and activates a matching tab panel.

> “the process of navigating a network of information resources” — [Wikipedia: Web navigation](wiki:Web_navigation). This quote supplies general domain context, not an API definition.

**Category:** [Navigation](../index.md) · **Availability:** Core · **Maturity:** Stable.

**Source:** [Web Awesome component source](https://github.com/shoelace-style/webawesome/blob/v3.14.0/packages/webawesome/src/components/tab/tab.ts#L1-L24) (MyST GitHub transformer); [official component documentation](https://webawesome.com/docs/components/tab/).

:::{note} Integration status

Uses the existing self-hosted Web Awesome 3.14.0 and MyST anywidget integration.
:::

## Atomic composition

Reuse: [Tab Group](../navigation/tab-group.md), [Tab Panel](../navigation/tab-panel.md). The full nested markup below remains independently usable.

## Live preview

### Static reference (works without JavaScript)

![NASA astronaut portrait](../../assets/static/showcase/astronaut.png)

The image and copyable HTML example below remain available if the interactive widget fails to initialize. The widget adds component behavior; it does not provide the only readable content.

```{anywidget} ../../widgets/webawesome-demo.mjs
{
  "tree": {
    "tag": "wa-tab-group",
    "attrs": {
      "active": "portrait"
    },
    "children": [
      {
        "tag": "wa-tab",
        "attrs": {
          "panel": "portrait"
        },
        "children": [
          "Portrait"
        ]
      },
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
        "tag": "wa-tab-panel",
        "attrs": {
          "name": "portrait"
        },
        "children": [
          {
            "tag": "img",
            "attrs": {
              "src": "showcase:astronaut.png",
              "alt": "NASA portrait of Eileen Collins"
            },
            "children": []
          }
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
              "src": "showcase:rocket.jpg",
              "alt": "Falcon 9 launch"
            },
            "children": []
          }
        ]
      }
    ]
  }
}
```

## Markdown code snippet

```html
<wa-tab-group active="portrait">
  <wa-tab panel="portrait">Portrait</wa-tab>
  <wa-tab panel="launch">Launch</wa-tab>
  <wa-tab-panel name="portrait"><img src="./images/astronaut.png" alt="NASA portrait of Eileen Collins"></wa-tab-panel>
  <wa-tab-panel name="launch"><img src="./images/rocket.jpg" alt="Falcon 9 launch"></wa-tab-panel>
</wa-tab-group>
```

## Usage and API notes

A tab is an atomic child of `wa-tab-group`. It refers to a panel using `panel`. This nested demo uses real image content so tab activation visibly changes the selected pane.

Media sources: [Showcase media](../showcase-media.md).
