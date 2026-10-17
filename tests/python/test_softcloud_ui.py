"""tests/python/test_softcloud_ui.py
Unit tests for softcloud_ui Python API.
"""

import json
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PYTHON_DIR = REPO_ROOT / "assets" / "python"
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from softcloud_ui import UI, TrustedHTML, HTMLOutput  # noqa: E402
from bs4 import BeautifulSoup  # noqa: E402


class SoftcloudUITests(unittest.TestCase):
    def _extract_meta(self, html_str: str) -> dict:
        soup = BeautifulSoup(html_str, "html.parser")
        meta_span = soup.find("span", class_="sc-wa-meta")
        self.assertIsNotNone(meta_span, "Missing sc-wa-meta span")
        return json.loads(meta_span.get_text())

    def test_trusted_html_type(self):
        th = TrustedHTML("<b>Bold</b>")
        self.assertEqual(str(th), "<b>Bold</b>")
        with self.assertRaises(TypeError):
            TrustedHTML(123)  # type: ignore

    def test_icon(self):
        res = UI.icon("rocket", style="solid", family="classic")
        self.assertIsInstance(res, HTMLOutput)
        html_str = res._repr_html_()
        self.assertIn("sc-wa-host", html_str)
        self.assertIn("sc-wa-icon", html_str)
        meta = self._extract_meta(html_str)
        self.assertEqual(meta["component"], "wa-icon")
        self.assertEqual(meta["schema_version"], "2.0.0")
        self.assertEqual(meta["name"], "rocket")
        self.assertEqual(meta["variant"], "solid")
        self.assertEqual(meta["family"], "classic")

    def test_button(self):
        res = UI.button(
            "Click Me",
            href="https://my.softcloud.dev/docs",
            variant="primary",
            target="_blank",
        )
        html_str = res._repr_html_()
        self.assertIn("sc-wa-host", html_str)
        self.assertIn("sc-wa-button", html_str)
        self.assertIn("Click Me", html_str)
        meta = self._extract_meta(html_str)
        self.assertEqual(meta["component"], "wa-button")
        self.assertEqual(meta["schema_version"], "2.0.0")
        self.assertEqual(meta["variant"], "brand")
        self.assertEqual(meta["href"], "https://my.softcloud.dev/docs")
        self.assertEqual(meta["target"], "_blank")
        self.assertEqual(meta["rel"], "noopener noreferrer")

    def test_button_unsafe_href_rejected(self):
        with self.assertRaises(ValueError):
            UI.button("Evil", href="javascript:alert(1)")

    def test_card_text_escapes_html(self):
        raw_text = "<b>Danger</b> <script>alert(1)</script>"
        res = UI.card_text(raw_text, header="Header Title", appearance="elevated")
        html_str = res._repr_html_()
        self.assertIn("&lt;b&gt;Danger&lt;/b&gt;", html_str)
        self.assertNotIn("<script>", html_str)
        meta = self._extract_meta(html_str)
        self.assertEqual(meta["header"], "Header Title")
        self.assertEqual(meta["schema_version"], "2.0.0")
        self.assertEqual(meta["appearance"], "filled-outlined")
        self.assertIn("sc-elevation", meta["class"])

    def test_card_trusted_html_requires_trusted_html(self):
        with self.assertRaises(TypeError):
            UI.card_trusted_html("<b>raw</b>")  # type: ignore

        th = TrustedHTML("<p class='custom'>Safe HTML</p>")
        res = UI.card_trusted_html(th, header="Card Header")
        html_str = res._repr_html_()
        self.assertIn("<p class='custom'>Safe HTML</p>", html_str)

    def test_callout_text_and_trusted(self):
        res = UI.callout_text("Plain text note", title="Callout Title", variant="warning")
        html_str = res._repr_html_()
        self.assertIn("Plain text note", html_str)
        meta = self._extract_meta(html_str)
        self.assertEqual(meta["title"], "Callout Title")
        self.assertEqual(meta["variant"], "warning")

        th = TrustedHTML("<div>Rich callout content</div>")
        res_th = UI.callout_trusted_html(th, title="Rich", variant="brand")
        self.assertIn("<div>Rich callout content</div>", res_th._repr_html_())


if __name__ == "__main__":
    unittest.main()
