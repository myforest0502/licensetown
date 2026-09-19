"""Read-only Phase 11 promotion gate status from existing diagnostic evidence.

This module is intentionally conservative. It reports PASS / OPEN / BLOCKED for
checkable evidence classes but never authorizes learner-facing promotion.
"""

from __future__ import annotations
from typing import Any

PASS = "pass"
OPEN = "open"
BLOCKED = "blocked"


def _int(source: dict[str, Any] | None, key: str) -> int:
    return int((source or {}).get(key) or 0)


def build_phase11_promotion_gate_status(
    *,
    retrospective_shadow_audit: dict[str, Any] | None,
    repeat_structure_audit: dict[str, Any] | None,
    retention_horizon: dict[str, Any] | None,
    state_counts: dict[str, Any] | None,
    transitions: dict[str, Any] | None,
    shadow_judgment: dict[str, Any] | None,
    retention_outcome_audit: dict[str, Any] | None = None,
    intent_selection_alignment: dict[str, Any] | None = None,
) -> dict[str, Any]:
    replay = retrospective_shadow_audit or {}
    repeat_counts = (repeat_structure_audit or {}).get("category_counts") or {}
    retention = retention_horizon or {}
    states = state_counts or {}
    transition_counts = transitions or {}
    outcomes = retention_outcome_audit
    alignment = intent_selection_alignment
    comparison = (shadow_judgment or {}).get("comparison") or {}

    safety_misses = _int(replay, "phase11_critical_safety_miss_candidate_count")
    safety_status = BLOCKED if safety_misses else PASS

    unexplained_repeat = _int(repeat_counts, "adaptive_unexplained_repeat")
    metadata_inconsistent = _int(repeat_counts, "adaptive_metadata_inconsistent")
    repeat_status = BLOCKED if unexplained_repeat or metadata_inconsistent else PASS

    trigger_mismatch = _int(replay, "ordinary_single_wrong_takeover_candidate_count")
    trigger_status = BLOCKED if trigger_mismatch else PASS

    due_now = _int(retention, "recheck_due_count")
    stable_now = _int(states, "stable")
    due_to_stable = _int(transition_counts, "recheck_due_to_stable")
    due_to_repairing = _int(transition_counts, "recheck_due_to_repairing")
    if outcomes is not None:
        retention_review_count = _int(outcomes, "review_attempt_count")
        qualified_retention_count = _int(outcomes, "qualified_strong_outcome_count")
        retention_observed = retention_review_count > 0
        retention_qualified = qualified_retention_count > 0
        retention_status = PASS if retention_qualified else OPEN
    else:
        retention_review_count = 0
        qualified_retention_count = 0
        retention_observed = bool(due_now or stable_now or due_to_stable or due_to_repairing)
        retention_qualified = bool(due_to_stable or due_to_repairing or stable_now)
        retention_status = PASS if retention_qualified else OPEN

    if alignment is None:
        alignment_status = OPEN
    else:
        raw_alignment_status = str(alignment.get("alignment_status") or OPEN)
        alignment_status = (
            BLOCKED if raw_alignment_status == "blocked"
            else PASS if raw_alignment_status == "pass"
            else OPEN
        )

    eligible = _int(replay, "eligible_snapshot_count")
    shadow_stronger = _int(replay, "shadow_stronger_disagreement_count")
    current_stronger = _int(replay, "current_stronger_disagreement_count")
    agreement = _int(replay, "agreement_count")
    inconclusive = _int(replay, "inconclusive_disagreement_count")
    observed_directions = sum(
        value > 0 for value in (shadow_stronger, current_stronger, agreement, inconclusive)
    )
    prospective_status = PASS if observed_directions >= 2 else OPEN

    profile_consistent = bool(comparison.get("shadow_reason_profile_consistent", True))
    comparison_status = PASS if profile_consistent else BLOCKED

    gates = {
        "safety": {"status": safety_status, "critical_miss_count": safety_misses},
        "repeat_audit": {
            "status": repeat_status,
            "unexplained_recent_repeat_count": unexplained_repeat,
            "metadata_inconsistent_count": metadata_inconsistent,
        },
        "formal_trigger_consistency": {
            "status": trigger_status,
            "single_wrong_takeover_candidate_count": trigger_mismatch,
        },
        "retention": {
            "status": retention_status,
            "natural_retention_observed": retention_observed,
            "qualified_strong_retention_observed": retention_qualified,
            "review_attempt_count": retention_review_count,
            "qualified_strong_outcome_count": qualified_retention_count,
            "review_stable_count": _int(outcomes, "stable_count") if outcomes is not None else 0,
            "review_repairing_count": _int(outcomes, "repairing_count") if outcomes is not None else 0,
            "review_still_due_count": _int(outcomes, "still_due_count") if outcomes is not None else 0,
            "strong_stable_count": _int(outcomes, "strong_stable_count") if outcomes is not None else 0,
            "strong_repairing_count": _int(outcomes, "strong_repairing_count") if outcomes is not None else 0,
            "strong_still_due_count": _int(outcomes, "strong_still_due_count") if outcomes is not None else 0,
            "recheck_due_count": due_now,
            "stable_count": stable_now,
            "recheck_due_to_stable": due_to_stable,
            "recheck_due_to_repairing": due_to_repairing,
            "upcoming_review_count": _int(retention, "upcoming_review_count"),
            "earliest_review_at_jst": retention.get("earliest_review_at_jst"),
        },
        "intent_selection_alignment": {
            "status": alignment_status,
            "saved_recheck_selection_count": _int(alignment, "saved_recheck_selection_count"),
            "evaluable_recheck_selection_count": _int(alignment, "evaluable_recheck_selection_count"),
            "aligned_recheck_selection_count": _int(alignment, "aligned_recheck_selection_count"),
            "misaligned_recheck_selection_count": _int(alignment, "misaligned_recheck_selection_count"),
            "not_evaluable_recheck_selection_count": _int(alignment, "not_evaluable_recheck_selection_count"),
        },
        "comparison_diversity": {
            "status": prospective_status,
            "eligible_snapshot_count": eligible,
            "shadow_stronger": shadow_stronger,
            "current_stronger": current_stronger,
            "agreement": agreement,
            "inconclusive": inconclusive,
            "observed_direction_count": observed_directions,
        },
        "profile_consistency": {
            "status": comparison_status,
            "shadow_reason_profile_consistent": profile_consistent,
        },
    }

    blocked = [name for name, item in gates.items() if item["status"] == BLOCKED]
    open_gates = [name for name, item in gates.items() if item["status"] == OPEN]
    return {
        "decision": "blocked" if blocked else "hold",
        "learner_facing_promotion_allowed": False,
        "manual_review_required": True,
        "automatically_clear": not blocked and not open_gates,
        "blocked_gates": blocked,
        "open_gates": open_gates,
        "gates": gates,
        "policy_note": (
            "Automatic diagnostics never promote Phase11. Even when every checkable "
            "gate is clear, learner-facing promotion requires an explicit human review."
        ),
    }


def build_phase11_promotion_gate_evidence_line(status: dict[str, Any] | None) -> str:
    source = status or {}
    gates = source.get("gates") or {}
    def gate(name: str) -> str:
        return str((gates.get(name) or {}).get("status") or OPEN)
    blocked = "|".join(source.get("blocked_gates") or []) or "none"
    open_gates = "|".join(source.get("open_gates") or []) or "none"
    return "phase11_gate_status=" + ",".join([
        f"decision:{source.get('decision') or 'hold'}",
        f"safety:{gate('safety')}",
        f"repeat:{gate('repeat_audit')}",
        f"trigger:{gate('formal_trigger_consistency')}",
        f"retention:{gate('retention')}",
        f"intent_selection:{gate('intent_selection_alignment')}",
        f"diversity:{gate('comparison_diversity')}",
        f"profile:{gate('profile_consistency')}",
        f"blocked:{blocked}",
        f"open:{open_gates}",
        "promotion_allowed:false",
        "manual_review_required:true",
    ])
