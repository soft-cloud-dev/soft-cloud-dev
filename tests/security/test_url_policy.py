"""tests/security/test_url_policy.py
Python unit tests for URL policy validation parity against url-corpus.json.
"""

import json
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PYTHON_DIR = REPO_ROOT / "assets" / "python"
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from softcloud_security import validate_url, sanitize_rel  # noqa: E402


class UrlPolicyTests(unittest.TestCase):
    def setUp(self):
        corpus_path = REPO_ROOT / "tests" / "security" / "url-corpus.json"
        self.corpus = json.loads(corpus_path.read_text(encoding="utf-8"))

    def test_corpus_parity(self):
        for item in self.corpus:
            url = item["url"]
            context = item["context"]
            expected = item["valid"]
            is_valid, reason = validate_url(url, context=context)
            self.assertEqual(
                is_valid,
                expected,
                f"Failed for {context} URL: '{url}'. Expected {expected}, got {is_valid} ({reason})",
            )

    def test_sanitize_rel(self):
        self.assertEqual(sanitize_rel("", "_blank"), "noopener noreferrer")
        self.assertEqual(sanitize_rel("author", "_blank"), "author noopener noreferrer")
        self.assertEqual(sanitize_rel("noreferrer", "_blank"), "noopener noreferrer")
        self.assertEqual(sanitize_rel("custom", "_self"), "custom")


if __name__ == "__main__":
    unittest.main()
