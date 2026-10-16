#!/usr/bin/env python3
"""Tests for GitHub Actions reconciliation, validation, and deployment workflows."""

import unittest
from pathlib import Path
import sys

TOOLS_DIR = Path(__file__).resolve().parent.parent / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from i18n_utils import load_yaml_file  # noqa: E402


class WorkflowIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent
        self.workflows_dir = self.root / ".github" / "workflows"

    def test_all_workflows_exist_and_parse(self):
        expected_workflows = [
            "deploy.yml",
            "validate-generated.yml",
            "reconcile-localization.yml",
            "_generate-locale.yml",
        ]
        for name in expected_workflows:
            path = self.workflows_dir / name
            self.assertTrue(path.is_file(), f"Missing workflow file: {name}")
            data = load_yaml_file(path)
            self.assertIsInstance(data, dict, f"Failed to parse {name} as YAML dict")
            self.assertIn("name", data)
            self.assertIn("jobs", data)

    def test_workflow_run_blocks_have_valid_indentation(self):
        """Ensure all multiline script blocks inside workflows maintain consistent indentation."""
        for wf_path in self.workflows_dir.glob("*.yml"):
            lines = wf_path.read_text(encoding="utf-8").splitlines()
            in_run_block = False
            base_run_indent = 0
            for lineno, line in enumerate(lines, 1):
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                indent = len(line) - len(line.lstrip())
                if line.rstrip().endswith(("run: |", "run: |-", "run: |+")):
                    in_run_block = True
                    base_run_indent = indent
                    continue
                if in_run_block:
                    if indent <= base_run_indent:
                        if (
                            stripped.startswith("- ")
                            or (indent <= 4 and ":" in stripped)
                            or any(
                                stripped.startswith(k + ":")
                                for k in ("name", "uses", "with", "env", "id", "if", "needs", "jobs", "outputs", "steps", "strategy")
                            )
                        ):
                            in_run_block = False
                        else:
                            self.fail(
                                f"Invalid YAML indentation in {wf_path.name}:{lineno}: "
                                f"line has indent {indent} <= base {base_run_indent}: '{stripped}'"
                            )

    def test_deploy_workflow_is_offline_and_secret_free(self):
        deploy_path = self.workflows_dir / "deploy.yml"
        content = deploy_path.read_text(encoding="utf-8")
        self.assertNotIn("GEMINI_API_KEY", content, "deploy.yml must not reference GEMINI_API_KEY")
        self.assertIn("SOFTCLOUD_AUDIO_OFFLINE: '1'", content, "deploy.yml must set SOFTCLOUD_AUDIO_OFFLINE to '1'")

    def test_validate_generated_workflow_is_secret_free(self):
        validate_path = self.workflows_dir / "validate-generated.yml"
        content = validate_path.read_text(encoding="utf-8")
        self.assertNotIn("GEMINI_API_KEY", content, "validate-generated.yml must not reference GEMINI_API_KEY")
        self.assertIn("--check-only", content)
        self.assertIn("--progressive", content)

    def test_reconcile_localization_workflow_structure(self):
        reconcile_path = self.workflows_dir / "reconcile-localization.yml"
        content = reconcile_path.read_text(encoding="utf-8")
        self.assertIn("plan_localization.py", content)
        self.assertIn("locales_needing_work", content)
        self.assertIn("max-parallel: 2", content)
        self.assertIn("uses: ./.github/workflows/_generate-locale.yml", content)

    def test_generate_locale_workflow_concurrency_and_branches(self):
        worker_path = self.workflows_dir / "_generate-locale.yml"
        content = worker_path.read_text(encoding="utf-8")
        self.assertIn("localization-${{ github.repository }}-${{ inputs.locale }}", content)
        self.assertIn("automation/narration/en", content)
        self.assertIn("automation/localize/", content)
        self.assertIn("translate_sources.py", content)
        self.assertIn("generate_audio.py", content)
        self.assertIn("--plan-needed", content)

    def test_pinned_action_shas_are_valid_full_hashes(self):
        """Ensure all external GitHub Actions pinned by SHA use full 40-character git commit hashes."""
        import re
        sha_pattern = re.compile(r"^[0-9a-f]{40}$")
        for wf_path in self.workflows_dir.glob("*.yml"):
            content = wf_path.read_text(encoding="utf-8")
            for m in re.finditer(r"uses:\s*([\w\-]+/[\w\-]+)@([a-f0-9]+|\S+)", content):
                action, ref = m.group(1), m.group(2)
                if action.startswith("."):
                    continue
                # If pinned by hash (hex string), verify it is exactly 40 chars
                if re.match(r"^[0-9a-fA-F]+$", ref):
                    self.assertTrue(
                        sha_pattern.match(ref),
                        f"Action {action} in {wf_path.name} has invalid commit SHA: '{ref}' (len {len(ref)} != 40)"
                    )


if __name__ == "__main__":
    unittest.main()
