"""Pure Phase11 J5/J6 candidate ordering using evaluable field evidence."""

from __future__ import annotations

from typing import Any, Mapping


def _evaluable_count(field: Mapping[str, Any]) -> int:
    if "evaluable_answer_count" in field:
        return int(field.get("evaluable_answer_count") or 0)
    return int(field.get("question_answer_count") or 0)


def build_j5_sparse_field_candidates(
    field_records: Mapping[int, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Return post-foundation J5 sparse fields using evaluable answers only."""
    candidates: list[dict[str, Any]] = []
    for field_id, field in field_records.items():
        evaluable_count = _evaluable_count(field)
        if evaluable_count >= 10:
            continue
        node_coverage = float((field.get("node_coverage") or {}).get("percent") or 0)
        candidates.append({
            "field_id": int(field_id),
            "evaluable_answer_count": evaluable_count,
            "node_coverage_percent": node_coverage,
            "raw_answer_count": int(field.get("question_answer_count") or 0),
            "unknown_answer_count": int(field.get("unknown_answer_count") or 0),
        })
    return sorted(
        candidates,
        key=lambda item: (
            item["evaluable_answer_count"],
            item["node_coverage_percent"],
            item["field_id"],
        ),
    )


def build_j6_uncertain_correct_candidates(
    field_records: Mapping[int, Mapping[str, Any]],
    *,
    uncertain_correct_by_field: Mapping[int, int],
) -> list[dict[str, Any]]:
    """Return J6 candidates with evaluable denominators."""
    candidates: list[dict[str, Any]] = []
    for field_id, field in field_records.items():
        evaluable_count = _evaluable_count(field)
        uncertain_correct = int(uncertain_correct_by_field.get(int(field_id), 0))
        if evaluable_count < 5 or uncertain_correct < 3:
            continue
        proportion = uncertain_correct / evaluable_count
        candidates.append({
            "field_id": int(field_id),
            "uncertain_correct_count": uncertain_correct,
            "evaluable_answer_count": evaluable_count,
            "uncertain_correct_proportion": proportion,
            "checking_node_count": int(field.get("checking_node_count") or 0),
        })
    return sorted(
        candidates,
        key=lambda item: (
            -item["uncertain_correct_count"],
            -item["uncertain_correct_proportion"],
            -item["checking_node_count"],
            item["field_id"],
        ),
    )
