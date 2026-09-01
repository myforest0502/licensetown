"""Deterministic read-only Phase 11 shadow learning judgment.

This layer chooses learning intent and scope only. It never selects exact Q IDs,
writes to the database, calls an LLM, or mutates formal Knowledge Node state.
Phase 10 remains responsible for exact adaptive selection and cooldown.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any, Iterable
from zoneinfo import ZoneInfo

from knowledge_node_canonical import canonicalize_knowledge_node_id
from knowledge_node_weakness_evidence import (
    CROSS_QUESTION_CONFIDENT_WRONG,
    CROSS_QUESTION_WRONG,
    REPEATED_SAME_QUESTION_WRONG,
    derive_repeated_weakness_evidence,
)
from question_bank import (
    BASIC_CATEGORY_SMALLS,
    CATEGORY_NAMES,
    get_category_small,
    get_question_tag,
    question_ids,
)


TOKYO = ZoneInfo("Asia/Tokyo")
UNRESOLVED_STATES = {"checking", "repairing", "recheck_due"}
REPEATED_LEVELS = {
    REPEATED_SAME_QUESTION_WRONG,
    CROSS_QUESTION_WRONG,
    CROSS_QUESTION_CONFIDENT_WRONG,
}
REASON_LABELS = {
    "safety_repair": "Critical Safetyの未解決誤答",
    "confident_wrong_cluster": "自信あり誤答のまとまり",
    "repeated_wrong_cluster": "反復誤答のまとまり",
    "recheck_due": "再確認時期のNode",
    "insufficient_coverage": "学習範囲の不足",
    "uncertain_correct_cluster": "迷いながらの正解が多い",
    "maintenance_only": "緊急の弱点がなく広く維持学習",
}
CONFIDENCE_RATIONALES = {
    "high": "Safetyまたは複数の誤答証拠があり、優先理由が明確です。",
    "medium": "決定表の条件には一致していますが、緊急修復より弱い根拠です。",
}


def _catalog() -> dict[str, Any]:
    field_by_question: dict[str, int] = {}
    node_by_question: dict[str, str] = {}
    fields_by_node: dict[str, set[int]] = defaultdict(set)
    critical_nodes: set[str] = set()
    for question_id in question_ids():
        field_id = get_category_small(question_id)
        tag = get_question_tag(question_id)
        node_id = canonicalize_knowledge_node_id(tag["knowledge_node_id"])
        field_by_question[question_id] = field_id
        node_by_question[question_id] = node_id
        fields_by_node[node_id].add(field_id)
        if tag.get("safety") == "critical":
            critical_nodes.add(node_id)
    return {
        "field_by_question": field_by_question,
        "node_by_question": node_by_question,
        "fields_by_node": fields_by_node,
        "critical_nodes": critical_nodes,
    }


_CATALOG = _catalog()


def _normalize_question_id(value: Any) -> str:
    text = str(value or "").upper().strip()
    return text if text.startswith("Q") else f"Q{text}" if text.isdigit() else text


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


def _field_map(field_evidence: dict[str, Any]) -> dict[int, dict[str, Any]]:
    return {
        int(item["field_id"]): item
        for item in field_evidence.get("fields", [])
        if item.get("field_id") is not None
    }


def _node_states(field_evidence: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(item["canonical_node_id"]): item
        for item in field_evidence.get("canonical_node_evidence", [])
        if item.get("canonical_node_id")
    }


def _make_result(
    *,
    intent: str,
    field_id: int | None,
    question_count: int,
    route: str,
    reason_code: str,
    confidence: str,
    evidence: list[str],
    observations: list[str],
) -> dict[str, Any]:
    return {
        "learning_intent": intent,
        "target_field_id": field_id,
        "target_field": CATEGORY_NAMES.get(field_id) if field_id is not None else None,
        "question_count": question_count,
        "recommended_route": route,
        "reason_code": reason_code,
        "reason_label": REASON_LABELS[reason_code],
        "confidence": confidence,
        "confidence_rationale": CONFIDENCE_RATIONALES[confidence],
        "evidence": evidence,
        "observations": observations,
        "shadow_only": True,
    }


def _current_target(current_guidance: dict[str, Any] | None) -> str | None:
    recommended = (current_guidance or {}).get("recommended_study") or []
    first = recommended[0] if recommended else None
    return str(first[0]) if isinstance(first, (list, tuple)) and first else None


def build_shadow_comparison(
    current_guidance: dict[str, Any] | None,
    shadow: dict[str, Any],
) -> dict[str, Any]:
    """Compare current and shadow targets without declaring a winner."""
    current_target = _current_target(current_guidance)
    shadow_target = shadow.get("target_field")
    current_phase = (current_guidance or {}).get("phase")
    if current_target == shadow_target and current_target is not None:
        label = (
            "same_target_same_reason"
            if shadow.get("reason_code") == "insufficient_coverage"
            and current_phase == "foundation"
            else "same_target_stronger_reason"
        )
    elif shadow.get("reason_code") in {
        "safety_repair",
        "confident_wrong_cluster",
        "repeated_wrong_cluster",
        "recheck_due",
    }:
        label = "different_target_shadow_has_stronger_evidence"
    else:
        label = "insufficient_evidence_to_judge"
    return {
        "current_target": current_target,
        "current_phase": current_phase,
        "shadow_target": shadow_target,
        "shadow_reason_code": shadow.get("reason_code"),
        "label": label,
    }


def build_shadow_judgment(
    attempts: Iterable[dict[str, Any]],
    field_evidence: dict[str, Any],
    current_guidance: dict[str, Any] | None,
    *,
    as_of: datetime | None = None,
) -> dict[str, Any]:
    """Return the first matching Phase 11 v0.1 rule in J1→J7 order."""
    attempts = [dict(item) for item in attempts]
    as_of = as_of or datetime.now(timezone.utc)
    if as_of.tzinfo is None:
        as_of = as_of.replace(tzinfo=timezone.utc)
    user_ids = {str(item.get("user_id") or "") for item in attempts}
    if len(user_ids) > 1:
        raise ValueError("attempts must belong to one user")

    fields = _field_map(field_evidence)
    states = _node_states(field_evidence)
    evaluable = [item for item in attempts if item.get("answer_status") != "unknown"]
    weakness = {
        item["canonical_node_id"]: item
        for item in derive_repeated_weakness_evidence(evaluable)
    }
    attempts_by_node: dict[str, list[dict[str, Any]]] = defaultdict(list)
    uncertain_correct_by_field: Counter[int] = Counter()
    tokyo_today = as_of.astimezone(TOKYO).date()
    today_count = 0
    for item in attempts:
        q_id = _normalize_question_id(item.get("question_id"))
        node_id = _CATALOG["node_by_question"].get(q_id)
        field_id = _CATALOG["field_by_question"].get(q_id)
        if node_id:
            attempts_by_node[node_id].append(item)
        if (
            field_id is not None
            and item.get("is_correct") is True
            and item.get("answer_status") != "unknown"
            and item.get("confidence") in {2, 3}
        ):
            uncertain_correct_by_field[field_id] += 1
        answered_at = _parse_time(item.get("answered_at") or item.get("attempted_at"))
        if answered_at and answered_at.astimezone(TOKYO).date() == tokyo_today:
            today_count += 1
    observations = ["high_same_day_volume"] if today_count >= 60 else []

    # J1: Critical Safety + unresolved state + evaluable wrong evidence.
    safety_candidates: list[tuple[Any, ...]] = []
    for node_id in sorted(_CATALOG["critical_nodes"]):
        state = states.get(node_id, {}).get("state", "unseen")
        wrong = [
            item
            for item in attempts_by_node.get(node_id, [])
            if item.get("is_correct") is False
            and item.get("answer_status") != "unknown"
        ]
        if state not in UNRESOLVED_STATES or not wrong:
            continue
        weak = weakness.get(node_id, {})
        level = weak.get("evidence_level")
        if level == CROSS_QUESTION_CONFIDENT_WRONG:
            tier = 0
        elif level == CROSS_QUESTION_WRONG:
            tier = 1
        elif any(item.get("confidence") == 1 for item in wrong):
            tier = 2
        elif level == REPEATED_SAME_QUESTION_WRONG:
            tier = 3
        else:
            tier = 4
        wrong_times = [
            parsed
            for parsed in (
                _parse_time(item.get("answered_at") or item.get("attempted_at"))
                for item in wrong
            )
            if parsed is not None
        ]
        recency_key = -max(wrong_times).timestamp() if wrong_times else 0
        for field_id in sorted(_CATALOG["fields_by_node"].get(node_id, ())):
            safety_candidates.append(
                (tier, recency_key, field_id, node_id, len(wrong), level)
            )
    if safety_candidates:
        tier, _recency, field_id, node_id, wrong_count, level = min(safety_candidates)
        return _make_result(
            intent="repair",
            field_id=field_id,
            question_count=10,
            route="dashboard_recommendation",
            reason_code="safety_repair",
            confidence="high",
            evidence=[
                f"critical_safety_node={node_id}",
                f"node_state={states[node_id]['state']}",
                f"wrong_attempts={wrong_count}",
                f"weakness_level={level or 'SINGLE_WRONG'}",
                f"safety_priority_tier={tier}",
            ],
            observations=observations,
        )

    facts: dict[int, dict[str, Any]] = {}
    for field_id, field in fields.items():
        node_ids = {
            node_id
            for node_id, member_fields in _CATALOG["fields_by_node"].items()
            if field_id in member_fields
        }
        field_weakness = [weakness[node_id] for node_id in node_ids if node_id in weakness]
        confident_repair_nodes = {
            node_id
            for node_id in node_ids
            if states.get(node_id, {}).get("state") == "repairing"
            and any(
                item.get("is_correct") is False
                and item.get("answer_status") != "unknown"
                and item.get("confidence") == 1
                for item in attempts_by_node.get(node_id, [])
            )
        }
        facts[field_id] = {
            "cross_confident": sum(
                item.get("evidence_level") == CROSS_QUESTION_CONFIDENT_WRONG
                for item in field_weakness
            ),
            "cross_wrong": sum(
                item.get("evidence_level") == CROSS_QUESTION_WRONG
                for item in field_weakness
            ),
            "repeated": sum(
                item.get("evidence_level") in REPEATED_LEVELS
                for item in field_weakness
            ),
            "confident_repair_nodes": len(confident_repair_nodes),
            "repairing": int(field.get("repairing_node_count") or 0),
            "answered": int(field.get("question_answer_count") or 0),
            "accuracy": field.get("question_accuracy"),
        }

    # J2: cross-question confident wrong, or confident wrong on >=2 repairing Nodes.
    j2 = []
    for field_id, fact in facts.items():
        if not (fact["cross_confident"] or fact["confident_repair_nodes"] >= 2):
            continue
        reliable_accuracy = (
            fact["accuracy"]
            if fact["answered"] >= 10 and fact["accuracy"] is not None
            else 1.0
        )
        j2.append(
            (
                -fact["cross_confident"],
                -fact["confident_repair_nodes"],
                -fact["repairing"],
                reliable_accuracy,
                field_id,
            )
        )
    if j2:
        *_unused, field_id = min(j2)
        fact = facts[field_id]
        return _make_result(
            intent="repair",
            field_id=field_id,
            question_count=10,
            route="dashboard_recommendation",
            reason_code="confident_wrong_cluster",
            confidence="high",
            evidence=[
                f"cross_question_confident_wrong_nodes={fact['cross_confident']}",
                f"distinct_confident_wrong_repairing_nodes={fact['confident_repair_nodes']}",
                f"repairing_nodes={fact['repairing']}",
            ],
            observations=observations,
        )

    # J3: a cross-question wrong Node, or >=2 repeated-weakness Nodes.
    j3 = []
    for field_id, fact in facts.items():
        if fact["cross_wrong"] or fact["repeated"] >= 2:
            j3.append(
                (-fact["cross_wrong"], -fact["repeated"], -fact["repairing"], field_id)
            )
    if j3:
        *_unused, field_id = min(j3)
        fact = facts[field_id]
        return _make_result(
            intent="repair",
            field_id=field_id,
            question_count=10,
            route="dashboard_recommendation",
            reason_code="repeated_wrong_cluster",
            confidence="high",
            evidence=[
                f"cross_question_wrong_nodes={fact['cross_wrong']}",
                f"repeated_weakness_nodes={fact['repeated']}",
                f"repairing_nodes={fact['repairing']}",
            ],
            observations=observations,
        )

    # J4: due retention work; tie by count, max overdue, total overdue, field ID.
    j4 = []
    for field_id, field in fields.items():
        due = [
            item
            for item in field.get("retention_nodes", [])
            if item.get("state") == "recheck_due"
        ]
        if not due:
            continue
        overdue = [int(item.get("due_overdue_days") or 0) for item in due]
        j4.append((-len(due), -max(overdue, default=0), -sum(overdue), field_id))
    if j4:
        *_unused, field_id = min(j4)
        due = [
            item
            for item in fields[field_id].get("retention_nodes", [])
            if item.get("state") == "recheck_due"
        ]
        overdue = [int(item.get("due_overdue_days") or 0) for item in due]
        return _make_result(
            intent="recheck",
            field_id=field_id,
            question_count=10,
            route="dashboard_recommendation",
            reason_code="recheck_due",
            confidence="medium",
            evidence=[
                f"recheck_due_nodes={len(due)}",
                f"max_overdue_days={max(overdue, default=0)}",
                f"total_overdue_days={sum(overdue)}",
            ],
            observations=observations,
        )

    # J5: under 100 answers preserve the existing deterministic foundation target.
    total_answers = len(attempts)
    if total_answers < 100:
        target_name = _current_target(current_guidance)
        target_id = next(
            (fid for fid, name in CATEGORY_NAMES.items() if name == target_name),
            None,
        )
        if target_id is None:
            basics = [fid for fid in BASIC_CATEGORY_SMALLS if fid in fields]
            target_id = min(
                basics,
                key=lambda fid: (
                    int(fields[fid].get("question_answer_count") or 0) > 0,
                    int(fields[fid].get("question_answer_count") or 0),
                    fid,
                ),
                default=None,
            )
        return _make_result(
            intent="coverage",
            field_id=target_id,
            question_count=10,
            route="dashboard_recommendation",
            reason_code="insufficient_coverage",
            confidence="medium",
            evidence=[
                f"total_answers={total_answers}",
                "foundation_threshold=100",
                "target_source=current_guidance",
            ],
            observations=observations,
        )

    # After 100 answers, v0.1 uses only a conservative <10-answer coverage trigger.
    # It intentionally does not infer weakness from Question Bank size.
    sparse_fields = [
        field
        for field in fields.values()
        if int(field.get("question_answer_count") or 0) < 10
    ]
    if sparse_fields:
        chosen = min(
            sparse_fields,
            key=lambda field: (
                int(field.get("question_answer_count") or 0),
                float((field.get("node_coverage") or {}).get("percent") or 0),
                int(field["field_id"]),
            ),
        )
        return _make_result(
            intent="coverage",
            field_id=int(chosen["field_id"]),
            question_count=10,
            route="dashboard_recommendation",
            reason_code="insufficient_coverage",
            confidence="medium",
            evidence=[
                f"field_answered_count={int(chosen.get('question_answer_count') or 0)}",
                f"field_node_coverage_percent={float((chosen.get('node_coverage') or {}).get('percent') or 0)}",
                "minimum_reliable_field_answers=10",
            ],
            observations=observations,
        )

    # J6: >=3 correct answers with confidence 2/3 in a field with >=5 answers.
    j6 = []
    for field_id, count in uncertain_correct_by_field.items():
        answered = int(fields.get(field_id, {}).get("question_answer_count") or 0)
        if answered < 5 or count < 3:
            continue
        checking = int(fields[field_id].get("checking_node_count") or 0)
        j6.append((-count, -(count / answered), -checking, field_id))
    if j6:
        *_unused, field_id = min(j6)
        count = uncertain_correct_by_field[field_id]
        answered = int(fields[field_id].get("question_answer_count") or 0)
        return _make_result(
            intent="stabilization",
            field_id=field_id,
            question_count=10,
            route="dashboard_recommendation",
            reason_code="uncertain_correct_cluster",
            confidence="medium",
            evidence=[
                f"uncertain_correct_count={count}",
                f"uncertain_correct_proportion={round(count / answered, 3)}",
                f"checking_nodes={int(fields[field_id].get('checking_node_count') or 0)}",
            ],
            observations=observations,
        )

    # J7: no higher-priority evidence. Let Phase 10 choose a broad 30-question set.
    return _make_result(
        intent="maintenance",
        field_id=None,
        question_count=30,
        route="adaptive_daily",
        reason_code="maintenance_only",
        confidence="medium",
        evidence=["no_higher_priority_rule_matched"],
        observations=observations,
    )
