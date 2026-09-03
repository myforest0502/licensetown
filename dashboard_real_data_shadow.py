"""Deterministic read-only dashboard real-data shadow v0.1.

This module turns authoritative question-attempt evidence into dashboard-facing
structured facts. It never writes learner data, calls an LLM, or chooses exact
question IDs. Exact-Q routing remains owned by the formal selector.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable, Mapping

from field_evidence import build_field_evidence
from field_progress import build_field_progress
from judgment_shadow import build_field_judgment_evidence_profiles


STATUS = "dashboard_real_data_shadow_v0.1"
MIN_RELIABLE_FIELD_EVALUABLE_ANSWERS = 10
MATERIALLY_LOW_PROGRESS_SCORE = 0.35
DEFAULT_REQUESTED_QUESTION_COUNT = 10

_REASON_BUCKET = {
    "safety_repair": 1,
    "confident_wrong_repair": 2,
    "repeated_wrong_repair": 3,
    "repairing_continue": 4,
    "retention_recheck": 5,
    "low_progress_repair": 6,
    "coverage_expand": 7,
}


def _field_progress_by_id(progress: Mapping[str, Any]) -> dict[int, dict[str, Any]]:
    return {
        int(item["field_id"]): dict(item)
        for item in progress.get("fields", [])
    }


def _profiles_by_id(profiles: Mapping[str, Mapping[str, Any]]) -> dict[int, dict[str, Any]]:
    result: dict[int, dict[str, Any]] = {}
    for item in profiles.values():
        field_id = item.get("field_id")
        if field_id is not None:
            result[int(field_id)] = dict(item)
    return result


def _candidate_for_field(
    field: Mapping[str, Any],
    progress: Mapping[str, Any],
    profile: Mapping[str, Any],
) -> dict[str, Any] | None:
    field_id = int(field["field_id"])
    field_name = str(field["field_name"])
    critical = int(profile.get("critical_safety_unresolved_count") or 0)
    cross_confident = int(profile.get("active_cross_question_confident_wrong_node_count") or 0)
    confident_nodes = int(profile.get("active_confident_wrong_repairing_node_count") or 0)
    cross_wrong = int(profile.get("active_cross_question_wrong_node_count") or 0)
    repeated = int(profile.get("active_repeated_weakness_node_count") or 0)
    active_repairing = int(profile.get("active_evaluable_wrong_repairing_node_count") or 0)
    recheck_due = int(profile.get("recheck_due_node_count") or 0)
    evaluable = int(field.get("evaluable_answer_count") or 0)
    progress_score = float(progress.get("field_progress_score") or 0.0)
    coverage = float(progress.get("node_coverage") or 0.0)

    if critical:
        reason_code = "safety_repair"
        severity = critical
        intent = "repair"
        advice_intent = "safety_repair"
    elif cross_confident or confident_nodes >= 2:
        reason_code = "confident_wrong_repair"
        severity = max(cross_confident, confident_nodes)
        intent = "repair"
        advice_intent = "confident_wrong_repair"
    elif cross_wrong or repeated >= 2:
        reason_code = "repeated_wrong_repair"
        severity = max(cross_wrong, repeated)
        intent = "repair"
        advice_intent = "repeated_wrong_repair"
    elif active_repairing:
        reason_code = "repairing_continue"
        severity = active_repairing
        intent = "repair"
        advice_intent = "repairing_continue"
    elif recheck_due:
        reason_code = "retention_recheck"
        severity = recheck_due
        intent = "recheck"
        advice_intent = "retention_recheck"
    elif evaluable >= MIN_RELIABLE_FIELD_EVALUABLE_ANSWERS and progress_score < MATERIALLY_LOW_PROGRESS_SCORE:
        reason_code = "low_progress_repair"
        severity = max(1, int(round((MATERIALLY_LOW_PROGRESS_SCORE - progress_score) * 100)))
        intent = "repair"
        advice_intent = "repairing_continue"
    else:
        return None

    return {
        "field_id": field_id,
        "field_name": field_name,
        "reason_code": reason_code,
        "bucket": _REASON_BUCKET[reason_code],
        "severity_count": severity,
        "advice_intent": advice_intent,
        "learning_intent": intent,
        "evaluable_answer_count": evaluable,
        "field_progress_score": progress_score,
        "field_progress_percent": progress.get("field_progress_percent"),
        "node_coverage": coverage,
        "critical_safety_unresolved_count": critical,
        "active_cross_question_confident_wrong_node_count": cross_confident,
        "active_confident_wrong_repairing_node_count": confident_nodes,
        "active_cross_question_wrong_node_count": cross_wrong,
        "active_repeated_weakness_node_count": repeated,
        "active_evaluable_wrong_repairing_node_count": active_repairing,
        "recheck_due_node_count": recheck_due,
        "is_proven_weakness": True,
        "is_coverage_priority": False,
    }


def _coverage_candidates(
    evidence: Mapping[str, Any],
    progress: Mapping[str, Any],
) -> list[dict[str, Any]]:
    progress_by_id = _field_progress_by_id(progress)
    candidates = []
    for field in evidence.get("fields", []):
        field_id = int(field["field_id"])
        p = progress_by_id[field_id]
        candidates.append({
            "field_id": field_id,
            "field_name": str(field["field_name"]),
            "reason_code": "coverage_expand",
            "bucket": _REASON_BUCKET["coverage_expand"],
            "severity_count": 0,
            "advice_intent": "coverage_expand",
            "learning_intent": "exploration",
            "evaluable_answer_count": int(field.get("evaluable_answer_count") or 0),
            "field_progress_score": float(p.get("field_progress_score") or 0.0),
            "field_progress_percent": p.get("field_progress_percent"),
            "node_coverage": float(p.get("node_coverage") or 0.0),
            "is_proven_weakness": False,
            "is_coverage_priority": True,
        })
    return sorted(
        candidates,
        key=lambda item: (
            item["node_coverage"],
            item["evaluable_answer_count"],
            item["field_id"],
        ),
    )


def _rank_candidates(candidates: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        candidates,
        key=lambda item: (
            int(item["bucket"]),
            -int(item.get("severity_count") or 0),
            float(item.get("field_progress_score") or 0.0),
            float(item.get("node_coverage") or 0.0),
            int(item["field_id"]),
        ),
    )


def _comparison(
    result: Mapping[str, Any],
    *,
    legacy_overall_progress_percent: int | float | None,
    legacy_weak_fields: Iterable[Any] | None,
    legacy_recommended_field: str | None,
) -> dict[str, Any]:
    top = list(result.get("weakness_top3") or [])
    shadow_fields = [item["field_name"] for item in top]
    recommendation = result.get("recommendation_intent") or {}
    shadow_recommended_field = recommendation.get("target_field")
    return {
        "legacy_overall_progress_percent": legacy_overall_progress_percent,
        "shadow_overall_progress_percent": result["overall"]["overall_progress_percent"],
        "legacy_weak_fields": list(legacy_weak_fields or []),
        "shadow_top_fields": shadow_fields,
        "legacy_recommended_field": legacy_recommended_field,
        "shadow_recommended_field": shadow_recommended_field,
        "recommended_field_same": bool(
            legacy_recommended_field
            and shadow_recommended_field
            and legacy_recommended_field == shadow_recommended_field
        ),
    }


def build_dashboard_real_data_shadow(
    attempts: Iterable[dict[str, Any]],
    evidence: Mapping[str, Any] | None = None,
    progress: Mapping[str, Any] | None = None,
    *,
    as_of: datetime | None = None,
    legacy_overall_progress_percent: int | float | None = None,
    legacy_weak_fields: Iterable[Any] | None = None,
    legacy_recommended_field: str | None = None,
) -> dict[str, Any]:
    """Build shadow dashboard facts from authoritative derived Node-state evidence."""
    attempts = [dict(item) for item in attempts]
    evidence = dict(evidence or build_field_evidence(attempts, as_of=as_of))
    progress = dict(progress or build_field_progress(evidence))
    profiles = build_field_judgment_evidence_profiles(attempts, evidence, as_of=as_of)
    profiles_by_id = _profiles_by_id(profiles)
    progress_by_id = _field_progress_by_id(progress)

    fields = []
    weakness_candidates = []
    for field in evidence.get("fields", []):
        field_id = int(field["field_id"])
        p = progress_by_id[field_id]
        profile = profiles_by_id.get(field_id, {})
        fields.append({
            "field_id": field_id,
            "field_name": str(field["field_name"]),
            "total_canonical_nodes": int(p["total_canonical_nodes"]),
            "touched_canonical_nodes": int(p["touched_canonical_nodes"]),
            "node_coverage": float(p["node_coverage"]),
            "state_mastery": float(p["state_mastery"]),
            "field_progress_score": float(p["field_progress_score"]),
            "field_progress_percent": p["field_progress_percent"],
            "state_counts": dict(p["state_counts"]),
            "question_answer_count": int(field.get("question_answer_count") or 0),
            "evaluable_answer_count": int(field.get("evaluable_answer_count") or 0),
            "question_accuracy": field.get("question_accuracy"),
            "evaluable_accuracy": field.get("evaluable_accuracy"),
        })
        candidate = _candidate_for_field(field, p, profile)
        if candidate:
            weakness_candidates.append(candidate)

    ranked = _rank_candidates(weakness_candidates)
    if ranked:
        weakness_top3 = ranked[:3]
    else:
        weakness_top3 = _coverage_candidates(evidence, progress)[:3]

    primary = weakness_top3[0] if weakness_top3 else None
    if primary:
        recommendation_intent = {
            "target_field_id": primary["field_id"],
            "target_field": primary["field_name"],
            "target_canonical_node_ids": [],
            "learning_intent": primary["learning_intent"],
            "priority_reason": primary["reason_code"],
            "safety_priority": primary["reason_code"] == "safety_repair",
            "new_vs_review_preference": (
                "new" if primary["reason_code"] == "coverage_expand" else "review"
            ),
            "requested_question_count": DEFAULT_REQUESTED_QUESTION_COUNT,
            "exact_question_ids": None,
            "selector_owns_exact_q": True,
        }
        advice = {
            "target_field_id": primary["field_id"],
            "target_field": primary["field_name"],
            "intent": primary["advice_intent"],
            "reason_code": primary["reason_code"],
        }
    else:
        recommendation_intent = {
            "target_field_id": None,
            "target_field": None,
            "target_canonical_node_ids": [],
            "learning_intent": "maintenance",
            "priority_reason": "stable_maintain",
            "safety_priority": False,
            "new_vs_review_preference": "mixed",
            "requested_question_count": 30,
            "exact_question_ids": None,
            "selector_owns_exact_q": True,
        }
        advice = {
            "target_field_id": None,
            "target_field": None,
            "intent": "stable_maintain",
            "reason_code": "stable_maintain",
        }

    overall = dict(progress["overall"])
    total = int(overall["total_unique_canonical_nodes"])
    touched = int(overall["touched_unique_canonical_nodes"])
    state_score_sum = float(overall["state_score_sum"])
    overall["node_coverage"] = touched / total if total else 0.0
    overall["state_mastery"] = state_score_sum / touched if touched else 0.0

    result = {
        "status": STATUS,
        "shadow_only": True,
        "authoritative_attempt_source": "question_attempts",
        "authoritative_node_state_source": "pure_derive_all_user_node_states",
        "field_count": len(fields),
        "overall": overall,
        "fields": fields,
        "weakness_top3": weakness_top3,
        "advice": advice,
        "recommendation_intent": recommendation_intent,
        "exact_question_selection_performed": False,
        "phase11_promoted": False,
    }
    result["comparison"] = _comparison(
        result,
        legacy_overall_progress_percent=legacy_overall_progress_percent,
        legacy_weak_fields=legacy_weak_fields,
        legacy_recommended_field=legacy_recommended_field,
    )
    return result
