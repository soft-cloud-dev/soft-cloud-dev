# Introducción

```{anywidget} ./widgets/voice-player.mjs
{
  "page": "introduction",
  "locale": "es"
}
```

**Software Cloud** proporciona un marco abierto y reproducible para la investigación computacional, la documentación arquitectónica y la ingeniería de software en la nube.

---

## El desafío de la reproducibilidad computacional

La investigación científica y los sistemas de software de alta confiabilidad dependen críticamente de la reproducibilidad. Sin embargo, los flujos de trabajo de desarrollo modernos sufren con frecuencia un sutil no determinismo ambiental:

- Dependencias transitivas no fijadas que cambian silenciosamente en origen.
- Binarios de plataforma divergentes entre macOS, Linux y Windows.
- Fugas implícitas de variables de entorno que afectan las rutas de ejecución.
- Versiones de kernel en tiempo de ejecución no supervisadas que producen resultados divergentes.

Para resolver estos modos de fallo, la plataforma Software Cloud implementa un perfil de publicación estrictamente gobernado.

---

## Alcance operativo

Software Cloud aborda estos desafíos mediante cuatro mecanismos interconectados:

1. **Especificación mediante memorando**: La arquitectura central del repositorio, las licencias, las herramientas y las configuraciones de canalización están codificadas como especificaciones formales.
2. **Resolución determinista de paquetes wheel**: Los requisitos directos se bloquean en resúmenes criptográficos de paquetes wheel resueltos exclusivamente frente a paquetes estándar de Linux/x86-64.
3. **Verificación automatizada del entorno de ejecución**: Cada solicitud de extracción y compilación de lanzamiento ejecuta una auditoría previa que verifica la activación del entorno virtual, la procedencia del intérprete, la presencia de Jupyter Server y la integridad de la tabla de contenidos.
4. **Publicación de artefactos en vivo**: Las compilaciones aceptadas se publican directamente como sitios estáticos con entrega HTTPS de alto rendimiento en [my.softcloud.dev](https://my.softcloud.dev/).

---

## Próximos pasos

Para explorar el diseño técnico de bajo nivel, la estructura base del repositorio y las implementaciones de la cadena de herramientas, continúe con [**Arquitectura y referencia del memorando**](architecture.md).
