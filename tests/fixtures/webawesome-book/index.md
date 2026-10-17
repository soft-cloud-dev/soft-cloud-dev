# Web Awesome SSR Fixture

This document exercises all Web Awesome directives and roles before SSR postprocessing.

```{wa-callout}
:variant: brand
:appearance: soft
:icon: info-circle
:title: Important Overview

This is an informational callout with a [documentation link](https://my.softcloud.dev/docs) and **bold** text.
```

```{wa-card} Card Header Title
:appearance: elevated
:image: /images/logo.svg
:image_alt: SoftCloud Logo
:footer: System Operational

### Nested Heading in Card

Card body containing a list:
- First item with special chars: `<test>` & "quotes"
- Second item with a [nested link](https://my.softcloud.dev/about)

<!-- HTML comment inside card body -->
```

```{wa-button}
:variant: primary
:appearance: filled
:size: m
:href: https://my.softcloud.dev/get-started
:target: _blank
:with-caret: true

Launch Console {fa}`brands github`
```

Inline icon test: Here is a rocket {icon}`classic solid rocket`, terminal icon {fa}`solid terminal`, brand icon {fa}`brands github`, and check icon {fa}`regular circle-check`.

<div class="sc-wa-telemetry">
  <span class="sc-wa-telemetry-label">Telemetry Status:</span>
  <span class="sc-wa-telemetry-status online">Operational</span>
</div>

### Responsive Section

| Metric Identifier | Target Specification | Current Measurement | Cluster Status | Compliance Threshold |
| :--- | :--- | :--- | :--- | :--- |
| Core Lit SSR TTFB | < 120 ms | 42 ms | Optimal | Passed |
| Declarative Shadow DOM Time | < 50 ms | 18 ms | Optimal | Passed |
| WCAG Contrast Ratio | >= 4.5:1 (AA) | 7.2:1 | Conforming | Passed |

```json
{
  "system_telemetry": {
    "cluster_name": "softcloud-primary-production-east-01",
    "datacenter_region": "us-east-1-compute-zone-alpha",
    "active_instances": 48
  }
}
```

### Icon Gallery Grid

<div class="sc-icon-grid">
  <div class="sc-icon-card">
    <div class="sc-icon-preview">💻</div>
    <div class="sc-icon-info">
      <span class="sc-icon-name"><code>server</code></span>
      <span class="sc-icon-desc">Compute Server</span>
    </div>
  </div>
  <div class="sc-icon-card">
    <div class="sc-icon-preview">⌨</div>
    <div class="sc-icon-info">
      <span class="sc-icon-name"><code>terminal</code></span>
      <span class="sc-icon-desc">Command Line</span>
    </div>
  </div>
</div>

