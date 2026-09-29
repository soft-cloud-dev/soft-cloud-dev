# Software Cloud

Welcome to **Software Cloud**, a research and computational publishing platform built on **Jupyter Book 2** and hosted on **GitHub Pages** at [my.softcloud.dev](https://my.softcloud.dev/).

Software Cloud serves as an open architecture and executable reference for deterministic research pipelines, reproducible cloud architectures, and verifiable computational notebooks.

---

## Key Pillars

- **Cryptographic Reproducibility**: All dependencies are locked to exact distributions with SHA-256 integrity hashes (`--require-hashes`, `--only-binary=:all:`), eliminating dependency drift.
- **Hermetic Execution**: Computational runs target canonical **CPython 3.12.14 on Linux x86-64** with explicit virtual environment isolation.
- **Strict Profile Conformance**: Every publication artifact undergoes automated preflight verification (`tools/check_profile.py`) before build and deployment.
- **Continuous Delivery**: Fully automated CI/CD via GitHub Actions builds and verifies documentation and notebooks upon every commit.

---

## Documentation Roadmap

- [**Introduction**](introduction.md): Background, platform philosophy, and operational scope.
- [**Architecture & Memorandum Reference**](architecture.md): Full technical specification, repository layout, verbatim scaffold files, and verification toolchain.
- [**Computational Verification Notebook**](notebooks/experiment.ipynb): Runtime validation notebook executing in the `jb2-python` kernel.
