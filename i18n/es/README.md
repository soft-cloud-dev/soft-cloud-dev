# Software Cloud

Bienvenido a **Software Cloud**, una plataforma de investigación y publicación computacional construida sobre **Jupyter Book 2** y alojada en **GitHub Pages** en [my.softcloud.dev](https://my.softcloud.dev/).

Software Cloud sirve como arquitectura abierta y referencia ejecutable para canalizaciones de investigación deterministas, arquitecturas en la nube reproducibles y cuadernos computacionales verificables.

---

## Pilares clave

- **Reproducibilidad criptográfica**: Todas las dependencias están fijadas a distribuciones exactas con resúmenes de integridad SHA-256 (`--require-hashes`, `--only-binary=:all:`), eliminando la deriva de dependencias.
- **Ejecución hermética**: Las ejecuciones computacionales apuntan al **CPython 3.12.14 canónico en Linux x86-64** con aislamiento explícito del entorno virtual.
- **Conformidad estricta del perfil**: Cada artefacto de publicación se somete a una verificación previa automatizada (`tools/check_profile.py`) antes de su compilación y despliegue.
- **Entrega continua**: El flujo CI/CD totalmente automatizado mediante GitHub Actions compila y verifica la documentación y los cuadernos en cada confirmación.

---

## Hoja de ruta de la documentación

- [**Introducción**](introduction.md): Antecedentes, filosofía de la plataforma y alcance operativo.
- [**Arquitectura y referencia del memorando**](architecture.md): Especificación técnica completa, diseño del repositorio, archivos base literales y cadena de herramientas de verificación.
- [**Cuaderno de verificación computacional**](notebooks/experiment.ipynb): Cuaderno de validación del entorno de ejecución que se ejecuta en el kernel `jb2-python`.
