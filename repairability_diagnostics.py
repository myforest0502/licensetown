"""Read-only diagnostics for the formal repairability of repairing Nodes."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Iterable

from knowledge_node_canonical import canonicalize_knowledge_node_id
from knowledge_node_repair_evidence import (
    DIFFERENT_QUESTION_STRONG,
    DIFFERENT_QUESTION_WEAK,
    classify_repair_confirmation,
)
from knowledge_node_repairability import build_repairability_audit
from knowledge_node_state_transition import (
    derive_all_user_node_states,
    derive_state_timeline,
)


STRONG_AVAILABLE = "strong_different_question_available"
WEAK_ONLY = "different_question_weak_only"
FORMALLY_BLOCKED = "same_question_only_or_formally_blocked"


def _sort_key(item: dict[str, Any]):
    return (
        str(item.get("attempted_at") or item.get("answered_at") or ""),
        str(item.get("event_key") or ""),
        int(item.get("attempt_position") or 0),
        int(item.get("id") or 0),
    )


def _current_repair_cycle(history: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return attempts in the current formal repairing run using state replay."""
    ordered = sorted((dict(item) for item in history), key=_sort_key)
    timeline = derive_state_timeline(ordered)
    if not timeline or timeline[-1]["state"] != "repairing":
        return []
    start = len(timeline) - 1
    while start > 0 and timeline[start - 1]["state"] == "repairing":
        start -= 1
    return ordered[start:]


def build_repairing_node_repairability(
    attempts: Iterable[dict[str, Any]],
    *,
    as_of: datetime | None = None,
    repairability_records: Iterable[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Classify current repairing Nodes with existing formal evidence rules."""
    attempts = [dict(item) for item in attempts]
    as_of = as_of or datetime.now(timezone.utc)
    states = {
        item["canonical_node_id"]: item
        for item in derive_all_user_node_states(attempts, as_of=as_of)
        if item["state"] == "repairing"
    }
    registry = {
        item["canonical_node_id"]: dict(item)
        for item in (
            repairability_records
            if repairability_records is not None
            else build_repairability_audit()
        )
    }
    histories: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for attempt in attempts:
        node = canonicalize_knowledge_node_id(
            str(attempt.get("knowledge_node_id") or "")
        )
        if node in states:
            histories[node].append(attempt)

    details = []
    for node_id in sorted(states):
        static = registry.get(node_id, {})
        all_questions = sorted(
            map(str, static.get("question_ids", [])),
            key=lambda value: int(value[1:]) if value[1:].isdigit() else 10**9,
        )
        history = sorted(histories.get(node_id, []), key=_sort_key)
        current_cycle = _current_repair_cycle(history)
        wrong_questions = sorted({
            str(item.get("question_id") or "")
            for item in current_cycle
            if item.get("answer_status") != "unknown"
            and item.get("is_correct") is False
            and item.get("question_id")
        })
        answered_questions = sorted({
            str(item.get("question_id") or "")
            for item in history if item.get("question_id")
        })
        confident_wrong_count = sum(
            item.get("answer_status") != "unknown"
            and item.get("is_correct") is False
            and item.get("confidence") == 1
            for item in current_cycle
        )
        strong_candidates = []
        weak_candidates = []
        for candidate in all_questions:
            if candidate in wrong_questions or not wrong_questions:
                continue
            strengths = {
                classify_repair_confirmation(wrong, candidate)
                for wrong in wrong_questions
            }
            if DIFFERENT_QUESTION_STRONG in strengths:
                strong_candidates.append(candidate)
            elif DIFFERENT_QUESTION_WEAK in strengths:
                weak_candidates.append(candidate)
        different_questions = [
            question_id for question_id in all_questions
            if question_id not in wrong_questions
        ] if wrong_questions else []
        if strong_candidates:
            classification = STRONG_AVAILABLE
        elif weak_candidates:
            classification = WEAK_ONLY
        else:
            classification = FORMALLY_BLOCKED
        safety_levels = sorted({
            str(value) for value in static.get("safety", [])
            if str(value) and str(value) != "none"
        })
        details.append({
            "canonical_node_id": node_id,
            "formal_label": " / ".join(static.get("knowledge_node_labels", [])) or "名称未登録",
            "current_state": "repairing",
            "answered_question_ids": answered_questions,
            "wrong_question_ids": wrong_questions,
            "confident_wrong": confident_wrong_count > 0,
            "confident_wrong_count": confident_wrong_count,
            "all_question_ids": all_questions,
            "unseen_different_question_ids": [
                question_id for question_id in different_questions
                if question_id not in answered_questions
            ],
            "classification": classification,
            "strong_repair_candidate_question_ids": strong_candidates,
            "weak_repair_candidate_question_ids": weak_candidates,
            "safety": bool(safety_levels),
            "safety_levels": safety_levels,
        })

    counts = {
        STRONG_AVAILABLE: sum(item["classification"] == STRONG_AVAILABLE for item in details),
        WEAK_ONLY: sum(item["classification"] == WEAK_ONLY for item in details),
        FORMALLY_BLOCKED: sum(item["classification"] == FORMALLY_BLOCKED for item in details),
    }
    total = len(details)
    return {
        "repairing_node_total": total,
        "strong_available_count": counts[STRONG_AVAILABLE],
        "weak_only_count": counts[WEAK_ONLY],
        "same_or_blocked_count": counts[FORMALLY_BLOCKED],
        "repairable_rate": round(counts[STRONG_AVAILABLE] * 100 / total, 1) if total else 0,
        "details": details,
    }
