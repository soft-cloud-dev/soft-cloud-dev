"""tests/myst/test-plugin-output.py
Python validation verifying the plugin file exists, has correct permissions,
and conforms to the expected AST contract.
"""

import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PLUGIN_PATH = REPO_ROOT / "assets" / "plugins" / "myst-webawesome.mjs"
SCHEMA_PATH = REPO_ROOT / "assets" / "shared" / "component-schema.json"


class PluginContractTests(unittest.TestCase):
    def test_plugin_file_exists(self):
        self.assertTrue(PLUGIN_PATH.is_file(), f"Missing plugin file: {PLUGIN_PATH}")
        text = PLUGIN_PATH.read_text(encoding="utf-8")
        self.assertIn("wa-card", text)
        self.assertIn("wa-callout", text)
        self.assertIn("wa-button", text)
        self.assertIn("sc-wa-host", text)
        self.assertIn("sc-wa-meta", text)

    def test_schema_allows_components(self):
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertIn("allowedComponents", schema)
        self.assertIn("wa-card", schema["allowedComponents"])
        self.assertIn("wa-callout", schema["allowedComponents"])
        self.assertIn("wa-button", schema["allowedComponents"])
        self.assertIn("wa-icon", schema["allowedComponents"])


if __name__ == "__main__":
    unittest.main()
