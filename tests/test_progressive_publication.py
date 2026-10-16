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
        # In current repo, introduction.md is the only page with narration assets on disk
        en_pages = ga.discover_enabled_pages(ROOT, locale="en", narrated_only=True)
        self.assertEqual(len(en_pages), 1)
        self.assertEqual(en_pages[0].name, "introduction.md")

        pl_pages = ga.discover_enabled_pages(ROOT, locale="pl", narrated_only=True)
        self.assertEqual(len(pl_pages), 1)
        self.assertEqual(pl_pages[0].name, "introduction.md")


if __name__ == "__main__":
    unittest.main()
