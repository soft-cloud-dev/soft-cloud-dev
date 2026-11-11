---
title: "Guide des contributeurs"
description: "Opérations de publication, configuration de l'environnement, validation et flux de travail de révision."
---

# Guide des contributeurs

```{anywidget} ./widgets/voice-player.mjs
{
  "page": "contributing",
  "locale": "fr"
}
```

Ce guide régit le flux de travail des contributeurs et les opérations de publication. Les garanties architecturales restent dans [Architecture & Specification](architecture.md) ; les conventions des pages Web Awesome restent dans le [component authoring guide](components/authoring-guide.md).
## Chaîne d'outils et source de vérité

- Projet et TOC : [`myst.yml`](https://github.com/soft-cloud-dev/soft-cloud-dev/blob/main/myst.yml)
- Distributions Python verrouillées : [`requirements.lock`](https://github.com/soft-cloud-dev/soft-cloud-dev/blob/main/requirements.lock)
- Pilote de construction local : [`tools/build.sh`](https://github.com/soft-cloud-dev/soft-cloud-dev/blob/main/tools/build.sh)
- Contrôle préliminaire : [`tools/check_profile.py`](https://github.com/soft-cloud-dev/soft-cloud-dev/blob/main/tools/check_profile.py)
- Flux de publication : [`.github/workflows/deploy.yml`](https://github.com/soft-cloud-dev/soft-cloud-dev/blob/main/.github/workflows/deploy.yml)
## Développement local

Préparez l'environnement en utilisant la configuration de l'environnement Python épinglé du dépôt, puis installez les dépendances JavaScript avec `npm ci`. L'environnement d'exécution cible est CPython 3.12.14 sur Linux x86-64. Le validateur requiert un environnement virtuel actif, le profil de noyau `jb2-python` enregistré et un `BASE_URL` explicite (vide est valide).

Depuis la racine du dépôt, après avoir activé l'environnement verrouillé :

```sh
npm ci
node scripts/check-node-dependencies.mjs
BASE_URL="" sh tools/build.sh
```

Le pilote de compilation vérifie le profil, valide la provenance de la traduction, compile toutes les langues activées, prépare les ressources Web Awesome et valide l'artefact de publication résultant. Il ne remplace pas l'exécution des suites de tests automatisés du dépôt.
## Édition du manuel

1. Modifiez la source Markdown ou le carnet de calcul (notebook) en anglais faisant autorité. Ne collez pas de copies de fichiers d'implémentation du dépôt dans la documentation narrative.
2. Pour une nouvelle page, ajoutez exactement une entrée `project.toc` et vérifiez sa route canonique.
3. Utilisez les [éléments intégrés MyST et les directives Web Awesome approuvées](components/authoring-guide.md) pour les exemples et l'interface utilisateur accessible.
4. Soumettez les mises à jour de traduction avec une provenance valide lors de la modification de pages déjà localisées. Les nouvelles pages optionnelles peuvent être publiées en anglais d'abord, mais les pages obligatoires dans `i18n/locales.yml` restent strictes.
5. Maintenez les liens profonds du laboratoire dirigés vers leurs domaines indépendants.
## Revue et publication

Le flux de travail GitHub Actions s'appuie sur `main` et déploie le site statique accepté sur GitHub Pages. Examinez d'abord les modifications dans une branche ou une demande de fusion (*pull request*). Une page d'accueil publiée ne doit pas suggérer une exécution de carnet de calcul côté navigateur ; le code et les résultats doivent rester attribuables à une construction vérifiée.

Pour l'implémentation de bas niveau et les contrôles de sécurité, suivez l'élément [Architecture & Specification](architecture.md).
