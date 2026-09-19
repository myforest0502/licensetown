"""Deterministic Phase11 formal policy assembled from current-cycle evidence helpers.

This module is read-only. It does not select exact Q IDs, write to the database,
call an LLM, or mutate formal Knowledge Node state. It is intentionally kept
separate from the current `judgment_shadow.py` until executable regression tests
are available; final integration can then delegate to this module with a small
surface-area change.
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from typing import Any, Iterable
from zoneinfo import ZoneInfo

from field_evidence import build_field_evidence
from knowledge_node_canonical import canonicalize_knowledge_node_id
from knowledge_node_state_transition import derive_all_user_node_states
from phase11_active_field_facts import build_active_field_facts
from phase11_active_repair_rules import build_j2_candidates, build_j3_candidates
from phase11_active_safety import build_active_safety_candidates
from phase11_active_weakness import build_active_repair_weakness
from phase11_evaluable_nonrepair_rules import (
    build_j5_sparse_field_candidates,
    build_j6_uncertain_correct_candidates,
)
from phase11_retention_field_facts import (
    build_j4_candidates,
    build_retention_field_facts,
)
from question_bank import (
    BASIC_CATEGORY_SMALLS,
    CATEGORY_NAMES,
    get_category_small,
    get_question_tag,
    question_ids,
)


TOKYO = ZoneInfo("Asia/Tokyo")
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
REASON_RANKS = {
    "safety_repair": 1,
    "confident_wrong_cluster": 2,
    "repeated_wrong_cluster": 3,
    "recheck_due": 4,
    "insufficient_coverage": 5,
    "uncertain_correct_cluster": 6,
    "maintenance_only": 7,
}


def _catalog() -> dict[str, Any]:
    field_by_question: dict[str, int] = {}
    critical_nodes: set[str] = set()
    for question_id in question_ids():
        field_by_question[question_id] = get_category_small(question_id)
        tag = get_question_tag(question_id)
        if tag.get("safety") == "critical":
            critical_nodes.add(
                canonicalize_knowledge_node_id(str(tag["knowledge_node_id"]))
            )
    return {
        "field_by_question": field_by_question,
        "critical_nodes": critical_nodes,
    }


_CATALOG = _catalog()


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


def _current_target(current_guidance: dict[str, Any] | None) -> str | None:
    recommended = (current_guidance or {}).get("recommended_study") or []
    first = recommended[0] if recommended else None
    return str(first[0]) if isinstance(first, (list, tuple)) and first else None


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


def _uncertain_correct_by_field(attempts: Iterable[dict[str, Any]]) -> Counter[int]:
    result: Counter[int] = Counter()
    field_by_question = _CATALOG["field_by_question"]
    for item in attempts:
        question_id = str(item.get("question_id") or "").upper().strip()
        field_id = field_by_question.get(question_id)
        if (
            field_id is not None
            and item.get("is_correct") is True
            and item.get("answer_status") != "unknown"
            and item.get("confidence") in {2, 3}
        ):
            result[field_id] += 1
    return result


def _same_day_observations(
    attempts: Iterable[dict[str, Any]],
    *,
    as_of: datetime,
) -> list[str]:
    today = as_of.astimezone(TOKYO).date()
    count = 0
    for item in attempts:
        answered_at = _parse_time(item.get("answered_at") or item.get("attempted_at"))
        if answered_at and answered_at.astimezone(TOKYO).date() == today:
            count += 1
    return ["high_same_day_volume"] if count >= 60 else []


def build_formal_context(
    attempts: Iterable[dict[str, Any]],
    field_evidence: dict[str, Any] | None = None,
    *,
    as_of: datetime | None = None,
) -> dict[str, Any]:
    """Build one shared evidence context for judgment and symmetric profiles."""
    attempts = [dict(item) for item in attempts]
    user_ids = {str(item.get("user_id") or "") for item in attempts}
    if len(user_ids) > 1:
        raise ValueError("attempts must belong to one user")
    as_of = as_of or datetime.now(timezone.utc)
    if as_of.tzinfo is None:
        as_of = as_of.replace(tzinfo=timezone.utc)

    evidence = field_evidence or build_field_evidence(attempts, as_of=as_of)
    fields = _field_map(evidence)
    active_by_node = build_active_repair_weakness(attempts, as_of=as_of)
    active_fields = build_active_field_facts(
        active_by_node,
        field_by_question=_CATALOG["field_by_question"],
        critical_nodes=_CATALOG["critical_nodes"],
    )
    node_states = derive_all_user_node_states(attempts, as_of=as_of)
    retention = build_retention_field_facts(
        node_states,
        field_by_question=_CATALOG["field_by_question"],
    )
    uncertain = _uncertain_correct_by_field(attempts)
    return {
        "attempts": attempts,
        "as_of": as_of,
        "field_evidence": evidence,
        "fields": fields,
        "active_by_node": active_by_node,
        "active_field_facts": active_fields,
        "node_states": node_states,
        "retention_facts": retention,
        "uncertain_correct_by_field": uncertain,
        "total_answers": len(attempts),
    }


def build_formal_shadow_judgment(
    attempts: Iterable[dict[str, Any]],
    field_evidence: dict[str, Any],
    current_guidance: dict[str, Any] | None,
    *,
    as_of: datetime | None = None,
) -> dict[str, Any]:
    """Return the first matching formal Phase11 v0.1 rule in J1→J7 order."""
    context = build_formal_context(attempts, field_evidence, as_of=as_of)
    attempts = context["attempts"]
    as_of = context["as_of"]
    fields = context["fields"]
    active_by_node = context["active_by_node"]
    active_fields = context["active_field_facts"]
    retention = context["retention_facts"]
    uncertain = context["uncertain_correct_by_field"]
    total_answers = context["total_answers"]
    observations = _same_day_observations(attempts, as_of=as_of)
    if retention.get("unattributed"):
        observations.append(
            f"unattributed_recheck_due={len(retention['unattributed'])}"
        )

    # J1: current-cycle Critical Safety evaluable wrong evidence only.
    safety = build_active_safety_candidates(
        active_by_node,
        field_by_question=_CATALOG["field_by_question"],
        critical_nodes=_CATALOG["critical_nodes"],
    )
    if safety:
        chosen = safety[0]
        return _make_result(
            intent="repair",
            field_id=chosen["field_id"],
            question_count=10,
            route="dashboard_recommendation",
            reason_code="safety_repair",
            confidence="high",
            evidence=[
                f"critical_safety_node={chosen['canonical_node_id']}",
                "node_state=repairing",
                f"active_wrong_attempts={chosen['active_wrong_attempt_count']}",
                f"active_weakness_level={chosen['active_weakness_evidence_level'] or 'SINGLE_WRONG'}",
                f"safety_priority_tier={chosen['priority_tier']}",
            ],
            observations=observations,
        )

    # J2: active cross-question confident wrong or >=2 current-cycle confident-wrong Nodes.
    j2 = build_j2_candidates(active_fields, field_records=fields)
    if j2:
        chosen = j2[0]
        return _make_result(
            intent="repair",
            field_id=chosen["field_id"],
            question_count=10,
            route="dashboard_recommendation",
            reason_code="confident_wrong_cluster",
            confidence="high",
            evidence=[
                "active_cross_question_confident_wrong_nodes="
                f"{chosen['active_cross_question_confident_wrong_node_count']}",
                "active_distinct_confident_wrong_repairing_nodes="
                f"{chosen['active_confident_wrong_repairing_node_count']}",
                "active_evaluable_wrong_repairing_nodes="
                f"{chosen['active_evaluable_wrong_repairing_node_count']}",
            ],
            observations=observations,
        )

    # J3: current-cycle cross-question wrong or >=2 repeated weakness Nodes.
    j3 = build_j3_candidates(active_fields)
    if j3:
        chosen = j3[0]
        return _make_result(
            intent="repair",
            field_id=chosen["field_id"],
            question_count=10,
            route="dashboard_recommendation",
            reason_code="repeated_wrong_cluster",
            confidence="high",
            evidence=[
                "active_cross_question_wrong_nodes="
                f"{chosen['active_cross_question_wrong_node_count']}",
                "active_repeated_weakness_nodes="
                f"{chosen['active_repeated_weakness_node_count']}",
                "active_evaluable_wrong_repairing_nodes="
                f"{chosen['active_evaluable_wrong_repairing_node_count']}",
            ],
            observations=observations,
        )

    # J4: due retention work attributed by formal retention reference question.
    j4 = build_j4_candidates(retention)
    if j4:
        chosen = j4[0]
        return _make_result(
            intent="recheck",
            field_id=chosen["field_id"],
            question_count=10,
            route="dashboard_recommendation",
            reason_code="recheck_due",
            confidence="medium",
            evidence=[
                f"recheck_due_nodes={chosen['recheck_due_node_count']}",
                f"max_overdue_days={chosen['max_overdue_days']}",
                f"total_overdue_days={chosen['total_overdue_days']}",
            ],
            observations=observations,
        )

    # J5 foundation: raw exposure remains learning-volume context before 100 attempts.
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

    # J5 post-foundation: field threshold uses evaluable answers, not unknown exposure.
    sparse = build_j5_sparse_field_candidates(fields)
    if sparse:
        chosen = sparse[0]
        return _make_result(
            intent="coverage",
            field_id=chosen["field_id"],
            question_count=10,
            route="dashboard_recommendation",
            reason_code="insufficient_coverage",
            confidence="medium",
            evidence=[
                f"field_evaluable_answer_count={chosen['evaluable_answer_count']}",
                f"field_raw_answer_count={chosen['raw_answer_count']}",
                f"field_unknown_answer_count={chosen['unknown_answer_count']}",
                f"field_node_coverage_percent={chosen['node_coverage_percent']}",
                "minimum_reliable_field_evaluable_answers=10",
            ],
            observations=observations,
        )

    # J6: uncertain-correct stabilization with evaluable denominator.
    j6 = build_j6_uncertain_correct_candidates(
        fields,
        uncertain_correct_by_field=uncertain,
    )
    if j6:
        chosen = j6[0]
        return _make_result(
            intent="stabilization",
            field_id=chosen["field_id"],
            question_count=10,
            route="dashboard_recommendation",
            reason_code="uncertain_correct_cluster",
            confidence="medium",
            evidence=[
                f"uncertain_correct_count={chosen['uncertain_correct_count']}",
                "uncertain_correct_proportion="
                f"{round(chosen['uncertain_correct_proportion'], 3)}",
                f"evaluable_answers={chosen['evaluable_answer_count']}",
                f"checking_nodes={chosen['checking_node_count']}",
            ],
            observations=observations,
        )

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


def build_formal_field_profiles(
    attempts: Iterable[dict[str, Any]],
    field_evidence: dict[str, Any],
    *,
    as_of: datetime | None = None,
) -> dict[str, dict[str, Any]]:
    """Build symmetric field profiles from the same evidence as formal judgment."""
    context = build_formal_context(attempts, field_evidence, as_of=as_of)
    fields = context["fields"]
    active_fields = context["active_field_facts"]
    retention_by_field = context["retention_facts"].get("by_field", {})
    uncertain = context["uncertain_correct_by_field"]
    total_answers = context["total_answers"]

    profiles: dict[str, dict[str, Any]] = {}
    for field_id, field in fields.items():
        active = active_fields.get(field_id, {})
        retention = retention_by_field.get(field_id, {})
        critical = int(active.get("critical_safety_unresolved_count") or 0)
        cross_confident = int(
            active.get("active_cross_question_confident_wrong_node_count") or 0
        )
        confident_nodes = int(
            active.get("active_confident_wrong_repairing_node_count") or 0
        )
        cross_wrong = int(active.get("active_cross_question_wrong_node_count") or 0)
        repeated = int(active.get("active_repeated_weakness_node_count") or 0)
        active_repairing = int(
            active.get("active_evaluable_wrong_repairing_node_count") or 0
        )
        recheck_due = int(retention.get("recheck_due_node_count") or 0)
        evaluable_answer_count = int(field.get("evaluable_answer_count") or 0)
        uncertain_correct = int(uncertain.get(field_id, 0))

        if critical:
            reason = "safety_repair"
        elif cross_confident or confident_nodes >= 2:
            reason = "confident_wrong_cluster"
        elif cross_wrong or repeated >= 2:
            reason = "repeated_wrong_cluster"
        elif recheck_due:
            reason = "recheck_due"
        elif total_answers < 100 or evaluable_answer_count < 10:
            reason = "insufficient_coverage"
        elif uncertain_correct >= 3 and evaluable_answer_count >= 5:
            reason = "uncertain_correct_cluster"
        else:
            reason = "maintenance_only"

        name = str(field.get("field_name") or CATEGORY_NAMES.get(field_id) or field_id)
        profiles[name] = {
            "field_id": field_id,
            "field_name": name,
            "strongest_reason_code": reason,
            "strongest_reason_label": REASON_LABELS[reason],
            "reason_rank": REASON_RANKS[reason],
            "critical_safety_unresolved_count": critical,
            "active_cross_question_confident_wrong_node_count": cross_confident,
            "active_confident_wrong_repairing_node_count": confident_nodes,
            "active_cross_question_wrong_node_count": cross_wrong,
            "active_repeated_weakness_node_count": repeated,
            "active_evaluable_wrong_repairing_node_count": active_repairing,
            "recheck_due_node_count": recheck_due,
            "uncertain_correct_count": uncertain_correct,
            "raw_answer_count": int(field.get("question_answer_count") or 0),
            "evaluable_answer_count": evaluable_answer_count,
            "raw_accuracy": field.get("question_accuracy"),
            "evaluable_accuracy": field.get("evaluable_accuracy"),
            "node_coverage_percent": float(
                (field.get("node_coverage") or {}).get("percent") or 0
            ),
            "repairing_node_count": int(field.get("repairing_node_count") or 0),
            "checking_node_count": int(field.get("checking_node_count") or 0),
        }
    return profiles
