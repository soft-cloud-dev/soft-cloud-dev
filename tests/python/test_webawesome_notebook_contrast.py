"""tests/python/test_webawesome_notebook_contrast.py
Regression checks ensuring the Web Awesome Token Architecture card and
custom markup in notebooks/webawesome-docs.ipynb use theme-adaptive Web Awesome
semantic surface/text tokens rather than static dark palette tokens.
"""

import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
NOTEBOOK_PATHS = [
    REPO_ROOT / "notebooks" / "webawesome-docs.ipynb",
    REPO_ROOT / "i18n" / "de" / "notebooks" / "webawesome-docs.ipynb",
    REPO_ROOT / "i18n" / "es" / "notebooks" / "webawesome-docs.ipynb",
    REPO_ROOT / "i18n" / "fr" / "notebooks" / "webawesome-docs.ipynb",
    REPO_ROOT / "i18n" / "pl" / "notebooks" / "webawesome-docs.ipynb",
]


class WebAwesomeNotebookContrastTests(unittest.TestCase):
    def test_token_architecture_card_uses_semantic_theme_tokens(self):
        for nb_path in NOTEBOOK_PATHS:
            with self.subTest(notebook=str(nb_path.relative_to(REPO_ROOT))):
                self.assertTrue(nb_path.is_file(), f"Missing notebook: {nb_path}")
                nb = json.loads(nb_path.read_text(encoding="utf-8"))

                matching_outputs = []
                for cell in nb.get("cells", []):
                    for out in cell.get("outputs", []):
                        raw_html = "".join(out.get("data", {}).get("text/html", []))
                        if "Web Awesome Token Architecture" in raw_html:
                            matching_outputs.append(raw_html)

                self.assertEqual(
                    len(matching_outputs),
                    1,
                    f"Expected 1 Token Architecture output in {nb_path}",
                )
                card_html = matching_outputs[0]

                # Must not use static dark palette ramp or nonexistent WA3 tokens/classes
                self.assertNotIn("--wa-color-gray-05", card_html)
                self.assertNotIn("--wa-color-gray-25", card_html)
                self.assertNotIn("--wa-shadow-sm", card_html)
                self.assertNotIn("wa-text-loud", card_html)
                self.assertNotIn("wa-text-normal", card_html)
                self.assertNotIn("wa-text-quiet", card_html)

                # Must bind both surface and foreground to semantic theme tokens
                self.assertIn("--wa-color-surface-raised", card_html)
                self.assertIn("--wa-color-surface-border", card_html)
                self.assertIn("--wa-color-text-normal", card_html)
                self.assertIn("--wa-color-text-quiet", card_html)
                self.assertIn("--wa-shadow-s", card_html)
                self.assertIn("wa-color-text-normal", card_html)
                self.assertIn("wa-color-text-quiet", card_html)


if __name__ == "__main__":
    unittest.main()
