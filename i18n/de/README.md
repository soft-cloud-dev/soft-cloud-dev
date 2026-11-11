---
title: Ausführbares SoftCloud-Handbuch
description: Anleitungen, ausführbare Notebooks, UI-Muster und Systemlabore mit überprüfbaren Quellen.
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

DAS SOFTCLOUD-HANDBUCH

# Ingenieurwissen, das sich reproduzieren lässt.

Praktische Anleitungen, ausführbare Notebooks und wiederverwendbare UI-Beispiele — mit ihren Quellen verknüpft.

[Mit einer Anleitung beginnen](guides.md) [Notebooks durchsuchen](notebooks.md)

:::::

:::::{div}
:class: sc-handbook__verification

### Rechnerische Verifikation

```python
import sys
print(sys.version.split()[0])
assert sys.version_info[:3] == (3, 12, 14)
```

**Erforderliches Ausführungsprofil**

`CPython 3.12.14 · Linux x86-64 · jb2-python`

[Verifikations-Notebook öffnen](notebooks/experiment.ipynb)

:::::

::::::

```{anywidget} ./widgets/voice-player.mjs
{
  "page": "readme",
  "locale": "de"
}
```

## Einen Einstieg wählen

::::::{div}
:class: sc-handbook__routes

:::::{div}
:class: sc-handbook__route sc-handbook__route--guide

### [Erste Seite veröffentlichen](guides.md)

Lernen Sie Struktur, Erstellung und Veröffentlichungsablauf des SoftCloud-Handbuchs kennen.

**GUIDE**

:::::

:::::{div}
:class: sc-handbook__route sc-handbook__route--notebook

### [Umgebungsprüfung reproduzieren](notebooks/experiment.ipynb)

Führen Sie das Referenz-Notebook zur Umgebungsverifikation aus und verstehen Sie das kontrollierte Ausführungsprofil.

**NOTEBOOK**

:::::

:::::{div}
:class: sc-handbook__route sc-handbook__route--library

### [Wiederverwendbares UI-Muster finden](ui-library.md)

Entdecken Sie den Web-Awesome-Katalog, Design-Tokens und wiederverwendbare Oberflächenbeispiele.

**UI-BIBLIOTHEK**

:::::

::::::

::::::{div}
:class: sc-handbook__projects

### [SoftCloud-Projekte entdecken](projects.md)

[**SoftCloud Node Linux**](projects/linux.md) — Reproduzierbare Dokumentation für Linux/Kubernetes-Knoten.

[**FreeIPA**](https://freeipa.softcloud.dev/) — Labor für Identität, Richtlinien und Zugriffsverwaltung.

::::::

::::::{div}
:class: sc-handbook__overview

## Reproduzierbare Entwicklung, überprüfbare Ergebnisse

SoftCloud veröffentlicht computergestützte Forschung, Cloud-Architektur und Betriebshandbücher zusammen mit ausführbaren Referenzen. Nicht fixierte Abhängigkeiten, abweichende Binärdateien, versteckter Umgebungszustand und ungeprüfte Laufzeit-Kernels erschweren die Reproduktion.

Der Publikationsvertrag umfasst SHA-256-gesicherte Abhängigkeiten, eine kanonische CPython-3.12.14-Laufzeit unter Linux x86-64, strenge Vorabprüfung und automatisierte CI/CD. Lesen Sie die [Architektur und Spezifikation](architecture.md) sowie den [Hintergrund und Betriebsumfang](introduction.md) für weitere Einzelheiten.

::::::

:::::::
