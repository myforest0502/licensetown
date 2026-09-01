"""Deterministic, read-only Phase 11 shadow judgment.

This module chooses learning intent/scope only. It does not mutate learner state,
select exact questions, call an LLM, or perform database writes.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime
from typing import Any, Iterable

from knowledge_node_canonical import canonicalize_knowledge_node_id
from knowledge_node_state_transition import derive_all_user_node_states
from knowledge_node_weakness_evidence import (
    CROSS_QUESTION_CONFIDENT_WRONG,
    CROSS_QUESTION_WRONG,
    REPEATED_SAME_QUESTION_WRONG,
    derive_repeated_weakness_evidence,
)
from question_bank import CATEGORY_NAMES, get_category_small, get_question_tag, question_ids


SHADOW_ONLY = True


def _catalog() -> tuple[dict[str, set[int]], dict[str, int]]:
    fields_by_node: dict[str, set[int]] = defaultdict(set)
    field_by_question: dict[str, int] = {}
    for question_id in question_ids():
        field_id = get_category_small(question_id)
        node_id = canonicalize_knowledge_node_id(
            get_question_tag(question_id)["knowledge_node_id"]
        )
        fields_by_node[node_id].add(field_id)
        field_by_question[question_id] = field_id
    return dict(fields_by_node), field_by_question


def _result(
    intent: str,
    reason_code: str,
    confidence: str,
    *,
    field_id: int | None,
    question_count: int,
    evidence: list[str],
    route: str | None = None,
) -> dict[str, Any]:
    if route is None:
        route = "adaptive_daily" if field_id is None else "dashboard_recommendation"
    return {
        "learning_intent": intent,
        "target_field_id": field_id,
        "target_field": CATEGORY_NAMES.get(field_id) if field_id is not None else None,
        "question_count": question_count,
        "recommended_route": route,
        "reason_code": reason_code,
        "confidence": confidence,
        "evidence": evidence,
        "shadow_only": SHADOW_ONLY,
    }


def _legacy_target(current_guidance: dict[str, Any]) -> tuple[str | None, int]:
    study = current_guidance.get("recommended_study") or []
    if not study:
        return None, 10
    name, count = study[0]
    return str(name), int(count)


def _field_id_from_name(name: str | None) -> int | None:
    if not name:
        return None
    for field_id, field_name in CATEGORY_NAMES.items():
        if field_name == name:
            return field_id
    return None


def build_shadow_judgment(
    attempts: Iterable[dict[str, Any]],
    field_evidence: dict[str, Any],
    current_guidance: dict[str, Any],
    *,
    as_of: datetime | None = None,
) -> dict[str, Any]:
    """Return one conservative Phase 11 recommendation for shadow comparison."""
    attempts = [dict(item) for item in attempts]
    fields = list(field_evidence.get("fields") or [])
    fields_by_id = {int(item["field_id"]): item for item in fields}
    fields_by_node, field_by_question = _catalog()
    states = {
        item["canonical_node_id"]: item
        for item in derive_all_user_node_states(attempts, as_of=as_of)
    }
    weakness = derive_repeated_weakness_evidence(attempts)

    # J1: unresolved critical-Safety wrong evidence.
    safety_candidates: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for item in attempts:
        if item.get("is_correct") is not False:
            continue
        question_id = str(item.get("question_id") or "")
        if not question_id or question_id not in field_by_question:
            continue
        tag = get_question_tag(question_id)
        if str(tag.get("safety", "none")) != "critical":
            continue
        node_id = canonicalize_knowledge_node_id(
            str(item.get("knowledge_node_id") or tag.get("knowledge_node_id") or "")
        )
        if states.get(node_id, {}).get("state") != "repairing":
            continue
        safety_candidates[field_by_question[question_id]].append(item)
    if safety_candidates:
        def safety_key(field_id: int):
            rows = safety_candidates[field_id]
            confident = sum(row.get("confidence") == 1 for row in rows)
            distinct = len({str(row.get("question_id")) for row in rows})
            return (-int(distinct >= 2 and confident > 0), -distinct, -confident, field_id)

        field_id = min(safety_candidates, key=safety_key)
        rows = safety_candidates[field_id]
        return _result(
            "repair", "safety_repair", "high",
            field_id=field_id, question_count=10,
            evidence=[
                f"critical_safety_wrong_attempts={len(rows)}",
                f"critical_safety_wrong_questions={len({str(row.get('question_id')) for row in rows})}",
            ],
        )

    # Map only currently unresolved formal weakness to member fields. Historical
    # weakness that has already reached repaired/stable/recheck_due must not keep
    # commandeering the daily recommendation forever.
    weakness_by_field: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for item in weakness:
        node_id = item["canonical_node_id"]
        if states.get(node_id, {}).get("state") != "repairing":
            continue
        for field_id in fields_by_node.get(node_id, set()):
            weakness_by_field[field_id].append(item)

    # J2: cross-question confident wrong, or >=2 confident-wrong repairing Nodes.
    cross_confident_counts = Counter()
    for field_id, rows in weakness_by_field.items():
        cross_confident_counts[field_id] = sum(
            row["evidence_level"] == CROSS_QUESTION_CONFIDENT_WRONG for row in rows
        )
    confident_repair_nodes: dict[int, set[str]] = defaultdict(set)
    for item in attempts:
        if item.get("is_correct") is not False or item.get("confidence") != 1:
            continue
        question_id = str(item.get("question_id") or "")
        if question_id not in field_by_question:
            continue
        tag = get_question_tag(question_id)
        node_id = canonicalize_knowledge_node_id(
            str(item.get("knowledge_node_id") or tag.get("knowledge_node_id") or "")
        )
        if states.get(node_id, {}).get("state") == "repairing":
            for field_id in fields_by_node.get(node_id, {field_by_question[question_id]}):
                confident_repair_nodes[field_id].add(node_id)
    j2_fields = {
        field_id for field_id in CATEGORY_NAMES
        if cross_confident_counts[field_id] > 0 or len(confident_repair_nodes[field_id]) >= 2
    }
    if j2_fields:
        def j2_key(field_id: int):
            field = fields_by_id.get(field_id, {})
            accuracy = field.get("question_accuracy")
            return (
                -cross_confident_counts[field_id],
                -len(confident_repair_nodes[field_id]),
                -int(field.get("repairing_node_count") or 0),
                accuracy if accuracy is not None else 1.0,
                field_id,
            )

        field_id = min(j2_fields, key=j2_key)
        return _result(
            "repair", "confident_wrong_cluster", "high",
            field_id=field_id, question_count=10,
            evidence=[
                f"cross_question_confident_wrong_nodes={cross_confident_counts[field_id]}",
                f"confident_wrong_repairing_nodes={len(confident_repair_nodes[field_id])}",
                f"repairing_nodes={int(fields_by_id.get(field_id, {}).get('repairing_node_count') or 0)}",
            ],
        )

    # J3: cross-question wrong or multiple repeated weakness Nodes in one field.
    repeated_levels = {
        REPEATED_SAME_QUESTION_WRONG,
        CROSS_QUESTION_WRONG,
        CROSS_QUESTION_CONFIDENT_WRONG,
    }
    j3_metrics: dict[int, tuple[int, int]] = {}
    for field_id, rows in weakness_by_field.items():
        cross_count = sum(row["evidence_level"] == CROSS_QUESTION_WRONG for row in rows)
        repeated_count = sum(row["evidence_level"] in repeated_levels for row in rows)
        if cross_count > 0 or repeated_count >= 2:
            j3_metrics[field_id] = (cross_count, repeated_count)
    if j3_metrics:
        def j3_key(field_id: int):
            cross_count, repeated_count = j3_metrics[field_id]
            return (
                -cross_count,
                -repeated_count,
                -int(fields_by_id.get(field_id, {}).get("repairing_node_count") or 0),
                field_id,
            )

        field_id = min(j3_metrics, key=j3_key)
        cross_count, repeated_count = j3_metrics[field_id]
        confidence = "high" if cross_count > 0 and repeated_count >= 2 else "medium"
        return _result(
            "repair", "repeated_wrong_cluster", confidence,
            field_id=field_id, question_count=10,
            evidence=[
                f"cross_question_wrong_nodes={cross_count}",
                f"repeated_weakness_nodes={repeated_count}",
            ],
        )

    # J4: retention recheck due.
    due_fields = {
        int(field["field_id"]): [
            node for node in field.get("retention_nodes", [])
            if node.get("state") == "recheck_due"
        ]
        for field in fields
    }
    due_fields = {field_id: nodes for field_id, nodes in due_fields.items() if nodes}
    if due_fields:
        def due_key(field_id: int):
            overdue = [int(node.get("due_overdue_days") or 0) for node in due_fields[field_id]]
            return (-len(overdue), -max(overdue, default=0), -sum(overdue), field_id)

        field_id = min(due_fields, key=due_key)
        overdue = [int(node.get("due_overdue_days") or 0) for node in due_fields[field_id]]
        return _result(
            "recheck", "recheck_due", "medium",
            field_id=field_id, question_count=10,
            evidence=[
                f"recheck_due_nodes={len(overdue)}",
                f"max_overdue_days={max(overdue, default=0)}",
                f"total_overdue_days={sum(overdue)}",
            ],
        )

    total_answers = len(attempts)

    # J5a: early foundation preserves the current production target exactly.
    if total_answers < 100:
        target_name, count = _legacy_target(current_guidance)
        field_id = _field_id_from_name(target_name)
        return _result(
            "coverage", "insufficient_coverage", "low",
            field_id=field_id, question_count=count,
            evidence=[f"total_answers={total_answers}", "foundation_threshold=100"],
        )

    # J5b: conservative post-foundation sparse-field coverage.
    sparse = [field for field in fields if int(field.get("question_answer_count") or 0) < 10]
    if sparse:
        field = min(
            sparse,
            key=lambda item: (
                int(item.get("question_answer_count") or 0),
                float(item.get("node_coverage", {}).get("percent") or 0),
                int(item["field_id"]),
            ),
        )
        field_id = int(field["field_id"])
        return _result(
            "coverage", "insufficient_coverage", "low",
            field_id=field_id, question_count=10,
            evidence=[
                f"field_answer_count={int(field.get('question_answer_count') or 0)}",
                f"node_coverage_percent={float(field.get('node_coverage', {}).get('percent') or 0)}",
            ],
        )

    # J6: uncertain-correct stabilization.
    uncertain_correct_by_field = Counter()
    for item in attempts:
        if (
            item.get("is_correct") is True
            and item.get("answer_status") != "unknown"
            and item.get("confidence") in {2, 3}
        ):
            question_id = str(item.get("question_id") or "")
            if question_id in field_by_question:
                uncertain_correct_by_field[field_by_question[question_id]] += 1
    j6_fields = [
        field_id for field_id, count in uncertain_correct_by_field.items()
        if count >= 3 and int(fields_by_id.get(field_id, {}).get("question_answer_count") or 0) >= 5
    ]
    if j6_fields:
        def j6_key(field_id: int):
            answers = int(fields_by_id[field_id].get("question_answer_count") or 0)
            count = uncertain_correct_by_field[field_id]
            proportion = count / answers if answers else 0
            return (-count, -proportion, -int(fields_by_id[field_id].get("checking_node_count") or 0), field_id)

        field_id = min(j6_fields, key=j6_key)
        answers = int(fields_by_id[field_id].get("question_answer_count") or 0)
        count = uncertain_correct_by_field[field_id]
        return _result(
            "stabilization", "uncertain_correct_cluster", "medium",
            field_id=field_id, question_count=10,
            evidence=[
                f"uncertain_correct_count={count}",
                f"field_answer_count={answers}",
            ],
        )

    # J7: broad maintenance.
    return _result(
        "maintenance", "maintenance_only", "low",
        field_id=None, question_count=30,
        evidence=[f"total_answers={total_answers}", "no_higher_priority_signal=true"],
    )


def compare_current_and_shadow(
    current_guidance: dict[str, Any], shadow: dict[str, Any]
) -> dict[str, Any]:
    """Describe current-vs-shadow target agreement without quality scoring."""
    current_name, current_count = _legacy_target(current_guidance)
    shadow_name = shadow.get("target_field")
    same_target = current_name == shadow_name
    if same_target:
        label = (
            "same_target_same_reason"
            if (
                shadow.get("reason_code") == "insufficient_coverage"
                and current_guidance.get("phase") == "foundation"
            )
            else "same_target_stronger_reason"
        )
    elif shadow.get("confidence") in {"high", "medium"}:
        label = "different_target_shadow_has_stronger_evidence"
    elif current_name:
        label = "different_target_current_has_stronger_evidence"
    else:
        label = "insufficient_evidence_to_judge"
    return {
        "current": {
            "target_field": current_name,
            "question_count": current_count,
            "phase": current_guidance.get("phase"),
        },
        "shadow": shadow,
        "comparison_label": label,
    }
