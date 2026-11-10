---
title: "Przewodnik współtwórcy"
description: "Operacje publikacyjne, konfiguracja środowiska, walidacja i przepływ pracy recenzji."
---

# Przewodnik dla współtwórców

Niniejszy przewodnik reguluje przepływ pracy współtwórców oraz operacje publikacyjne. Gwarancje architektoniczne pozostają w [Architecture & Specification](architecture.md); konwencje stron Web Awesome pozostają w [component authoring guide](components/authoring-guide.md).
## Narzędzia i źródło prawdy

- Projekt i spis treści: [`myst.yml`](https://github.com/soft-cloud-dev/soft-cloud-dev/blob/main/myst.yml)
- Zablokowane dystrybucje Python: [`requirements.lock`](https://github.com/soft-cloud-dev/soft-cloud-dev/blob/main/requirements.lock)
- Lokalny sterownik kompilacji: [`tools/build.sh`](https://github.com/soft-cloud-dev/soft-cloud-dev/blob/main/tools/build.sh)
- Weryfikacja wstępna: [`tools/check_profile.py`](https://github.com/soft-cloud-dev/soft-cloud-dev/blob/main/tools/check_profile.py)
- Przepływ pracy publikacji: [`.github/workflows/deploy.yml`](https://github.com/soft-cloud-dev/soft-cloud-dev/blob/main/.github/workflows/deploy.yml)
## Lokalny rozwój

Przygotuj środowisko, korzystając z przypiętej konfiguracji środowiska Python w repozytorium, a następnie zainstaluj zależności JavaScript za pomocą `npm ci`. Docelowym środowiskiem uruchomieniowym jest CPython 3.12.14 na systemie Linux x86-64. Walidator wymaga aktywnego środowiska wirtualnego, zarejestrowanego specyfikatora jądra `jb2-python` oraz jawnego pliku `BASE_URL` (pusty plik jest poprawny).

Z głównego katalogu repozytorium, po aktywacji zablokowanego środowiska:

```sh
npm ci
node scripts/check-node-dependencies.mjs
BASE_URL="" sh tools/build.sh
```

Sterownik kompilacji sprawdza profil, weryfikuje pochodzenie tłumaczenia, buduje wszystkie włączone wersje językowe, przygotowuje zasoby Web Awesome oraz waliduje wynikowy artefakt publikacji. Nie jest to alternatywa dla uruchamiania zautomatyzowanych zestawów testów repozytorium.
## Edycja podręcznika

1. Edytuj istniejące, wiążące źródło w języku angielskim w formacie Markdown lub jako notatnik. Nie wklejaj kopii plików implementacyjnych repozytorium do dokumentacji narracyjnej.
2. W przypadku nowej strony dodaj dokładnie jeden wpis `project.toc` i zweryfikuj jego kanoniczną ścieżkę.
3. Używaj [wbudowanych elementów języka MyST oraz zatwierdzonych dyrektyw Web Awesome](components/authoring-guide.md) do prezentacji przykładów oraz dostępnego interfejsu użytkownika.
4. Zgłaszaj aktualizacje tłumaczeń z poprawnym pochodzeniem (provenance) podczas modyfikowania stron już zlokalizowanych. Nowe strony opcjonalne mogą być publikowane najpierw w języku angielskim, jednak strony obowiązkowe w `i18n/locales.yml` pozostają objęte ścisłymi wymaganiami.
5. Utrzymuj głębokie linki (deep links) do laboratoriów skierowane do ich niezależnych domen.
## Przegląd i publikacja

Przepływ pracy GitHub Actions opiera się na `main` i wdraża zaakceptowaną witrynę statyczną na GitHub Pages. Najpierw należy przejrzeć zmiany w gałęzi (branch) lub pul requestcie. Opublikowana strona główna nie może sugerować wykonywania notatników po stronie przeglądarki; kod i wyniki muszą w dalszym ciągu pochodzić ze zweryfikowanej kompilacji.

Aby zapoznać się z implementacją niskiego poziomu i kontrolami bezpieczeństwa, skorzystaj z sekcji [Architecture & Specification](architecture.md).
