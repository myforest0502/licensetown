"""Read-only per-field evidence for future mastery design.

This module deliberately does not calculate or expose an official mastery score.
Canonical Nodes that belong to multiple fields are reported in every membership;
the future allocation policy remains an explicit product decision.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime
from typing import Any, Iterable

from database import get_question_attempts
from knowledge_node_canonical import canonicalize_knowledge_node_id
from knowledge_node_state_transition import STATES, derive_all_user_node_states
from knowledge_node_weakness_evidence import (
    CROSS_QUESTION_CONFIDENT_WRONG,
    CROSS_QUESTION_WRONG,
    REPEATED_SAME_QUESTION_WRONG,
    derive_repeated_weakness_evidence,
)
from question_bank import (
    CATEGORY_NAMES,
    QuestionBankError,
    get_category_small,
    get_question_tag,
    question_ids,
)


REPEATED_WEAKNESS_LEVELS = {
    REPEATED_SAME_QUESTION_WRONG,
    CROSS_QUESTION_WRONG,
    CROSS_QUESTION_CONFIDENT_WRONG,
}
RETENTION_STATES = {"repaired", "recheck_due", "stable"}


def _catalog() -> dict[str, Any]:
    questions_by_field: dict[int, set[str]] = {
        field_id: set() for field_id in CATEGORY_NAMES
    }
    nodes_by_field: dict[int, set[str]] = {
        field_id: set() for field_id in CATEGORY_NAMES
    }
    fields_by_node: dict[str, set[int]] = defaultdict(set)
    field_by_question: dict[str, int] = {}
    node_by_question: dict[str, str] = {}

    for question_id in question_ids():
        field_id = get_category_small(question_id)
        node_id = canonicalize_knowledge_node_id(
            get_question_tag(question_id)["knowledge_node_id"]
        )
        field_by_question[question_id] = field_id
        node_by_question[question_id] = node_id
        questions_by_field[field_id].add(question_id)
        nodes_by_field[field_id].add(node_id)
        fields_by_node[node_id].add(field_id)

    multi_field_nodes = [
        {
            "canonical_node_id": node_id,
            "field_ids": sorted(field_ids),
            "field_names": [CATEGORY_NAMES[field_id] for field_id in sorted(field_ids)],
        }
        for node_id, field_ids in sorted(fields_by_node.items())
        if len(field_ids) > 1
    ]
    return {
        "field_by_question": field_by_question,
        "node_by_question": node_by_question,
        "questions_by_field": questions_by_field,
        "nodes_by_field": nodes_by_field,
        "fields_by_node": fields_by_node,
        "multi_field_nodes": multi_field_nodes,
    }


_CATALOG = _catalog()


def _percent(numerator: int, denominator: int) -> float:
    return round(numerator * 100 / denominator, 1) if denominator else 0.0


def _timestamp(value):
    return value.isoformat() if isinstance(value, datetime) else value


def build_field_evidence(
    attempts: Iterable[dict[str, Any]],
    *,
    as_of: datetime | None = None,
) -> dict[str, Any]:
    """Aggregate anonymous evidence for all 18 fields without a mastery formula."""
    attempts = [dict(item) for item in attempts]
    user_ids = {str(item.get("user_id") or "") for item in attempts}
    if len(user_ids) > 1:
        raise ValueError("attempts must belong to one user")

    states = {
        item["canonical_node_id"]: item
        for item in derive_all_user_node_states(attempts, as_of=as_of)
    }
    evaluable_attempts = [
        item for item in attempts
        if item.get("answer_status") != "unknown"
    ]
    weakness = {
        item["canonical_node_id"]: item
        for item in derive_repeated_weakness_evidence(evaluable_attempts)
    }
    attempts_by_field: dict[int, list[dict[str, Any]]] = defaultdict(list)
    answered_questions_by_field: dict[int, set[str]] = defaultdict(set)
    for item in attempts:
        question_id = str(item.get("question_id") or "").upper().strip()
        try:
            field_id = _CATALOG["field_by_question"][question_id]
        except KeyError:
            continue
        attempts_by_field[field_id].append(item)
        answered_questions_by_field[field_id].add(question_id)

    fields = []
    for field_id, field_name in CATEGORY_NAMES.items():
        field_questions = _CATALOG["questions_by_field"][field_id]
        field_nodes = _CATALOG["nodes_by_field"][field_id]
        field_attempts = attempts_by_field[field_id]
        attempted_nodes = field_nodes & set(states)
        state_counts = Counter(states[node_id]["state"] for node_id in attempted_nodes)
        state_counts["unseen"] = len(field_nodes - attempted_nodes)
        confidence_counts = Counter(
            item.get("confidence")
            for item in field_attempts
            if item.get("confidence") in {1, 2, 3}
        )
        unknown_count = sum(
            item.get("answer_status") == "unknown"
            or (not item.get("selected_answers") and item.get("confidence") is None)
            for item in field_attempts
        )
        correct_answer_count = sum(
            item.get("is_correct") is True and item.get("answer_status") != "unknown"
            for item in field_attempts
        )
        weakness_counts = Counter(
            weakness[node_id]["evidence_level"]
            for node_id in attempted_nodes
            if node_id in weakness
        )
        retention_nodes = [
            {
                "canonical_node_id": node_id,
                "state": states[node_id]["state"],
                "next_review_at": _timestamp(states[node_id].get("next_review_at")),
                "due_overdue_days": int(states[node_id].get("due_overdue_days") or 0),
            }
            for node_id in sorted(attempted_nodes)
            if states[node_id]["state"] in RETENTION_STATES
        ]
        multi_field_ids = sorted(
            node_id
            for node_id in field_nodes
            if len(_CATALOG["fields_by_node"][node_id]) > 1
        )
        answered_unique = len(answered_questions_by_field[field_id])
        attempted_node_count = len(attempted_nodes)
        repair_confirmations = sum(
            int(states[node_id].get("confident_correct_after_wrong_count") or 0)
            for node_id in attempted_nodes
        )
        fields.append({
            "field_id": field_id,
            "field_name": field_name,
            "total_question_count": len(field_questions),
            "answered_unique_question_count": answered_unique,
            "question_coverage": {
                "numerator": answered_unique,
                "denominator": len(field_questions),
                "percent": _percent(answered_unique, len(field_questions)),
                "status": "candidate_metric",
            },
            "total_canonical_node_count": len(field_nodes),
            "attempted_canonical_node_count": attempted_node_count,
            "node_coverage": {
                "numerator": attempted_node_count,
                "denominator": len(field_nodes),
                "percent": _percent(attempted_node_count, len(field_nodes)),
                "status": "candidate_metric",
            },
            "state_counts": {state: state_counts[state] for state in STATES},
            "unseen_node_count": state_counts["unseen"],
            "checking_node_count": state_counts["checking"],
            "repairing_node_count": state_counts["repairing"],
            "repaired_node_count": state_counts["repaired"],
            "recheck_due_node_count": state_counts["recheck_due"],
            "stable_node_count": state_counts["stable"],
            "retention_target_node_count": len(retention_nodes),
            "retention_nodes": retention_nodes,
            "confidence_counts": {
                "1": confidence_counts[1],
                "2": confidence_counts[2],
                "3": confidence_counts[3],
            },
            "unknown_answer_count": unknown_count,
            "question_answer_count": len(field_attempts),
            "question_correct_count": correct_answer_count,
            "question_accuracy": (
                correct_answer_count / len(field_attempts)
                if field_attempts else None
            ),
            "repeated_weakness_evidence_count": sum(
                weakness_counts[level] for level in REPEATED_WEAKNESS_LEVELS
            ),
            "repeated_weakness_evidence_levels": dict(sorted(weakness_counts.items())),
            "different_question_repair_confirmation_count": repair_confirmations,
            "multi_field_canonical_node_count": len(multi_field_ids),
            "multi_field_canonical_node_ids": multi_field_ids,
        })

    canonical_nodes = set(_CATALOG["fields_by_node"])
    canonical_node_evidence = []
    for node_id in sorted(canonical_nodes):
        state = states.get(node_id)
        canonical_node_evidence.append({
            "canonical_node_id": node_id,
            "field_ids": sorted(_CATALOG["fields_by_node"][node_id]),
            "state": state["state"] if state else "unseen",
            "next_review_at": _timestamp(state.get("next_review_at")) if state else None,
            "due_overdue_days": int(state.get("due_overdue_days") or 0) if state else 0,
        })
    return {
        "status": "evidence_only",
        "official_mastery_score": None,
        "field_count": len(fields),
        "question_total": len(_CATALOG["field_by_question"]),
        "canonical_node_total": len(canonical_nodes),
        "canonical_node_membership_total": sum(
            len(nodes) for nodes in _CATALOG["nodes_by_field"].values()
        ),
        "multi_field_node_count": len(_CATALOG["multi_field_nodes"]),
        "multi_field_nodes": _CATALOG["multi_field_nodes"],
        "canonical_node_evidence": canonical_node_evidence,
        "multi_field_membership_policy": "duplicated_in_each_member_field_for_evidence_only",
        "fields": fields,
    }


def get_user_field_evidence(
    user_id: str,
    *,
    as_of: datetime | None = None,
) -> dict[str, Any]:
    """READ ONLY adapter: question_attempts -> pure field evidence."""
    return build_field_evidence(get_question_attempts(user_id), as_of=as_of)
