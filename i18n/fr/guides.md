---
title: Guides
description: Procédures pratiques de rédaction et de publication.
---

# Guides

```{anywidget} ./widgets/voice-player.mjs
{
  "page": "guides",
  "locale": "fr"
}
```

Publiez des pages reliées à leurs sources avec le pipeline MyST contrôlé.

## Publier sa première page

1. Choisissez la rubrique documentaire appropriée et créez un fichier source Markdown faisant autorité.
2. Enregistrez la page une seule fois dans le [`myst.yml`](https://github.com/soft-cloud-dev/soft-cloud-dev/blob/main/myst.yml) `project.toc`.
3. Exécutez [`tools/check_profile.py`](https://github.com/soft-cloud-dev/soft-cloud-dev/blob/main/tools/check_profile.py) et la compilation à dépendances verrouillées avant d'ouvrir une demande de fusion.
4. Vérifiez les routes localisées et la provenance des traductions avant publication.

## Pour aller plus loin

[Architecture et spécification](architecture.md) · [Notebooks de calcul](notebooks.md) · [Bibliothèque UI](ui-library.md) · [Projets](projects.md).
