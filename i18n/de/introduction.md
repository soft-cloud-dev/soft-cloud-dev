# Einführung

```{anywidget} ./widgets/voice-player.mjs
{
  "page": "introduction",
  "locale": "de"
}
```

**Software Cloud** bietet ein offenes, reproduzierbares Framework für computergestützte Forschung, Architekturdokumentation und Cloud-Software-Engineering.

---

## Die Herausforderung der rechnerischen Reproduzierbarkeit

Wissenschaftliche Forschung und hochzuverlässige Softwaresysteme hängen entscheidend von Reproduzierbarkeit ab. Moderne Entwicklungsabläufe leiden jedoch häufig unter subtilem Umgebungs-Nichtdeterminismus:

- Nicht fixierte transitive Abhängigkeiten, die sich im Upstream stillschweigend ändern.
- Abweichende Plattform-Binärdateien zwischen macOS, Linux und Windows.
- Implizite Lecks von Umgebungsvariablen, die Ausführungspfade beeinflussen.
- Unüberwachte Laufzeit-Kernel-Versionen, die zu abweichenden Ausführungsergebnissen führen.

Um diese Fehlermodi zu beheben, implementiert die Plattform Software Cloud ein streng kontrolliertes Publikationsprofil.

---

## Operativer Umfang

Software Cloud begegnet diesen Herausforderungen durch vier miteinander verbundene Mechanismen:

1. **Spezifikation durch Memorandum**: Kernarchitektur des Repositorys, Lizenzierung, Tooling und Pipeline-Konfigurationen sind als formale Spezifikationen kodifiziert.
2. **Deterministische Wheelhouse-Auflösung**: Direkte Anforderungen sind in kryptografischen Wheel-Prüfsummen fixiert, die ausschließlich gegen Standard-Wheels für Linux/x86-64 aufgelöst werden.
3. **Automatisierte Laufzeitverifikation**: Jeder Pull Request und Release-Build führt ein Vorab-Audit durch, das die Aktivierung der virtuellen Umgebung, die Herkunft des Interpreters, das Vorhandensein von Jupyter Server und die Vollständigkeit des Inhaltsverzeichnisses prüft.
4. **Live-Artefakt-Publikation**: Akzeptierte Builds werden direkt als statische Websites mit hochperformanter HTTPS-Auslieferung unter [my.softcloud.dev](https://my.softcloud.dev/) veröffentlicht.

---

## Nächste Schritte

Um das technische Low-Level-Design, das Repository-Gerüst und die Implementierungen der Toolchain zu erkunden, fahren Sie mit der [**Architektur & Memorandumsreferenz**](architecture.md) fort.
