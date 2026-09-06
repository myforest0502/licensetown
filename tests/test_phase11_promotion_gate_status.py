from phase11_promotion_gate_status import (
    BLOCKED,
    OPEN,
    PASS,
    build_phase11_promotion_gate_evidence_line,
    build_phase11_promotion_gate_status,
)


def _status(**overrides):
    kwargs = dict(
        retrospective_shadow_audit={
            "eligible_snapshot_count": 2,
            "shadow_stronger_disagreement_count": 2,
            "current_stronger_disagreement_count": 0,
            "agreement_count": 0,
            "inconclusive_disagreement_count": 0,
            "phase11_critical_safety_miss_candidate_count": 0,
            "ordinary_single_wrong_takeover_candidate_count": 0,
        },
        repeat_structure_audit={
            "category_counts": {
                "adaptive_unexplained_repeat": 0,
                "adaptive_metadata_inconsistent": 0,
            }
        },
        retention_horizon={
            "recheck_due_count": 0,
            "upcoming_review_count": 13,
            "earliest_review_at_jst": "2026-09-09T08:26:32+09:00",
        },
        state_counts={"stable": 0},
        transitions={
            "recheck_due_to_stable": 0,
            "recheck_due_to_repairing": 0,
        },
        shadow_judgment={
            "comparison": {"shadow_reason_profile_consistent": True}
        },
    )
    kwargs.update(overrides)
    return build_phase11_promotion_gate_status(**kwargs)


def test_current_natural_shape_stays_hold_with_retention_and_diversity_open():
    result = _status(retention_outcome_audit={"review_attempt_count": 0})
    assert result["decision"] == "hold"
    assert result["learner_facing_promotion_allowed"] is False
    assert result["manual_review_required"] is True
    assert result["gates"]["safety"]["status"] == PASS
    assert result["gates"]["repeat_audit"]["status"] == PASS
    assert result["gates"]["formal_trigger_consistency"]["status"] == PASS
    assert result["gates"]["retention"]["status"] == OPEN
    assert result["gates"]["comparison_diversity"]["status"] == OPEN
    assert set(result["open_gates"]) == {"retention", "comparison_diversity"}


def test_safety_repeat_or_trigger_regression_blocks_without_enabling_promotion():
    result = _status(
        retrospective_shadow_audit={
            "eligible_snapshot_count": 3,
            "shadow_stronger_disagreement_count": 1,
            "current_stronger_disagreement_count": 1,
            "phase11_critical_safety_miss_candidate_count": 1,
            "ordinary_single_wrong_takeover_candidate_count": 1,
        },
        repeat_structure_audit={
            "category_counts": {
                "adaptive_unexplained_repeat": 2,
                "adaptive_metadata_inconsistent": 1,
            }
        },
        retention_outcome_audit={"review_attempt_count": 0},
    )
    assert result["decision"] == "blocked"
    assert result["gates"]["safety"]["status"] == BLOCKED
    assert result["gates"]["repeat_audit"]["status"] == BLOCKED
    assert result["gates"]["formal_trigger_consistency"]["status"] == BLOCKED
    assert result["learner_facing_promotion_allowed"] is False


def test_qualified_strong_retention_outcome_and_direction_diversity_clear_checkable_gates_only():
    result = _status(
        retrospective_shadow_audit={
            "eligible_snapshot_count": 4,
            "shadow_stronger_disagreement_count": 2,
            "current_stronger_disagreement_count": 1,
            "agreement_count": 1,
            "inconclusive_disagreement_count": 0,
            "phase11_critical_safety_miss_candidate_count": 0,
            "ordinary_single_wrong_takeover_candidate_count": 0,
        },
        retention_horizon={"recheck_due_count": 0, "upcoming_review_count": 8},
        retention_outcome_audit={
            "review_attempt_count": 1,
            "stable_count": 1,
            "repairing_count": 0,
            "still_due_count": 0,
            "strong_stable_count": 1,
            "strong_repairing_count": 0,
            "strong_still_due_count": 0,
            "qualified_strong_outcome_count": 1,
        },
        state_counts={"stable": 1},
        transitions={
            "recheck_due_to_stable": 0,
            "recheck_due_to_repairing": 0,
        },
    )
    assert result["gates"]["retention"]["status"] == PASS
    assert result["gates"]["retention"]["review_attempt_count"] == 1
    assert result["gates"]["retention"]["qualified_strong_outcome_count"] == 1
    assert result["gates"]["retention"]["qualified_strong_retention_observed"] is True
    assert result["gates"]["comparison_diversity"]["status"] == PASS
    assert result["automatically_clear"] is True
    assert result["decision"] == "hold"
    assert result["learner_facing_promotion_allowed"] is False
    assert result["manual_review_required"] is True


def test_weak_or_same_q_natural_review_does_not_false_pass_j4():
    result = _status(
        retention_outcome_audit={
            "review_attempt_count": 2,
            "stable_count": 0,
            "repairing_count": 0,
            "still_due_count": 2,
            "qualified_strong_outcome_count": 0,
        }
    )
    assert result["gates"]["retention"]["natural_retention_observed"] is True
    assert result["gates"]["retention"]["qualified_strong_retention_observed"] is False
    assert result["gates"]["retention"]["status"] == OPEN


def test_strong_but_still_due_review_does_not_false_pass_j4():
    result = _status(
        retention_outcome_audit={
            "review_attempt_count": 1,
            "still_due_count": 1,
            "strong_still_due_count": 1,
            "qualified_strong_outcome_count": 0,
        }
    )
    assert result["gates"]["retention"]["status"] == OPEN
    assert result["gates"]["retention"]["strong_still_due_count"] == 1


def test_explicit_zero_review_does_not_use_legacy_stable_or_timeline_as_false_pass():
    result = _status(
        retention_outcome_audit={"review_attempt_count": 0},
        state_counts={"stable": 5},
        transitions={
            "recheck_due_to_stable": 4,
            "recheck_due_to_repairing": 2,
        },
    )
    assert result["gates"]["retention"]["status"] == OPEN
    assert result["gates"]["retention"]["natural_retention_observed"] is False


def test_evidence_line_is_non_identifying_and_never_says_promotion_allowed_true():
    result = _status(retention_outcome_audit={"review_attempt_count": 0})
    result["user_id"] = "must-not-leak"
    result["token"] = "must-not-leak"
    line = build_phase11_promotion_gate_evidence_line(result)
    assert line.startswith("phase11_gate_status=decision:hold")
    assert "retention:open" in line
    assert "diversity:open" in line
    assert "promotion_allowed:false" in line
    assert "manual_review_required:true" in line
    assert "must-not-leak" not in line
    assert "user_id" not in line
    assert "token" not in line
