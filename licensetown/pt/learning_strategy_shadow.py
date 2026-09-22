"""Stage E: PT 18-field strategy candidates consumed by the opt-in PT pilot.

This module produces field/intent candidates; the existing adaptive selector
retains exact-question authority. It is not a qualification-neutral policy."""
from __future__ import annotations

from field_learning_target_shadow import build_field_targets, count

VERSION = "learning_strategy_shadow_v0.1"


def _clamp(value):
    return min(1.0, max(0.0, value))


def _rank_field(target, urgency):
    evaluation = target["evaluation"]
    sufficient = evaluation["evidence_sufficient"]
    initial_floor_incomplete = bool(
        target["total_question_count"] >= target["classification_question_floor"]
        and evaluation["evaluable_answer_count"] < target["classification_question_floor"]
    )
    weight = target["exam_weight"]["relative_weight"]
    weight_score = weight / (1 + weight)
    reasons = list(target["reason_codes"])
    if initial_floor_incomplete:
        reasons.append("initial_question_floor_incomplete")
    if sufficient:
        accuracy = evaluation["evaluable_accuracy"]
        weakness = max(
            _clamp(evaluation["repairing_ratio"]),
            _clamp((0.80 - accuracy) / 0.80) if accuracy is not None else 0.0,
            0.5 if "repeated_weakness" in evaluation["reasons"] else 0.0,
        )
        if "repeated_weakness" in evaluation["reasons"]:
            reasons.append("repeated_weakness")
    else:
        weakness = 0.0
        reasons.append("initial_evidence_insufficient")
    gap = max(
        _clamp((target["target_progress_score"] - target["current_progress_score"]) / target["target_progress_score"]),
        _clamp((target["target_stable_ratio"] - evaluation["stable_ratio"]) / target["target_stable_ratio"]),
        _clamp((target["target_resolved_ratio"] - evaluation["resolved_ratio"]) / target["target_resolved_ratio"]),
    )
    total = target["total_canonical_nodes"]
    coverage = max(
        1 - evaluation["touched_canonical_nodes"] / total if total else 0.0,
        _clamp(1 - evaluation["evaluable_answer_count"] / target["classification_question_floor"]),
    )
    retention = max(
        _clamp(target["recheck_due_count"] / max(1, evaluation["touched_canonical_nodes"])),
        _clamp(target["stable_ratio_drop"]), 0.5 if target["maintenance_needed"] else 0.0,
    )
    concentration = _clamp(target["consecutive_field_blocks"] / 3)
    if target["additional_block_cap_reached"]:
        concentration = 1.0
    safety = float(target["critical_safety_unresolved_count"] > 0)
    components = {
        "weakness_score": weakness, "attainment_gap_score": gap,
        "coverage_gap_score": _clamp(coverage), "exam_weight_score": weight_score,
        "retention_score": retention, "safety_score": safety,
        "concentration_penalty": concentration, "time_urgency_score": urgency,
    }
    # Additive components avoid multiplication by zero. Urgency increases the
    # exam-weight/attainment/retention contribution, never fabricates year trends.
    base = (0.15 * weakness + 0.20 * gap + 0.30 * coverage +
            0.20 * weight_score + 0.15 * retention)
    score = _clamp(base * (0.5 + 0.5 * weight_score) +
                   0.10 * urgency * max(gap * weight_score, retention) - 0.20 * concentration)
    if weight >= 1:
        reasons.append("high_exam_weight")
    if gap >= 0.5:
        reasons.append("large_attainment_gap")
    if coverage > 0:
        reasons.append("coverage_insufficient")
    if target["recheck_due_count"]:
        reasons.append("retention_due")
    if target["stable_ratio_drop"]:
        reasons.append("stable_ratio_declined")
    if target["maintenance_needed"]:
        reasons.append("maintenance_needed")
    if concentration:
        reasons.append("concentration_penalty")
    if urgency:
        reasons.append("exam_time_urgency")
    if safety:
        # A separate top tier: a fatigue penalty cannot suppress critical Safety.
        score += 1.0
        intent = "safety_review"
        reasons.append("critical_safety")
    elif target["additional_block_cap_reached"]:
        intent = "strategy_change"
    elif not sufficient:
        intent = "coverage"
    elif target["recheck_due_count"]:
        intent = "retention"
    elif target["field_state"] == "weak":
        intent = "repair"
    elif target["maintenance_needed"]:
        intent = "maintenance"
    elif gap > 0:
        intent = "attainment"
    else:
        intent = "maintenance"
        reasons.append("stable_maintenance_only")
        score = 0.0
    if initial_floor_incomplete:
        # An unfinished formal first pass must remain selectable even after
        # concentration penalties; rotation may lower its score, not strand it.
        score = max(score, 0.01)
    eligible = bool(total and target["total_question_count"] and (safety or not target["additional_block_cap_reached"]))
    if not total or not target["total_question_count"]:
        reasons.append("no_field_supply")
    return {
        "field_id": target["field_id"], "field_name": target["field_name"],
        "shadow_only": True, "selection_authority": False,
        "field_state": target["field_state"], "recovery_level": target["recovery_level"],
        "initial_question_floor_incomplete": initial_floor_incomplete,
        "learning_intent": intent, "priority_score": score,
        "priority_components": components, "reason_codes": reasons,
        "allocation_candidate": eligible, "target": target,
    }


def build_learning_strategy(evidence_bundle, progress_bundle, *, context_by_field=None, days_to_exam=None):
    """Return a candidate budget, not Q IDs or an executable session instruction.

    Inputs must be one learner's aligned derived snapshots. Optional context is
    explicit observed history; this module neither reads nor writes that history.
    """
    days = None if days_to_exam is None else count(days_to_exam, "days_to_exam")
    urgency = 0.0 if days is None else _clamp((90 - days) / 90)
    targets = build_field_targets(evidence_bundle, progress_bundle, context_by_field=context_by_field)
    ranked = [_rank_field(target, urgency) for target in targets["fields"]]
    # One decision contract: Critical Safety remains first. Otherwise, finish
    # the formal 60-answer first pass before ranking already-assessable fields.
    # This prevents low-sample fields from being stranded indefinitely.
    def priority_tier(row):
        if row["priority_components"]["safety_score"] > 0:
            return 0
        if row.get("initial_question_floor_incomplete"):
            return 1
        return 2

    ranked.sort(key=lambda row: (priority_tier(row), -row["priority_score"], row["field_id"]))
    recommended = next((row for row in ranked if row["allocation_candidate"] and row["priority_score"] > 0), None)
    return {
        "version": VERSION, "shadow_only": True, "selection_authority": False,
        "provisional": True, "temporal_adjustment": False,
        "days_to_exam": days, "time_evidence_available": days is not None,
        "recommended_field_id": recommended["field_id"] if recommended else None,
        "recommended_field_name": recommended["field_name"] if recommended else None,
        "recommended_question_count": 30 if recommended else 0,
        "learning_intent": recommended["learning_intent"] if recommended else "defer",
        "priority_score": recommended["priority_score"] if recommended else 0.0,
        "priority_components": dict(recommended["priority_components"]) if recommended else {},
        "reason_codes": list(recommended["reason_codes"]) if recommended else ["no_allocation_candidate"],
        "ranked_fields": ranked,
        "question_selection_required": True,
        "current_eligible_question_supply_checked": False,
    }
