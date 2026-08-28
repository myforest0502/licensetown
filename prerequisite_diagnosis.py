"""Pure, read-only PREREQUISITE diagnosis simulation helpers."""

from __future__ import annotations

from collections import Counter
from datetime import datetime
from typing import Any, Iterable


SOURCE_UNSEEN = "SOURCE_UNSEEN"
SOURCE_UNSTABLE = "SOURCE_UNSTABLE"
SOURCE_CONFIDENT_CORRECT = "SOURCE_CONFIDENT_CORRECT"
SOURCE_CONFLICT = "SOURCE_CONFLICT"
SOURCE_STATUSES = (
    SOURCE_UNSEEN,
    SOURCE_UNSTABLE,
    SOURCE_CONFIDENT_CORRECT,
    SOURCE_CONFLICT,
)

REASONS = {
    SOURCE_UNSEEN: "source Node has no attempt before the target error",
    SOURCE_UNSTABLE: "latest source evidence is weak, guessed, or incorrect",
    SOURCE_CONFIDENT_CORRECT: "latest source evidence is a confidence-1 correct answer",
    SOURCE_CONFLICT: "latest source evidence is a confidence-1 incorrect answer",
}


def _timestamp_key(value: Any) -> str:
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value or "")


def attempt_order_key(attempt: dict[str, Any]) -> tuple[str, str, int, int]:
    """Match the persisted deterministic order without consulting future rows."""
    return (
        _timestamp_key(attempt.get("answered_at")),
        str(attempt.get("event_key") or ""),
        int(attempt.get("attempt_position") or 0),
        int(attempt.get("id") or 0),
    )


def is_formal_prerequisite_relation(relation: dict[str, Any]) -> bool:
    return (
        relation.get("relation_type") == "PREREQUISITE"
        and relation.get("confidence") == "high"
        and relation.get("review_status") in {"reviewed", "reviewed_candidate"}
    )


def derive_prerequisite_diagnosis(
    target_attempt: dict[str, Any],
    prior_attempts: Iterable[dict[str, Any]],
    relation: dict[str, Any],
) -> dict[str, Any]:
    """Classify source evidence available strictly before one target attempt."""
    if not is_formal_prerequisite_relation(relation):
        raise ValueError("relation is not a formal high-confidence PREREQUISITE")
    if target_attempt.get("knowledge_node_id") != relation.get("target_node_id"):
        raise ValueError("target attempt does not match relation target Node")

    target_key = attempt_order_key(target_attempt)
    target_user = target_attempt.get("user_id")
    source_attempts = sorted(
        (
            attempt for attempt in prior_attempts
            if attempt.get("knowledge_node_id") == relation.get("source_node_id")
            and (target_user is None or attempt.get("user_id") == target_user)
            and attempt_order_key(attempt) < target_key
        ),
        key=attempt_order_key,
    )

    if not source_attempts:
        status = SOURCE_UNSEEN
    else:
        latest = source_attempts[-1]
        confidence = latest.get("confidence")
        if latest.get("is_correct") is True and confidence == 1:
            status = SOURCE_CONFIDENT_CORRECT
        elif latest.get("is_correct") is False and confidence == 1:
            status = SOURCE_CONFLICT
        else:
            status = SOURCE_UNSTABLE

    return {
        "relation_id": relation["relation_id"],
        "source_node_id": relation["source_node_id"],
        "target_node_id": relation["target_node_id"],
        "source_question_ids": sorted({
            attempt.get("question_id") for attempt in source_attempts
            if attempt.get("question_id")
        }),
        "target_question_id": target_attempt.get("question_id"),
        "source_status": status,
        "target_confidence": target_attempt.get("confidence"),
        "recommended_backtrack": status != SOURCE_CONFIDENT_CORRECT,
        "reason": REASONS[status],
    }


def simulate_prerequisite_diagnoses(
    attempts: Iterable[dict[str, Any]],
    relations: Iterable[dict[str, Any]],
    example_limit: int = 20,
) -> dict[str, Any]:
    """Replay saved attempts without mutating attempts, relations, or Node state."""
    ordered = sorted((dict(attempt) for attempt in attempts), key=attempt_order_key)
    eligible = sorted(
        (dict(relation) for relation in relations if is_formal_prerequisite_relation(relation)),
        key=lambda relation: relation["relation_id"],
    )
    by_target: dict[str, list[dict[str, Any]]] = {}
    for relation in eligible:
        by_target.setdefault(relation["target_node_id"], []).append(relation)

    target_attempts = [a for a in ordered if a.get("knowledge_node_id") in by_target]
    target_wrong = [a for a in target_attempts if a.get("is_correct") is False]
    diagnoses: list[dict[str, Any]] = []
    relation_reports = {
        relation["relation_id"]: {
            "relation_id": relation["relation_id"],
            "source_node_id": relation["source_node_id"],
            "target_node_id": relation["target_node_id"],
            "target_attempt_count": 0,
            "target_wrong_count": 0,
            **{status: 0 for status in SOURCE_STATUSES},
            "recommended_backtrack_true": 0,
            "recommended_backtrack_false": 0,
        }
        for relation in eligible
    }

    for target in target_attempts:
        for relation in by_target[target["knowledge_node_id"]]:
            relation_reports[relation["relation_id"]]["target_attempt_count"] += 1

    for target in target_wrong:
        for relation in by_target[target["knowledge_node_id"]]:
            diagnosis = derive_prerequisite_diagnosis(target, ordered, relation)
            diagnoses.append(diagnosis)
            item = relation_reports[relation["relation_id"]]
            item["target_wrong_count"] += 1
            item[diagnosis["source_status"]] += 1
            key = (
                "recommended_backtrack_true"
                if diagnosis["recommended_backtrack"]
                else "recommended_backtrack_false"
            )
            item[key] += 1

    status_counts = Counter(item["source_status"] for item in diagnoses)
    backtrack_counts = Counter(item["recommended_backtrack"] for item in diagnoses)
    return {
        "total_attempts": len(ordered),
        "prerequisite_relation_count": len(eligible),
        "target_node_attempts": len(target_attempts),
        "target_wrong_attempts": len(target_wrong),
        "prerequisite_evaluable_target_wrong_attempts": len(diagnoses),
        **{status: status_counts[status] for status in SOURCE_STATUSES},
        "recommended_backtrack_true": backtrack_counts[True],
        "recommended_backtrack_false": backtrack_counts[False],
        "relations": list(relation_reports.values()),
        "examples": diagnoses[:max(0, example_limit)],
    }
