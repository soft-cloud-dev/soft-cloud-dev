#!/usr/bin/env python3
"""
plan_localization.py
--------------------
Read-only reconciliation planner for SoftCloud localization.

Compares the *desired* state (published English documents from myst.yml, the
effective glossary and the policy in i18n/locales.yml) with the *recorded* state
(i18n/<locale>/provenance.json, narration manifests and audio files in the
working tree) and emits a deterministic plan. It never calls a model API and
never modifies tracked files.

The plan is computed from file state, not from the latest commit's diff, so a
previously failed run cannot leave an older gap permanently overlooked.

Translation states per document:
  missing        localized file absent                      -> translate
  stale          English changed since recorded translation -> update
  human_edit     localized file differs from recorded hash  -> preserve, refresh narration
  stale+edit     both of the above                          -> needs explicit refresh
  policy_changed glossary/policy changed, text otherwise ok -> reassess
  invalid        preservation checks fail                   -> regenerate or review
  current        nothing to do
  removed        provenance/localized file for an unpublished page -> propose cleanup

Narration states per narrated document:
  missing, corrupt (absent/mismatched chunk), stale (text/voice/model changed), current
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from i18n_utils import (  # noqa: E402
    atomic_write_json,
    get_enabled_locales,
    load_glossary,
    load_locales_config,
    sha256_file,
    sha256_json,
)
from translate_sources import (  # noqa: E402
    discover_source_documents,
    translation_policy_fingerprint,
    verify_document_preservation,
)
from translation_engine import document_dependencies  # noqa: E402

PLAN_SCHEMA_VERSION = "1.0"


def page_id_from_path(rel_path: str) -> str:
    """Mirror generate_audio.page_id_from_path without importing the TTS stack."""
    import generate_audio as ga

    return ga.page_id_from_path(rel_path)


def policy_settings(cfg: dict[str, Any]) -> dict[str, Any]:
    loc = cfg.get("localization") or {}
    narr = loc.get("narration") or {}
    return {
        "branch_prefix": str(loc.get("branch_prefix", "automation/localize/")),
        "english_narration_branch": str(loc.get("english_narration_branch", "automation/narration/en")),
        "max_parallel_locales": int(loc.get("max_parallel_locales", 2)),
        "translation": loc.get("translation") or {},
        "narration_mode": str(narr.get("mode", "all_except")),
        "narration_opt_out": list(narr.get("opt_out") or []),
        "narrated_pages": list(cfg.get("narrated_pages") or []),
    }


def narrated_documents(docs: list[str], policy: dict[str, Any]) -> list[str]:
    """Narration is enabled by default (all_except) with explicit opt-outs."""
    narratable = [d for d in docs if d.endswith(".md")]
    if policy["narration_mode"] == "allowlist":
        return [d for d in narratable if d in policy["narrated_pages"]]
    return [d for d in narratable if d not in policy["narration_opt_out"]]


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except (OSError, ValueError):
        return None


def audio_state(
    root: Path, locale: str, info: dict[str, Any], is_default: bool, rel_doc: str, text_path: Path
) -> tuple[str, list[str]]:
    audio_root = root / str(info.get("audio_dir", "audio" if is_default else f"audio/{locale}"))
    page_dir = audio_root / page_id_from_path(rel_doc)
    manifest = load_json(page_dir / "manifest.json")
    if manifest is None:
        return "missing", ["no narration manifest"]
    reasons: list[str] = []
    voice = info.get("voice") or {}
    cfg = manifest.get("narration_config") or {}
    if manifest.get("locale") != locale:
        reasons.append("manifest locale mismatch")
    if manifest.get("source_file_sha256") != sha256_file(text_path):
        reasons.append("spoken text changed since narration")
    if voice.get("voice_name") and cfg.get("voice_name") != voice["voice_name"]:
        reasons.append("voice changed")
    if voice.get("tts_model") and cfg.get("tts_model") != voice["tts_model"]:
        reasons.append("TTS model changed")
    if voice.get("text_model") and cfg.get("text_model") != voice["text_model"]:
        reasons.append("code-explanation model changed")
    corrupt: list[str] = []
    if not (page_dir / str(manifest.get("transcript_file", "transcript.json"))).is_file():
        corrupt.append("transcript missing")
    for chunk in manifest.get("chunks", []):
        f = page_dir / str(chunk.get("audio_file", ""))
        if not f.is_file():
            corrupt.append(f"missing {chunk.get('audio_file')}")
        elif sha256_file(f) != chunk.get("audio_sha256"):
            corrupt.append(f"checksum mismatch {chunk.get('audio_file')}")
    if corrupt:
        return "corrupt", corrupt
    if reasons:
        return "stale", reasons
    return "current", []


def plan_translation(
    root: Path,
    locale: str,
    info: dict[str, Any],
    docs: list[str],
    glossary_sha: str,
    policy_sha: str,
) -> tuple[dict[str, dict[str, Any]], list[str]]:
    loc_root = root / str(info.get("source_dir", f"i18n/{locale}"))
    prov = load_json(loc_root / "provenance.json") or {}
    recorded_docs: dict[str, Any] = prov.get("documents") or {}
    out: dict[str, dict[str, Any]] = {}
    for rel in docs:
        en_path, loc_path = root / rel, loc_root / rel
        entry = recorded_docs.get(rel)
        deps = document_dependencies(root, rel)
        reasons: list[str] = []
        if not loc_path.is_file():
            state = "missing"
            reasons.append("no localized file")
        elif not isinstance(entry, dict):
            state = "stale"
            reasons.append("no provenance record")
        else:
            src_changed = entry.get("source_sha256") != sha256_file(en_path)
            dep_changed = (
                "dependency_sha256" in entry and entry["dependency_sha256"] != sha256_json(deps)
            )
            human_edit = entry.get("translated_sha256") != sha256_file(loc_path)
            policy_changed = bool(prov) and (
                entry.get("glossary_sha256", prov.get("glossary_sha256")) != glossary_sha
                or ("policy_sha256" in entry and entry["policy_sha256"] != policy_sha)
            )
            if src_changed:
                reasons.append("English source changed")
            if dep_changed:
                reasons.append("included dependency changed")
            if human_edit:
                reasons.append("localized text differs from recorded output (human edit)")
            if (src_changed or dep_changed) and human_edit:
                state = "stale+edit"
            elif src_changed or dep_changed:
                state = "stale"
            elif human_edit:
                state = "human_edit"
            else:
                problems = verify_document_preservation(en_path, loc_path, locale)
                if problems:
                    state, reasons = "invalid", problems
                elif policy_changed:
                    state = "policy_changed"
                    reasons.append("glossary or translation policy changed")
                else:
                    state = "current"
        out[rel] = {"state": state, "reasons": reasons, "dependencies": deps}
    removed = sorted(set(recorded_docs) - set(docs))
    return out, removed


def build_plan(root: Path, only_locale: str | None = None) -> dict[str, Any]:
    cfg = load_locales_config(root)
    locales = get_enabled_locales(cfg)
    default = str(cfg.get("default_locale", "en"))
    policy = policy_settings(cfg)
    docs = discover_source_documents(root)
    narrated = narrated_documents(docs, policy)
    glossary_sha = sha256_json(load_glossary(root))
    policy_sha = translation_policy_fingerprint(root)

    plan: dict[str, Any] = {
        "schema_version": PLAN_SCHEMA_VERSION,
        "published_documents": docs,
        "narrated_documents": narrated,
        "max_parallel_locales": policy["max_parallel_locales"],
        "locales": {},
    }
    for code, info in locales.items():
        if only_locale and code != only_locale:
            continue
        is_default = code == default
        loc_root = root / str(info.get("source_dir", "." if is_default else f"i18n/{code}"))
        translation: dict[str, dict[str, Any]] = {}
        removed: list[str] = []
        if not is_default:
            translation, removed = plan_translation(root, code, info, docs, glossary_sha, policy_sha)
        items = []
        for rel in docs:
            t = translation.get(rel, {"state": "n/a", "reasons": [], "dependencies": {}})
            a_state, a_reasons = "n/a", []
            if rel in narrated:
                text_path = (root / rel) if is_default else (loc_root / rel)
                if text_path.is_file():
                    a_state, a_reasons = audio_state(root, code, info, is_default, rel, text_path)
                else:
                    a_state, a_reasons = "blocked", ["localized text not yet available"]
            actions: list[str] = []
            if t["state"] in ("missing", "stale", "invalid", "policy_changed"):
                actions.append("translate")
            if t["state"] in ("stale+edit",):
                actions.append("manual_refresh_required")
            if a_state in ("missing", "stale", "corrupt") or (
                t["state"] in ("human_edit", "missing", "stale", "invalid", "policy_changed")
                and rel in narrated
            ):
                actions.append("narrate")
            items.append(
                {
                    "document": rel,
                    "translation": t["state"],
                    "translation_reasons": t["reasons"],
                    "dependencies": t["dependencies"],
                    "narration": a_state,
                    "narration_reasons": a_reasons,
                    "actions": actions,
                }
            )
        cleanup = [
            {"document": rel, "action": "propose_removal"} for rel in removed
        ]
        branch = (
            policy["english_narration_branch"] if is_default else f"{policy['branch_prefix']}{code}"
        )
        needs_worker = any(i["actions"] for i in items) or bool(cleanup)
        plan["locales"][code] = {
            "branch": branch,
            "authoritative": is_default,
            "needs_worker": needs_worker,
            "documents": items,
            "cleanup": cleanup,
        }
    plan["locales_needing_work"] = sorted(c for c, v in plan["locales"].items() if v["needs_worker"])
    return plan


def explain(plan: dict[str, Any]) -> str:
    lines: list[str] = []
    for code, loc in plan["locales"].items():
        lines.append(f"[{code}] branch {loc['branch']}: " + ("WORK NEEDED" if loc["needs_worker"] else "current"))
        for d in loc["documents"]:
            if not d["actions"] and d["translation"] in ("current", "n/a") and d["narration"] in ("current", "n/a"):
                continue
            why = "; ".join(d["translation_reasons"] + d["narration_reasons"]) or "-"
            lines.append(
                f"  {d['document']}: translation={d['translation']} narration={d['narration']} "
                f"actions={','.join(d['actions']) or 'none'} ({why})"
            )
        for c in loc["cleanup"]:
            lines.append(f"  {c['document']}: no longer published -> {c['action']}")
    lines.append("Locales needing work: " + (", ".join(plan["locales_needing_work"]) or "none"))
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Read-only localization reconciliation planner.")
    p.add_argument("--locale", default="", help="Plan a single configured locale.")
    p.add_argument("--output", default="", help="Write the JSON plan to this path.")
    p.add_argument("--json", action="store_true", help="Print JSON instead of the explanation.")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = Path.cwd().resolve()
    configured = get_enabled_locales(load_locales_config(root))
    if args.locale and args.locale not in configured:
        print(f"Unknown or disabled locale: {args.locale!r}", file=sys.stderr)
        return 2
    plan = build_plan(root, args.locale or None)
    if args.output:
        atomic_write_json(Path(args.output), plan)
    print(json.dumps(plan, indent=2, ensure_ascii=False) if args.json else explain(plan))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
