"""Regression tests for tools/plan_localization.py (stdlib unittest, no network)."""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import plan_localization as pl  # noqa: E402


def stage(tmp: Path) -> Path:
    for name in ("myst.yml", "README.md", "introduction.md", "architecture.md", "i18n", "projects", "notebooks", "audio"):
        src = ROOT / name
        if src.is_dir():
            shutil.copytree(src, tmp / name)
        elif src.is_file():
            shutil.copy2(src, tmp / name)
    return tmp


class PlannerTests(unittest.TestCase):
    def setUp(self) -> None:
        self._td = tempfile.TemporaryDirectory()
        self.root = stage(Path(self._td.name))

    def tearDown(self) -> None:
        self._td.cleanup()

    def doc(self, locale: str, rel: str) -> dict:
        plan = pl.build_plan(self.root)
        return next(d for d in plan["locales"][locale]["documents"] if d["document"] == rel)

    def test_current_translation_needs_no_translation(self) -> None:
        self.assertEqual(self.doc("pl", "introduction.md")["translation"], "current")
        self.assertNotIn("translate", self.doc("pl", "introduction.md")["actions"])

    def test_existing_stale_translation_is_detected(self) -> None:
        p = self.root / "architecture.md"
        p.write_text(p.read_text(encoding="utf-8") + "\nNew paragraph.\n", encoding="utf-8")
        d = self.doc("pl", "architecture.md")
        self.assertEqual(d["translation"], "stale")
        self.assertIn("translate", d["actions"])

    def test_missing_translation(self) -> None:
        (self.root / "i18n/de/architecture.md").unlink()
        self.assertEqual(self.doc("de", "architecture.md")["translation"], "missing")

    def test_human_edit_preserved_and_refreshes_narration_only(self) -> None:
        p = self.root / "i18n/pl/introduction.md"
        p.write_text(p.read_text(encoding="utf-8") + "\nPoprawka.\n", encoding="utf-8")
        d = self.doc("pl", "introduction.md")
        self.assertEqual(d["translation"], "human_edit")
        self.assertNotIn("translate", d["actions"])
        self.assertIn("narrate", d["actions"])

    def test_stale_plus_human_edit_requires_manual_refresh(self) -> None:
        en = self.root / "architecture.md"
        en.write_text(en.read_text(encoding="utf-8") + "\nMore.\n", encoding="utf-8")
        lp = self.root / "i18n/fr/architecture.md"
        lp.write_text(lp.read_text(encoding="utf-8") + "\nCorrection.\n", encoding="utf-8")
        d = self.doc("fr", "architecture.md")
        self.assertEqual(d["translation"], "stale+edit")
        self.assertIn("manual_refresh_required", d["actions"])
        self.assertNotIn("translate", d["actions"])

    def test_corrupt_audio_repairs_audio_without_retranslating(self) -> None:
        chunk = next((self.root / "audio/pl/introduction").glob("chunk-001-*.mp3"))
        chunk.write_bytes(b"corrupt")
        d = self.doc("pl", "introduction.md")
        self.assertEqual(d["narration"], "corrupt")
        self.assertEqual(d["translation"], "current")
        self.assertEqual(d["actions"], ["narrate"])

    def test_voice_change_invalidates_audio_only(self) -> None:
        cfg = self.root / "i18n/locales.yml"
        text = cfg.read_text(encoding="utf-8")
        cfg.write_text(text.replace('voice_name: "Kore"', 'voice_name: "Puck"', 1), encoding="utf-8")
        plan = pl.build_plan(self.root)
        en = next(d for d in plan["locales"]["en"]["documents"] if d["document"] == "introduction.md")
        self.assertEqual(en["narration"], "stale")
        self.assertIn("voice changed", en["narration_reasons"])

    def test_glossary_change_reassesses_translations(self) -> None:
        g = self.root / "i18n/glossary.yml"
        g.write_text(g.read_text(encoding="utf-8") + "\n# policy edit\ninvariant_terms_extra: [\"X\"]\n", encoding="utf-8")
        self.assertEqual(self.doc("pl", "introduction.md")["translation"], "policy_changed")

    def test_removed_page_proposes_cleanup_only(self) -> None:
        cfg = self.root / "myst.yml"
        lines = [l for l in cfg.read_text(encoding="utf-8").splitlines() if "architecture.md" not in l]
        cfg.write_text("\n".join(lines) + "\n", encoding="utf-8")
        plan = pl.build_plan(self.root)
        cleanup = plan["locales"]["pl"]["cleanup"]
        self.assertEqual([c["document"] for c in cleanup], ["architecture.md"])
        self.assertTrue((self.root / "i18n/pl/architecture.md").is_file())  # planner never deletes

    def test_planner_is_read_only_and_deterministic(self) -> None:
        before = sorted(p.relative_to(self.root).as_posix() for p in self.root.rglob("*") if p.is_file())
        a = json.dumps(pl.build_plan(self.root), sort_keys=True)
        b = json.dumps(pl.build_plan(self.root), sort_keys=True)
        after = sorted(p.relative_to(self.root).as_posix() for p in self.root.rglob("*") if p.is_file())
        self.assertEqual(a, b)
        self.assertEqual(before, after)

    def test_unknown_locale_rejected(self) -> None:
        import os

        cwd = os.getcwd()
        os.chdir(self.root)
        try:
            self.assertEqual(pl.main(["--locale", "xx"]), 2)
        finally:
            os.chdir(cwd)


if __name__ == "__main__":
    unittest.main()
