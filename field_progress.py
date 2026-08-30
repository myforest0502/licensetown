"""Pure v0.1 Field/Overall Progress shadow calculation from Field Evidence."""

from __future__ import annotations

from collections import Counter
from math import isclose
from typing import Any, Mapping


STATE_SCORES = {
    "unseen": 0.00,
    "repairing": 0.10,
    "checking": 0.30,
    "recheck_due": 0.60,
    "repaired": 0.70,
    "stable": 1.00,
}
PROGRESS_STATUS = "field_progress_v0.1_shadow"


def score_to_percent(score: float, digits: int = 1) -> float:
    """Presentation helper; progress calculations themselves remain unrounded."""
    return round(float(score) * 100, digits)


def calculate_progress_from_state_counts(
    state_counts: Mapping[str, int],
    total_canonical_nodes: int,
) -> dict[str, Any]:
    """Return Coverage, touched-state Mastery, and all-Node Progress."""
    total = int(total_canonical_nodes)
    if total < 0:
        raise ValueError("total_canonical_nodes must be non-negative")
    unknown_states = set(state_counts) - set(STATE_SCORES)
    if unknown_states:
        raise ValueError(f"unknown Node states: {sorted(unknown_states)}")
    counts = {state: int(state_counts.get(state, 0)) for state in STATE_SCORES}
    if any(value < 0 for value in counts.values()):
        raise ValueError("state counts must be non-negative")
    if sum(counts.values()) != total:
        raise ValueError("state counts must equal total_canonical_nodes")

    touched = total - counts["unseen"]
    state_score_sum = sum(counts[state] * score for state, score in STATE_SCORES.items())
    node_coverage = touched / total if total else 0.0
    state_mastery = state_score_sum / touched if touched else 0.0
    field_progress_score = state_score_sum / total if total else 0.0
    if not isclose(field_progress_score, node_coverage * state_mastery, abs_tol=1e-12):
        raise AssertionError("Field Progress must equal Node Coverage x State Mastery")
    return {
        "touched_canonical_nodes": touched,
        "node_coverage": node_coverage,
        "state_score_sum": state_score_sum,
        "state_mastery": state_mastery,
        "progress_score": field_progress_score,
    }


def build_field_progress(
    evidence: Mapping[str, Any],
    *,
    legacy_overall_progress_percent: int | float | None = None,
) -> dict[str, Any]:
    """Convert v0.1 evidence into UI-disconnected shadow progress values."""
    if evidence.get("status") != "evidence_only":
        raise ValueError("Field Progress requires evidence_only input")

    fields = []
    for source in evidence["fields"]:
        counts = {state: int(source["state_counts"].get(state, 0)) for state in STATE_SCORES}
        progress = calculate_progress_from_state_counts(
            counts, source["total_canonical_node_count"]
        )
        fields.append({
            "field_id": source["field_id"],
            "field_name": source["field_name"],
            "total_canonical_nodes": source["total_canonical_node_count"],
            **progress,
            "state_counts": counts,
            "field_progress_score": progress["progress_score"],
            "field_progress_percent": score_to_percent(progress["progress_score"]),
            "question_accuracy": source.get("question_accuracy"),
            "question_coverage": source["question_coverage"],
            "status": PROGRESS_STATUS,
        })

    canonical_records = list(evidence["canonical_node_evidence"])
    canonical_ids = [item["canonical_node_id"] for item in canonical_records]
    if len(canonical_ids) != len(set(canonical_ids)):
        raise ValueError("canonical_node_evidence must be unique")
    overall_counts = Counter(item["state"] for item in canonical_records)
    overall = calculate_progress_from_state_counts(overall_counts, len(canonical_records))
    canonical_node_scores = [
        {
            "canonical_node_id": item["canonical_node_id"],
            "field_ids": list(item["field_ids"]),
            "state": item["state"],
            "state_score": STATE_SCORES[item["state"]],
        }
        for item in canonical_records
    ]
    return {
        "status": PROGRESS_STATUS,
        "state_scores": dict(STATE_SCORES),
        "fields": fields,
        "overall": {
            "total_unique_canonical_nodes": len(canonical_records),
            "touched_unique_canonical_nodes": overall["touched_canonical_nodes"],
            "state_counts": {state: overall_counts[state] for state in STATE_SCORES},
            "state_score_sum": overall["state_score_sum"],
            "overall_progress_score": overall["progress_score"],
            "overall_progress_percent": score_to_percent(overall["progress_score"]),
        },
        "canonical_node_scores": canonical_node_scores,
        "multi_field_node_count": evidence["multi_field_node_count"],
        "canonical_node_membership_total": evidence["canonical_node_membership_total"],
        "legacy_overall_progress_percent": legacy_overall_progress_percent,
        "retention_multiplier_applied": False,
        "confidence_adjustment_applied": False,
        "unknown_answer_adjustment_applied": False,
        "repeated_weakness_adjustment_applied": False,
        "written_evidence_adjustment_applied": False,
    }
