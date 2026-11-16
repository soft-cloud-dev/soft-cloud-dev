# Introduction

```{anywidget} ./widgets/voice-player.mjs
{
  "page": "introduction",
  "locale": "fr"
}
```

**Software Cloud** fournit un cadre ouvert et reproductible pour la recherche informatique, la documentation architecturale et l'ingénierie logicielle cloud.

---

## Le défi de la reproductibilité informatique

La recherche scientifique et les systèmes logiciels à haute fiabilité dépendent de manière critique de la reproductibilité. Cependant, les flux de développement modernes souffrent fréquemment d'un subtil non-déterminisme environnemental :

- Des dépendances transitives non épinglées qui changent silencieusement en amont.
- Des binaires de plateforme divergents entre macOS, Linux et Windows.
- Des fuites implicites de variables d'environnement affectant les chemins d'exécution.
- Des versions non surveillées du noyau d'exécution entraînant des résultats d'exécution divergents.

Pour résoudre ces modes de défaillance, la plateforme Software Cloud met en œuvre un profil de publication strictement gouverné.

---

## Périmètre opérationnel

Software Cloud répond à ces défis grâce à quatre mécanismes interconnectés :

1. **Spécification par mémorandum** : L'architecture centrale du dépôt, les licences, l'outillage et les configurations de pipeline sont codifiés sous forme de spécifications formelles.
2. **Résolution déterministe du wheelhouse** : Les exigences directes sont verrouillées dans des empreintes cryptographiques de paquets wheel résolues exclusivement par rapport aux paquets standard Linux/x86-64.
3. **Vérification automatisée de l'environnement d'exécution** : Chaque demande de fusion et compilation de version exécute un audit préalable vérifiant l'activation de l'environnement virtuel, la provenance de l'interpréteur, la présence de Jupyter Server et l'exhaustivité de la table des matières.
4. **Publication d'artefacts en direct** : Les compilations acceptées sont publiées directement sous forme de sites statiques avec une diffusion HTTPS haute performance sur [my.softcloud.dev](https://my.softcloud.dev/).

---

## Prochaines étapes

Pour explorer la conception technique de bas niveau, l'échafaudage du dépôt et les implémentations de la chaîne d'outils, passez à la section [**Architecture et référence du mémorandum**](architecture.md).
