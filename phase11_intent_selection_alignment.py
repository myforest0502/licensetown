"""Read-only Phase11 intent vs Phase10 exact-Q alignment audit.

This audit does not change either policy.  It inspects persisted adaptive_daily
selection metadata together with formal attempt history and asks whether exact-Q
execution was directionally compatible with the Phase11-relevant intent encoded
in the saved selector reason.

The first supported hard check is J4/recheck_due: when a persisted adaptive row
was selected for ``recheck_due`` and the formal Node was still due immediately
before that answer, the chosen Q should be STRONG different-question evidence
against the retention reference.  Weak/same-Q choices remain visible as J5
alignment defects/candidates; they are never silently reinterpreted as valid J4.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any, Iterable

from knowledge_node_canonical import canonicalize_knowledge_node_id
from knowledge_node_repair_evidence import (
    DIFFERENT_QUESTION_STRONG,
    DIFFERENT_QUESTION_WEAK,
    SAME_QUESTION,
    classify_repair_confirmation,
)
from knowledge_node_state_transition import derive_knowledge_node_state


RECHECK_REASON = "recheck_due"


def _dt(value: Any) -> datetime | None:
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
        _dt(item.get("answered_at") or item.get("attempted_at"))
        or datetime.min.replace(tzinfo=timezone.utc),
        str(item.get("event_key") or ""),
        int(item.get("attempt_position") or 0),
        int(item.get("id") or 0),
    )


def _event_results(events: Iterable[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    import json

    lookup: dict[tuple[str, str], dict[str, Any]] = {}
    for event in events or ():
        event_key = str(event.get("event_key") or "")
        rows = event.get("question_results")
        if isinstance(rows, str):
            try:
                rows = json.loads(rows)
            except (TypeError, ValueError):
                rows = []
        if not isinstance(rows, list):
            continue
        for row in rows:
            if not isinstance(row, dict) or not row.get("question_id"):
                continue
            lookup[(event_key, str(row["question_id"]))] = dict(row)
    return lookup


def build_phase11_intent_selection_alignment(
    attempts: Iterable[dict[str, Any]],
    learning_events: Iterable[dict[str, Any]],
) -> dict[str, Any]:
    """Audit saved adaptive intent against the exact Q actually answered."""
    attempts = sorted((dict(item) for item in attempts or ()), key=_sort_key)
    metadata = _event_results(learning_events)

    histories: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    details: list[dict[str, Any]] = []

    for attempt in attempts:
        user_id = str(attempt.get("user_id") or "")
        node_id = canonicalize_knowledge_node_id(
            str(attempt.get("knowledge_node_id") or "")
        )
        if not node_id:
            continue
        key = (user_id, node_id)
        prior = histories[key]
        event_key = str(attempt.get("event_key") or "")
        question_id = str(attempt.get("question_id") or "")
        saved = metadata.get((event_key, question_id))

        if saved and str(saved.get("selection_reason") or "") == RECHECK_REASON:
            attempted_at = _dt(attempt.get("answered_at") or attempt.get("attempted_at"))
            before = (
                derive_knowledge_node_state(
                    prior,
                    canonical_node_id=node_id,
                    as_of=attempted_at,
                )
                if prior and attempted_at
                else None
            )
            before_state = str((before or {}).get("state") or "")
            reference_q = str((before or {}).get("retention_reference_question_id") or "")
            if before_state == "recheck_due" and reference_q:
                quality = classify_repair_confirmation(reference_q, question_id)
                status = "aligned" if quality == DIFFERENT_QUESTION_STRONG else "misaligned"
                evaluable = True
                reason = (
                    "recheck_due selected Q is STRONG vs retention reference"
                    if status == "aligned"
                    else "recheck_due selected Q is not STRONG vs retention reference"
                )
            else:
                quality = None
                status = "not_evaluable"
                evaluable = False
                reason = (
                    "saved recheck_due intent could not be revalidated at answer time; "
                    "state may have changed inside the already-generated set"
                )
            details.append({
                "canonical_node_id": node_id,
                "question_id": question_id,
                "event_key": event_key,
                "selection_reason": RECHECK_REASON,
                "selection_group": saved.get("selection_group"),
                "saved_repair_evidence_quality": saved.get("repair_evidence_quality"),
                "recent_question_repeat": saved.get("recent_question_repeat") is True,
                "recent_cooldown_bypassed": saved.get("recent_cooldown_bypassed") is True,
                "formal_state_before_answer": before_state or None,
                "retention_reference_question_id": reference_q or None,
                "retention_evidence_quality": quality,
                "evaluable": evaluable,
                "status": status,
                "reason": reason,
            })

        prior.append(attempt)

    counts = Counter(item["status"] for item in details)
    evaluable = [item for item in details if item["evaluable"]]
    quality_counts = Counter(item["retention_evidence_quality"] for item in evaluable)
    return {
        "saved_recheck_selection_count": len(details),
        "evaluable_recheck_selection_count": len(evaluable),
        "aligned_recheck_selection_count": counts["aligned"],
        "misaligned_recheck_selection_count": counts["misaligned"],
        "not_evaluable_recheck_selection_count": counts["not_evaluable"],
        "strong_retention_q_count": quality_counts[DIFFERENT_QUESTION_STRONG],
        "weak_retention_q_count": quality_counts[DIFFERENT_QUESTION_WEAK],
        "same_question_retention_q_count": quality_counts[SAME_QUESTION],
        "recent_repeat_recheck_count": sum(item["recent_question_repeat"] for item in details),
        "cooldown_bypass_recheck_count": sum(item["recent_cooldown_bypassed"] for item in details),
        "alignment_status": (
            "blocked"
            if counts["misaligned"]
            else "pass"
            if evaluable
            else "open"
        ),
        "details": details,
        "diagnostic_only": True,
        "policy_note": (
            "This audit detects J5 compatibility evidence only. It does not change the "
            "Phase10 selector or authorize Phase11 learner-facing promotion."
        ),
    }


def build_intent_selection_alignment_evidence_line(audit: dict[str, Any] | None) -> str:
    source = audit or {}
    return "intent_selection_alignment=" + ",".join([
        f"status:{source.get('alignment_status') or 'open'}",
        f"saved_recheck:{int(source.get('saved_recheck_selection_count') or 0)}",
        f"evaluable:{int(source.get('evaluable_recheck_selection_count') or 0)}",
        f"aligned:{int(source.get('aligned_recheck_selection_count') or 0)}",
        f"misaligned:{int(source.get('misaligned_recheck_selection_count') or 0)}",
        f"not_evaluable:{int(source.get('not_evaluable_recheck_selection_count') or 0)}",
        f"strong:{int(source.get('strong_retention_q_count') or 0)}",
        f"weak:{int(source.get('weak_retention_q_count') or 0)}",
        f"same_q:{int(source.get('same_question_retention_q_count') or 0)}",
        f"recent_repeat:{int(source.get('recent_repeat_recheck_count') or 0)}",
        f"cooldown_bypass:{int(source.get('cooldown_bypass_recheck_count') or 0)}",
    ])
