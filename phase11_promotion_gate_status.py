"""Read-only Phase 11 promotion gate status from existing diagnostic evidence.

This module is intentionally conservative.  It can report PASS / OPEN / BLOCKED
for evidence classes, but it never authorizes learner-facing promotion.  A human
promotion review remains required even when every automatically checkable gate
is clear.
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
) -> dict[str, Any]:
    """Return deterministic gate states without inventing promotion thresholds."""
    replay = retrospective_shadow_audit or {}
    repeat = repeat_structure_audit or {}
    repeat_counts = repeat.get("category_counts") or {}
    retention = retention_horizon or {}
    states = state_counts or {}
    transition_counts = transitions or {}
    outcomes = retention_outcome_audit
    shadow = shadow_judgment or {}
    comparison = shadow.get("comparison") or {}

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
    # New callers provide an explicit due-before-attempt outcome audit.  This is
    # authoritative for whether a natural spaced review was actually observed,
    # because prefix timelines can jump repaired -> stable on the review attempt.
    if outcomes is not None:
        retention_review_count = _int(outcomes, "review_attempt_count")
        retention_observed = retention_review_count > 0
        retention_status = PASS if retention_observed else OPEN
    else:
        # Backward-compatible fallback for callers not yet wired to the explicit
        # retention outcome audit.
        retention_review_count = 0
        retention_observed = bool(due_now or stable_now or due_to_stable or due_to_repairing)
        retention_status = PASS if (due_to_stable or due_to_repairing or stable_now) else OPEN

    eligible = _int(replay, "eligible_snapshot_count")
    shadow_stronger = _int(replay, "shadow_stronger_disagreement_count")
    current_stronger = _int(replay, "current_stronger_disagreement_count")
    agreement = _int(replay, "agreement_count")
    inconclusive = _int(replay, "inconclusive_disagreement_count")
    observed_directions = sum(
        value > 0 for value in (shadow_stronger, current_stronger, agreement, inconclusive)
    )
    # No fixed sample threshold is encoded.  Diversity is OPEN until at least two
    # naturally observed result directions exist, then PASS as a collection gate.
    prospective_status = PASS if observed_directions >= 2 else OPEN

    profile_consistent = bool(comparison.get("shadow_reason_profile_consistent", True))
    comparison_status = PASS if profile_consistent else BLOCKED

    gates = {
        "safety": {
            "status": safety_status,
            "critical_miss_count": safety_misses,
        },
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
            "review_attempt_count": retention_review_count,
            "review_stable_count": _int(outcomes, "stable_count") if outcomes is not None else 0,
            "review_repairing_count": _int(outcomes, "repairing_count") if outcomes is not None else 0,
            "review_still_due_count": _int(outcomes, "still_due_count") if outcomes is not None else 0,
            "recheck_due_count": due_now,
            "stable_count": stable_now,
            "recheck_due_to_stable": due_to_stable,
            "recheck_due_to_repairing": due_to_repairing,
            "upcoming_review_count": _int(retention, "upcoming_review_count"),
            "earliest_review_at_jst": retention.get("earliest_review_at_jst"),
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
    automatically_clear = not blocked and not open_gates

    return {
        "decision": "blocked" if blocked else "hold",
        "learner_facing_promotion_allowed": False,
        "manual_review_required": True,
        "automatically_clear": automatically_clear,
        "blocked_gates": blocked,
        "open_gates": open_gates,
        "gates": gates,
        "policy_note": (
            "Automatic diagnostics never promote Phase11. Even when every checkable "
            "gate is clear, learner-facing promotion requires an explicit human review."
        ),
    }


def build_phase11_promotion_gate_evidence_line(status: dict[str, Any] | None) -> str:
    """Serialize a compact non-identifying status line for the evidence bundle."""
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
        f"diversity:{gate('comparison_diversity')}",
        f"profile:{gate('profile_consistency')}",
        f"blocked:{blocked}",
        f"open:{open_gates}",
        "promotion_allowed:false",
        "manual_review_required:true",
    ])
