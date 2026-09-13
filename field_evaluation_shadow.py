"""Shadow-only field evaluation for the LicenseTown learning strategy.

Pure deterministic logic. No DB writes, LLM calls, learner-facing labels, or
question selection authority.
"""
from __future__ import annotations

from math import ceil
from typing import Any, Mapping

VERSION = "field_evaluation_shadow_v0.1"
INITIAL_QUESTION_FLOOR = 60
REEVALUATION_BLOCK = 30
NODE_COVERAGE_FLOOR = 0.35
MIN_NODE_SPREAD = 6


def required_node_spread(total_nodes: int) -> int:
    """Return a field-size-aware spread target that is attainable at 60 answers.

    A raw percentage alone is invalid for very large fields because 35% of the
    field may exceed the entire initial 60-question evidence budget. The target
    therefore scales with field supply but is capped by the initial budget.
    """
    total_nodes = max(0, int(total_nodes))
    if not total_nodes:
        return 0
    proportional = max(MIN_NODE_SPREAD, ceil(total_nodes * NODE_COVERAGE_FLOOR))
    return min(total_nodes, INITIAL_QUESTION_FLOOR, proportional)


def _ratio(value: int, denominator: int) -> float:
    return value / denominator if denominator else 0.0


def evaluate_field(
    evidence: Mapping[str, Any],
    progress: Mapping[str, Any],
    *,
    critical_safety_unresolved_count: int = 0,
    additional_blocks_completed: int = 0,
    previous_progress_score: float | None = None,
) -> dict[str, Any]:
    answers = int(evidence.get("evaluable_answer_count") or 0)
    total_nodes = int(progress.get("total_canonical_nodes") or evidence.get("total_canonical_node_count") or 0)
    touched = int(progress.get("touched_canonical_nodes") or evidence.get("attempted_canonical_node_count") or 0)
    required_nodes = required_node_spread(total_nodes)
    sufficient = answers >= INITIAL_QUESTION_FLOOR and touched >= required_nodes and total_nodes > 0

    counts = dict(progress.get("state_counts") or evidence.get("state_counts") or {})
    repairing = int(counts.get("repairing") or 0)
    repaired = int(counts.get("repaired") or 0)
    recheck_due = int(counts.get("recheck_due") or 0)
    stable = int(counts.get("stable") or 0)
    repairing_ratio = _ratio(repairing, touched)
    resolved_ratio = _ratio(repaired + recheck_due + stable, touched)
    stable_ratio = _ratio(stable, touched)
    accuracy = evidence.get("evaluable_accuracy")
    accuracy = float(accuracy) if accuracy is not None else None
    repeated = int(evidence.get("repeated_weakness_evidence_count") or 0)
    repairs = int(evidence.get("different_question_repair_confirmation_count") or 0)
    safety = max(0, int(critical_safety_unresolved_count or 0))
    score = float(progress.get("field_progress_score") or progress.get("progress_score") or 0.0)

    reasons: list[str] = []
    if not sufficient:
        state = "assessing" if answers or touched else "unassessed"
        if answers < INITIAL_QUESTION_FLOOR:
            reasons.append("question_floor_not_met")
        if touched < required_nodes:
            reasons.append("node_spread_not_met")
    else:
        weak_reasons = []
        if safety:
            weak_reasons.append("critical_safety_unresolved")
        if accuracy is not None and accuracy < 0.65:
            weak_reasons.append("low_accuracy")
        if repairing_ratio >= 0.25:
            weak_reasons.append("repairing_ratio_high")
        if repeated >= 2:
            weak_reasons.append("repeated_weakness")
        if weak_reasons:
            state = "weak"
            reasons.extend(weak_reasons)
        elif accuracy is not None and accuracy >= 0.80 and repairing_ratio <= 0.10 and resolved_ratio >= 0.60:
            state = "strong"
            reasons.append("strong_multi_signal_evidence")
        else:
            state = "ordinary"
            reasons.append("mixed_or_intermediate_evidence")

    if state == "weak":
        blocks = max(0, answers - INITIAL_QUESTION_FLOOR) // REEVALUATION_BLOCK
        next_eval = INITIAL_QUESTION_FLOOR + (blocks + 1) * REEVALUATION_BLOCK
    elif state in {"unassessed", "assessing"}:
        next_eval = INITIAL_QUESTION_FLOOR
    else:
        next_eval = None

    if stable_ratio >= 0.40 and repairing == 0 and not safety:
        recovery = "durable_recovery"
    elif resolved_ratio >= 0.40 and repairs > 0 and not safety:
        recovery = "provisional_recovery"
    else:
        recovery = "not_recovered"

    gain = None if previous_progress_score is None else score - float(previous_progress_score)
    strategy_change = bool(state == "weak" and additional_blocks_completed >= 3 and gain is not None and gain < 0.03)
    if safety:
        priority_hint = "safety"
    elif strategy_change:
        priority_hint = "strategy_change_candidate"
    elif state == "weak":
        priority_hint = "repair_candidate"
    elif state in {"unassessed", "assessing"}:
        priority_hint = "coverage_candidate"
    else:
        priority_hint = "maintenance_candidate"

    return {
        "version": VERSION,
        "shadow_only": True,
        "selection_authority": False,
        "field_id": evidence.get("field_id") or progress.get("field_id"),
        "field_name": evidence.get("field_name") or progress.get("field_name"),
        "field_state": state,
        "strategy_priority_hint": priority_hint,
        "evidence_sufficient": sufficient,
        "evaluable_answer_count": answers,
        "required_node_spread": required_nodes,
        "touched_canonical_nodes": touched,
        "node_spread_met": touched >= required_nodes,
        "evaluable_accuracy": accuracy,
        "repairing_ratio": repairing_ratio,
        "resolved_ratio": resolved_ratio,
        "stable_ratio": stable_ratio,
        "next_evaluation_answer_count": next_eval,
        "recovery_level": recovery,
        "strategy_change_candidate": strategy_change,
        "marginal_progress_gain": gain,
        "reasons": reasons,
    }


def evaluate_all_fields(evidence_bundle: Mapping[str, Any], progress_bundle: Mapping[str, Any]) -> dict[str, Any]:
    progress_by_id = {int(row["field_id"]): row for row in progress_bundle.get("fields", [])}
    fields = [evaluate_field(row, progress_by_id[int(row["field_id"])]) for row in evidence_bundle.get("fields", [])]
    return {"version": VERSION, "shadow_only": True, "selection_authority": False, "field_count": len(fields), "fields": fields}
