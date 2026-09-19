"""Pure Phase11 J1 Safety candidates from current-cycle active weakness."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

from knowledge_node_weakness_evidence import (
    CROSS_QUESTION_CONFIDENT_WRONG,
    CROSS_QUESTION_WRONG,
    REPEATED_SAME_QUESTION_WRONG,
)


def _parse_time(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _priority_tier(source: Mapping[str, Any]) -> int:
    level = source.get("active_weakness_evidence_level")
    if level == CROSS_QUESTION_CONFIDENT_WRONG:
        return 0
    if level == CROSS_QUESTION_WRONG:
        return 1
    if source.get("active_has_confident_wrong"):
        return 2
    if level == REPEATED_SAME_QUESTION_WRONG:
        return 3
    return 4


def build_active_safety_candidates(
    active_by_node: Mapping[str, Mapping[str, Any]],
    *,
    field_by_question: Mapping[str, int],
    critical_nodes: set[str] | frozenset[str],
) -> list[dict[str, Any]]:
    """Return ordered Critical Safety J1 candidates from active wrong evidence.

    Fields are attributed only from active evaluable wrong question sources.
    Unknown-only active repair cycles do not create J1 candidates.
    """
    candidates: list[dict[str, Any]] = []
    for node_id in sorted(critical_nodes):
        source = active_by_node.get(node_id)
        if not source or int(source.get("active_evaluable_wrong_attempt_count") or 0) <= 0:
            continue
        wrong_qs = {
            str(q)
            for q in source.get("active_evaluable_wrong_question_ids", [])
            if str(q) in field_by_question
        }
        source_fields = sorted({int(field_by_question[q]) for q in wrong_qs})
        if not source_fields:
            continue
        tier = _priority_tier(source)
        parsed = _parse_time(source.get("active_last_evaluable_wrong_at"))
        recency_key = -parsed.timestamp() if parsed else 0
        for field_id in source_fields:
            candidates.append({
                "priority_tier": tier,
                "recency_key": recency_key,
                "field_id": field_id,
                "canonical_node_id": node_id,
                "active_wrong_attempt_count": int(
                    source.get("active_evaluable_wrong_attempt_count") or 0
                ),
                "active_weakness_evidence_level": source.get(
                    "active_weakness_evidence_level"
                ),
            })
    return sorted(
        candidates,
        key=lambda item: (
            item["priority_tier"],
            item["recency_key"],
            item["field_id"],
            item["canonical_node_id"],
        ),
    )
