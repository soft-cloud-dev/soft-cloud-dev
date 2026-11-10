---
title: Podręcznik wykonywalny SoftCloud
description: Poradniki, wykonywalne notatniki, wzorce UI i laboratoria systemowe z weryfikowalnymi źródłami.
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

PODRĘCZNIK SOFTCLOUD

# Wiedza inżynierska, którą można odtworzyć.

Praktyczne poradniki, wykonywalne notatniki i wielokrotnego użytku przykłady UI — powiązane ze źródłem.

[Rozpocznij od poradnika](guides.md) [Przeglądaj notatniki](notebooks.md)

:::::

:::::{div}
:class: sc-handbook__verification

### Weryfikacja obliczeniowa

```python
import sys
print(sys.version.split()[0])
assert sys.version_info[:3] == (3, 12, 14)
```

**Wymagany profil wykonania**

`CPython 3.12.14 · Linux x86-64 · jb2-python`

[Otwórz notatnik weryfikacyjny](notebooks/experiment.ipynb)

:::::

::::::

## Wybierz punkt początkowy

::::::{div}
:class: sc-handbook__routes

:::::{div}
:class: sc-handbook__route sc-handbook__route--guide

### [Opublikuj pierwszą stronę](guides.md)

Poznaj strukturę dokumentacji, sposób tworzenia treści i proces publikowania podręcznika SoftCloud.

**GUIDE**

:::::

:::::{div}
:class: sc-handbook__route sc-handbook__route--notebook

### [Odtwórz kontrolę środowiska](notebooks/experiment.ipynb)

Uruchom referencyjny notatnik weryfikujący środowisko i poznaj kontrolowany profil wykonania.

**NOTEBOOK**

:::::

:::::{div}
:class: sc-handbook__route sc-handbook__route--library

### [Znajdź wzorzec interfejsu](ui-library.md)

Przeglądaj katalog Web Awesome, tokeny projektowe i przykłady interfejsów do ponownego użycia.

**BIBLIOTEKA UI**

:::::

::::::

::::::{div}
:class: sc-handbook__projects

### [Poznaj projekty SoftCloud](projects.md)

[**SoftCloud Node Linux**](projects/linux.md) — Powtarzalna dokumentacja węzłów Linux/Kubernetes.

[**FreeIPA**](https://freeipa.softcloud.dev/) — Laboratorium tożsamości, zasad i zarządzania dostępem.

::::::

::::::{div}
:class: sc-handbook__overview

## Powtarzalna inżynieria, weryfikowalne wyniki

SoftCloud publikuje badania obliczeniowe, architekturę chmurową i wskazówki operacyjne wraz z wykonywalnymi materiałami referencyjnymi. Nieprzypięte zależności, różne wersje plików binarnych, ukryty stan środowiska i nieweryfikowane jądra wykonawcze utrudniają odtwarzanie wyników.

Kontrakt publikacji obejmuje blokowanie zależności skrótami SHA-256, kanoniczne środowisko CPython 3.12.14 na Linux x86-64, ścisłą kontrolę wstępną i zautomatyzowane CI/CD. Zobacz [Architekturę i specyfikację](architecture.md) oraz [kontekst i zakres operacyjny](introduction.md) aby poznać założenia.

::::::

:::::::
