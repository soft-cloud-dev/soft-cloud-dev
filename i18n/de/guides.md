---
title: Anleitungen
description: Praktische Abläufe für Autorenschaft und Veröffentlichung.
---

# Anleitungen

```{anywidget} ./widgets/voice-player.mjs
{
  "page": "guides",
  "locale": "de"
}
```

Veröffentlichen Sie quellengestützte Seiten über die kontrollierte MyST-Pipeline.

## Erste Seite veröffentlichen

1. Wählen Sie den passenden Dokumentationsbereich und erstellen Sie eine maßgebliche Markdown-Quelldatei.
2. Registrieren Sie die Seite genau einmal in der zentralen [`myst.yml`](https://github.com/soft-cloud-dev/soft-cloud-dev/blob/main/myst.yml) `project.toc`.
3. Führen Sie [`tools/check_profile.py`](https://github.com/soft-cloud-dev/soft-cloud-dev/blob/main/tools/check_profile.py) und den gesperrten Build vor dem Pull Request aus.
4. Prüfen Sie vor der Veröffentlichung lokalisierte Routen und Übersetzungsnachweise.

## Weitere Informationen

[Architektur und Spezifikation](architecture.md) · [Rechen-Notebooks](notebooks.md) · [UI-Bibliothek](ui-library.md) · [Projekte](projects.md).
