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
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = ROOT / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

SWITCHER_PATH = ROOT / "widgets" / "language-switcher.mjs"


class TestLanguageSwitcherAlignment(unittest.TestCase):
    def setUp(self) -> None:
        self.assertTrue(SWITCHER_PATH.is_file(), f"Missing {SWITCHER_PATH}")
        self.content = SWITCHER_PATH.read_text(encoding="utf-8")

    def test_round_trigger_button_styling(self) -> None:
        """The trigger button must be a 36px circular button matching the theme switch toggle with an SVG icon."""
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

        # SVG icon styling and trigger button template
        icon_pattern = re.search(r"\.sc-lang-icon\s*\{([^}]+)\}", self.content)
        self.assertIsNotNone(icon_pattern, "Could not find .sc-lang-icon CSS rule")
        icon_css = icon_pattern.group(1)
        self.assertIn("width: 18px;", icon_css)
        self.assertIn("height: 18px;", icon_css)

        # Trigger button markup template
        self.assertIn('<svg class="sc-lang-icon"', self.content)
        self.assertIn('setAttribute("aria-haspopup", "true")', self.content)
        self.assertIn('setAttribute("aria-expanded", "false")', self.content)

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

    def test_safari_inset_safety_and_badge_shrink(self) -> None:
        """Verify WebKit/Safari does not suffer from inset clearing or badge shrinkage."""
        badge_pattern = re.search(r"\.sc-lang-code-badge\s*\{([^}]+)\}", self.content)
        self.assertIsNotNone(badge_pattern, "Could not find .sc-lang-code-badge CSS rule")
        badge_css = badge_pattern.group(1)
        self.assertIn("flex-shrink: 0;", badge_css, "Badge chips must have flex-shrink: 0 to prevent WebKit clipping")

        # Alignment classes must have !important to override any browser quirk
        align_right_pattern = re.search(r"\.sc-lang-panel\.sc-lang-panel-align-right\s*\{([^}]+)\}", self.content)
        self.assertIsNotNone(align_right_pattern, "Could not find .sc-lang-panel-align-right CSS rule")
        self.assertIn("right: 0 !important;", align_right_pattern.group(1))

        # Anchor positioning blocks must NOT clear top or right to auto
        supports_blocks = re.findall(r"@supports\s*\([^\)]+\)\s*\{([^}]+(?:\{[^}]+\}[^}]*)*)\}", self.content)
        for block in supports_blocks:
            if "position-area" in block:
                self.assertNotIn("top: auto;", block, "@supports block must not clear top to auto")
                self.assertNotIn("right: auto;", block, "@supports block must not clear right to auto")

        # adjustPanelAlignment must have runtime guard against vertical overlap and right viewport overflow
        self.assertIn("postRect.top < triggerRect.bottom", self.content)
        self.assertIn("postRect.right > viewportWidth - 8", self.content)

    def test_search_button_accessibility_and_selector(self) -> None:
        """Verify MyST search bar button accessibility remediation and control selector."""
        # Ensure searchControl selector includes button.myst-search-bar
        self.assertIn("button.myst-search-bar", self.content)
        self.assertIn(".myst-search-bar", self.content)

        # Ensure ensureAccessibleControls function and localized search labels exist
        self.assertIn("function ensureAccessibleControls(", self.content)
        self.assertIn("SEARCH_LABELS", self.content)
        self.assertIn('"Search"', self.content)
        self.assertIn('"Szukaj"', self.content)
        self.assertIn('"Suchen"', self.content)
        self.assertIn('"Buscar"', self.content)
        self.assertIn('"Rechercher"', self.content)

        # Ensure aria-label, title, and sr-only insertion
        self.assertIn('btn.setAttribute("aria-label", searchLabel)', self.content)
        self.assertIn('btn.setAttribute("title", searchLabel)', self.content)
        self.assertIn('srSpan.className = "sr-only"', self.content)

    def test_fix_seo_artifacts_accessibility(self) -> None:
        """Verify fix_seo_artifacts.py patches button.myst-search-bar with discernible text."""
        fix_seo_path = ROOT / "tools" / "fix_seo_artifacts.py"
        self.assertTrue(fix_seo_path.is_file(), f"Missing {fix_seo_path}")
        from fix_seo_artifacts import fix_html_accessibility

        sample_html = (
            '<header class="myst-top-nav">'
            '<nav class="myst-top-nav-bar">'
            '<div class="flex">'
            '<button type="button" aria-haspopup="dialog" aria-expanded="false" data-state="closed" '
            'class="myst-search-bar flex items-center h-10 aspect-square sm:w-64 text-left text-myst-text-secondary '
            'border border-myst-border-strong rounded-lg bg-myst-bg-secondary dark:bg-myst-surface-hover myst-search-bar-disabled">'
            '<svg class="w-10 h-10"></svg>'
            '<span class="myst-search-text-placeholder hidden sm:block grow">Search</span>'
            '</button>'
            '</div></nav></header>'
        )

        # Test English remediation
        en_patched = fix_html_accessibility(sample_html, loc_code="en")
        self.assertIn('aria-label="Search"', en_patched)
        self.assertIn('title="Search"', en_patched)
        self.assertIn('<span class="sr-only">Search</span>', en_patched)

        # Test Polish remediation
        pl_patched = fix_html_accessibility(sample_html, loc_code="pl")
        self.assertIn('aria-label="Szukaj"', pl_patched)
        self.assertIn('title="Szukaj"', pl_patched)
        self.assertIn('<span class="sr-only">Szukaj</span>', pl_patched)

        # Verify idempotence (does not double inject)
        re_patched = fix_html_accessibility(en_patched, loc_code="en")
        self.assertEqual(en_patched.count('aria-label="Search"'), 1)
        self.assertEqual(re_patched.count('aria-label="Search"'), 1)
        self.assertEqual(re_patched.count('<span class="sr-only">Search</span>'), 1)


if __name__ == "__main__":
    unittest.main()
