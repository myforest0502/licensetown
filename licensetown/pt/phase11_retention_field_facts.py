"""Pure Phase11 J4 retention attribution from formal reference questions."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable, Mapping


def build_retention_field_facts(
    node_states: Iterable[Mapping[str, Any]],
    *,
    field_by_question: Mapping[str, int],
) -> dict[str, Any]:
    """Attribute recheck_due Nodes to the field of their retention reference Q.

    Missing/unmapped reference questions are surfaced as unattributed instead of
    being copied across static canonical-Node memberships.
    """
    by_field: dict[int, dict[str, Any]] = defaultdict(lambda: {
        "recheck_due_node_count": 0,
        "max_overdue_days": 0,
        "total_overdue_days": 0,
        "canonical_node_ids": [],
        "retention_reference_question_ids": [],
    })
    unattributed: list[dict[str, Any]] = []

    for source in node_states:
        if source.get("state") != "recheck_due":
            continue
        node_id = str(source.get("canonical_node_id") or "")
        reference_q = str(source.get("retention_reference_question_id") or "")
        overdue = max(0, int(source.get("due_overdue_days") or 0))
        field_id = field_by_question.get(reference_q)
        if field_id is None:
            unattributed.append({
                "canonical_node_id": node_id,
                "retention_reference_question_id": reference_q or None,
                "due_overdue_days": overdue,
                "reason": "missing_or_unmapped_retention_reference_question",
            })
            continue
        field_id = int(field_id)
        item = by_field[field_id]
        item["recheck_due_node_count"] += 1
        item["max_overdue_days"] = max(item["max_overdue_days"], overdue)
        item["total_overdue_days"] += overdue
        item["canonical_node_ids"].append(node_id)
        item["retention_reference_question_ids"].append(reference_q)

    normalized: dict[int, dict[str, Any]] = {}
    for field_id, source in sorted(by_field.items()):
        item = dict(source)
        item["canonical_node_ids"] = sorted(item["canonical_node_ids"])
        item["retention_reference_question_ids"] = sorted(
            item["retention_reference_question_ids"]
        )
        normalized[field_id] = item

    return {
        "by_field": normalized,
        "unattributed": sorted(
            unattributed,
            key=lambda item: (
                -item["due_overdue_days"],
                item["canonical_node_id"],
            ),
        ),
    }


def build_j4_candidates(retention_facts: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Return J4 fields in the existing Phase11 retention tie-break order."""
    candidates = []
    for field_id, source in retention_facts.get("by_field", {}).items():
        count = int(source.get("recheck_due_node_count") or 0)
        if count <= 0:
            continue
        candidates.append({
            "field_id": int(field_id),
            "recheck_due_node_count": count,
            "max_overdue_days": int(source.get("max_overdue_days") or 0),
            "total_overdue_days": int(source.get("total_overdue_days") or 0),
        })
    return sorted(
        candidates,
        key=lambda item: (
            -item["recheck_due_node_count"],
            -item["max_overdue_days"],
            -item["total_overdue_days"],
            item["field_id"],
        ),
    )
