"""Read-only status summary for the LicenseTown internal developer console.

This module intentionally reads only repository files and non-secret feature-flag
presence. It never opens Production DB connections and never exposes secret
values. The internal console can therefore show high-level system health without
adding work to learner or supporter routes.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
BANK_DIR = ROOT / "data" / "question_bank"
MANIFEST_PATH = BANK_DIR / "bank_manifest.json"
TAG_AUDIT_PATH = BANK_DIR / "question_tags_audit.txt"

_TRUE_VALUES = {"1", "true", "yes", "on"}


def _flag(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in _TRUE_VALUES


def _read_manifest() -> dict:
    try:
        payload = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _read_audit_text() -> str:
    try:
        return TAG_AUDIT_PATH.read_text(encoding="utf-8")
    except OSError:
        return ""


def _extract_int(text: str, pattern: str) -> int | None:
    match = re.search(pattern, text, re.MULTILINE)
    return int(match.group(1)) if match else None


def _audit_summary(text: str) -> dict:
    errors = _extract_int(text, r"^errors:\s*(\d+)\s*$")
    return {
        "records": _extract_int(text, r"^records:\s*(\d+)\s*$"),
        "errors": errors,
        "status": "PASS" if errors == 0 else ("WARN" if errors is not None else "UNKNOWN"),
        "original": _extract_int(text, r"^\s*original:\s*(\d+)"),
        "past_exam": _extract_int(text, r"^\s*past_exam:\s*(\d+)"),
        "safety_critical": _extract_int(text, r"^\s*critical:\s*(\d+)"),
        "safety_moderate": _extract_int(text, r"^\s*moderate:\s*(\d+)"),
        "canonical_registry": _extract_int(text, r"^\s*registry nodes:\s*(\d+)"),
        "canonical_represented": _extract_int(
            text, r"^\s*canonical nodes represented by questions:\s*(\d+)"
        ),
        "canonical_singleton": _extract_int(text, r"^\s*singleton canonical nodes:\s*(\d+)"),
        "canonical_multi": _extract_int(text, r"^\s*multi-question canonical nodes:\s*(\d+)"),
        "shared_groups": _extract_int(text, r"^\s*confirmed-shared registry groups:\s*(\d+)"),
    }


def build_developer_system_status() -> dict:
    """Return a compact developer-only status snapshot without DB/network I/O."""
    manifest = _read_manifest()
    audit = _audit_summary(_read_audit_text())
    return {
        "question_bank": {
            "version": manifest.get("bank_version") or "unknown",
            "question_count": manifest.get("question_count"),
            "first_question_number": manifest.get("first_question_number"),
            "last_question_number": manifest.get("last_question_number"),
            **audit,
        },
        "feature_flags": {
            "node_adaptive": _flag("ENABLE_NODE_ADAPTIVE_RECOMMENDATION"),
            "prerequisite_backtrack": _flag("ENABLE_PREREQUISITE_BACKTRACK"),
            "learner_perf_log": _flag("LT_LEARNER_PATH_PERF_LOG"),
            "supporter_perf_log": _flag("LT_SUPPORTER_PERF_LOG"),
            "rich_menu_apply_once": _flag("LT_APPLY_RICH_MENU_V2_ON_BOOT"),
        },
        "capabilities": [
            {
                "name": "学習診断",
                "state": "available",
                "detail": "Phase11・repeat・cooldownをユーザー単位で確認",
            },
            {
                "name": "本人画面プレビュー",
                "state": "available",
                "detail": "開発QA用に合格への道を本人視点で確認",
            },
            {
                "name": "Question Bank監査",
                "state": "available" if audit.get("status") == "PASS" else "attention",
                "detail": "正式4ストア・タグ・Knowledge Node整合性の保存済み監査",
            },
            {
                "name": "Knowledge Node / Repair Supply",
                "state": "available",
                "detail": "正式データと学習診断から確認可能",
            },
            {
                "name": "性能・エラー監視",
                "state": "external",
                "detail": "Renderログで確認。常時の詳細計測ログは原則OFF",
            },
            {
                "name": "DB状態・履歴監査",
                "state": "external",
                "detail": "Neon/専用監査から確認。内部トップでは重いDB読込を行わない",
            },
        ],
    }
