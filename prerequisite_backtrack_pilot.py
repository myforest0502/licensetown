"""Small, feature-flagged integration helpers for PREREQUISITE backtracking."""

from __future__ import annotations

from typing import Any, Callable, Iterable

from prerequisite_backtrack import select_prerequisite_backtrack_candidate
from prerequisite_diagnosis import (
    attempt_order_key,
    derive_prerequisite_diagnosis,
    is_formal_prerequisite_relation,
)


def parse_prerequisite_backtrack_pilot_user_ids(value: str | None) -> set[str]:
    """Parse a comma-separated allowlist without retaining empty entries."""
    return {
        item.strip()
        for item in str(value or "").split(",")
        if item.strip()
    }


def is_prerequisite_backtrack_pilot_enabled(
    feature_enabled: bool,
    user_id: str | None,
    pilot_user_ids: Iterable[str],
) -> bool:
    """Fail closed unless both the feature and explicit user allowlist match."""
    return bool(feature_enabled and user_id and user_id in set(pilot_user_ids))


def build_pending_backtrack_candidate(
    current_attempts: Iterable[dict[str, Any]],
    all_attempts: Iterable[dict[str, Any]],
    relations: Iterable[dict[str, Any]],
    excluded_question_ids: Iterable[str] = (),
) -> dict[str, Any] | None:
    """Return at most one safe depth-1 source candidate for the next set."""
    excluded = {str(item) for item in excluded_question_ids}
    ordered = sorted((dict(item) for item in all_attempts), key=attempt_order_key)
    formal = sorted(
        (dict(item) for item in relations if is_formal_prerequisite_relation(item)),
        key=lambda item: item["relation_id"],
    )
    by_target: dict[str, list[dict[str, Any]]] = {}
    for relation in formal:
        by_target.setdefault(relation["target_node_id"], []).append(relation)

    for target in sorted((dict(item) for item in current_attempts), key=attempt_order_key):
        if target.get("is_correct") is not False:
            continue
        for relation in by_target.get(target.get("knowledge_node_id"), ()):
            prior = [
                item for item in ordered
                if item.get("user_id") == target.get("user_id")
                and attempt_order_key(item) < attempt_order_key(target)
            ]
            diagnosis = derive_prerequisite_diagnosis(target, prior, relation)
            selection = select_prerequisite_backtrack_candidate(diagnosis, relation, prior)
            candidate_id = selection.get("candidate_question_id")
            if (
                not selection.get("backtrack")
                or not candidate_id
                or candidate_id == target.get("question_id")
                or candidate_id in excluded
            ):
                continue
            return {
                "question_id": candidate_id,
                "selection_reason": "prerequisite_backtrack",
                "relation_id": relation["relation_id"],
                "source_node_id": relation["source_node_id"],
                "target_node_id": relation["target_node_id"],
                "trigger_target_question_id": target.get("question_id"),
                "source_status": diagnosis["source_status"],
                "candidate_reason": selection["candidate_reason"],
                "depth": 1,
            }
    return None


def inject_pending_backtrack_candidate(
    all_questions: Iterable[dict[str, Any]],
    candidate: dict[str, Any] | None,
    next_start_index: int,
    questions_per_set: int,
    question_loader: Callable[[str], dict[str, Any]],
) -> tuple[list[dict[str, Any]], bool]:
    """Put one candidate at the next-set head while preserving length and uniqueness."""
    questions = [dict(item) for item in all_questions]
    if not candidate or candidate.get("depth") != 1:
        return questions, False
    if next_start_index < 0 or next_start_index >= len(questions) or questions_per_set < 1:
        return questions, False

    candidate_id = str(candidate.get("question_id") or "")
    if not candidate_id:
        return questions, False
    previous_ids = {str(item.get("id")) for item in questions[:next_start_index]}
    if candidate_id in previous_ids:
        return questions, False

    next_end = min(len(questions), next_start_index + questions_per_set)
    next_ids = [str(item.get("id")) for item in questions[next_start_index:next_end]]
    if candidate_id in next_ids:
        candidate_index = next_start_index + next_ids.index(candidate_id)
        questions[next_start_index], questions[candidate_index] = (
            questions[candidate_index], questions[next_start_index]
        )
        return questions, True

    later_index = next(
        (
            index for index in range(next_end, len(questions))
            if str(questions[index].get("id")) == candidate_id
        ),
        None,
    )
    displaced = questions[next_start_index]
    questions[next_start_index] = question_loader(candidate_id)
    if later_index is not None:
        questions[later_index] = displaced
    return questions, True
