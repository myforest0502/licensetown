"""Pure Node-state-aware recommendation selector (feature-gated by caller)."""

from __future__ import annotations

import random
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any, Iterable

from knowledge_node_canonical import canonicalize_knowledge_node_id
from knowledge_node_state_transition import derive_all_user_node_states
from question_bank import get_question_tag, get_quiz_question, question_ids
from prerequisite_backtrack_pilot import (
    is_prerequisite_backtrack_pilot_enabled,
    parse_prerequisite_backtrack_pilot_user_ids,
)


REPAIR_REASONS = {
    "safety_wrong", "confident_wrong", "cross_question_wrong", "repairing",
    "previous_wrong_unconfirmed",
}


def parse_node_adaptive_pilot_user_ids(value: str | None) -> set[str]:
    """Reuse the established comma-separated, trimmed, deduplicated parser."""
    return parse_prerequisite_backtrack_pilot_user_ids(value)


def is_node_adaptive_recommendation_enabled(
    feature_enabled: bool, user_id: str | None, pilot_user_ids
) -> bool:
    """Fail closed unless both the flag and explicit allowlist match."""
    return is_prerequisite_backtrack_pilot_enabled(
        feature_enabled, user_id, pilot_user_ids
    )


def _attempt_time(item: dict[str, Any]):
    return item.get("answered_at") or item.get("attempted_at") or ""


def _node_attempt_summary(attempts: Iterable[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    summaries: dict[str, dict[str, Any]] = defaultdict(lambda: {
        "wrong_questions": set(), "correct_questions": set(),
        "confident_wrong": False, "uncertain_correct": False, "unknown": False,
    })
    for item in sorted((dict(value) for value in attempts), key=_attempt_time):
        node = canonicalize_knowledge_node_id(str(item.get("knowledge_node_id") or ""))
        if not node:
            continue
        question_id = str(item.get("question_id") or "")
        summary = summaries[node]
        is_unknown = item.get("answer_status") == "unknown"
        is_correct = False if is_unknown else item.get("is_correct") is True
        if is_correct:
            summary["correct_questions"].add(question_id)
            if item.get("confidence") in {2, 3}:
                summary["uncertain_correct"] = True
        else:
            summary["wrong_questions"].add(question_id)
            summary["unknown"] = summary["unknown"] or is_unknown
            summary["confident_wrong"] = (
                summary["confident_wrong"] or item.get("confidence") == 1
            )
    return summaries


def _priority(state: str, summary: dict[str, Any], safety: str) -> tuple[int, str, str]:
    has_wrong = bool(summary["wrong_questions"])
    if has_wrong and safety in {"critical", "high", "moderate"}:
        return 1000, "safety_wrong", "repair"
    if summary["confident_wrong"]:
        return 950, "confident_wrong", "repair"
    if len(summary["wrong_questions"]) >= 2:
        return 900, "cross_question_wrong", "repair"
    if state == "repairing" or summary["unknown"]:
        return 850, "repairing", "repair"
    if has_wrong:
        return 800, "previous_wrong_unconfirmed", "repair"
    if state == "recheck_due":
        return 700, "recheck_due", "checking"
    if summary["uncertain_correct"]:
        return 600, "uncertain_correct", "checking"
    if state == "checking":
        return 500, "checking", "checking"
    if state == "unseen":
        return 300, "unseen", "exploration"
    return 100, "stable_maintenance", "maintenance"


def select_node_adaptive_questions(
    attempts: Iterable[dict[str, Any]],
    question_count: int = 30,
    *,
    exclude_ids=(),
    rng=None,
    as_of: datetime | None = None,
) -> list[dict[str, Any]]:
    """Return unique recommendation records with balanced repair/exploration."""
    attempts = [dict(item) for item in attempts]
    user_ids = {str(item.get("user_id") or "") for item in attempts}
    if len(user_ids) > 1:
        raise ValueError("attempts must belong to one user")
    randomizer = rng or random.Random()
    as_of = as_of or datetime.now(timezone.utc)
    states = {
        item["canonical_node_id"]: item["state"]
        for item in derive_all_user_node_states(attempts, as_of=as_of)
    }
    summaries = _node_attempt_summary(attempts)
    seen_question_ids = {str(item.get("question_id") or "") for item in attempts}
    excluded = {str(value) for value in (exclude_ids or ())}
    candidates = []
    for question_id in question_ids():
        if question_id in excluded:
            continue
        tag = get_question_tag(question_id)
        node = canonicalize_knowledge_node_id(tag["knowledge_node_id"])
        state = states.get(node, "unseen")
        summary = summaries.get(node, {
            "wrong_questions": set(), "correct_questions": set(),
            "confident_wrong": False, "uncertain_correct": False, "unknown": False,
        })
        score, reason, group = _priority(state, summary, str(tag.get("safety", "none")))
        is_same_q_repeat = question_id in summary["wrong_questions"]
        if is_same_q_repeat:
            score -= 180
        elif summary["wrong_questions"]:
            score += 80  # Prefer another Q in the same canonical repair target.
        if question_id not in seen_question_ids:
            score += 10
        candidates.append({
            "question_id": question_id,
            "canonical_node_id": node,
            "state": state,
            "priority_reason": reason,
            "priority_group": group,
            "priority_score": score,
            "previous_wrong_count": len(summary["wrong_questions"]),
            "previous_correct_count": len(summary["correct_questions"]),
            "same_question_repeat": is_same_q_repeat,
            "safety": str(tag.get("safety", "none")),
            "confident_wrong": summary["confident_wrong"],
            "unknown_evidence": summary["unknown"],
            "tie": randomizer.random(),
        })
    candidates.sort(key=lambda item: (item["priority_score"], item["tie"]), reverse=True)

    # Soft composition targets: repair half, checking about a third, exploration remainder.
    targets = {
        "repair": (question_count + 1) // 2,
        "checking": question_count // 3,
        "exploration": max(1, question_count - ((question_count + 1) // 2) - (question_count // 3)),
    }
    selected: list[dict[str, Any]] = []
    selected_ids: set[str] = set()
    node_counts: Counter[str] = Counter()

    def take(group: str, limit: int, node_cap: int = 2):
        for item in candidates:
            if len([value for value in selected if value["priority_group"] == group]) >= limit:
                break
            if item["priority_group"] != group or item["question_id"] in selected_ids:
                continue
            if node_counts[item["canonical_node_id"]] >= node_cap:
                continue
            selected.append(item)
            selected_ids.add(item["question_id"])
            node_counts[item["canonical_node_id"]] += 1

    for group, limit in targets.items():
        take(group, limit)
    # Maintenance and any unused groups fill natural shortages; keep 2/Node where possible.
    for cap in (2, 3, question_count):
        for item in candidates:
            if len(selected) >= question_count:
                break
            if item["question_id"] in selected_ids or node_counts[item["canonical_node_id"]] >= cap:
                continue
            selected.append(item)
            selected_ids.add(item["question_id"])
            node_counts[item["canonical_node_id"]] += 1
        if len(selected) >= question_count:
            break
    return selected[:question_count]


def build_node_adaptive_session(attempts, question_count=30, exclude_ids=(), rng=None):
    records = select_node_adaptive_questions(
        attempts, question_count, exclude_ids=exclude_ids, rng=rng
    )
    if len(records) < question_count:
        raise ValueError("Not enough questions for Node adaptive session")
    return [get_quiz_question(item["question_id"]) for item in records]
