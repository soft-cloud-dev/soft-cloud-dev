---
title: Contributor Guide
description: Publication operations, environment setup, validation, and review workflow.
---

# Contributor Guide

This guide owns contributor workflow and publication operations. Architectural guarantees remain in [Architecture & Specification](architecture.md); Web Awesome page conventions remain in the [component authoring guide](components/authoring-guide.md).

## Toolchain and source of truth

- Project and TOC: [`myst.yml`](https://github.com/soft-cloud-dev/soft-cloud-dev/blob/main/myst.yml)
- Locked Python distributions: [`requirements.lock`](https://github.com/soft-cloud-dev/soft-cloud-dev/blob/main/requirements.lock)
- Local build driver: [`tools/build.sh`](https://github.com/soft-cloud-dev/soft-cloud-dev/blob/main/tools/build.sh)
- Preflight: [`tools/check_profile.py`](https://github.com/soft-cloud-dev/soft-cloud-dev/blob/main/tools/check_profile.py)
- Publication workflow: [`.github/workflows/deploy.yml`](https://github.com/soft-cloud-dev/soft-cloud-dev/blob/main/.github/workflows/deploy.yml)

## Local development

Prepare the environment using the repository's pinned Python environment setup, then install JavaScript dependencies with `npm ci`. The target runtime is CPython 3.12.14 on Linux x86-64. The validator requires an active virtual environment, the registered `jb2-python` kernelspec, and an explicit `BASE_URL` (empty is valid).

From the repository root, after activating the locked environment:

```sh
npm ci
node scripts/check-node-dependencies.mjs
BASE_URL="" sh tools/build.sh
```

The build driver checks the profile, verifies translation provenance, builds every enabled locale, stages Web Awesome assets, and validates the resulting publication artifact. It is not an alternative to running the repository's automated test suites.

## Editing the handbook

1. Edit the existing authoritative English Markdown or notebook source. Do not paste copies of repository implementation files into narrative documentation.
2. For a new page, add exactly one `project.toc` entry and verify its canonical route.
3. Use [MyST built-ins and approved Web Awesome directives](components/authoring-guide.md) for examples and accessible UI.
4. Submit translation updates with valid provenance when changing already-localized pages. New optional pages may publish in English first, but mandatory pages in `i18n/locales.yml` remain strict.
5. Keep laboratory deep links directed at their independent domains.

## Review and publication

The GitHub Actions workflow builds on `main` and deploys the accepted static site to GitHub Pages. Review changes in a branch or pull request first. A published homepage must not imply browser-side notebook execution; code and outputs must remain attributable to a verified build.

For low-level implementation and security controls, follow the [Architecture & Specification](architecture.md).
