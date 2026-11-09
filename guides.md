---
title: Guides
description: Practical authoring and release workflows for the SoftCloud Executable Handbook.
---

# Guides

Start with an authoring task and follow links to the canonical source files and tooling.

## Publish your first page

1. Choose the appropriate section of the [handbook](handbook.md): systems, notebooks, or UI reference.
2. Author a MyST Markdown page following the [MyST and Web Awesome authoring guide](components/authoring-guide.md).
3. Register the file once in the root [`myst.yml`](https://github.com/soft-cloud-dev/soft-cloud-dev/blob/main/myst.yml) `project.toc`.
4. Run the [publication profile validator](https://github.com/soft-cloud-dev/soft-cloud-dev/blob/main/tools/check_profile.py) and build with the repository's pinned environment.
5. Submit the change for review; do not bypass multilingual provenance or artifact verification.

For the exact build commands and prerequisites, use the [Contributor Guide](contributing.md).

## Choose the right source

- **Platform architecture:** [Architecture & Specification](architecture.md).
- **Executable examples:** [Computational notebooks](notebooks.md).
- **Components, design tokens, and UI patterns:** [UI Library](components/index.md).
- **Systems engineering laboratories:** [Projects](projects.md).

The English content is authoritative. A localized page is published only when its approved translation and provenance are valid.
