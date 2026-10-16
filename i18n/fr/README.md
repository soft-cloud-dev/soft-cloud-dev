# Software Cloud

Bienvenue sur **Software Cloud**, une plateforme de recherche et de publication informatique construite avec **Jupyter Book 2** et hébergée sur **GitHub Pages** à l'adresse [my.softcloud.dev](https://my.softcloud.dev/).

Software Cloud sert d'architecture ouverte et de référence exécutable pour les pipelines de recherche déterministes, les architectures cloud reproductibles et les carnets de calcul vérifiables.

---

## Piliers clés

- **Reproductibilité cryptographique** : Toutes les dépendances sont verrouillées sur des distributions exactes avec des empreintes d'intégrité SHA-256 (`--require-hashes`, `--only-binary=:all:`), éliminant ainsi la dérive des dépendances.
- **Exécution hermétique** : Les exécutions informatiques ciblent **CPython 3.12.14 canonique sous Linux x86-64** avec une isolation explicite de l'environnement virtuel.
- **Conformité stricte au profil** : Chaque artefact de publication fait l'objet d'une vérification préalable automatisée (`tools/check_profile.py`) avant la compilation et le déploiement.
- **Livraison continue** : Le pipeline CI/CD entièrement automatisé via GitHub Actions compile et vérifie la documentation et les carnets à chaque validation.

---

## Feuille de route de la documentation

- [**Introduction**](introduction.md) : Contexte, philosophie de la plateforme et périmètre opérationnel.
- [**Architecture et référence du mémorandum**](architecture.md) : Spécification technique complète, structure du dépôt, fichiers d'échafaudage textuels et chaîne d'outils de vérification.
- [**Carnet de vérification informatique**](notebooks/experiment.ipynb) : Carnet de validation de l'environnement d'exécution s'exécutant dans le noyau `jb2-python`.
