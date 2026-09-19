"""Read-only audit of formal alternate-question supply for retention reviews.

The retention policy requires a STRONG different-question check to move a due
Node to ``stable``.  This module inspects current formal Node states against the
existing Question Bank repairability registry so missing retention supply can be
seen *before* a natural review becomes due.

When attempt history is supplied, the audit also mirrors the selector's current
30-attempt Recent Question Cooldown window so it can distinguish STRONG supply
that is immediately non-recent from STRONG supply that is currently cooldown-
constrained.  This remains diagnostic only; it does not decide exact Q selection.

It never changes Node state, selection, cooldown, Question Bank data, or learner-
facing recommendations.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Iterable

from knowledge_node_repair_evidence import (
    DIFFERENT_QUESTION_STRONG,
    DIFFERENT_QUESTION_WEAK,
    classify_repair_confirmation,
)
from knowledge_node_repairability import build_repairability_audit


STRONG_AVAILABLE = "strong_available"
WEAK_ONLY = "weak_only"
NO_ALTERNATE = "no_formal_alternate"
RECENT_WINDOW = 30


def _as_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        parsed = value
    elif value:
        try:
            parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except (TypeError, ValueError):
            parsed = datetime.min.replace(tzinfo=timezone.utc)
    else:
        parsed = datetime.min.replace(tzinfo=timezone.utc)
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _attempt_sort_key(item: dict[str, Any]) -> tuple:
    return (
        _as_datetime(item.get("answered_at") or item.get("attempted_at")),
        str(item.get("event_key") or ""),
        int(item.get("attempt_position") or 0),
        int(item.get("id") or 0),
    )


def build_retention_supply_audit(
    node_states: Iterable[dict[str, Any]],
    *,
    attempts: Iterable[dict[str, Any]] | None = None,
    repairability_records: Iterable[dict[str, Any]] | None = None,
    recent_window: int = RECENT_WINDOW,
) -> dict[str, Any]:
    """Classify retention-question supply for repaired/recheck_due/stable Nodes."""
    registry = {
        str(item.get("canonical_node_id") or ""): dict(item)
        for item in (
            repairability_records
            if repairability_records is not None
            else build_repairability_audit()
        )
    }

    cooldown_known = attempts is not None
    recent_question_ids: set[str] = set()
    if attempts is not None:
        ordered_attempts = sorted(
            (dict(item) for item in attempts), key=_attempt_sort_key, reverse=True
        )[: max(0, int(recent_window))]
        recent_question_ids = {
            str(item.get("question_id") or "")
            for item in ordered_attempts
            if item.get("question_id")
        }

    details: list[dict[str, Any]] = []
    for raw in node_states or ():
        state = str(raw.get("state") or "")
        if state not in {"repaired", "recheck_due", "stable"}:
            continue
        reference_q = str(raw.get("retention_reference_question_id") or "")
        if not reference_q:
            continue
        node_id = str(raw.get("canonical_node_id") or "")
        static = registry.get(node_id, {})
        question_ids = [str(value) for value in static.get("question_ids", []) if value]

        strong: list[str] = []
        weak: list[str] = []
        for candidate in question_ids:
            if candidate == reference_q:
                continue
            quality = classify_repair_confirmation(reference_q, candidate)
            if quality == DIFFERENT_QUESTION_STRONG:
                strong.append(candidate)
            elif quality == DIFFERENT_QUESTION_WEAK:
                weak.append(candidate)

        strong = sorted(strong)
        weak = sorted(weak)
        non_recent_strong = (
            [qid for qid in strong if qid not in recent_question_ids]
            if cooldown_known
            else []
        )
        recent_strong = (
            [qid for qid in strong if qid in recent_question_ids]
            if cooldown_known
            else []
        )

        if strong:
            classification = STRONG_AVAILABLE
        elif weak:
            classification = WEAK_ONLY
        else:
            classification = NO_ALTERNATE

        details.append({
            "canonical_node_id": node_id,
            "state": state,
            "retention_reference_question_id": reference_q,
            "next_review_at": raw.get("next_review_at"),
            "classification": classification,
            "strong_candidate_question_ids": strong,
            "weak_candidate_question_ids": weak,
            "strong_candidate_count": len(strong),
            "weak_candidate_count": len(weak),
            "cooldown_known": cooldown_known,
            "non_recent_strong_candidate_question_ids": non_recent_strong,
            "recent_strong_candidate_question_ids": recent_strong,
            "non_recent_strong_candidate_count": (
                len(non_recent_strong) if cooldown_known else None
            ),
            "recent_strong_candidate_count": (
                len(recent_strong) if cooldown_known else None
            ),
            "strong_supply_currently_cooldown_constrained": bool(
                cooldown_known and strong and not non_recent_strong
            ),
        })

    due = [item for item in details if item["state"] == "recheck_due"]
    upcoming = [item for item in details if item["state"] == "repaired"]
    stable = [item for item in details if item["state"] == "stable"]

    def count(items: list[dict[str, Any]], classification: str) -> int:
        return sum(item["classification"] == classification for item in items)

    due_non_recent_strong = sum(
        bool(item.get("non_recent_strong_candidate_count")) for item in due
    ) if cooldown_known else None
    upcoming_non_recent_strong = sum(
        bool(item.get("non_recent_strong_candidate_count")) for item in upcoming
    ) if cooldown_known else None
    cooldown_constrained = sum(
        item["strong_supply_currently_cooldown_constrained"] for item in details
    ) if cooldown_known else None

    return {
        "retention_node_count": len(details),
        "due_node_count": len(due),
        "upcoming_repaired_node_count": len(upcoming),
        "stable_node_count": len(stable),
        "strong_available_count": count(details, STRONG_AVAILABLE),
        "weak_only_count": count(details, WEAK_ONLY),
        "no_formal_alternate_count": count(details, NO_ALTERNATE),
        "due_strong_available_count": count(due, STRONG_AVAILABLE),
        "due_without_strong_count": len(due) - count(due, STRONG_AVAILABLE),
        "upcoming_without_strong_count": len(upcoming) - count(upcoming, STRONG_AVAILABLE),
        "all_due_have_strong_supply": bool(due) and all(
            item["classification"] == STRONG_AVAILABLE for item in due
        ),
        "cooldown_known": cooldown_known,
        "recent_window": max(0, int(recent_window)),
        "recent_question_count": len(recent_question_ids) if cooldown_known else None,
        "cooldown_constrained_strong_node_count": cooldown_constrained,
        "due_non_recent_strong_available_count": due_non_recent_strong,
        "due_without_non_recent_strong_count": (
            len(due) - int(due_non_recent_strong or 0) if cooldown_known else None
        ),
        "upcoming_non_recent_strong_available_count": upcoming_non_recent_strong,
        "upcoming_without_non_recent_strong_count": (
            len(upcoming) - int(upcoming_non_recent_strong or 0)
            if cooldown_known else None
        ),
        "details": details,
        "diagnostic_only": True,
        "policy_note": (
            "STRONG supply and current cooldown eligibility are preflight diagnostics only. "
            "Exact-Q selection remains owned by Phase10; Safety and the selector's controlled "
            "cooldown fallback remain authoritative."
        ),
    }


def build_retention_supply_evidence_line(audit: dict[str, Any] | None) -> str:
    source = audit or {}
    return "retention_supply=" + ",".join([
        f"nodes:{int(source.get('retention_node_count') or 0)}",
        f"due:{int(source.get('due_node_count') or 0)}",
        f"due_strong:{int(source.get('due_strong_available_count') or 0)}",
        f"due_without_strong:{int(source.get('due_without_strong_count') or 0)}",
        f"upcoming:{int(source.get('upcoming_repaired_node_count') or 0)}",
        f"upcoming_without_strong:{int(source.get('upcoming_without_strong_count') or 0)}",
        f"cooldown_known:{1 if source.get('cooldown_known') else 0}",
        f"due_nonrecent_strong:{int(source.get('due_non_recent_strong_available_count') or 0)}",
        f"due_without_nonrecent_strong:{int(source.get('due_without_non_recent_strong_count') or 0)}",
        f"upcoming_without_nonrecent_strong:{int(source.get('upcoming_without_non_recent_strong_count') or 0)}",
        f"cooldown_constrained:{int(source.get('cooldown_constrained_strong_node_count') or 0)}",
        f"weak_only:{int(source.get('weak_only_count') or 0)}",
        f"no_alt:{int(source.get('no_formal_alternate_count') or 0)}",
    ])
