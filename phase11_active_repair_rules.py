"""Pure Phase11 J2/J3 candidate ordering from active current-cycle facts."""

from __future__ import annotations

from typing import Any, Mapping


def _field_record(field_records: Mapping[int, Mapping[str, Any]], field_id: int) -> Mapping[str, Any]:
    return field_records.get(field_id, {})


def build_j2_candidates(
    active_field_facts: Mapping[int, Mapping[str, Any]],
    *,
    field_records: Mapping[int, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Return J2 candidates using confirmed active weakness only."""
    candidates: list[dict[str, Any]] = []
    for field_id, active in active_field_facts.items():
        cross_confident = int(
            active.get("active_cross_question_confident_wrong_node_count") or 0
        )
        confident_nodes = int(
            active.get("active_confident_wrong_repairing_node_count") or 0
        )
        if not (cross_confident or confident_nodes >= 2):
            continue
        active_repairing = int(
            active.get("active_evaluable_wrong_repairing_node_count") or 0
        )
        field = _field_record(field_records, int(field_id))
        evaluable_count = int(field.get("evaluable_answer_count") or 0)
        evaluable_accuracy = field.get("evaluable_accuracy")
        reliable_accuracy = (
            float(evaluable_accuracy)
            if evaluable_count >= 10 and evaluable_accuracy is not None
            else 1.0
        )
        candidates.append({
            "field_id": int(field_id),
            "active_cross_question_confident_wrong_node_count": cross_confident,
            "active_confident_wrong_repairing_node_count": confident_nodes,
            "active_evaluable_wrong_repairing_node_count": active_repairing,
            "evaluable_answer_count": evaluable_count,
            "evaluable_accuracy": evaluable_accuracy,
            "reliable_accuracy": reliable_accuracy,
        })
    return sorted(
        candidates,
        key=lambda item: (
            -item["active_cross_question_confident_wrong_node_count"],
            -item["active_confident_wrong_repairing_node_count"],
            -item["active_evaluable_wrong_repairing_node_count"],
            item["reliable_accuracy"],
            item["field_id"],
        ),
    )


def build_j3_candidates(
    active_field_facts: Mapping[int, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Return J3 candidates using confirmed active weakness only."""
    candidates: list[dict[str, Any]] = []
    for field_id, active in active_field_facts.items():
        cross_wrong = int(active.get("active_cross_question_wrong_node_count") or 0)
        repeated = int(active.get("active_repeated_weakness_node_count") or 0)
        if not (cross_wrong or repeated >= 2):
            continue
        active_repairing = int(
            active.get("active_evaluable_wrong_repairing_node_count") or 0
        )
        candidates.append({
            "field_id": int(field_id),
            "active_cross_question_wrong_node_count": cross_wrong,
            "active_repeated_weakness_node_count": repeated,
            "active_evaluable_wrong_repairing_node_count": active_repairing,
        })
    return sorted(
        candidates,
        key=lambda item: (
            -item["active_cross_question_wrong_node_count"],
            -item["active_repeated_weakness_node_count"],
            -item["active_evaluable_wrong_repairing_node_count"],
            item["field_id"],
        ),
    )
