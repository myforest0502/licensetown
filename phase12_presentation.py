"""Pure learner-facing presentation for the Phase 11 shadow judgment."""

from __future__ import annotations

from collections import Counter
from typing import Any


STATES = ("unseen", "checking", "repairing", "repaired", "recheck_due", "stable")
REASON_WORDING = {
    "safety_repair": "安全に関わる重要な内容を優先して確認します。",
    "confident_wrong_cluster": "自信を持って間違えた内容が複数確認されています。",
    "repeated_wrong_cluster": "繰り返し間違えている内容を優先して直します。",
    "recheck_due": "一度直した内容を、時間を空けて確認する時期です。",
    "insufficient_coverage": "まだ十分に取り組めていない分野を広げます。",
    "uncertain_correct_cluster": "迷いながら正解した内容を、もう一度確認して定着させます。",
    "maintenance_only": "大きな弱点は見つかっていません。広く確認して定着を維持します。",
}
ATTENTION_WORDING = {
    "safety_repair": ("重要確認", "安全に関わる内容を確認する必要があります。"),
    "confident_wrong_cluster": ("修復中", "自信を持って間違えた内容を確認します。"),
    "repeated_wrong_cluster": ("修復中", "繰り返し確認が必要な内容があります。"),
    "recheck_due": ("再確認待ち", "一度直した内容を確認する時期です。"),
    "uncertain_correct_cluster": ("確認中", "迷いながら正解した内容を確認します。"),
}


def _state_summary(field_evidence: dict[str, Any]) -> dict[str, int]:
    counts = Counter(
        item.get("state")
        for item in field_evidence.get("canonical_node_evidence", ())
        if item.get("state") in STATES
    )
    return {state: counts[state] for state in STATES}


def build_phase12_presentation(
    shadow_judgment: dict[str, Any],
    field_evidence: dict[str, Any],
) -> dict[str, Any]:
    """Convert approved Shadow output without exposing technical evidence."""
    reason_code = str(shadow_judgment.get("reason_code") or "")
    if reason_code not in REASON_WORDING:
        raise ValueError(f"unsupported Phase 11 reason: {reason_code}")
    target_field = shadow_judgment.get("target_field")
    question_count = int(shadow_judgment.get("question_count") or 0)
    headline = (
        f"今日は{target_field}を{question_count}問"
        if target_field
        else f"今日はおすすめ学習を{question_count}問"
    )
    attention_items = []
    if reason_code in ATTENTION_WORDING:
        label, message = ATTENTION_WORDING[reason_code]
        attention_items.append({
            "label": label,
            "field": target_field or "全体",
            "message": message,
        })
    return {
        "enabled": True,
        "intent": str(shadow_judgment.get("learning_intent") or ""),
        "headline": headline,
        "reason": REASON_WORDING[reason_code],
        "target_field": target_field,
        "question_count": question_count,
        "recommended_route": str(shadow_judgment.get("recommended_route") or ""),
        "state_summary": _state_summary(field_evidence),
        "attention_items": attention_items[:3],
    }
