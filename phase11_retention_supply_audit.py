"""Read-only audit of formal alternate-question supply for retention reviews.

The retention policy requires a STRONG different-question check to move a due
Node to ``stable``.  This module inspects current formal Node states against the
existing Question Bank repairability registry so missing retention supply can be
seen *before* a natural review becomes due.

It never changes Node state, selection, cooldown, Question Bank data, or learner-
facing recommendations.
"""

from __future__ import annotations

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


def build_retention_supply_audit(
    node_states: Iterable[dict[str, Any]],
    *,
    repairability_records: Iterable[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Classify retention-question supply for repaired/recheck_due Nodes."""
    registry = {
        str(item.get("canonical_node_id") or ""): dict(item)
        for item in (
            repairability_records
            if repairability_records is not None
            else build_repairability_audit()
        )
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
            "strong_candidate_question_ids": sorted(strong),
            "weak_candidate_question_ids": sorted(weak),
            "strong_candidate_count": len(strong),
            "weak_candidate_count": len(weak),
        })

    due = [item for item in details if item["state"] == "recheck_due"]
    upcoming = [item for item in details if item["state"] == "repaired"]
    stable = [item for item in details if item["state"] == "stable"]

    def count(items: list[dict[str, Any]], classification: str) -> int:
        return sum(item["classification"] == classification for item in items)

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
        "details": details,
        "diagnostic_only": True,
        "policy_note": (
            "STRONG supply availability is a preflight diagnostic only. Exact-Q selection "
            "remains owned by Phase10 and still must obey Safety and Recent Cooldown."
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
        f"weak_only:{int(source.get('weak_only_count') or 0)}",
        f"no_alt:{int(source.get('no_formal_alternate_count') or 0)}",
    ])
