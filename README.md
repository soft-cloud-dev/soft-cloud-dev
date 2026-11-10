---
title: SoftCloud Executable Handbook
description: Guides, executable notebooks, UI patterns, and systems laboratories with verifiable sources.
site:
  hide_title_block: true
  hide_outline: true
  hide_toc: true
  hide_footer_links: true
---

:::::::{div}
:class: sc-handbook

::::::{div}
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

::::::

## Choose a starting point

::::::{div}
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

### [Find a reusable UI pattern](ui-library.md)

Explore the Web Awesome catalog, design tokens, and reusable interface examples.

**UI LIBRARY**

:::::

::::::

::::::{div}
:class: sc-handbook__projects

### [Explore SoftCloud projects](projects.md)

[**SoftCloud Node Linux**](projects/linux.md) — Reproducible Linux/Kubernetes node documentation.

[**FreeIPA**](https://freeipa.softcloud.dev/) — Identity, policy, and access management laboratory.

::::::

::::::{div}
:class: sc-handbook__overview

## Reproducible engineering, accountable results

SoftCloud publishes computational research, cloud architecture, and operational guidance alongside executable references. Unpinned dependencies, divergent binaries, implicit environment state, and unverified runtime kernels can make research difficult to reproduce.

Its publication contract uses SHA-256 dependency locking, a canonical CPython 3.12.14 runtime on Linux x86-64, strict preflight verification, and automated CI/CD. See the [Architecture & Specification](architecture.md) for guarantees and the [background and operational scope](introduction.md) for context.

::::::

:::::::
