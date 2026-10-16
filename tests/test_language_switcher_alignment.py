#!/usr/bin/env python3
"""
Unit tests for widgets/language-switcher.mjs dropdown alignment, positioning,
and responsive viewport bounds protection.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SWITCHER_PATH = ROOT / "widgets" / "language-switcher.mjs"


class TestLanguageSwitcherAlignment(unittest.TestCase):
    def setUp(self) -> None:
        self.assertTrue(SWITCHER_PATH.is_file(), f"Missing {SWITCHER_PATH}")
        self.content = SWITCHER_PATH.read_text(encoding="utf-8")

    def test_default_alignment_prevents_left_clipping(self) -> None:
        """The language switcher panel must align to left: 0 by default to prevent left-side clipping."""
        # Check that .sc-lang-panel has left: 0 and right: auto by default
        panel_pattern = re.search(r"\.sc-lang-panel\s*\{([^}]+)\}", self.content)
        self.assertIsNotNone(panel_pattern, "Could not find .sc-lang-panel CSS rule")
        panel_css = panel_pattern.group(1)
        self.assertIn("left: 0;", panel_css)
        self.assertIn("right: auto;", panel_css)
        self.assertIn("max-width: calc(100vw - 1.5rem);", panel_css)

        # Check that .sc-lang-switcher has align-items: flex-start by default
        switcher_pattern = re.search(r"\.sc-lang-switcher\s*\{([^}]+)\}", self.content)
        self.assertIsNotNone(switcher_pattern, "Could not find .sc-lang-switcher CSS rule")
        switcher_css = switcher_pattern.group(1)
        self.assertIn("align-items: flex-start;", switcher_css)

    def test_floating_host_overrides_alignment_to_right(self) -> None:
        """When floating at the top-right, the switcher and panel must align right to prevent right overflow."""
        floating_css_matches = re.findall(
            r"\[data-sc-lang-switcher\]\.sc-lang-host-floating[^{]*\{([^}]+)\}",
            self.content,
        )
        self.assertTrue(len(floating_css_matches) > 0, "Missing floating host CSS rules")
        combined_floating = " ".join(floating_css_matches)
        self.assertTrue(
            "align-items: flex-end;" in combined_floating or "right: 0;" in combined_floating
        )

    def test_alignment_classes_defined(self) -> None:
        """Ensure alignment utility classes exist for runtime viewport adjustment."""
        self.assertIn(".sc-lang-panel.sc-lang-panel-align-right", self.content)
        self.assertIn(".sc-lang-panel.sc-lang-panel-align-left", self.content)

    def test_css_anchor_positioning_syntax(self) -> None:
        """Verify modern CSS anchor positioning declarations and fallback structure."""
        self.assertIn("anchor-name: --sc-lang-trigger;", self.content)
        self.assertIn("position-anchor: --sc-lang-trigger;", self.content)
        self.assertIn("position-area: bottom span-right;", self.content)
        self.assertIn("flip-inline", self.content)

    def test_dynamic_boundary_detection_logic_present(self) -> None:
        """Verify JavaScript boundary detection prevents left and right viewport clipping."""
        self.assertIn("adjustPanelAlignment", self.content)
        self.assertIn("panelRect.left < 8", self.content)
        self.assertIn("panelRect.right > viewportWidth - 8", self.content)

    def test_dom_class_helpers_present(self) -> None:
        """Verify addClass, removeClass, and hasClass helpers protect non-browser and mock DOM environments."""
        self.assertIn("function addClass(", self.content)
        self.assertIn("function removeClass(", self.content)
        self.assertIn("function hasClass(", self.content)


if __name__ == "__main__":
    unittest.main()
