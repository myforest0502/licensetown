"""Pure Knowledge Node state transitions; no persistence or selection effects."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any, Iterable

from knowledge_node_canonical import canonicalize_knowledge_node_id
from knowledge_node_weakness_evidence import derive_repeated_weakness_evidence
from knowledge_node_repair_evidence import (
    DIFFERENT_QUESTION_STRONG,
    classify_repair_confirmation,
)


STATES = ("unseen", "checking", "repairing", "repaired", "stable", "recheck_due")
REPAIRED_RECHECK_AFTER = timedelta(days=7)
STABLE_RECHECK_AFTER = timedelta(days=30)


def _sort_key(attempt: dict[str, Any]) -> tuple[str, str, int, int]:
    return (
        str(attempt.get("attempted_at") or attempt.get("answered_at") or ""),
        str(attempt.get("event_key") or ""),
        int(attempt.get("attempt_position") or 0),
        int(attempt.get("id") or 0),
    )


def is_recheck_due(state: str, last_attempted_at: datetime, as_of: datetime) -> bool:
    interval = REPAIRED_RECHECK_AFTER if state == "repaired" else STABLE_RECHECK_AFTER
    return state in {"repaired", "stable"} and as_of - last_attempted_at >= interval


def _as_datetime(value) -> datetime | None:
    if isinstance(value, str):
        value = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if not isinstance(value, datetime):
        return None
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


def _evidence(history: list[dict[str, Any]]) -> dict[str, Any]:
    records = derive_repeated_weakness_evidence(history)
    if len(records) != 1:
        raise ValueError("history must contain exactly one user and canonical Node")
    return records[0]


def _result(
    canonical_node_id: str,
    state: str,
    reason: str,
    history: list[dict[str, Any]],
    confident_correct_after_wrong_count: int,
    retention_reference_question_id: str | None = None,
) -> dict[str, Any]:
    if not history:
        return {
            "canonical_node_id": canonical_node_id,
            "state": "unseen",
            "reason": "No attempt has been recorded for this canonical Node.",
            "distinct_question_count": 0,
            "wrong_question_count": 0,
            "confident_correct_after_wrong_count": 0,
            "evidence_level": "NO_WRONG_EVIDENCE",
            "retention_reference_question_id": None,
        }
    evidence = _evidence(history)
    return {
        "canonical_node_id": canonical_node_id,
        "state": state,
        "reason": reason,
        "distinct_question_count": evidence["distinct_question_count"],
        "wrong_question_count": evidence["wrong_question_count"],
        "confident_correct_after_wrong_count": confident_correct_after_wrong_count,
        "evidence_level": evidence["evidence_level"],
        "retention_reference_question_id": retention_reference_question_id,
    }


def derive_knowledge_node_state(
    attempts: Iterable[dict[str, Any]],
    canonical_node_id: str | None = None,
    as_of: datetime | None = None,
) -> dict[str, Any]:
    """Derive the final state for one user's one canonical Node history."""
    ordered = sorted((dict(item) for item in attempts), key=_sort_key)
    if not ordered:
        return _result(str(canonical_node_id or ""), "unseen", "", [], 0)

    canonical_ids = {
        canonicalize_knowledge_node_id(str(item.get("knowledge_node_id") or ""))
        for item in ordered
    }
    user_ids = {str(item.get("user_id") or "") for item in ordered}
    if len(canonical_ids) != 1 or len(user_ids) != 1:
        raise ValueError("attempts must belong to one user and one canonical Node")
    canonical = canonical_ids.pop()

    state = "unseen"
    reason = ""
    repair_wrong_questions: set[str] = set()
    confident_correct_after_wrong_count = 0
    has_prior_wrong = False
    next_review_at: datetime | None = None
    retention_reference_question: str | None = None
    history: list[dict[str, Any]] = []

    for item in ordered:
        attempted_at = _as_datetime(item.get("attempted_at") or item.get("answered_at"))
        if state in {"repaired", "stable"} and next_review_at and attempted_at and attempted_at >= next_review_at:
            state = "recheck_due"
            reason = "The spaced retention review date has arrived."
        history.append(item)
        question_id = str(item.get("question_id") or "")
        is_correct = (
            False if item.get("answer_status") == "unknown"
            else item.get("is_correct")
        )
        confidence = item.get("confidence")

        if is_correct is False:
            previous_state = state
            state = "repairing"
            reason = "A wrong answer requires repair, regardless of the previous state."
            if not has_prior_wrong or previous_state in {"repaired", "stable", "recheck_due"}:
                repair_wrong_questions = {question_id}
            else:
                repair_wrong_questions.add(question_id)
            has_prior_wrong = True
            next_review_at = None
            retention_reference_question = None
            continue

        if is_correct is not True:
            continue
        if state == "unseen":
            state = "checking"
            reason = "The first recorded attempt is correct; more evidence is required."
            continue
        if not has_prior_wrong:
            state = "checking"
            reason = "Correct answers without prior repair evidence remain checking."
            continue

        evidence_strengths = {
            classify_repair_confirmation(wrong_question, question_id)
            for wrong_question in repair_wrong_questions
        }
        is_strong_confirmation = DIFFERENT_QUESTION_STRONG in evidence_strengths
        if state == "recheck_due":
            retention_strength = classify_repair_confirmation(retention_reference_question, question_id)
            if confidence == 1 and retention_strength == DIFFERENT_QUESTION_STRONG:
                state = "stable"
                retention_reference_question = question_id
                next_review_at = attempted_at + STABLE_RECHECK_AFTER if attempted_at else None
                reason = "A spaced strong different-question check was correct with confidence=1."
            else:
                reason = "Retention evidence was same/weak or lacked confidence=1; review remains due."
            continue
        if confidence == 1 and is_strong_confirmation:
            confident_correct_after_wrong_count += 1
            if state == "repairing":
                state = "repaired"
                retention_reference_question = question_id
                next_review_at = attempted_at + REPAIRED_RECHECK_AFTER if attempted_at else None
                reason = "A strong different-question confirmation was correct with confidence=1 after a wrong answer."
            elif state == "repaired":
                reason = "Short-term repair remains repaired; stable requires the future time-based policy."
        elif state == "repairing":
            reason = (
                "The correct answer is same/weakly different or lacks confidence=1; repair remains unconfirmed."
            )

    result = _result(
        canonical,
        state,
        reason,
        history,
        confident_correct_after_wrong_count,
        retention_reference_question,
    )
    as_of = _as_datetime(as_of)
    if state in {"repaired", "stable"} and next_review_at and as_of and as_of >= next_review_at:
        result["state"] = "recheck_due"
        result["reason"] = "The spaced retention review date has arrived."
    result["next_review_at"] = next_review_at
    result["due_overdue_days"] = max(0, (as_of - next_review_at).days) if as_of and next_review_at and as_of >= next_review_at else 0
    return result


def derive_all_user_node_states(
    attempts: Iterable[dict[str, Any]], as_of: datetime | None = None
) -> list[dict[str, Any]]:
    """Group by user and canonical Node without returning user identifiers."""
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for source in attempts:
        item = dict(source)
        canonical = canonicalize_knowledge_node_id(str(item.get("knowledge_node_id") or ""))
        grouped[(str(item.get("user_id") or ""), canonical)].append(item)
    return [
        derive_knowledge_node_state(history, canonical, as_of=as_of)
        for (_user, canonical), history in sorted(grouped.items())
    ]


def derive_state_timeline(attempts: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return prefix-only states to make future-leakage tests explicit."""
    ordered = sorted((dict(item) for item in attempts), key=_sort_key)
    return [derive_knowledge_node_state(ordered[: index + 1]) for index in range(len(ordered))]
