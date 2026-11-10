"""Structural regression checks for the Executable Handbook first implementation."""
from __future__ import annotations

import re
import unittest
from pathlib import Path
from urllib.parse import urlsplit

import yaml


ROOT = Path(__file__).resolve().parents[1]
HANDBOOK_PAGES = (
    "README.md",
    "ui-library.md",
    "guides.md",
    "notebooks.md",
    "projects.md",
    "projects/freeipa.md",
    "contributing.md",
)


def toc_files(entries):
    for entry in entries:
        if "file" in entry:
            yield entry["file"]
        yield from toc_files(entry.get("children", []))


class HandbookInformationArchitectureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = yaml.safe_load((ROOT / "myst.yml").read_text(encoding="utf-8"))
        cls.locales = yaml.safe_load((ROOT / "i18n/locales.yml").read_text(encoding="utf-8"))
        cls.files = list(toc_files(cls.config["project"]["toc"]))

    def test_references_are_unique_and_exist(self):
        self.assertEqual(len(self.files), len(set(self.files)), "Duplicate TOC file")
        for path in self.files:
            with self.subTest(path=path):
                self.assertTrue((ROOT / path).is_file(), f"Missing TOC source: {path}")

    def test_existing_catalog_and_notebooks_are_preserved(self):
        component_pages = [p for p in self.files if p.startswith("components/")]
        self.assertGreaterEqual(len(component_pages), 85)
        for required in (
            "components/index.md",
            "components/authoring-guide.md",
            "notebooks/experiment.ipynb",
            "notebooks/webawesome-docs.ipynb",
            *HANDBOOK_PAGES,
        ):
            with self.subTest(path=required):
                self.assertIn(required, self.files)

    def test_sections_and_nav_match_the_handbook(self):
        groups = [e["title"] for e in self.config["project"]["toc"] if e.get("children")]
        self.assertEqual(groups, ["Systems & Laboratories", "Platform Engineering"])
        self.assertEqual(
            [(i["title"], i["url"]) for i in self.config["site"]["nav"]],
            [
                ("Guides", "/guides"),
                ("Notebooks", "/notebooks"),
                ("UI Library", "/ui-library"),
                ("Projects", "/projects"),
            ],
        )

    def test_stylesheet_and_document_links_exist(self):
        style = self.config["site"]["options"]["style"]
        css = (ROOT / style).read_text(encoding="utf-8")
        for name in ("sc-handbook__hero", "sc-handbook__verification",
                     "sc-handbook__routes", "sc-handbook__projects"):
            self.assertIn(name, css)

        for page in HANDBOOK_PAGES:
            text = (ROOT / page).read_text(encoding="utf-8")
            for target in re.findall(r"\]\(([^\s)]+)(?:\s+[^)]*)?\)", text):
                parts = urlsplit(target)
                if parts.scheme or parts.netloc or target.startswith("#"):
                    continue
                expected = (ROOT / page).parent / parts.path
                with self.subTest(page=page, target=target):
                    self.assertTrue(expected.is_file(), f"Broken local link in {page}: {target}")

    def test_required_localized_pages_still_in_toc(self):
        required = set(self.locales["required_pages"])
        self.assertTrue(required <= set(self.files))
        required_nav = {"Guides", "Notebooks", "UI Library", "Projects"}
        self.assertEqual(set(self.locales["locales"]), {"en", "pl", "de", "es", "fr"})
        for code, info in self.locales["locales"].items():
            with self.subTest(locale=code):
                self.assertEqual(required_nav, set(info["site"]["nav_titles"]))
                for mandatory in self.locales["required_pages"]:
                    expected = ROOT / mandatory if code == "en" else ROOT / "i18n" / code / mandatory
                    self.assertTrue(expected.is_file(), f"Missing core localized source {expected}")


if __name__ == "__main__":
    unittest.main()
