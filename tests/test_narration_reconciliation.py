#!/usr/bin/env python3
"""
Unit tests for Stage 3: Narration reconciliation.

Covers:
- Locale voice resolution from i18n/locales.yml with CLI override precedence.
- speech_input_hash computation and stability.
- Speech reuse independent of chunk position / element IDs.
- Plan-needed discovery and filtering.
- Explicit TTS model identifier validation.
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = ROOT / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import generate_audio as ga


class DummyGeminiClient:
    """Mock Gemini client tracking speech synthesis and code explanation calls."""

    def __init__(self) -> None:
        self.synthesize_calls: list[str] = []
        self.code_summary_calls: list[tuple[str, str]] = []

    def verify_model_available(self, model_id: str) -> dict[str, str]:
        return {"name": f"models/{model_id}"}

    def generate_code_summary(self, code: str, language: str, config: ga.NarrationConfig) -> str:
        self.code_summary_calls.append((code, language))
        return f"Spoken explanation for {language} code."

    def synthesize_speech(self, text: str, config: ga.NarrationConfig) -> tuple[bytes, str]:
        self.synthesize_calls.append(text)
        if shutil.which("ffmpeg") is None:
            fixture_mp3 = next((ROOT / "audio" / "introduction").glob("chunk-*.mp3"))
            return fixture_mp3.read_bytes(), "audio/mp3"
        # Synthetic 16-bit PCM: 24000 samples/sec * 0.2 sec = 4800 samples = 9600 bytes
        pcm_bytes = b"\x00\x00" * 4800
        return pcm_bytes, "audio/L16;rate=24000"


class TestNarrationReconciliation(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = Path(tempfile.mkdtemp(prefix="test_narr_recon_"))
        self.addCleanup(lambda: shutil.rmtree(self.tmp_dir, ignore_errors=True))

    def test_explicit_tts_model_validation(self) -> None:
        # Valid identifiers
        self.assertEqual(ga.validate_tts_model_identifier("gemini-3.8-flash-tts"), "gemini-3.8-flash-tts")
        self.assertEqual(ga.validate_tts_model_identifier("models/gemini-2.5-flash"), "models/gemini-2.5-flash")

        # Invalid identifiers
        with self.assertRaises(ga.NarrationError):
            ga.validate_tts_model_identifier("")
        with self.assertRaises(ga.NarrationError):
            ga.validate_tts_model_identifier("   ")
        with self.assertRaises(ga.NarrationError):
            ga.validate_tts_model_identifier("invalid model; rm -rf")

    def test_locale_voice_resolution(self) -> None:
        # Default locales in repo
        en_cfg = ga.resolve_locale_narration_config(ROOT, "en")
        self.assertEqual(en_cfg.voice_name, "Kore")
        self.assertEqual(en_cfg.tts_model, "gemini-3.8-flash-tts")
        self.assertEqual(en_cfg.text_model, "gemini-3.8-flash")

        # Custom locales.yml in temp dir with a different voice
        custom_root = self.tmp_dir / "custom_proj"
        custom_i18n = custom_root / "i18n"
        custom_i18n.mkdir(parents=True, exist_ok=True)
        (custom_i18n / "locales.yml").write_text(
            """
schema_version: "1.0.0"
default_locale: "en"
locales:
  pl:
    code: "pl"
    enabled: true
    voice:
      voice_name: "Aoede"
      tts_model: "gemini-3.8-flash-tts"
      text_model: "gemini-3.8-flash"
