---
title: "Mitwirkenden-Leitfaden"
description: "Publikationsvorgänge, Einrichtung der Umgebung, Validierung und Überprüfungsworkflow."
---

# Leitfaden für Mitwirkende

Dieser Leitfaden regelt den Workflow für Mitwirkende und die Publikationsabläufe. Architektonische Garantien verbleiben in [Architecture & Specification](architecture.md); Web-Awesome-Seitenkonventionen verbleiben im [component authoring guide](components/authoring-guide.md).
## Toolchain und Quelle der Wahrheit

- Projekt und TOC: [`myst.yml`](https://github.com/soft-cloud-dev/soft-cloud-dev/blob/main/myst.yml)
- Gesperrte Python-Distributionen: [`requirements.lock`](https://github.com/soft-cloud-dev/soft-cloud-dev/blob/main/requirements.lock)
- Lokaler Build-Treiber: [`tools/build.sh`](https://github.com/soft-cloud-dev/soft-cloud-dev/blob/main/tools/build.sh)
- Preflight: [`tools/check_profile.py`](https://github.com/soft-cloud-dev/soft-cloud-dev/blob/main/tools/check_profile.py)
- Publikations-Workflow: [`.github/workflows/deploy.yml`](https://github.com/soft-cloud-dev/soft-cloud-dev/blob/main/.github/workflows/deploy.yml)
## Lokale Entwicklung

Bereiten Sie die Umgebung mithilfe des im Repository festgelegten Python-Umgebungssetups vor und installieren Sie anschließend die JavaScript-Abhängigkeiten mit `npm ci`. Die Ziel-Laufzeitumgebung ist CPython 3.12.14 auf Linux x86-64. Der Validator erfordert eine aktive virtuelle Umgebung, den registrierten `jb2-python`-Kernelspec und ein explizites `BASE_URL` (leer ist gültig).

Aus dem Repository-Stammverzeichnis, nach dem Aktivieren der gesperrten Umgebung:

```sh
npm ci
node scripts/check-node-dependencies.mjs
BASE_URL="" sh tools/build.sh
```

Der Build-Treiber überprüft das Profil, verifiziert die Übersetzung Herkunft, baut jede aktivierte Locale, stellt Web Awesome-Assets bereit und validiert das resultierende Publikationsartefakt. Er ist keine Alternative zur Ausführung der automatisierten Test-Suiten des Repositorys.
## Bearbeiten des Handbuchs

1. Bearbeiten Sie die bestehenden maßgeblichen englischen Markdown- oder Notebook-Quellen. Fügen Sie keine Kopien von Repository-Implementierungsdateien in die narrative Dokumentation ein.
2. Fügen Sie für eine neue Seite genau einen `project.toc`-Eintrag hinzu und überprüfen Sie dessen kanonische Route.
3. Verwenden Sie [MyST-integrierte und genehmigte Web-Awesome-Direktiven](components/authoring-guide.md) für Beispiele und barrierefreie Benutzeroberflächen.
4. Reichen Sie Übersetzungsaktualisierungen mit gültiger Herkunft ein, wenn Sie bereits lokalisierte Seiten ändern. Neue optionale Seiten können zuerst auf Englisch veröffentlicht werden, aber obligatorische Seiten in `i18n/locales.yml` bleiben strikt.
5. Halten Sie Deep Links von Laboren auf deren unabhängige Domains gerichtet.
## Überprüfung und Veröffentlichung

Der GitHub Actions-Workflow baut auf `main` auf und stellt die akzeptierte statische Website auf GitHub Pages bereit. Überprüfen Sie Änderungen zunächst in einem Branch oder Pull Request. Eine veröffentlichte Startseite darf keine browserseitige Notebook-Ausführung implizieren; Code und Ausgaben müssen auf einen verifizierten Build zurückführbar sein.

Für Low-Level-Implementierung und Sicherheitskontrollen folgen Sie der [Architecture & Specification](architecture.md).
