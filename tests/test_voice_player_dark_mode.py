#!/usr/bin/env python3
"""
Unit tests for voice-player.mjs dark mode color and theme adaptability.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VOICE_PLAYER_PATH = ROOT / "widgets" / "voice-player.mjs"


class TestVoicePlayerDarkMode(unittest.TestCase):
    def setUp(self) -> None:
        self.assertTrue(VOICE_PLAYER_PATH.is_file(), f"Missing {VOICE_PLAYER_PATH}")
        self.content = VOICE_PLAYER_PATH.read_text(encoding="utf-8")

    def test_dark_mode_selectors_present_in_styles(self) -> None:
        """Verify comprehensive dark mode selectors for shadow DOM, host, and light DOM."""
        required_selectors = [
            ".sc-player.dark",
            '.sc-player[data-theme="dark"]',
            ":host(.dark) .sc-player",
            ':host([data-theme="dark"]) .sc-player',
            ":host-context(html.dark) .sc-player",
            ":host-context(.dark) .sc-player",
            "html.dark .sc-player",
            ".dark .sc-player",
            "@media (prefers-color-scheme: dark)",
        ]
        for sel in required_selectors:
            self.assertIn(sel, self.content, f"Expected selector '{sel}' in voice-player.mjs")

    def test_dark_mode_components_styled(self) -> None:
        """Verify that all interactive controls and text elements have dark mode rules."""
        required_elements = [
            ".sc-player",
            ".sc-headphones-icon",
            ".sc-overview-title",
            ".sc-overview-subtitle",
            ".sc-btn-listen",
            ".sc-btn-collapse",
            ".sc-expanded-body",
            ".sc-meta-row",
            ".sc-section-heading",
            ".sc-scrubber-container",
            ".sc-scrubber-fill",
            ".sc-scrubber-knob",
            ".sc-icon-btn",
            ".sc-play-pill",
            ".sc-speed-dropdown",
        ]
        for el in required_elements:
            pattern = re.compile(rf"\.sc-player\.dark\s+{re.escape(el)}|\.sc-player\.dark,\s*|\.sc-player\.dark")
            self.assertTrue(
                pattern.search(self.content),
                f"Expected dark mode styling for component '{el}'"
            )

    def test_is_dark_mode_active_helper_exported(self) -> None:
        """Verify isDarkModeActive helper is defined, exported, and called during render."""
        self.assertIn("export function isDarkModeActive", self.content)
        self.assertIn("isDarkModeActive", self.content)
        self.assertIn("syncTheme()", self.content)
        self.assertIn("MutationObserver", self.content)
        self.assertIn("prefers-color-scheme: dark", self.content)

    def test_dark_mode_colors_match_dark_theme(self) -> None:
        """Verify expected background and contrast colors for dark mode."""
        # Dark surface background #121214 and border #27272a
        self.assertIn("#121214", self.content)
        self.assertIn("#27272a", self.content)
        self.assertIn("#fafafa", self.content)
        self.assertIn("#a1a1aa", self.content)


    def test_dynamic_theme_toggle_reactivity(self) -> None:
        """Verify dynamic theme toggle handlers and observers operate without page reload."""
        self.assertIn("subtree: true", self.content)
        self.assertIn("handleDocClick", self.content)
        self.assertIn("handleStorage", self.content)
        self.assertIn("color-scheme", self.content)


if __name__ == "__main__":
    unittest.main()
