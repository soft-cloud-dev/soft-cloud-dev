"""Regression tests for stage 2: translation update, preservation of human edits, provenance (no network)."""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import i18n_utils  # noqa: E402
import translate_sources as ts  # noqa: E402
import translation_engine as te  # noqa: E402


def stage(tmp: Path) -> Path:
    for name in ("myst.yml", "README.md", "introduction.md", "architecture.md", "i18n", "projects", "notebooks", "audio", "widgets"):
        src = ROOT / name
        if src.is_dir():
            shutil.copytree(src, tmp / name)
        elif src.is_file():
            shutil.copy2(src, tmp / name)
    return tmp


class Fake:
    """Deterministic stand-in for the model; counts calls and can fail on a marker."""

    def __init__(self, boom: str | None = None, exc: Exception | None = None) -> None:
        self.calls = 0
        self.boom, self.exc = boom, exc

    def __call__(self, text, locale, lang, glossary, key):
        self.calls += 1
        if self.exc is not None:
            raise self.exc
        if self.boom and self.boom in text:
            raise RuntimeError("provider failure")
        out = []
        for line in text.split("\n"):
            if line.startswith("#"):
                out.append(line + " ~")  # heading stays a heading
            elif line[:1].isalpha():
                out.append("TR:" + line)
            else:
                out.append(line)
        return "\n".join(out)


class Base(unittest.TestCase):
    def setUp(self) -> None:
        self._td = tempfile.TemporaryDirectory()
        self.root = stage(Path(self._td.name))
        self.docs = ts.discover_source_documents(self.root)
        self.glossary = i18n_utils.load_glossary(self.root)

    def tearDown(self) -> None:
        self._td.cleanup()

    def run_update(self, locale="fr", fake=None, **kw):
        fake = fake or Fake()
        manifest, report = ts.update_locale_translations(
            self.root, locale, self.docs, self.glossary, "k", translate_fn=fake, **kw
        )
        return manifest, report, fake

    def prov_path(self, locale="fr") -> Path:
        return self.root / "i18n" / locale / "provenance.json"

    def append(self, path: Path, text: str) -> None:
        path.write_text(path.read_text(encoding="utf-8") + text, encoding="utf-8")


class ProtectionTests(unittest.TestCase):
    SAMPLE = (
        "## Title\n\nUse `pip install x` and $a+b$ then see [docs](https://e.org/x).\n\n"
        "```python\nprint('hi')\n```\n\n$$\nE=mc^2\n$$\n\n"
        ":::{note}\nProse here.\n```bash\nls\n```\n:::\n"
    )

    def test_roundtrip_is_identity(self) -> None:
        masked, originals = te.protect_markdown(self.SAMPLE)
        self.assertNotIn("print('hi')", masked)
        self.assertNotIn("E=mc^2", masked)
        self.assertNotIn("https://e.org/x", masked)
        self.assertNotIn("pip install", masked)
        self.assertIn("Prose here.", masked)  # note body stays translatable
        self.assertNotIn("ls\n", masked.replace("Prose", ""))  # nested code protected
        self.assertEqual(te.restore_markdown(masked, originals), self.SAMPLE)

    def test_dropped_placeholder_is_rejected(self) -> None:
        calls = []

        def bad(masked: str) -> str:
            calls.append(1)
            return masked.replace(te.TOKEN_FMT.format(n=0), "")

        with self.assertRaises(te.ProtectionError):
            te.translate_protected(self.SAMPLE, bad, max_attempts=2)
        self.assertEqual(len(calls), 2)

    def test_duplicated_or_invented_placeholder_is_rejected(self) -> None:
        masked, originals = te.protect_markdown(self.SAMPLE)
        with self.assertRaises(te.ProtectionError):
            te.restore_markdown(masked + te.TOKEN_FMT.format(n=0), originals)
        with self.assertRaises(te.ProtectionError):
            te.restore_markdown(masked + te.TOKEN_FMT.format(n=999), originals)

    def test_prompt_mentions_placeholders_and_glossary(self) -> None:
        g = i18n_utils.load_glossary(ROOT)
        prompt = ts.build_translation_prompt("x", "pl", "Polish", g)
        self.assertIn("\u27e6SC", prompt)


