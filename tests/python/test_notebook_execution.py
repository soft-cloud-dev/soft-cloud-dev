"""tests/python/test_notebook_execution.py
Validates execution of webawesome-api.ipynb using the jb2-python kernel
and verifies the emitted placeholder structures.
"""

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from bs4 import BeautifulSoup

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
NOTEBOOK_PATH = REPO_ROOT / "tests" / "fixtures" / "webawesome-book" / "notebooks" / "webawesome-api.ipynb"
PYTHON_BIN = REPO_ROOT / ".venv" / "bin" / "python"
JUPYTER_BIN = REPO_ROOT / ".venv" / "bin" / "jupyter"


class NotebookExecutionTests(unittest.TestCase):
    def test_execute_notebook_fixture(self):
        self.assertTrue(NOTEBOOK_PATH.is_file(), f"Notebook not found: {NOTEBOOK_PATH}")
        with tempfile.NamedTemporaryFile(suffix=".ipynb", delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            cmd = [
                str(JUPYTER_BIN),
                "nbconvert",
                "--to",
                "notebook",
                "--execute",
                str(NOTEBOOK_PATH),
                "--output",
                str(tmp_path),
                "--ExecutePreprocessor.kernel_name=jb2-python",
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO_ROOT))
            self.assertEqual(
                res.returncode,
                0,
                f"Notebook execution failed:\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}",
            )

            executed_nb = json.loads(tmp_path.read_text(encoding="utf-8"))
            html_outputs = []
            for cell in executed_nb.get("cells", []):
                for out in cell.get("outputs", []):
                    data = out.get("data", {})
                    if "text/html" in data:
                        raw = "".join(data["text/html"])
                        html_outputs.append(raw)

            self.assertGreaterEqual(len(html_outputs), 4, "Expected at least 4 HTML component outputs")

            for html_str in html_outputs:
                soup = BeautifulSoup(html_str, "html.parser")
                host = soup.find(class_=lambda c: c and "sc-wa-host" in c.split())
                self.assertIsNotNone(host, f"Missing sc-wa-host in output: {html_str}")

                meta_span = host.find(class_=lambda c: c and "sc-wa-meta" in c.split())
                self.assertIsNotNone(meta_span, f"Missing sc-wa-meta in output: {html_str}")

                meta_data = json.loads(meta_span.get_text())
                self.assertEqual(meta_data.get("schema_version"), "1.0.0")
                self.assertIn(meta_data.get("component"), ["wa-card", "wa-callout", "wa-button", "wa-icon"])
        finally:
            if tmp_path.exists():
                tmp_path.unlink()


if __name__ == "__main__":
    unittest.main()
