---
title: Manuel exécutable SoftCloud
description: Guides, notebooks exécutables, modèles d'interface et laboratoires système aux sources vérifiables.
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

LE MANUEL SOFTCLOUD

# Un savoir d'ingénierie reproductible.

Des guides pratiques, des notebooks exécutables et des exemples d'interface réutilisables, reliés à leurs sources.

[Commencer par un guide](guides.md) [Parcourir les notebooks](notebooks.md)

:::::

:::::{div}
:class: sc-handbook__verification

### Vérification computationnelle

```python
import sys
print(sys.version.split()[0])
assert sys.version_info[:3] == (3, 12, 14)
```

**Profil d'exécution requis**

`CPython 3.12.14 · Linux x86-64 · jb2-python`

[Ouvrir le notebook de vérification](notebooks/experiment.ipynb)

:::::

::::::

```{anywidget} ./widgets/voice-player.mjs
{
  "page": "readme",
  "locale": "fr"
}
```

## Choisir un point de départ

::::::{div}
:class: sc-handbook__routes

:::::{div}
:class: sc-handbook__route sc-handbook__route--guide

### [Publier sa première page](guides.md)

Découvrez la structure documentaire, le processus de rédaction et le modèle de publication du manuel SoftCloud.

**GUIDE**

:::::

:::::{div}
:class: sc-handbook__route sc-handbook__route--notebook

### [Reproduire un contrôle d'environnement](notebooks/experiment.ipynb)

Exécutez le notebook de vérification de référence et comprenez son profil d'exécution contrôlé.

**NOTEBOOK**

:::::

:::::{div}
:class: sc-handbook__route sc-handbook__route--library

### [Trouver un modèle d'interface réutilisable](ui-library.md)

Découvrez le catalogue Web Awesome, les jetons de conception et les exemples d'interface réutilisables.

**BIBLIOTHÈQUE UI**

:::::

::::::

::::::{div}
:class: sc-handbook__projects

### [Découvrir les projets SoftCloud](projects.md)

[**SoftCloud Node Linux**](projects/linux.md) — Documentation reproductible des nœuds Linux/Kubernetes.

[**FreeIPA**](https://freeipa.softcloud.dev/) — Laboratoire d'identité, de politiques et de gestion des accès.

::::::

::::::{div}
:class: sc-handbook__overview

## Ingénierie reproductible, résultats vérifiables

SoftCloud publie des recherches computationnelles, des architectures cloud et des guides opérationnels avec des références exécutables. Des dépendances non figées, des binaires divergents, un état d'environnement implicite et des noyaux d'exécution non vérifiés nuisent à la reproductibilité.

Son contrat de publication s'appuie sur des dépendances verrouillées par SHA-256, un environnement CPython 3.12.14 sous Linux x86-64, des vérifications préalables strictes et une CI/CD automatisée. Consultez [Architecture et spécification](architecture.md) ainsi que le [contexte et périmètre opérationnel](introduction.md) pour davantage de détails.

::::::

:::::::
