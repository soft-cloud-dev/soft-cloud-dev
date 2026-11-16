# Wprowadzenie

```{anywidget} ./widgets/voice-player.mjs
{
  "page": "introduction",
  "locale": "pl"
}
```

**Software Cloud** zapewnia otwarte, powtarzalne środowisko dla badań obliczeniowych, dokumentacji architektonicznej oraz inżynierii oprogramowania chmurowego.

---

## Wyzwanie powtarzalności obliczeniowej

Badania naukowe i systemy oprogramowania o wysokiej niezawodności zależą w kluczowym stopniu od powtarzalności. Współczesne przepływy pracy programistycznej często cierpią jednak na subtelny niedeterminizm środowiska:

- Nieprzypięte zależności przechodnie zmieniające się po cichu w repozytoriach nadrzędnych.
- Rozbieżne pliki binarne platform w systemach macOS, Linux i Windows.
- Niejawne wycieki zmiennych środowiskowych wpływające na ścieżki wykonania.
- Niemonitorowane wersje jądra uruchomieniowego prowadzące do rozbieżnych wyników wykonania.

Aby wyeliminować te tryby awarii, platforma Software Cloud wdraża ściśle kontrolowany profil publikacji.

---

## Zakres operacyjny

Software Cloud rozwiązuje te wyzwania za pomocą czterech powiązanych mechanizmów:

1. **Specyfikacja poprzez memorandum**: Podstawowa architektura repozytorium, licencjonowanie, narzędzia oraz konfiguracje potoków są skodyfikowane jako formalne specyfikacje.
2. **Deterministyczne rozwiązywanie pakietów wheel**: Bezpośrednie wymagania są blokowane w kryptograficznych skrótach pakietów wheel rozwiązywanych wyłącznie dla standardowych pakietów Linux/x86-64.
3. **Automatyczna weryfikacja środowiska uruchomieniowego**: Każde żądanie pull request i kompilacja wydania wykonuje audyt wstępny weryfikujący aktywację środowiska wirtualnego, pochodzenie interpretera, obecność Jupyter Server oraz kompletność spisu treści.
4. **Publikacja artefaktów na żywo**: Zaakceptowane kompilacje są publikowane bezpośrednio jako witryny statyczne z wysokowydajnym dostarczaniem HTTPS pod adresem [my.softcloud.dev](https://my.softcloud.dev/).

---

## Kolejne kroki

Aby zapoznać się z niskopoziomowym projektem technicznym, szkieletem repozytorium oraz implementacjami łańcucha narzędzi, przejdź do sekcji [**Architektura i referencja memorandum**](architecture.md).
