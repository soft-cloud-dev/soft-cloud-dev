# Software Cloud

Willkommen bei **Software Cloud**, einer Plattform für computergestützte Forschung und Veröffentlichung auf Basis von **Jupyter Book 2**, gehostet über **GitHub Pages** unter [my.softcloud.dev](https://my.softcloud.dev/).

Software Cloud dient als offene Architektur und ausführbare Referenz für deterministische Forschungspipelines, reproduzierbare Cloud-Architekturen und verifizierbare Berechnungs-Notebooks.

---

## Zentrale Säulen

- **Kryptografische Reproduzierbarkeit**: Alle Abhängigkeiten sind mit SHA-256-Integritätsprüfsummen (`--require-hashes`, `--only-binary=:all:`) fest an exakte Distributionen gebunden, wodurch Abhängigkeitsdrift ausgeschlossen wird.
- **Hermetische Ausführung**: Berechnungsläufe zielen auf kanonisches **CPython 3.12.14 unter Linux x86-64** mit expliziter Isolierung der virtuellen Umgebung ab.
- **Strikte Profilkonformität**: Jedes Publikationsartefakt durchläuft vor dem Build und Deployment eine automatisierte Vorabprüfung (`tools/check_profile.py`).
- **Kontinuierliche Bereitstellung**: Vollautomatisiertes CI/CD über GitHub Actions erstellt und verifiziert Dokumentation und Notebooks bei jedem Commit.

---

## Dokumentations-Roadmap

- [**Einführung**](introduction.md): Hintergrund, Plattformphilosophie und operativer Umfang.
- [**Architektur & Memorandumsreferenz**](architecture.md): Vollständige technische Spezifikation, Repository-Struktur, wortgetreue Gerüstdateien und Verifikations-Toolchain.
- [**Notebook zur Berechnungsverifikation**](notebooks/experiment.ipynb): Notebook zur Laufzeitvalidierung, das im `jb2-python`-Kernel ausgeführt wird.
