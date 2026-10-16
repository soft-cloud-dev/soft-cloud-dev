# Software Cloud

Witamy w **Software Cloud**, platformie publikacji obliczeniowych i badawczych zbudowanej w oparciu o **Jupyter Book 2** i hostowanej na **GitHub Pages** pod adresem [my.softcloud.dev](https://my.softcloud.dev/).

Software Cloud służy jako otwarta architektura i wykonywalna referencja dla deterministycznych potoków badawczych, powtarzalnych architektur chmurowych oraz weryfikowalnych notatników obliczeniowych.

---

## Kluczowe filary

- **Powtarzalność kryptograficzna**: Wszystkie zależności są przypięte do dokładnych dystrybucji z kryptograficznymi skrótami integralności SHA-256 (`--require-hashes`, `--only-binary=:all:`), co eliminuje dryf zależności.
- **Wykonywanie hermetyczne**: Przebiegi obliczeniowe są ukierunkowane na kanoniczny **CPython 3.12.14 na platformie Linux x86-64** z jawną izolacją środowiska wirtualnego.
- **Ścisła zgodność z profilem**: Każdy artefakt publikacji przechodzi automatyczną weryfikację wstępną (`tools/check_profile.py`) przed kompilacją i wdrożeniem.
- **Ciągłe dostarczanie**: W pełni zautomatyzowany potok CI/CD w GitHub Actions buduje i weryfikuje dokumentację oraz notatniki przy każdym zatwierdzeniu zmian.

---

## Mapa drogowa dokumentacji

- [**Wprowadzenie**](introduction.md): Kontekst, filozofia platformy i zakres operacyjny.
- [**Architektura i referencja memorandum**](architecture.md): Pełna specyfikacja techniczna, układ repozytorium, dosłowne pliki szkieletowe i narzędzia weryfikacyjne.
- [**Notatnik weryfikacji obliczeniowej**](notebooks/experiment.ipynb): Notatnik walidacji środowiska uruchomieniowego wykonywany w jądrze `jb2-python`.
