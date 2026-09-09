"""Pure longitudinal companion-record derivation from authoritative attempt history.

The record summarizes meaningful learner-state episodes without persisting a second
state authority. Raw attempts remain the source of truth; Knowledge Node state and
question-equivalence semantics are reused from the formal derivation modules.
"""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

from knowledge_node_state_transition import derive_knowledge_node_state, derive_state_timeline
from question_equivalence import canonicalize_question_evidence_node


BANK_DIR = Path(__file__).resolve().parent / "data" / "question_bank"

WRONG_PATTERN_LABELS = {
    "retention_regression": "いったん直した内容を時間を空けた確認で再び誤答",
    "confident_wrong": "自信ありで誤答",
    "repeated_cross_question_wrong": "同じ知識を別問題でも繰り返し誤答",
    "repeated_same_question_wrong": "同じ問題を繰り返し誤答",
    "unknown_answer": "分からないと回答",
    "uncertain_wrong": "迷い・あてずっぽうで誤答",
    "wrong_answer": "単発の誤答",
}


def _load_node_labels() -> dict[str, str]:
    nodes = json.loads((BANK_DIR / "knowledge_nodes.json").read_text(encoding="utf-8-sig"))
    labels = {
        str(item.get("knowledge_node_id")): str(item.get("label") or item.get("knowledge_node_id"))
        for item in nodes
    }
    canonical = json.loads(
        (BANK_DIR / "knowledge_node_canonical_map.json").read_text(encoding="utf-8-sig")
    )
    for item in canonical:
        node_id = str(item.get("canonical_node_id") or "")
        if node_id:
            labels[node_id] = str(item.get("canonical_label") or labels.get(node_id) or node_id)
    return labels


_NODE_LABELS = _load_node_labels()


def _sort_key(item: dict[str, Any]) -> tuple[str, str, int, int]:
    return (
        str(item.get("attempted_at") or item.get("answered_at") or ""),
        str(item.get("event_key") or ""),
        int(item.get("attempt_position") or 0),
        int(item.get("id") or 0),
    )


def _timestamp(item: dict[str, Any]) -> str | None:
    value = item.get("attempted_at") or item.get("answered_at")
    return value.isoformat() if isinstance(value, datetime) else (str(value) if value else None)


def _is_wrong(item: dict[str, Any]) -> bool:
    return item.get("answer_status") == "unknown" or item.get("is_correct") is False


def _wrong_pattern(
    history: list[dict[str, Any]],
    timeline: list[dict[str, Any]],
    final: dict[str, Any],
) -> dict[str, Any] | None:
    """Classify observable wrong-answer evidence without claiming a hidden psychology."""
    wrong_indexes = [index for index, item in enumerate(history) if _is_wrong(item)]
    if not wrong_indexes:
        return None

    for index in reversed(wrong_indexes):
        previous_state = "unseen" if index == 0 else str(timeline[index - 1]["state"])
        if previous_state in {"repaired", "stable", "recheck_due"}:
            code = "retention_regression"
            return {
                "code": code,
                "label": WRONG_PATTERN_LABELS[code],
                "basis": "wrong_after_repaired_or_retention_state",
            }

    latest_wrong = history[wrong_indexes[-1]]
    if latest_wrong.get("answer_status") == "unknown":
        code = "unknown_answer"
        return {"code": code, "label": WRONG_PATTERN_LABELS[code], "basis": "answer_status_unknown"}

    if latest_wrong.get("confidence") == 1:
        code = "confident_wrong"
        return {"code": code, "label": WRONG_PATTERN_LABELS[code], "basis": "wrong_with_confidence_1"}

    level = str(final.get("confirmed_weakness_evidence_level") or final.get("evidence_level") or "")
    if level in {"CROSS_QUESTION_WRONG", "CROSS_QUESTION_CONFIDENT_WRONG"}:
        code = "repeated_cross_question_wrong"
        return {"code": code, "label": WRONG_PATTERN_LABELS[code], "basis": level}
    if level == "REPEATED_SAME_QUESTION_WRONG":
        code = "repeated_same_question_wrong"
        return {"code": code, "label": WRONG_PATTERN_LABELS[code], "basis": level}

    if latest_wrong.get("confidence") in {2, 3, "2", "3"}:
        code = "uncertain_wrong"
        return {"code": code, "label": WRONG_PATTERN_LABELS[code], "basis": "wrong_with_confidence_2_or_3"}

    code = "wrong_answer"
    return {"code": code, "label": WRONG_PATTERN_LABELS[code], "basis": "single_evaluable_wrong"}


def _priority_reason(history: list[dict[str, Any]], final: dict[str, Any]) -> str | None:
    wrong = [item for item in history if _is_wrong(item)]
    if not wrong:
        return None
    if any(item.get("confidence") == 1 for item in wrong if item.get("answer_status") != "unknown"):
        return "confident_wrong"
    level = str(final.get("confirmed_weakness_evidence_level") or final.get("evidence_level") or "")
    if level in {"CROSS_QUESTION_WRONG", "CROSS_QUESTION_CONFIDENT_WRONG", "REPEATED_SAME_QUESTION_WRONG"}:
        return "repeated_wrong"
    if any(item.get("answer_status") == "unknown" for item in wrong):
        return "unknown_answer"
    return "wrong_answer"


