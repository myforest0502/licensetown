"""Anonymous READ ONLY comparison of legacy dashboard and v0.1 Progress."""

from __future__ import annotations

from typing import Any, Mapping

from database import (
    calculate_overall_progress,
    get_dashboard_learning_data,
    get_question_attempts,
)
from field_evidence import build_field_evidence
from field_progress import STATE_SCORES, build_field_progress, score_to_percent


AUDIT_STATUS = "production_shadow_progress_audit_v0.1"


def _rounding_candidates(score: float) -> dict[str, float | int]:
    raw_percent = float(score) * 100
    return {
        "raw_score": float(score),
        "raw_percent": raw_percent,
        "integer_percent": round(raw_percent),
        "one_decimal_percent": round(raw_percent, 1),
    }


def _rank(fields, key, *, reverse):
    eligible = [item for item in fields if item.get(key) is not None]
    return [
        {
            "field_id": item["field_id"],
            "field_name": item["field_name"],
            "value": item[key],
        }
        for item in sorted(
            eligible,
            key=lambda item: (
                -(item[key]) if reverse else item[key],
                item["field_id"],
            ),
        )
    ]


def build_progress_shadow_audit(
    evidence: Mapping[str, Any],
    *,
    legacy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a human-auditable comparison without changing any score."""
    legacy = dict(legacy or {})
    progress = build_field_progress(
        evidence,
        legacy_overall_progress_percent=legacy.get("overall_progress_percent"),
    )
    evidence_by_field = {item["field_id"]: item for item in evidence["fields"]}
    fields = []
    for item in progress["fields"]:
        source = evidence_by_field[item["field_id"]]
        accuracy = item["question_accuracy"]
        accuracy_percent = accuracy * 100 if accuracy is not None else None
        progress_percent = item["field_progress_score"] * 100
        fields.append({
            **item,
            "field_answer_count": source["question_answer_count"],
            "question_accuracy_percent": accuracy_percent,
            "accuracy_progress_gap_points": (
                accuracy_percent - progress_percent
                if accuracy_percent is not None else None
            ),
            "rounding_candidates": _rounding_candidates(item["field_progress_score"]),
        })

    overall = dict(progress["overall"])
    total = overall["total_unique_canonical_nodes"]
    touched = overall["touched_unique_canonical_nodes"]
    overall["node_coverage"] = touched / total if total else 0.0
    overall["node_coverage_percent"] = score_to_percent(overall["node_coverage"])
    overall["rounding_candidates"] = _rounding_candidates(
        overall["overall_progress_score"]
    )
    attempts = int(legacy.get("question_attempt_count") or 0)
    correct = int(legacy.get("question_correct_count") or 0)
    overall["question_accuracy_percent"] = (
        correct * 100 / attempts if attempts else None
    )

    due_count = overall["state_counts"]["recheck_due"]
    due_contribution = due_count * STATE_SCORES["recheck_due"]
    repaired_counterfactual = due_count * STATE_SCORES["repaired"]
    recheck_due_impact = {
        "recheck_due_node_count": due_count,
        "repaired_node_count": overall["state_counts"]["repaired"],
        "stable_node_count": overall["state_counts"]["stable"],
        "score_contribution": due_contribution,
        "overall_progress_points": due_contribution / total if total else 0.0,
        "difference_vs_repaired_score": (
            (due_contribution - repaired_counterfactual) / total if total else 0.0
        ),
        "score_changed_by_audit": False,
    }
    return {
        "status": AUDIT_STATUS,
        "read_only": True,
        "anonymous_target": "one_authorized_user",
        "multi_field_node_count": progress["multi_field_node_count"],
        "canonical_node_membership_total": progress[
            "canonical_node_membership_total"
        ],
        "legacy": {
            "overall_progress_percent": legacy.get("overall_progress_percent"),
            "total_answers": legacy.get("total_answers"),
            "study_minutes": legacy.get("study_minutes"),
            "average_accuracy_percent": legacy.get("average_accuracy_percent"),
        },
        "overall": overall,
        "fields": fields,
        "rankings": {
            "field_progress_high": _rank(fields, "field_progress_score", reverse=True),
            "field_progress_low": _rank(fields, "field_progress_score", reverse=False),
            "node_coverage_high": _rank(fields, "node_coverage", reverse=True),
            "node_coverage_low": _rank(fields, "node_coverage", reverse=False),
            "question_accuracy_high": _rank(fields, "question_accuracy_percent", reverse=True),
            "question_accuracy_low": _rank(fields, "question_accuracy_percent", reverse=False),
        },
        "recheck_due_impact": recheck_due_impact,
        "score_specification_changed": False,
        "ui_connected": False,
    }


def get_user_progress_shadow_audit(user_id: str) -> dict[str, Any]:
    """READ ONLY adapter using saved attempts and current legacy dashboard data."""
    attempts = get_question_attempts(user_id)
    dashboard_data = get_dashboard_learning_data(user_id)
    summary = dashboard_data["summary"]
    legacy_overall = calculate_overall_progress(
        summary["study_minutes"],
        summary["total_answers"],
        dashboard_data["unique_question_count"],
    )
    return build_progress_shadow_audit(
        build_field_evidence(attempts),
        legacy={
            "overall_progress_percent": legacy_overall,
            "total_answers": summary["total_answers"],
            "study_minutes": summary["study_minutes"],
            "average_accuracy_percent": summary["average_accuracy"],
            "question_attempt_count": len(attempts),
            "question_correct_count": sum(
                item.get("is_correct") is True
                and item.get("answer_status") != "unknown"
                for item in attempts
            ),
        },
    )
