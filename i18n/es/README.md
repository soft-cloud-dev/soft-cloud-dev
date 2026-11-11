---
title: Manual ejecutable de SoftCloud
description: Guías, cuadernos ejecutables, patrones de interfaz y laboratorios de sistemas con fuentes verificables.
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

EL MANUAL DE SOFTCLOUD

# Conocimiento de ingeniería reproducible.

Guías prácticas, cuadernos ejecutables y ejemplos de interfaz reutilizables, vinculados a sus fuentes.

[Empezar con una guía](guides.md) [Explorar cuadernos](notebooks.md)

:::::

:::::{div}
:class: sc-handbook__verification

### Verificación computacional

```python
import sys
print(sys.version.split()[0])
assert sys.version_info[:3] == (3, 12, 14)
```

**Perfil de ejecución requerido**

`CPython 3.12.14 · Linux x86-64 · jb2-python`

[Abrir cuaderno de verificación](notebooks/experiment.ipynb)

:::::

::::::

```{anywidget} ./widgets/voice-player.mjs
{
  "page": "readme",
  "locale": "es"
}
```

## Elige un punto de partida

::::::{div}
:class: sc-handbook__routes

:::::{div}
:class: sc-handbook__route sc-handbook__route--guide

### [Publica tu primera página](guides.md)

Conoce la estructura, el proceso de autoría y el modelo de publicación del manual SoftCloud.

**GUIDE**

:::::

:::::{div}
:class: sc-handbook__route sc-handbook__route--notebook

### [Reproduce una comprobación del entorno](notebooks/experiment.ipynb)

Ejecuta el cuaderno de verificación de referencia y comprende su perfil de ejecución controlado.

**NOTEBOOK**

:::::

:::::{div}
:class: sc-handbook__route sc-handbook__route--library

### [Encuentra un patrón de interfaz](ui-library.md)

Explora el catálogo de Web Awesome, los tokens de diseño y los ejemplos reutilizables.

**BIBLIOTECA UI**

:::::

::::::

::::::{div}
:class: sc-handbook__projects

### [Explora los proyectos de SoftCloud](projects.md)

[**SoftCloud Node Linux**](projects/linux.md) — Documentación reproducible de nodos Linux/Kubernetes.

[**FreeIPA**](https://freeipa.softcloud.dev/) — Laboratorio de identidad, políticas y gestión de acceso.

::::::

::::::{div}
:class: sc-handbook__overview

## Ingeniería reproducible, resultados verificables

SoftCloud publica investigación computacional, arquitectura de nube y documentación operativa junto con referencias ejecutables. Las dependencias sin fijar, los binarios divergentes, el estado implícito del entorno y los núcleos sin verificar dificultan reproducir resultados.

Su contrato de publicación utiliza dependencias bloqueadas con SHA-256, un entorno canónico CPython 3.12.14 sobre Linux x86-64, verificación previa estricta y CI/CD automatizado. Consulta [Arquitectura y especificación](architecture.md) y el [contexto y alcance operativo](introduction.md) para conocer los detalles.

::::::

:::::::