def _events(history: list[dict[str, Any]], timeline: list[dict[str, Any]], current: dict[str, Any]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    previous = "unseen"
    previous_retention_stage = None
    for item, state_row in zip(history, timeline):
        state = str(state_row["state"])
        retention_stage = state_row.get("retention_stage")
        event_type = None
        if state == "repairing" and previous in {"unseen", "checking"}:
            event_type = "weakness_detected"
        elif state == "repaired" and previous == "repairing":
            event_type = "repair_confirmed"
        elif (
            state == "repaired"
            and retention_stage != previous_retention_stage
            and retention_stage in {"day3_passed", "day7_passed"}
        ):
            event_type = "retention_checkpoint_passed"
        elif state == "stable" and previous in {"repaired", "recheck_due"}:
            event_type = "retention_confirmed"
        elif state == "repairing" and previous in {"repaired", "stable", "recheck_due"}:
            event_type = "regression_detected"
        elif state == "checking" and previous == "unseen":
            event_type = "checking_started"
        if event_type:
            events.append({
                "event": event_type,
                "at": _timestamp(item),
                "question_id": str(item.get("question_id") or ""),
                "is_correct": item.get("is_correct"),
                "confidence": item.get("confidence"),
                "state_after": state,
                "retention_stage_after": retention_stage,
            })
        previous = state
        previous_retention_stage = retention_stage

    if current.get("state") == "recheck_due" and (not events or events[-1].get("state_after") != "recheck_due"):
        events.append({
            "event": "retention_recheck_due",
            "at": (
                current.get("next_review_at").isoformat()
                if isinstance(current.get("next_review_at"), datetime)
                else current.get("next_review_at")
            ),
            "question_id": current.get("retention_reference_question_id"),
            "is_correct": None,
            "confidence": None,
            "state_after": "recheck_due",
            "retention_stage_after": current.get("retention_stage"),
            "retention_checkpoint": current.get("retention_checkpoint"),
        })
    return events


def build_companion_record(
    attempts: Iterable[dict[str, Any]],
    *,
    as_of: datetime | None = None,
    include_checking_only: bool = False,
) -> dict[str, Any]:
    """Build compact longitudinal episodes without creating another state authority."""
    rows = [dict(item) for item in attempts]
    user_ids = {str(item.get("user_id") or "") for item in rows}
    if len(user_ids) > 1:
        raise ValueError("attempts must belong to one user")

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in rows:
        node_id = canonicalize_question_evidence_node(
            str(item.get("question_id") or ""),
            str(item.get("knowledge_node_id") or ""),
        )
        if node_id:
            grouped[str(node_id)].append(item)

    episodes = []
    for node_id, history in sorted(grouped.items()):
        history.sort(key=_sort_key)
        current = derive_knowledge_node_state(history, node_id, as_of=as_of)
        timeline = derive_state_timeline(history)
        has_wrong = any(_is_wrong(item) for item in history)
        if not has_wrong and not include_checking_only:
            continue
        events = _events(history, timeline, current)
        wrong_pattern = _wrong_pattern(history, timeline, current)
        episodes.append({
            "canonical_node_id": node_id,
            "label": _NODE_LABELS.get(node_id, node_id),
            "current_state": current["state"],
            "priority_reason": _priority_reason(history, current),
            "wrong_pattern": wrong_pattern,
            "attempt_count": len(history),
            "distinct_question_count": int(current.get("distinct_question_count") or 0),
            "wrong_question_count": int(current.get("wrong_question_count") or 0),
            "confirmed_weakness_evidence_level": current.get("confirmed_weakness_evidence_level"),
            "repair_confirmation_count": int(current.get("confident_correct_after_wrong_count") or 0),
            "retention_reference_question_id": current.get("retention_reference_question_id"),
            "retention_stage": current.get("retention_stage"),
            "retention_checkpoint": current.get("retention_checkpoint"),
            "next_review_at": (
                current.get("next_review_at").isoformat()
                if isinstance(current.get("next_review_at"), datetime)
                else current.get("next_review_at")
            ),
            "events": events,
        })

    state_rank = {"repairing": 0, "recheck_due": 1, "repaired": 2, "stable": 3, "checking": 4, "unseen": 5}
    episodes.sort(
        key=lambda item: (
            state_rank.get(str(item["current_state"]), 9),
            0 if item.get("priority_reason") == "confident_wrong" else 1,
            -int(item.get("wrong_question_count") or 0),
            str(item["canonical_node_id"]),
        )
    )
    counts: dict[str, int] = defaultdict(int)
    for item in episodes:
        counts[str(item["current_state"])] += 1
    return {
        "status": "companion_record_v0.2",
        "authoritative_attempt_source": "question_attempts",
        "authoritative_state_source": "derive_knowledge_node_state",
        "wrong_pattern_semantics": "observable_evidence_not_psychological_diagnosis",
        "persisted": False,
        "episode_count": len(episodes),
        "state_counts": dict(sorted(counts.items())),
        "episodes": episodes,
    }
