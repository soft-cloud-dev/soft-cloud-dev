#!/usr/bin/env python3
"""
Unit tests for Stage 4: Review and publication rules.

Covers:
- Progressive publication: untranslated or unready pages omitted from locale routes and marked unavailable in route-manifest.
- Audio controls: rendered only when narration is current (voice-player widget stripped at build time for un-narrated pages).
- API-free deployment verification using --narrated-only.
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = ROOT / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import build_locales as bl
import generate_audio as ga


class TestProgressivePublication(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = Path(tempfile.mkdtemp(prefix="test_prog_pub_"))
        self.addCleanup(lambda: shutil.rmtree(self.tmp_dir, ignore_errors=True))

    def test_strip_voice_player_widget(self) -> None:
        md_with_player = (
            "# Introduction\n\n"
            "```{anywidget} ./widgets/voice-player.mjs\n"
            "{\n"
            '  "page": "introduction"\n'
            "}\n"
            "```\n\n"
            "Some content here.\n"
        )
        stripped = bl.strip_voice_player_widget(md_with_player)
        self.assertNotIn("voice-player.mjs", stripped)
        self.assertIn("# Introduction", stripped)
        self.assertIn("Some content here.", stripped)

    def test_prune_toc_for_untranslated_pages(self) -> None:
        base_myst = {
            "version": 1,
            "project": {
                "toc": [
                    {"file": "README.md"},
                    {"file": "introduction.md"},
                    {"file": "architecture.md"},
                ]
            },
        }
        locale_info = {"site": {"title": "Polish Docs"}}
        # Only README.md and introduction.md are staged
        staged_files = {"README.md", "introduction.md"}
        pruned_cfg = bl.build_localized_myst_config(
            base_myst=base_myst,
            locale_code="pl",
            locale_info=locale_info,
            staged_files=staged_files,
        )
        pruned_files = [e["file"] for e in pruned_cfg["project"]["toc"]]
        self.assertEqual(pruned_files, ["README.md", "introduction.md"])
        self.assertNotIn("architecture.md", pruned_files)

    def test_route_manifest_availability(self) -> None:
        # On main, introduction.md is current in all locales
        locales_cfg = bl.load_locales_config(ROOT)
        base_myst = bl.load_yaml_file(ROOT / "myst.yml")
        manifest = bl.build_route_manifest(ROOT, locales_cfg, base_myst)

        intro_rec = manifest["pages"].get("introduction")
        self.assertIsNotNone(intro_rec)
        self.assertTrue(intro_rec["translations"]["en"]["available"])
        self.assertTrue(intro_rec["translations"]["pl"]["available"])
        self.assertEqual(intro_rec["translations"]["pl"]["route"], "/pl/introduction")

    def test_narrated_only_discovery(self) -> None:
        # introduction.md is always discoverable among narrated pages on disk
        en_pages = ga.discover_enabled_pages(ROOT, locale="en", narrated_only=True)
        en_names = [p.name for p in en_pages]
        self.assertIn("introduction.md", en_names)

        pl_pages = ga.discover_enabled_pages(ROOT, locale="pl", narrated_only=True)
        pl_names = [p.name for p in pl_pages]
        self.assertIn("introduction.md", pl_names)

    def test_authoritative_github_urls_and_injection(self) -> None:
        locales_cfg = bl.load_locales_config(ROOT)
        enabled = bl.get_enabled_locales(locales_cfg)
        base_myst = bl.load_yaml_file(ROOT / "myst.yml")

        en_edit, en_src = bl.authoritative_github_urls(
            base_myst, "en", "en", enabled["en"], "ui-library.md"
        )
        self.assertEqual(
            en_edit, "https://github.com/soft-cloud-dev/soft-cloud-dev/edit/main/ui-library.md"
        )
        self.assertEqual(
            en_src, "https://github.com/soft-cloud-dev/soft-cloud-dev/blob/main/ui-library.md"
        )

        pl_edit, pl_src = bl.authoritative_github_urls(
            base_myst, "pl", "en", enabled["pl"], "ui-library.md"
        )
        self.assertEqual(
            pl_edit,
            "https://github.com/soft-cloud-dev/soft-cloud-dev/edit/main/i18n/pl/ui-library.md",
        )
        self.assertEqual(
            pl_src,
            "https://github.com/soft-cloud-dev/soft-cloud-dev/blob/main/i18n/pl/ui-library.md",
        )

        md_with_fm = "---\ntitle: UI Library\n---\n\n# UI Library\n"
        injected_md = bl.inject_authoritative_repo_urls(
            md_with_fm, "ui-library.md", pl_edit, pl_src
        )
        self.assertIn(f"edit_url: {pl_edit}", injected_md)
        self.assertIn(f"source_url: {pl_src}", injected_md)

        md_without_fm = "# Architecture\n\nBody.\n"
        injected_no_fm = bl.inject_authoritative_repo_urls(
            md_without_fm, "architecture.md", en_edit, en_src
        )
        self.assertTrue(injected_no_fm.startswith("---\n"))
        self.assertIn(f"edit_url: {en_edit}", injected_no_fm)

    def test_rewrite_staged_source_urls_in_text(self) -> None:
        locales_cfg = bl.load_locales_config(ROOT)
        leaked = (
            '<a href="https://github.com/soft-cloud-dev/soft-cloud-dev/edit/main/'
            '_build/locales/en/workspace/ui-library.md">Edit</a>'
            '<a href="https://github.com/soft-cloud-dev/soft-cloud-dev/edit/main/'
            '_build/locales/pl/workspace/guides.md">Edit PL</a>'
        )
        cleaned = bl.rewrite_staged_source_urls_in_text(leaked, locales_cfg)
        self.assertNotIn("/_build/locales/", cleaned)
        self.assertIn(
            "https://github.com/soft-cloud-dev/soft-cloud-dev/edit/main/ui-library.md",
            cleaned,
        )
        self.assertIn(
            "https://github.com/soft-cloud-dev/soft-cloud-dev/edit/main/i18n/pl/guides.md",
            cleaned,
        )

    def test_materialize_explicit_slug_routes(self) -> None:
        base_myst = bl.load_yaml_file(ROOT / "myst.yml")
        locales_cfg = bl.load_locales_config(ROOT)
        self.assertEqual(
            bl.extract_explicit_frontmatter_slug(ROOT / "components" / "index.md"),
            "components",
        )

        out_dir = self.tmp_dir / "html"
        index1_dir = out_dir / "index-1"
        index1_dir.mkdir(parents=True, exist_ok=True)
        (index1_dir / "index.html").write_text(
            '<html><body><a href="/index-1">Catalog</a><script>{"slug":"index-1","url":"/index-1"}</script></body></html>',
            encoding="utf-8",
        )
        (out_dir / "index-1.json").write_text('{"slug":"index-1"}', encoding="utf-8")

        materialized = bl.materialize_explicit_slug_routes(ROOT, base_myst, out_dir)
        self.assertIn("components", materialized)
        self.assertTrue((out_dir / "components" / "index.html").is_file())
        self.assertTrue((out_dir / "components.json").is_file())
        self.assertIn('"slug":"components"', (out_dir / "components" / "index.html").read_text(encoding="utf-8"))
        self.assertIn('"slug":"components"', (out_dir / "components.json").read_text(encoding="utf-8"))

        manifest = bl.build_route_manifest(ROOT, locales_cfg, base_myst, output_html_dir=out_dir)
        self.assertIn("components", manifest["pages"])
        self.assertEqual(
            manifest["pages"]["components"]["translations"]["en"]["route"],
            "/components",
        )


if __name__ == "__main__":
    unittest.main()