class UpdateTests(Base):
    def test_stale_existing_translation_is_updated_not_skipped(self) -> None:
        old_text = (self.root / "i18n/fr/architecture.md").read_text(encoding="utf-8")
        self.append(self.root / "architecture.md", "\nA brand new paragraph.\n")
        _, report, fake = self.run_update()
        self.assertIn("architecture.md", report["generated"])
        self.assertGreater(fake.calls, 0)
        new_text = (self.root / "i18n/fr/architecture.md").read_text(encoding="utf-8")
        self.assertIn("A brand new paragraph.", new_text)
        # unchanged sections are preserved byte-for-byte
        self.assertTrue(new_text.startswith(old_text[:2000]))

    def test_other_documents_keep_their_records_verbatim(self) -> None:
        before = json.loads(self.prov_path().read_text(encoding="utf-8"))["documents"]
        self.append(self.root / "architecture.md", "\nMore.\n")
        self.run_update()
        after = json.loads(self.prov_path().read_text(encoding="utf-8"))
        for doc, entry in before.items():
            if doc != "architecture.md":
                self.assertEqual(after["documents"][doc], entry)
        self.assertEqual(after["documents"]["architecture.md"]["revision_state"], "draft")
        self.assertIn("policy_sha256", after["documents"]["architecture.md"])
        copy = dict(after)
        digest = copy.pop("provenance_sha256")
        self.assertEqual(digest, i18n_utils.sha256_json(copy))

    def test_current_state_makes_no_calls_and_no_writes(self) -> None:
        before = self.prov_path().read_bytes()
        snap = {p: p.read_bytes() for p in (self.root / "i18n/fr").rglob("*") if p.is_file()}
        _, report, fake = self.run_update()
        self.assertEqual(fake.calls, 0)
        self.assertEqual(report["generated"], [])
        self.assertEqual(self.prov_path().read_bytes(), before)
        self.assertEqual(snap, {p: p.read_bytes() for p in (self.root / "i18n/fr").rglob("*") if p.is_file()})

    def test_human_edit_is_preserved_and_provenance_untouched(self) -> None:
        p = self.root / "i18n/fr/introduction.md"
        self.append(p, "\nCorrection humaine.\n")
        before_prov = self.prov_path().read_bytes()
        _, report, fake = self.run_update()
        self.assertEqual(fake.calls, 0)
        self.assertIn("Correction humaine.", p.read_text(encoding="utf-8"))
        self.assertIn("introduction.md", report["preserved_human_edits"])
        self.assertEqual(self.prov_path().read_bytes(), before_prov)

    def test_conflict_when_english_and_human_edit_same_section(self) -> None:
        self.append(self.root / "architecture.md", "\nEnglish addition.\n")
        loc = self.root / "i18n/fr/architecture.md"
        self.append(loc, "\nAjout humain.\n")
        before = loc.read_bytes()
        _, report, fake = self.run_update()
        self.assertIn("architecture.md", report["conflicts"])
        self.assertEqual(loc.read_bytes(), before)
        self.assertEqual(fake.calls, 0)

    def test_english_change_elsewhere_keeps_human_edit_and_flags_it(self) -> None:
        loc = self.root / "i18n/fr/architecture.md"
        lines = loc.read_text(encoding="utf-8").split("\n")
        lines[2] += " (corrigé par un humain)"
        loc.write_text("\n".join(lines), encoding="utf-8")
        self.append(self.root / "architecture.md", "\nEnglish tail.\n")
        _, report, _ = self.run_update()
        text = loc.read_text(encoding="utf-8")
        self.assertIn("(corrigé par un humain)", text)
        self.assertIn("English tail.", text)
        self.assertIn("architecture.md", report["generated"])
        entry = json.loads(self.prov_path().read_text(encoding="utf-8"))["documents"]["architecture.md"]
        self.assertEqual(entry["revision_state"], "draft")
        self.assertTrue(entry["preserved_human_edits"])

    def test_code_change_in_english_reaches_translation_unmodified(self) -> None:
        en = self.root / "architecture.md"
        text = en.read_text(encoding="utf-8")
        marker = "```"
        i = text.index(marker)
        j = text.index("\n", i) + 1
        en.write_text(text[:j] + "echo CHANGED_BY_TEST\n" + text[j:], encoding="utf-8")
        _, report, _ = self.run_update()
        self.assertIn("architecture.md", report["generated"])
        self.assertIn("echo CHANGED_BY_TEST", (self.root / "i18n/fr/architecture.md").read_text(encoding="utf-8"))
        self.assertEqual(ts.verify_document_preservation(en, self.root / "i18n/fr/architecture.md", "fr"), [])

    def test_failure_is_isolated_and_keeps_last_coherent_state(self) -> None:
        self.append(self.root / "architecture.md", "\nBOOM here.\n")
        self.append(self.root / "README.md", "\nFine addition.\n")
        before_arch = (self.root / "i18n/fr/architecture.md").read_bytes()
        before_prov = json.loads(self.prov_path().read_text(encoding="utf-8"))["documents"]["architecture.md"]
        _, report, _ = self.run_update(fake=Fake(boom="BOOM"))
        self.assertIn("architecture.md", report["failed"])
        self.assertIn("README.md", report["generated"])
        self.assertEqual((self.root / "i18n/fr/architecture.md").read_bytes(), before_arch)
        after = json.loads(self.prov_path().read_text(encoding="utf-8"))["documents"]["architecture.md"]
        self.assertEqual(after, before_prov)

    def test_fatal_error_aborts_without_writing(self) -> None:
        self.append(self.root / "architecture.md", "\nX.\n")
        before = self.prov_path().read_bytes()
        with self.assertRaises(ts.FatalTranslationError):
            self.run_update(fake=Fake(exc=ts.FatalTranslationError("bad key")))
        self.assertEqual(self.prov_path().read_bytes(), before)

    def test_missing_api_key_is_fatal_only_when_generation_is_needed(self) -> None:
        # current state: no key needed
        ts.update_locale_translations(self.root, "fr", self.docs, self.glossary, "")
        self.append(self.root / "architecture.md", "\nX.\n")
        with self.assertRaises(ts.FatalTranslationError):
            ts.update_locale_translations(self.root, "fr", self.docs, self.glossary, "")

    def test_glossary_change_reassesses_only_when_requested(self) -> None:
        g = self.root / "i18n/glossary.yml"
        g.write_text(g.read_text(encoding="utf-8") + "\nextra_policy_note: changed\n", encoding="utf-8")
        glossary = i18n_utils.load_glossary(self.root)
        fake = Fake()
        _, report = ts.update_locale_translations(self.root, "fr", self.docs, glossary, "k", translate_fn=fake)
        self.assertEqual(fake.calls, 0)
        self.assertTrue(report["policy_pending"])
        fake2 = Fake()
        _, report2 = ts.update_locale_translations(
            self.root, "fr", self.docs, glossary, "k", translate_fn=fake2, reassess_policy=True
        )
        self.assertGreater(fake2.calls, 0)
        self.assertTrue(report2["generated"] or report2["refreshed"] or report2["failed"] or report2["conflicts"])


