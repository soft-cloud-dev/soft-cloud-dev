---
title: Guías
description: Procedimientos prácticos de autoría y publicación.
---

# Guías

```{anywidget} ./widgets/voice-player.mjs
{
  "page": "guides",
  "locale": "es"
}
```

Publica páginas vinculadas a sus fuentes mediante el proceso gobernado de MyST.

## Publica tu primera página

1. Elige la sección de documentación y crea un archivo fuente Markdown autorizado.
2. Registra la página una sola vez en el [`myst.yml`](https://github.com/soft-cloud-dev/soft-cloud-dev/blob/main/myst.yml) `project.toc`.
3. Ejecuta [`tools/check_profile.py`](https://github.com/soft-cloud-dev/soft-cloud-dev/blob/main/tools/check_profile.py) y la compilación con dependencias fijadas antes de abrir una solicitud de cambios.
4. Verifica las rutas localizadas y la procedencia de las traducciones antes de publicar.

## Más recursos

[Arquitectura y especificación](architecture.md) · [Cuadernos computacionales](notebooks.md) · [Biblioteca UI](ui-library.md) · [Proyectos](projects.md).
