---
description: >-
  Pricing and feature comparison patterns combining MyST {list-table}, Pipe Tables, and {grid} with Lit SSR {wa-card} and {wa-button} directives and interactive {anywidget} wa-slider, wa-switch, and wa-radio-group controls.
keywords:
  - MyST
  - Web Awesome
  - pricing table
  - comparison matrix
  - list-table
  - wa-card
  - wa-button
  - wa-slider
  - wa-switch
  - wa-radio-group
tags:
  - patterns
  - documentation
  - web-components
edit_url: https://github.com/soft-cloud-dev/soft-cloud-dev/edit/main/components/pricing-comparison.md
source_url: https://github.com/soft-cloud-dev/soft-cloud-dev/blob/main/components/pricing-comparison.md
---

# Pricing & Comparison Patterns

Pricing pages, resource tier catalogs, and architectural feature comparisons require structured tabular semantics alongside clear calls to action and optional capacity estimators. This pattern specification maps the **Pricing / Comparison** category across SoftCloud's three progressive rendering tiers without introducing external CSS frameworks.

**Related references:** [Practical UI patterns](practical-patterns.md) · [Authoring guide](authoring-guide.md) · [Design tokens](design-tokens.md) · [Component catalog](index.md).

:::{note} Progressive rendering contract
1. **MyST Native Layout (`{list-table}`, Pipe Tables, `{grid}`)**: Encodes all primary pricing tiers, SLA figures, and feature matrices in portable Markdown that exports cleanly to HTML, PDF/Typst, and machine-readable JSON ASTs.
2. **Typed Lit SSR Directives (`{wa-card}`, `{wa-button}`)**: Renders tier containers and call-to-action buttons with Declarative Shadow DOM (`<template shadowrootmode="open">` stamped with `did-ssr`) so visual hierarchy and links survive with JavaScript disabled.
3. **Client-Hydrated Controls (`wa-slider`, `wa-switch`, `wa-radio-group`)**: Hosted in `{anywidget}` only when user-selectable billing cycles, node quotas, or SLA toggles are demonstrated interactively.
:::

(sec-pricing-pattern-mapping)=
## 1. Pattern mapping overview

```{list-table} Pricing / Comparison Architecture Mapping
:header-rows: 1
:name: table-pricing-pattern-mapping

* - Pattern Category
  - MyST Native Primitives
  - Typed Lit SSR / DSD
  - Client `{anywidget}` Controls
* - **Pricing / Comparison**
  - `{list-table}`, Pipe Tables, `{grid}`
  - `{wa-card}`, `{wa-button}`
  - `wa-slider`, `wa-switch`, `wa-radio-group`
```

- **When to stop at MyST + Lit SSR**: Static tier comparisons, architectural tradeoff tables, and documentation matrices where every tier is visible at once.
- **When to add `{anywidget}` form atoms**: Interactive quota calculators, billing cadence toggles (monthly vs. annual commitment), or add-on switches (such as multi-region failover).

---

(sec-pricing-tier-grid)=
## 2. Multi-tier pricing cards (`{grid}` + SSR `{wa-card}` & `{wa-button}`)

Use a responsive MyST `{grid}` to arrange tier cards across mobile and desktop viewports (`1 1 2 3`), and compose typed `{wa-card}` and `{wa-button}` directives inside each column for server-rendered Declarative Shadow DOM output.

:::::{grid} 1 1 2 3

::::{wa-card} Edge Starter
:appearance: outlined
:footer: Billed monthly · Cancel anytime

**\$49 / month** per edge node

Ideal for single-site lab telemetry, bastion routing, and development enclaves.

- 4 vCPU / 16 GB ECC RAM
- 250 GB NVMe ZFS mirror
- Dual-stack IPv4 / IPv6 BGP session
- Community support & automated advisories

:::{wa-button}
:variant: neutral
:appearance: outlined
:href: https://my.softcloud.dev/
Deploy Starter Node
:::
::::

::::{wa-card} Production Cluster
:appearance: filled-outlined
:footer: Includes 99.95% uptime SLA

**\$189 / month** per HA node pair

Designed for production FreeIPA identity fabrics, WireGuard mesh gateways, and container workloads.

- 16 vCPU / 64 GB ECC RAM
- 1 TB NVMe RAID-Z2 distributed storage
- Automated multi-master FreeIPA replication
- 24/7 incident response (< 1 hour SLA)

:::{wa-button}
:variant: brand
:appearance: filled
:href: https://my.softcloud.dev/
Provision Production HA
:::
::::

::::{wa-card} Sovereign Enterprise
:appearance: outlined
:footer: Annual or 3-year reserved commitment

**\$640 / month** per dedicated rack unit

Full hardware isolation, dedicated HSM key custody, and cross-continental active-active failover.

