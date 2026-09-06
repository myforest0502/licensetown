"""Read-only audit of naturally occurring spaced-retention review attempts.

The core state machine can move ``repaired -> recheck_due -> stable`` while
processing one attempt.  A prefix-only state timeline therefore may not expose
``recheck_due`` as an adjacent persisted state.  This audit asks the formal state
machine for the state immediately *before* each real attempt at that attempt's
timestamp, then processes the attempt and records the outcome.

No timestamps, attempts, Node states, selectors, or learner-facing decisions are
mutated here.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any, Iterable
from zoneinfo import ZoneInfo

from knowledge_node_canonical import canonicalize_knowledge_node_id
from knowledge_node_repair_evidence import classify_repair_confirmation
from knowledge_node_state_transition import derive_knowledge_node_state


TOKYO = ZoneInfo("Asia/Tokyo")


def _as_datetime(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        parsed = value
    elif value:
        try:
            parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except (TypeError, ValueError):
            return None
    else:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _sort_key(item: dict[str, Any]) -> tuple:
    return (
        _as_datetime(item.get("attempted_at") or item.get("answered_at"))
        or datetime.min.replace(tzinfo=timezone.utc),
        str(item.get("event_key") or ""),
        int(item.get("attempt_position") or 0),
        int(item.get("id") or 0),
    )


def build_retention_outcome_audit(
    attempts: Iterable[dict[str, Any]],
) -> dict[str, Any]:
    """Find real attempts that occurred after a formal retention review became due."""
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for source in attempts or ():
        item = dict(source)
        node_id = canonicalize_knowledge_node_id(
            str(item.get("knowledge_node_id") or "")
        )
        if not node_id:
            continue
        grouped[(str(item.get("user_id") or ""), node_id)].append(item)

    reviews: list[dict[str, Any]] = []
    for (_user_id, node_id), raw_history in sorted(grouped.items()):
        history = sorted(raw_history, key=_sort_key)
        prior: list[dict[str, Any]] = []
        for attempt in history:
            attempted_at = _as_datetime(
                attempt.get("attempted_at") or attempt.get("answered_at")
            )
            if not attempted_at:
                prior.append(attempt)
                continue
            if not prior:
                prior.append(attempt)
                continue

            before = derive_knowledge_node_state(
                prior,
                canonical_node_id=node_id,
                as_of=attempted_at,
            )
            if before.get("state") != "recheck_due":
                prior.append(attempt)
                continue

            reference_q = str(before.get("retention_reference_question_id") or "")
            question_id = str(attempt.get("question_id") or "")
            evidence_quality = classify_repair_confirmation(reference_q, question_id)
            after = derive_knowledge_node_state(
                prior + [attempt],
                canonical_node_id=node_id,
                as_of=attempted_at,
            )
            after_state = str(after.get("state") or "")
            outcome = {
                "stable": "stable",
                "repairing": "repairing",
                "recheck_due": "still_due",
            }.get(after_state, after_state or "unknown")
            due_at = _as_datetime(before.get("next_review_at"))
            reviews.append({
                "canonical_node_id": node_id,
                "question_id": question_id,
                "retention_reference_question_id": reference_q or None,
                "review_attempted_at_jst": attempted_at.astimezone(TOKYO).isoformat(),
                "due_at_jst": due_at.astimezone(TOKYO).isoformat() if due_at else None,
                "hours_after_due": (
                    round((attempted_at - due_at).total_seconds() / 3600.0, 1)
                    if due_at else None
                ),
                "outcome": outcome,
                "post_state": after_state,
                "evidence_quality": evidence_quality,
                "confidence": attempt.get("confidence"),
                "is_correct": attempt.get("is_correct") is True,
                "answer_status": str(attempt.get("answer_status") or "answered"),
            })
            prior.append(attempt)

    outcome_counts = Counter(item["outcome"] for item in reviews)
    evidence_counts = Counter(item["evidence_quality"] for item in reviews)
    return {
        "review_attempt_count": len(reviews),
        "stable_count": outcome_counts["stable"],
        "repairing_count": outcome_counts["repairing"],
        "still_due_count": outcome_counts["still_due"],
        "other_outcome_count": len(reviews)
        - outcome_counts["stable"]
        - outcome_counts["repairing"]
        - outcome_counts["still_due"],
        "strong_evidence_count": evidence_counts["different_question_strong"],
        "weak_evidence_count": evidence_counts["different_question_weak"],
        "same_question_count": evidence_counts["same_question"],
        "confident_correct_count": sum(
            item["is_correct"] and item.get("confidence") == 1 for item in reviews
        ),
        "reviews": reviews,
        "diagnostic_only": True,
        "policy_note": (
            "These are naturally occurring formal retention-review attempts. "
            "The audit does not create due states or authorize Phase11 promotion."
        ),
    }


def build_retention_outcome_evidence_line(audit: dict[str, Any] | None) -> str:
    """Serialize aggregate, non-identifying retention outcome evidence."""
    source = audit or {}
    return "retention_outcomes=" + ",".join([
        f"reviews:{int(source.get('review_attempt_count') or 0)}",
        f"stable:{int(source.get('stable_count') or 0)}",
        f"repairing:{int(source.get('repairing_count') or 0)}",
        f"still_due:{int(source.get('still_due_count') or 0)}",
        f"other:{int(source.get('other_outcome_count') or 0)}",
        f"strong:{int(source.get('strong_evidence_count') or 0)}",
        f"weak:{int(source.get('weak_evidence_count') or 0)}",
        f"same_q:{int(source.get('same_question_count') or 0)}",
        f"confident_correct:{int(source.get('confident_correct_count') or 0)}",
    ])