class NotebookTests(Base):
    def test_missing_notebook_translation_is_created_with_code_preserved(self) -> None:
        loc = self.root / "i18n/es/notebooks/experiment.ipynb"
        loc.unlink()
        _, report, fake = self.run_update(locale="es")
        self.assertIn("notebooks/experiment.ipynb", report["generated"])
        en_nb = json.loads((self.root / "notebooks/experiment.ipynb").read_text(encoding="utf-8"))
        loc_nb = json.loads(loc.read_text(encoding="utf-8"))
        for e, l in zip(en_nb["cells"], loc_nb["cells"]):
            if e["cell_type"] == "code":
                self.assertEqual(e, l)  # source, outputs, ids, metadata
            else:
                self.assertIn(" ~", "".join(l["source"]))
        self.assertEqual(en_nb["metadata"], loc_nb["metadata"])

    def test_stale_notebook_markdown_cell_updated_code_cells_untouched(self) -> None:
        nb_path = self.root / "notebooks/experiment.ipynb"
        nb = json.loads(nb_path.read_text(encoding="utf-8"))
        md = next(c for c in nb["cells"] if c["cell_type"] == "markdown")
        md["source"] = md["source"] + ["\n", "Extra explanation."]
        nb_path.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        _, report, _ = self.run_update(locale="es")
        self.assertIn("notebooks/experiment.ipynb", report["generated"])
        loc_nb = json.loads((self.root / "i18n/es/notebooks/experiment.ipynb").read_text(encoding="utf-8"))
        lmd = next(c for c in loc_nb["cells"] if c["cell_type"] == "markdown")
        self.assertIn("Extra explanation.", "".join(lmd["source"]))

    def test_human_edited_notebook_cell_conflicts_when_english_changes(self) -> None:
        nb_path = self.root / "notebooks/experiment.ipynb"
        nb = json.loads(nb_path.read_text(encoding="utf-8"))
        next(c for c in nb["cells"] if c["cell_type"] == "markdown")["source"].append("\nNew EN line.")
        nb_path.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        loc_path = self.root / "i18n/es/notebooks/experiment.ipynb"
        lnb = json.loads(loc_path.read_text(encoding="utf-8"))
        next(c for c in lnb["cells"] if c["cell_type"] == "markdown")["source"].append("\nEdición humana.")
        loc_path.write_text(json.dumps(lnb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        before = loc_path.read_bytes()
        _, report, fake = self.run_update(locale="es")
        self.assertIn("notebooks/experiment.ipynb", report["conflicts"])
        self.assertEqual(loc_path.read_bytes(), before)


class AcceptReviewedTests(Base):
    def test_accepting_validated_human_edit_records_reviewed_state(self) -> None:
        p = self.root / "i18n/fr/introduction.md"
        self.append(p, "\nCorrection humaine.\n")
        res = ts.accept_reviewed_translations(self.root, "fr", self.docs)
        self.assertEqual(res["accepted"], ["introduction.md"])
        entry = json.loads(self.prov_path().read_text(encoding="utf-8"))["documents"]["introduction.md"]
        self.assertEqual(entry["revision_state"], "reviewed")
        self.assertEqual(entry["translated_sha256"], i18n_utils.sha256_file(p))
        errors = [e for e in ts.check_locale_provenance(self.root, "fr", self.docs) if "introduction.md" in e]
        self.assertEqual(errors, [])

    def test_accept_refused_when_english_changed(self) -> None:
        self.append(self.root / "introduction.md", "\nNew EN.\n")
        self.append(self.root / "i18n/fr/introduction.md", "\nEdit.\n")
        res = ts.accept_reviewed_translations(self.root, "fr", self.docs)
        self.assertIn("introduction.md", res["refused"])
        self.assertEqual(res["accepted"], [])

    def test_accept_refused_when_edit_breaks_code(self) -> None:
        loc = self.root / "i18n/fr/architecture.md"
        text = loc.read_text(encoding="utf-8")
        i = text.index("```")
        j = text.index("\n", i) + 1
        loc.write_text(text[:j] + "tampered\n" + text[j:], encoding="utf-8")
        res = ts.accept_reviewed_translations(self.root, "fr", self.docs)
        self.assertIn("architecture.md", res["refused"])


class CliTests(Base):
    def test_invalid_locale_rejected(self) -> None:
        import os

        cwd = os.getcwd()
        os.chdir(self.root)
        try:
            with self.assertRaises(SystemExit):
                ts.main(["--prepare", "--locale", "xx"])
            with self.assertRaises(SystemExit):
                ts.main(["--prepare", "--locale", "en"])
        finally:
            os.chdir(cwd)


if __name__ == "__main__":
    unittest.main()