- 64 vCPU / 256 GB ECC RAM
- 8 TB enterprise NVMe + air-gapped backups
- Dedicated hardware security module (FIPS 140-3)
- 99.99% SLA with dedicated systems engineer

:::{wa-button}
:variant: brand
:appearance: outlined
:href: https://github.com/soft-cloud-dev/soft-cloud-dev
Request Architecture Review
:::
::::

:::::

---

(sec-pricing-comparison-tables)=
## 3. Feature & SLA comparison matrices (`{list-table}` & Pipe Tables)

### 3.1 Concise feature matrix (CommonMark Pipe Table)

Use standard CommonMark pipe tables when cells contain concise single-line values, checkmarks, or short metrics:

| Capability | Edge Starter | Production Cluster | Sovereign Enterprise |
| :--- | :---: | :---: | :---: |
| **Compute Isolation** | Shared KVM | Dedicated vCPU | Bare-Metal / Single-Tenant |
| **FreeIPA Topology** | Standalone Replica | 3-Node Multi-Master | Geo-Distributed Quorum |
| **BGP Anycast Routing** | Optional | Included | Redundant Dual-Transit |
| **Automated Snapshots** | Daily (7-day retention) | Hourly (30-day retention) | Continuous + Immutable WORM |
| **Availability SLA** | 99.5% | 99.95% | 99.99% |

### 3.2 Detailed specification matrix (`{list-table}`)

When comparison rows require multiline descriptions, inline code, or explicit column width ratios, use MyST's `{list-table}` directive with an explicit cross-reference target:

```{list-table} Infrastructure Tier Technical Comparison
:header-rows: 1
:name: table-tier-technical-comparison

* - Subsystem
  - Edge Starter (`\$49/mo`)
  - Production Cluster (`\$189/mo`)
  - Sovereign Enterprise (`\$640/mo`)
* - **Kernel & OS Profile**
  - Standard Linux LTS or FreeBSD RELEASE image with unattended security patching.
  - Tuned `sysctl` network profile (`net.core.rmem_max`, BBR congestion control) and live kernel patching.
  - Custom signed kernel builds, Secure Boot attestation, and remote TPM 2.0 measured boot verification.
* - **Identity & mTLS Fabric**
  - Single-node Kerberos KDC and Let's Encrypt ACME certificate automation.
  - Multi-master FreeIPA directory (`389/tcp`), integrated split-horizon DNSSEC, and short-lived step-ca mTLS certificates.
  - Hardware-backed PKI root CA, cross-realm Kerberos trust brokering, and automated HashiCorp Vault secret rotation.
* - **Observability & Audit**
  - Node Exporter metrics and 14-day local journald ring buffer.
  - Prometheus remote-write, eBPF packet flow telemetry, and 90-day Loki audit log retention.
  - Dedicated SIEM streaming, cryptographic audit log signing, and 7-year compliance archival.
```

### 3.3 Responsive & accessible comparison table styling

For wide comparison tables in custom web views, keep native `<table>`, `<thead>`, `<tbody>`, and `<th scope="col|row">` semantics intact. Wrap scrollable matrices in a keyboard-focusable region (`tabindex="0" role="region"`) and use CSS container queries (`container-type: inline-size`) with sticky headers so column and row labels remain visible on narrow viewports:

```css
.sc-comparison-region {
  overflow: auto;
  max-inline-size: 100%;
  max-block-size: min(520px, 80vh);
  container-type: inline-size;
  border: var(--wa-border-width-s, 1px) solid var(--wa-color-surface-border, #cbd5e1);
  border-radius: var(--wa-border-radius-m, 0.5rem);
}

.sc-comparison-region table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
}

.sc-comparison-region thead {
  position: sticky;
  inset-block-start: 0;
  z-index: 2;
  background: var(--wa-color-surface-raised, #ffffff);
}

.sc-comparison-region tbody th {
  position: sticky;
  inset-inline-start: 0;
  z-index: 1;
  background: var(--wa-color-surface-raised, #ffffff);
}

@container (width < 560px) {
  .sc-comparison-region thead {
    display: none;
  }
  .sc-comparison-region tr {
    display: block;
    margin-block-end: var(--wa-space-m, 1rem);
    border-block-end: 1px solid var(--wa-color-surface-border, #cbd5e1);
  }
  .sc-comparison-region td {
    display: block;
  }
  .sc-comparison-region td:nth-child(2)::before { content: "Edge Starter: "; font-weight: 600; }
  .sc-comparison-region td:nth-child(3)::before { content: "Production Cluster: "; font-weight: 600; }
  .sc-comparison-region td:nth-child(4)::before { content: "Sovereign Enterprise: "; font-weight: 600; }
}
```

---

