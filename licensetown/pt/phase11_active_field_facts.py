"""Pure Phase11 J1-J3 field facts from active current-cycle weakness."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Mapping

from knowledge_node_weakness_evidence import (
    CROSS_QUESTION_CONFIDENT_WRONG,
    CROSS_QUESTION_WRONG,
    REPEATED_SAME_QUESTION_WRONG,
)


REPEATED_LEVELS = {
    REPEATED_SAME_QUESTION_WRONG,
    CROSS_QUESTION_WRONG,
    CROSS_QUESTION_CONFIDENT_WRONG,
}


def build_active_field_facts(
    active_by_node: Mapping[str, Mapping[str, Any]],
    *,
    field_by_question: Mapping[str, int],
    critical_nodes: set[str] | frozenset[str] = frozenset(),
) -> dict[int, dict[str, Any]]:
    """Attribute active J1-J3 evidence only to fields of active wrong Qs.

    Generic canonical-Node field memberships are deliberately not used here.
    If one active repair cycle contains wrong Qs from two fields, both observed
    source fields receive that Node's cross-question evidence.
    """
    facts: dict[int, dict[str, Any]] = defaultdict(lambda: {
        "critical_safety_unresolved_count": 0,
        "active_cross_question_confident_wrong_node_count": 0,
        "active_cross_question_wrong_node_count": 0,
        "active_repeated_weakness_node_count": 0,
        "active_confident_wrong_repairing_node_count": 0,
        "active_evaluable_wrong_repairing_node_count": 0,
        "active_node_ids": set(),
        "active_wrong_question_ids": set(),
    })

    for node_id, source in active_by_node.items():
        wrong_qs = {
            str(q)
            for q in source.get("active_evaluable_wrong_question_ids", [])
            if str(q) in field_by_question
        }
        if not wrong_qs:
            continue
        source_fields = {int(field_by_question[q]) for q in wrong_qs}
        confident_qs = {
            str(q)
            for q in source.get("active_confident_wrong_question_ids", [])
            if str(q) in field_by_question
        }
        confident_fields = {int(field_by_question[q]) for q in confident_qs}
        level = source.get("active_weakness_evidence_level")

        for field_id in source_fields:
            item = facts[field_id]
            item["active_node_ids"].add(node_id)
            item["active_wrong_question_ids"].update(
                q for q in wrong_qs if int(field_by_question[q]) == field_id
            )
            item["active_evaluable_wrong_repairing_node_count"] += 1
            if node_id in critical_nodes:
                item["critical_safety_unresolved_count"] += 1
            if level == CROSS_QUESTION_CONFIDENT_WRONG:
                item["active_cross_question_confident_wrong_node_count"] += 1
            if level == CROSS_QUESTION_WRONG:
                item["active_cross_question_wrong_node_count"] += 1
            if level in REPEATED_LEVELS:
                item["active_repeated_weakness_node_count"] += 1

        for field_id in confident_fields:
            facts[field_id]["active_confident_wrong_repairing_node_count"] += 1

    normalized: dict[int, dict[str, Any]] = {}
    for field_id, source in sorted(facts.items()):
        item = dict(source)
        item["active_node_ids"] = sorted(item["active_node_ids"])
        item["active_wrong_question_ids"] = sorted(item["active_wrong_question_ids"])
        normalized[field_id] = item
    return normalized
