---
title: "Guía de colaboradores"
description: "Operaciones de publicación, configuración del entorno, validación y flujo de trabajo de revisión."
---

# Guía de colaboradores

Esta guía regula el flujo de trabajo de los colaboradores y las operaciones de publicación. Las garantías arquitectónicas se mantienen en [Architecture & Specification](architecture.md); las convenciones de las páginas de Web Awesome se mantienen en la [component authoring guide](components/authoring-guide.md).
## Cadena de herramientas y fuente de la verdad

- Proyecto y TOC: [`myst.yml`](https://github.com/soft-cloud-dev/soft-cloud-dev/blob/main/myst.yml)
- Distribuciones de Python bloqueadas: [`requirements.lock`](https://github.com/soft-cloud-dev/soft-cloud-dev/blob/main/requirements.lock)
- Controlador de compilación local: [`tools/build.sh`](https://github.com/soft-cloud-dev/soft-cloud-dev/blob/main/tools/build.sh)
- Verificación previa (Preflight): [`tools/check_profile.py`](https://github.com/soft-cloud-dev/soft-cloud-dev/blob/main/tools/check_profile.py)
- Flujo de trabajo de publicación: [`.github/workflows/deploy.yml`](https://github.com/soft-cloud-dev/soft-cloud-dev/blob/main/.github/workflows/deploy.yml)
## Desarrollo local

Prepare el entorno utilizando la configuración del entorno de Python fijada del repositorio, luego instale las dependencias de JavaScript con `npm ci`. El tiempo de ejecución de destino es CPython 3.12.14 en Linux x86-64. El validador requiere un entorno virtual activo, el `jb2-python` kernelspec registrado y un `BASE_URL` explícito (vacío es válido).

Desde la raíz del repositorio, después de activar el entorno bloqueado:

```sh
npm ci
node scripts/check-node-dependencies.mjs
BASE_URL="" sh tools/build.sh
```

El controlador de compilación verifica el perfil, comprueba la procedencia de la traducción, compila todos los locales habilitados, prepara los recursos de Web Awesome y valida el artefacto de publicación resultante. No es una alternativa a la ejecución de las suites de pruebas automatizadas del repositorio.
## Edición del manual

1. Edite el código fuente en Markdown o cuaderno en inglés oficial existente. No pegue copias de los archivos de implementación del repositorio en la documentación narrativa.
2. Para una página nueva, agregue exactamente una entrada `project.toc` y verifique su ruta canónica.
3. Utilice los [elementos integrados de MyST y las directivas aprobadas de Web Awesome](components/authoring-guide.md) para ejemplos y una interfaz de usuario accesible.
4. Envíe las actualizaciones de traducción con una procedencia válida al modificar páginas que ya están localizadas. Las nuevas páginas opcionales se pueden publicar primero en inglés, pero las páginas obligatorias en `i18n/locales.yml` siguen siendo estrictas.
5. Mantenga los enlaces profundos del laboratorio dirigidos a sus dominios independientes.
## Revisión y publicación

El flujo de trabajo de GitHub Actions se basa en `main` y despliega el sitio estático aceptado en GitHub Pages. Primero revise los cambios en una rama o *pull request*. Una página de inicio publicada no debe sugerir la ejecución de cuadernos en el lado del navegador; el código y las salidas deben seguir siendo atribuibles a una compilación verificada.

Para la implementación de bajo nivel y los controles de seguridad, siga la sección [Architecture & Specification](architecture.md).
