---
title: Poradniki
description: Praktyczne procedury tworzenia treści i publikowania.
---

# Poradniki

```{anywidget} ./widgets/voice-player.mjs
{
  "page": "guides",
  "locale": "pl"
}
```

Publikuj strony powiązane ze źródłami w kontrolowanym potoku MyST.

## Opublikuj pierwszą stronę

1. Wybierz odpowiednią sekcję dokumentacji i utwórz źródłowy plik Markdown.
2. Zarejestruj stronę dokładnie raz w głównym [`myst.yml`](https://github.com/soft-cloud-dev/soft-cloud-dev/blob/main/myst.yml) `project.toc`.
3. Uruchom [`tools/check_profile.py`](https://github.com/soft-cloud-dev/soft-cloud-dev/blob/main/tools/check_profile.py) oraz kompilację z zablokowanymi zależnościami przed otwarciem pull requestu.
4. Przed publikacją sprawdź lokalizowane adresy i pochodzenie tłumaczeń.

## Dalsza lektura

[Architektura i specyfikacja](architecture.md) · [Notatniki obliczeniowe](notebooks.md) · [Biblioteka UI](ui-library.md) · [Projekty](projects.md).
