---
title: SoftCloud Executable Handbook
description: Practical engineering guides, executable notebooks, UI patterns, and systems laboratories connected to their source.
site:
  hide_title_block: true
  hide_outline: true
  hide_toc: true
  hide_footer_links: true
---

:::{div}
:class: sc-handbook

::::{div}
:class: sc-handbook__hero

:::::{div}
:class: sc-handbook__intro

THE SOFTCLOUD HANDBOOK

# Engineering knowledge you can reproduce.

Practical guides, executable notebooks, and reusable UI examples — connected to their source.

[Start with a guide](guides.md) [Browse notebooks](notebooks.md)

:::::

:::::{div}
:class: sc-handbook__verification

### Computational verification

```python
import sys
print(sys.version.split()[0])
assert sys.version_info[:3] == (3, 12, 14)
```

**Required execution profile**

`CPython 3.12.14 · Linux x86-64 · jb2-python`

[Open verification notebook](notebooks/experiment.ipynb)

:::::

::::

## Choose a starting point

::::{div}
:class: sc-handbook__routes

:::::{div}
:class: sc-handbook__route sc-handbook__route--guide

### [Publish your first page](guides.md)

Learn the documentation structure, authoring workflow, and publishing model for the SoftCloud handbook.

**GUIDE**

:::::

:::::{div}
:class: sc-handbook__route sc-handbook__route--notebook

### [Reproduce an environment check](notebooks/experiment.ipynb)

Run the reference environment verification notebook and understand its controlled execution profile.

**NOTEBOOK**

:::::

:::::{div}
:class: sc-handbook__route sc-handbook__route--library

### [Find a reusable UI pattern](components/index.md)

Explore the Web Awesome component catalog, design tokens, and reusable interface examples.

**UI LIBRARY**

:::::

::::

::::{div}
:class: sc-handbook__projects

### [Explore SoftCloud projects](projects.md)

[**SoftCloud Node Linux**](projects/linux.md) — Reproducible Linux/Kubernetes node documentation.

[**FreeIPA**](projects/freeipa.md) — Identity, policy, and access management laboratory.

::::

::::{div}
:class: sc-handbook__overview

## Open engineering, verifiable results

SoftCloud publishes computational research, cloud architecture, and operational guidance together with executable references. The publication profile addresses dependency drift, inconsistent runtimes, unverified execution, and documentation changes that escape build checks.

The four governing principles are **cryptographic dependency locking**, **isolated canonical execution**, **strict profile validation**, and **automated publication**. The [Architecture & Specification](architecture.md) explains the guarantees; the [Contributor Guide](contributing.md) explains how to operate the toolchain.

::::

:::