""",
            encoding="utf-8",
        )
        pl_custom_cfg = ga.resolve_locale_narration_config(custom_root, "pl")
        self.assertEqual(pl_custom_cfg.voice_name, "Aoede")
        self.assertEqual(pl_custom_cfg.tts_model, "gemini-3.8-flash-tts")

        # Explicit CLI overrides must override locales.yml
        custom_cfg = ga.resolve_locale_narration_config(
            custom_root,
            "pl",
            cli_voice="Fenrir",
            cli_tts_model="custom-tts-model",
            cli_text_model="custom-text-model",
        )
        self.assertEqual(custom_cfg.voice_name, "Fenrir")
        self.assertEqual(custom_cfg.tts_model, "custom-tts-model")
        self.assertEqual(custom_cfg.text_model, "custom-text-model")

    def test_speech_input_hash_stability(self) -> None:
        cfg = ga.resolve_locale_narration_config(ROOT, "en")
        text = "Hello world of documentation."
        t_sha = ga.sha256_text(text)
        h1 = ga.compute_speech_input_hash("en", t_sha, cfg.tts_config_hash())
        h2 = ga.compute_speech_input_hash("en", t_sha, cfg.tts_config_hash())
        self.assertEqual(h1, h2)

        # Different locale or text changes the hash
        h_pl = ga.compute_speech_input_hash("pl", t_sha, cfg.tts_config_hash())
        self.assertNotEqual(h1, h_pl)

        t2_sha = ga.sha256_text("Different text.")
        h_diff_text = ga.compute_speech_input_hash("en", t2_sha, cfg.tts_config_hash())
        self.assertNotEqual(h1, h_diff_text)

    def test_speech_reuse_when_chunks_shift(self) -> None:
        """When an earlier section is added or modified, subsequent chunks shift position

        but their speech is reused without synthesizing speech via API.
        """
        doc_v1 = self.tmp_dir / "sample.md"
        doc_v1.write_text(
            "# Title\n\nSection one content that will be chunk 1.\n\n"
            "## Subhead\n\nSection two content that will be chunk 2.\n",
            encoding="utf-8",
        )
        audio_root = self.tmp_dir / "audio"
        cfg = ga.resolve_locale_narration_config(self.tmp_dir, "en")
        client = DummyGeminiClient()

        # Step 1: Initial generation
        manifest_v1 = ga.process_page(
            source_path=doc_v1,
            root=self.tmp_dir,
            audio_root=audio_root,
            config=cfg,
            client=client,
        )
        self.assertEqual(len(client.synthesize_calls), 2)
        self.assertEqual(manifest_v1["total_chunks"], 2)
        chunk2_v1 = manifest_v1["chunks"][1]
        chunk2_v1_audio_file = chunk2_v1["audio_file"]
        chunk2_v1_audio_sha = chunk2_v1["audio_sha256"]
        self.assertTrue((audio_root / "sample" / chunk2_v1_audio_file).is_file())

        # Step 2: Now insert an introductory section at the very beginning.
        # Section two content is now chunk 3 instead of chunk 2!
        doc_v2 = self.tmp_dir / "sample.md"
        doc_v2.write_text(
            "# Title\n\nNewly inserted preamble.\n\n"
            "## Section A\n\nSection one content that will be chunk 1.\n\n"
            "## Subhead\n\nSection two content that will be chunk 2.\n",
            encoding="utf-8",
        )

        client.synthesize_calls.clear()
        manifest_v2 = ga.process_page(
            source_path=doc_v2,
            root=self.tmp_dir,
            audio_root=audio_root,
            config=cfg,
            client=client,
        )
        # Only the newly inserted chunk and changed section one should require synthesis.
        # Section two content was reused by speech_input_hash!
        self.assertNotIn("Section two content that will be chunk 2.", [c for c in client.synthesize_calls])

        # Verify that chunk 3 in manifest_v2 has the exact same audio SHA-256 and duration as chunk 2 from v1
        chunk3_v2 = manifest_v2["chunks"][2]
        self.assertEqual(chunk3_v2["audio_sha256"], chunk2_v1_audio_sha)
        self.assertEqual(chunk3_v2["duration_seconds"], chunk2_v1["duration_seconds"])
        self.assertTrue((audio_root / "sample" / chunk3_v2["audio_file"]).is_file())

    def test_plan_needed_discovery(self) -> None:
        pages = ga.discover_enabled_pages(
            root=ROOT,
            locale="pl",
            plan_needed_only=True,
        )
        # Introduction is already narrated on main; README, architecture, projects/linux need narration
        page_names = [p.name for p in pages]
        self.assertNotIn("introduction.md", page_names)
        self.assertIn("README.md", page_names)
        self.assertIn("architecture.md", page_names)


if __name__ == "__main__":
    unittest.main()
