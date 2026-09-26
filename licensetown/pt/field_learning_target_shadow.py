"""Stage D: pure PT field budgets and targets, never selection authority."""
from __future__ import annotations

from math import isfinite
from typing import Any, Mapping

from exam_weight_shadow import field_exam_weight
from field_evaluation_shadow import INITIAL_QUESTION_FLOOR, REEVALUATION_BLOCK, evaluate_field
from field_progress import calculate_progress_from_state_counts

VERSION = "field_learning_target_shadow_v0.1"
MAX_ADDITIONAL_BLOCKS = 3


def nonnegative(value: Any, name: str) -> float:
    number = float(value)
    if not isfinite(number) or number < 0:
        raise ValueError(f"{name} must be finite and non-negative")
    return number


def count(value: Any, name: str) -> int:
    number = nonnegative(value, name)
    if number != int(number):
        raise ValueError(f"{name} must be an integer")
    return int(number)


def unit(value: Any, name: str) -> float:
    number = nonnegative(value, name)
    if number > 1:
        raise ValueError(f"{name} must be in [0, 1]")
    return number


def build_field_target(
    evidence: Mapping[str, Any], progress: Mapping[str, Any], *,
    context: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Consume existing evidence/progress rows and explicit observation context.

    The supply-capped first-pass budget does NOT relax Stage B's 60-answer gate.
    Counts are historical/static supply, not currently cooldown-eligible supply.
    No wall clock, DB adapter, data loader, or runtime imports are used here.
    """
    context = dict(context or {})
    field_id = count(evidence["field_id"], "field_id")
    if field_id != count(progress["field_id"], "field_id"):
        raise ValueError("evidence and progress field IDs must match")
    weight = field_exam_weight(field_id)
    total = count(progress["total_canonical_nodes"], "total_canonical_nodes")
    if total != count(evidence["total_canonical_node_count"], "total_canonical_node_count"):
        raise ValueError("evidence and progress Node supply must match")
    counts = {key: count(value, key) for key, value in progress["state_counts"].items()}
    current = calculate_progress_from_state_counts(counts, total)
    # Reject mismatched snapshots rather than silently altering displayed progress.
    if any(counts.get(key, 0) != value for key, value in evidence["state_counts"].items()):
        raise ValueError("evidence and progress Node states must match")
    if abs(unit(progress["field_progress_score"], "field_progress_score") - current["progress_score"]) > 1e-9:
        raise ValueError("progress score must match derived Node states")
    if count(progress["touched_canonical_nodes"], "touched_canonical_nodes") != current["touched_canonical_nodes"]:
        raise ValueError("touched count must match derived Node states")
    supply = count(evidence["total_question_count"], "total_question_count")
    if total > supply:
        raise ValueError("Node supply cannot exceed question supply")
    answers = count(evidence["evaluable_answer_count"], "evaluable_answer_count")
    accuracy = evidence.get("evaluable_accuracy")
    if accuracy is not None:
        unit(accuracy, "evaluable_accuracy")
    for key in ("repeated_weakness_evidence_count", "different_question_repair_confirmation_count"):
        count(evidence.get(key, 0), key)
    critical = count(context.get("critical_safety_unresolved_count", 0), "critical_safety_unresolved_count")
    blocks = count(context.get("additional_blocks_completed", 0), "additional_blocks_completed")
    consecutive = count(context.get("consecutive_field_blocks", 0), "consecutive_field_blocks")
    previous = context.get("previous_progress_score")
    if previous is not None:
        unit(previous, "previous_progress_score")
    prior_stable = context.get("previous_stable_ratio")
    if prior_stable is not None:
        unit(prior_stable, "previous_stable_ratio")
    elapsed = context.get("days_since_last_field_study")
    if elapsed is not None:
        nonnegative(elapsed, "days_since_last_field_study")
    evaluation = evaluate_field(
        evidence, progress, critical_safety_unresolved_count=critical,
        additional_blocks_completed=blocks, previous_progress_score=previous,
    )
    high_weight = weight["relative_weight"] >= 1.0
    # Smooth, bounded policy targets; these are hypotheses, not pass probabilities.
    weight_strength = weight["relative_weight"] / (1 + weight["relative_weight"])
    interval = 7 if high_weight else 14
    due = count(counts.get("recheck_due", 0), "recheck_due")
    stable_drop = max(0.0, float(prior_stable) - evaluation["stable_ratio"]) if prior_stable is not None else 0.0
    maintenance = bool(due or stable_drop or (elapsed is not None and elapsed >= interval))
    cap_reached = blocks >= MAX_ADDITIONAL_BLOCKS
    reasons = []
    if supply < INITIAL_QUESTION_FLOOR:
        reasons.append("initial_supply_limited")
    if cap_reached:
        reasons.append("additional_block_cap_reached")
    if evaluation["strategy_change_candidate"]:
        reasons.append("strategy_change_candidate")
    if "critical_safety_unresolved_count" not in context:
        reasons.append("safety_evidence_unavailable")
    return {
        "version": VERSION, "shadow_only": True, "selection_authority": False,
        "provisional": True, "field_id": field_id, "field_name": weight["field_name"],
        "exam_weight": weight, "field_state": evaluation["field_state"],
        "recovery_level": evaluation["recovery_level"], "evaluation": evaluation,
        "minimum_initial_questions": min(INITIAL_QUESTION_FLOOR, supply),
        "classification_question_floor": INITIAL_QUESTION_FLOOR,
        "minimum_node_spread": evaluation["required_node_spread"],
        "total_question_count": supply, "total_canonical_nodes": total,
        "target_progress_score": 0.60 + 0.20 * weight_strength,
        "target_stable_ratio": 0.40 + 0.20 * weight_strength,
        "target_resolved_ratio": 0.60 + 0.20 * weight_strength,
        "current_progress_score": current["progress_score"],
        "repeated_weakness_evidence_count": count(
            evidence.get("repeated_weakness_evidence_count", 0),
            "repeated_weakness_evidence_count",
        ),
        "repairing_node_count": count(
            evidence.get("repairing_node_count", counts.get("repairing", 0)),
            "repairing_node_count",
        ),
        "max_additional_blocks": MAX_ADDITIONAL_BLOCKS,
        "additional_block_size": REEVALUATION_BLOCK,
        "additional_blocks_completed": blocks,
        "remaining_additional_blocks": max(0, MAX_ADDITIONAL_BLOCKS - blocks),
        "additional_block_cap_reached": cap_reached,
        "next_evaluation_answer_count": evaluation["next_evaluation_answer_count"],
        "strategy_change_candidate": evaluation["strategy_change_candidate"],
        "consecutive_field_blocks": consecutive,
        "maintenance_interval_days": interval,
        "maintenance_needed": maintenance,
        "maintenance_timing_available": elapsed is not None,
        "stable_ratio_drop": stable_drop, "recheck_due_count": due,
        "critical_safety_unresolved_count": critical,
        "safety_evidence_available": "critical_safety_unresolved_count" in context,
        "context_available": sorted(context), "reason_codes": reasons,
    }


def build_field_targets(evidence_bundle, progress_bundle, *, context_by_field=None):
    """Require a complete, unambiguous 18-field snapshot; never invent missing rows."""
    def index(bundle):
        rows = list(bundle["fields"])
        indexed = {count(row["field_id"], "field_id"): row for row in rows}
        if len(indexed) != len(rows) or set(indexed) != set(range(1, 19)):
            raise ValueError("exactly one row per field 1-18 is required")
        return indexed

    evidence, progress = index(evidence_bundle), index(progress_bundle)
    contexts = context_by_field or {}
    if set(contexts) - set(evidence):
        raise ValueError("context contains unknown field IDs")
    return {
        "version": VERSION, "shadow_only": True, "selection_authority": False,
        "provisional": True, "field_count": 18,
        "fields": [build_field_target(evidence[i], progress[i], context=contexts.get(i)) for i in range(1, 19)],
    }
