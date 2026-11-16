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

    def test_visual_images_do_not_change_spoken_content(self) -> None:
        """Adding standalone or inline images must not invalidate audio chunks."""
        page = self.tmp_dir / "media.md"
        plain = "# Introduction\n\nThe content stays the same.\n\n## Next\n\nContinue reading.\n"
        with_standalone_image = plain.replace(
            "The content stays the same.\n\n",
            "The content stays the same.\n\n"
            "![Animated silhouette with earphones](assets/static/animations/softcloud-introduction.gif)\n\n",
        )
        with_inline_image = plain.replace(
            "The content stays the same.",
            "The content ![decorative image](assets/image.gif) stays the same.",
        )

        page.write_text(plain, encoding="utf-8")
        original = ga.extract_document(page, self.tmp_dir)
        original_elements = [e.to_dict() for e in original.elements]

        for updated in (with_standalone_image, with_inline_image):
            page.write_text(updated, encoding="utf-8")
            after = ga.extract_document(page, self.tmp_dir)
            self.assertEqual([e.to_dict() for e in after.elements], original_elements)
            self.assertEqual(after.page_source_hash, original.page_source_hash)
            self.assertNotEqual(after.source_file_sha256, original.source_file_sha256)

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
        import plan_localization as pl

        # Polish was upgraded to 128k + style/language_code, so existing audio/pl/introduction
        # is pending CI regeneration alongside un-narrated pages.
        pl_pages = ga.discover_enabled_pages(
            root=ROOT,
            locale="pl",
            plan_needed_only=True,
        )
        pl_names = [p.name for p in pl_pages]
        self.assertIn("introduction.md", pl_names)
        self.assertIn("README.md", pl_names)
        self.assertIn("architecture.md", pl_names)

        pl_plan = pl.build_plan(ROOT, only_locale="pl")["locales"]["pl"]["documents"]
        expected_pl = {
            item["document"]
            for item in pl_plan
            if "narrate" in item["actions"]
        }
        pl_rels = {p.relative_to(ROOT / "i18n" / "pl").as_posix() for p in pl_pages}
        self.assertEqual(pl_rels, expected_pl)

        # German remains on the baseline 64k config, so current introduction.md is skipped.
        de_pages = ga.discover_enabled_pages(
            root=ROOT,
            locale="de",
            plan_needed_only=True,
        )
        de_names = [p.name for p in de_pages]
        self.assertNotIn("introduction.md", de_names)
        self.assertIn("README.md", de_names)
        self.assertIn("architecture.md", de_names)

    def test_locale_tts_quality_config_and_hash_compatibility(self) -> None:
        import json

        en_cfg = ga.resolve_locale_narration_config(ROOT, "en")
        self.assertEqual(en_cfg.tts_model, "gemini-3.8-flash-tts")
        self.assertEqual(en_cfg.mp3_bitrate, "128k")
        self.assertEqual(en_cfg.sample_rate, 24000)
        self.assertEqual(en_cfg.language_code, "en-US")
        self.assertTrue(en_cfg.speech_style)

        pl_cfg = ga.resolve_locale_narration_config(ROOT, "pl")
        self.assertEqual(pl_cfg.tts_model, "gemini-3.8-flash-tts")
        self.assertEqual(pl_cfg.mp3_bitrate, "128k")
        self.assertEqual(pl_cfg.sample_rate, 24000)
        self.assertEqual(pl_cfg.language_code, "pl-PL")
        self.assertTrue(pl_cfg.speech_style)

        # Unchanged locales preserve exact baseline config hash so existing audio stays valid.
        de_cfg = ga.resolve_locale_narration_config(ROOT, "de")
        self.assertEqual(de_cfg.mp3_bitrate, "64k")
        self.assertEqual(de_cfg.language_code, "")
        self.assertEqual(de_cfg.speech_style, "")
        self.assertNotIn("language_code", de_cfg.tts_config_dict())
        self.assertNotIn("speech_style", de_cfg.tts_config_dict())
        manifest = json.loads((ROOT / "audio/de/introduction/manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["chunks"][0]["tts_config_hash"], de_cfg.tts_config_hash())

    def test_synthesize_speech_sends_style_and_language_code(self) -> None:
        import base64
        from unittest import mock

        en_cfg = ga.resolve_locale_narration_config(ROOT, "en")
        de_cfg = ga.resolve_locale_narration_config(ROOT, "de")
        client = ga.GeminiClient(api_key="AIzaSyDummyKeyForUnitTesting123456")

        recorded: list[tuple[str, str, dict | None]] = []

        def fake_request(method: str, endpoint: str, payload: dict | None = None) -> dict:
            recorded.append((method, endpoint, payload))
            if method == "GET":
                return {
                    "name": f"models/{en_cfg.tts_model}",
                    "supportedGenerationMethods": ["generateContent"],
                }
            return {
                "candidates": [
                    {
                        "content": {
                            "parts": [
                                {
                                    "inlineData": {
                                        "data": base64.b64encode(b"RIFFdemo").decode("ascii"),
                                        "mimeType": "audio/wav",
                                    }
                                }
                            ]
                        }
                    }
                ]
            }

        with mock.patch.object(client, "_request_json", side_effect=fake_request):
            audio_en, mime_en = client.synthesize_speech("SoftCloud overview.", en_cfg)
            self.assertEqual(audio_en, b"RIFFdemo")
            self.assertEqual(mime_en, "audio/wav")

            audio_de, _ = client.synthesize_speech("SoftCloud Überblick.", de_cfg)
            self.assertEqual(audio_de, b"RIFFdemo")

        post_calls = [p for m, _, p in recorded if m == "POST"]
        self.assertEqual(len(post_calls), 2)
        en_payload, de_payload = post_calls
        self.assertEqual(en_payload["contents"][0]["role"], "user")
        self.assertEqual(
            en_payload["contents"][0]["parts"][0]["speechMetadata"],
            {"style": en_cfg.speech_style},
        )
        self.assertEqual(
            en_payload["generationConfig"]["speechConfig"]["languageCode"],
            "en-US",
        )
        self.assertEqual(
            en_payload["generationConfig"]["speechConfig"]["voiceConfig"]["prebuiltVoiceConfig"]["voiceName"],
            en_cfg.voice_name,
        )
        self.assertNotIn("speechMetadata", de_payload["contents"][0]["parts"][0])
        self.assertNotIn("languageCode", de_payload["generationConfig"]["speechConfig"])

    def test_tts_model_404_fails_closed_without_fallback(self) -> None:
        import io
        import urllib.error
        from unittest import mock

        client = ga.GeminiClient(api_key="AIzaSyDummyKeyForUnitTesting123456", max_retries=0)

        def make_404(*args, **kwargs):
            raise urllib.error.HTTPError(
                url="https://example.invalid/models/gemini-3.8-flash-tts",
                code=404,
                msg="Not Found",
                hdrs=None,
                fp=io.BytesIO(b'{"error": {"message": "Model not found"}}'),
            )

        with mock.patch("urllib.request.urlopen", side_effect=make_404) as mocked_open:
            with self.assertRaises(ga.NarrationError):
                client.verify_model_available("gemini-3.8-flash-tts")
            self.assertEqual(mocked_open.call_count, 1)

        with mock.patch("urllib.request.urlopen", side_effect=make_404) as mocked_open:
            with self.assertRaises(ga.NarrationError):
                client._request_json("POST", "models/gemini-3.8-flash-tts:generateContent", {"contents": []})
            self.assertEqual(mocked_open.call_count, 1)

    def test_progressive_check_only_accepts_stale_config_and_strict_rejects(self) -> None:
        self.assertEqual(
            ga.main(["--locale", "en", "--page", "introduction.md", "--check-only", "--progressive"]),
            0,
        )
        self.assertNotEqual(
            ga.main(["--locale", "en", "--page", "introduction.md", "--check-only"]),
            0,
        )


if __name__ == "__main__":
    unittest.main()