(sec-pricing-interactive-configurator)=
## 4. Interactive capacity configurator (`wa-slider`, `wa-switch`, `wa-radio-group`)

When a pricing or comparison view lets users adjust billing cadence, compute capacity, or high-availability add-ons, host the interactive form controls in the self-hosted `{anywidget}` preview while keeping a complete static reference above or alongside it.

### Static reference (works without JavaScript)

:::{card} Baseline cluster estimate (no-JS fallback)
- **Billing commitment (`wa-radio-group`)**: Annual commitment (15% discount applied) — options: `Monthly`, `Annual (-15%)`, `3-Year Reserved (-30%)`.
- **Allocated vCPU capacity (`wa-slider`)**: `32 vCPUs` across 4–128 vCPU range (step: 4 vCPUs).
- **Add-on controls (`wa-switch`)**: Multi-region active-active failover enabled (`+\$120/mo`); FIPS 140-3 HSM key custody optional.
- **Estimated baseline total**: **\$442 / month** (Production Cluster HA with 32 vCPUs and multi-region failover).
:::

### Live preview

```{anywidget} ../widgets/webawesome-demo.mjs
{
  "tree": [
    {
      "tag": "wa-radio-group",
      "attrs": {
        "label": "Billing cadence",
        "name": "billing-cadence",
        "value": "annual"
      },
      "children": [
        {
          "tag": "wa-radio",
          "attrs": { "value": "monthly" },
          "children": ["Monthly"]
        },
        {
          "tag": "wa-radio",
          "attrs": { "value": "annual" },
          "children": ["Annual (save 15%)"]
        },
        {
          "tag": "wa-radio",
          "attrs": { "value": "reserved-3yr" },
          "children": ["3-Year Reserved (save 30%)"]
        }
      ]
    },
    {
      "tag": "wa-slider",
      "attrs": {
        "label": "Cluster vCPU allocation (4 to 128 cores)",
        "min": "4",
        "max": "128",
        "step": "4",
        "value": "32"
      },
      "children": []
    },
    {
      "tag": "wa-switch",
      "attrs": {
        "checked": ""
      },
      "children": ["Multi-region active-active BGP failover (+99.99% SLA)"]
    },
    {
      "tag": "wa-switch",
      "attrs": {},
      "children": ["Dedicated FIPS 140-3 HSM key custody"]
    },
    {
      "tag": "wa-button",
      "attrs": {
        "variant": "brand",
        "appearance": "filled",
        "href": "https://my.softcloud.dev/"
      },
      "children": ["Export Sizing Manifest"]
    }
  ]
}
```

**Atomic component reuse:**
- [`wa-card`](layout/card.md) and [`wa-button`](actions/button.md) provide server-rendered tier containers and call-to-action triggers via SoftCloud's typed MyST directives.
- [`wa-radio-group`](forms/radio-group.md) and [`wa-radio`](forms/radio.md) enforce mutually exclusive billing cadence selection.
- [`wa-slider`](forms/slider.md) constrains numeric capacity selection along stepped intervals (`min="4"`, `max="128"`, `step="4"`).
- [`wa-switch`](forms/switch.md) toggles boolean infrastructure add-ons immediately.

---

(sec-pricing-code-snippets)=
## 5. Markdown & HTML code snippets

:::::{tab-set}

::::{tab-item} MyST + Lit SSR Authoring
````markdown
:::::{grid} 1 1 2 3
:gutter: 3

::::{wa-card} Production Cluster
:appearance: filled-outlined
:footer: Includes 99.95% uptime SLA

**\$189 / month** per HA node pair

- 16 vCPU / 64 GB ECC RAM
- 1 TB NVMe RAID-Z2 distributed storage

:::{wa-button}
:variant: brand
:appearance: filled
:href: https://my.softcloud.dev/
Provision Production HA
:::
::::
:::::
````
::::

::::{tab-item} Standalone Web Awesome HTML
```html
<wa-radio-group label="Billing cadence" name="billing-cadence" value="annual">
  <wa-radio value="monthly">Monthly</wa-radio>
  <wa-radio value="annual">Annual (save 15%)</wa-radio>
  <wa-radio value="reserved-3yr">3-Year Reserved (save 30%)</wa-radio>
</wa-radio-group>

<wa-slider
  label="Cluster vCPU allocation (4 to 128 cores)"
  min="4"
  max="128"
  step="4"
  value="32"
></wa-slider>

<wa-switch checked="">Multi-region active-active BGP failover (+99.99% SLA)</wa-switch>
<wa-switch>Dedicated FIPS 140-3 HSM key custody</wa-switch>

<wa-button variant="brand" appearance="filled" href="https://my.softcloud.dev/">
  Export Sizing Manifest
</wa-button>
```
::::

:::::
