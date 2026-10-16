#!/usr/bin/env python3
"""
Unit tests for widgets/language-switcher.mjs:
- Round button (matching theme switch) styling and country flag emojis
- Proximity and DOM placement adjacent to the site theme toggle button
- Dropdown inward alignment (right: 0, position-area: bottom span-left)
- Responsive viewport boundary protection
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

    def test_round_trigger_button_styling(self) -> None:
        """The trigger button must be a 36px circular button matching the theme switch toggle."""
        trigger_pattern = re.search(r"\.sc-lang-trigger\s*\{([^}]+)\}", self.content)
        self.assertIsNotNone(trigger_pattern, "Could not find .sc-lang-trigger CSS rule")
        trigger_css = trigger_pattern.group(1)

        self.assertIn("border-radius: 50%;", trigger_css)
        self.assertIn("width: 36px;", trigger_css)
        self.assertIn("height: 36px;", trigger_css)
        self.assertIn("padding: 0;", trigger_css)
        self.assertIn("display: inline-flex;", trigger_css)
        self.assertIn("align-items: center;", trigger_css)
        self.assertIn("justify-content: center;", trigger_css)

        # Flag span styling
        flag_pattern = re.search(r"\.sc-lang-flag\s*\{([^}]+)\}", self.content)
        self.assertIsNotNone(flag_pattern, "Could not find .sc-lang-flag CSS rule")
        flag_css = flag_pattern.group(1)
        self.assertIn("display: inline-flex;", flag_css)

    def test_locale_flags_mapping(self) -> None:
        """Verify country flag emojis for all supported locales and dropdown flag styling."""
        self.assertIn('"🇬🇧"', self.content)
        self.assertIn('"🇵🇱"', self.content)
        self.assertIn('"🇩🇪"', self.content)
        self.assertIn('"🇪🇸"', self.content)
        self.assertIn('"🇫🇷"', self.content)
        self.assertIn("DEFAULT_LOCALE_FLAGS", self.content)
        self.assertIn("function getLocaleFlag(", self.content)

        # Dropdown option flag class
        self.assertIn(".sc-lang-option-flag", self.content)
        self.assertIn(".sc-lang-option-left", self.content)

    def test_theme_toggle_discovery_and_adjacency(self) -> None:
        """Verify theme toggle finder and DOM adjacency logic."""
        self.assertIn("function findThemeToggle(", self.content)
        self.assertIn("button.theme-toggle", self.content)
        self.assertIn("button[aria-label*=\"theme\" i]", self.content)
        self.assertIn("function isAdjacent(", self.content)
        self.assertIn("function ensureLanguageSwitcherHost(", self.content)

    def test_dropdown_panel_inward_alignment(self) -> None:
        """The dropdown panel located in the top-right header must align right: 0 to open inward."""
        panel_pattern = re.search(r"\.sc-lang-panel\s*\{([^}]+)\}", self.content)
        self.assertIsNotNone(panel_pattern, "Could not find .sc-lang-panel CSS rule")
        panel_css = panel_pattern.group(1)

        self.assertIn("right: 0;", panel_css)
        self.assertIn("left: auto;", panel_css)
        self.assertIn("max-width: calc(100vw - 1.5rem);", panel_css)

    def test_css_anchor_positioning_syntax(self) -> None:
        """Verify modern CSS anchor positioning declarations and fallback structure."""
        self.assertIn("anchor-name: --sc-lang-trigger;", self.content)
        self.assertIn("position-anchor: --sc-lang-trigger;", self.content)
        self.assertIn("position-area: bottom span-left;", self.content)
        self.assertIn("position-area: block-end span-inline-start;", self.content)
        self.assertIn("flip-inline", self.content)

    def test_alignment_classes_and_boundary_detection(self) -> None:
        """Ensure alignment utility classes and runtime viewport boundary detection exist."""
        self.assertIn(".sc-lang-panel.sc-lang-panel-align-right", self.content)
        self.assertIn(".sc-lang-panel.sc-lang-panel-align-left", self.content)
        self.assertIn("function adjustPanelAlignment(", self.content)
        self.assertIn("currentRect.left < 8", self.content)
        self.assertIn("currentRect.right > viewportWidth - 8", self.content)

    def test_dom_class_helpers_present(self) -> None:
        """Verify addClass, removeClass, and hasClass helpers protect non-browser and mock DOM environments."""
        self.assertIn("function addClass(", self.content)
        self.assertIn("function removeClass(", self.content)
        self.assertIn("function hasClass(", self.content)

    def test_safari_even_spacing_and_dropdown_alignment(self) -> None:
        """Verify even spacing between search, lang switcher and theme toggle, and Safari height fix."""
        host_pattern = re.search(r"\[data-sc-lang-switcher\]\s*\{([^}]+)\}", self.content)
        self.assertIsNotNone(host_pattern, "Could not find [data-sc-lang-switcher] CSS rule")
        host_css = host_pattern.group(1)
        self.assertTrue(
            "margin: 0 0.5rem;" in host_css or "margin-inline: 0.5rem;" in host_css,
            "Expected even margin around language switcher host element",
        )

        switcher_pattern = re.search(r"\.sc-lang-switcher\s*\{([^}]+)\}", self.content)
        self.assertIsNotNone(switcher_pattern, "Could not find .sc-lang-switcher CSS rule")
        switcher_css = switcher_pattern.group(1)
        self.assertIn("height: 36px;", switcher_css, "Expected definite height on .sc-lang-switcher for Safari WebKit layout")

        self.assertIn("currentRect.width > 0", self.content)
        self.assertIn("viewportWidth - 8", self.content)


if __name__ == "__main__":
    unittest.main()
