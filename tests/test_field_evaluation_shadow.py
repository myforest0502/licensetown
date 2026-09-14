from field_evaluation_shadow import evaluate_field, required_node_spread


def _evidence(**overrides):
    row = {
        "field_id": 1,
        "field_name": "test",
        "total_question_count": 200,
        "evaluable_answer_count": 60,
        "evaluable_accuracy": 0.75,
        "repeated_weakness_evidence_count": 0,
        "different_question_repair_confirmation_count": 0,
    }
    row.update(overrides)
    return row


def _progress(**overrides):
    row = {
        "field_id": 1,
        "field_name": "test",
        "total_canonical_nodes": 100,
        "touched_canonical_nodes": 40,
        "field_progress_score": 0.40,
        "state_counts": {
            "unseen": 60,
            "repairing": 5,
            "checking": 10,
            "recheck_due": 5,
            "repaired": 10,
            "stable": 10,
        },
    }
    row.update(overrides)
    return row


def test_node_spread_scales_with_field_supply_and_stays_attainable():
    assert required_node_spread(10) == 6
    assert required_node_spread(100) == 35
    assert required_node_spread(200) == 60
    assert required_node_spread(291) == 60


def test_under_sixty_answers_remains_assessing():
    result = evaluate_field(_evidence(evaluable_answer_count=59), _progress())
    assert result["field_state"] == "assessing"
    assert result["evidence_sufficient"] is False
    assert result["next_evaluation_answer_count"] == 60


def test_sixty_answers_without_node_spread_remains_assessing():
    result = evaluate_field(_evidence(), _progress(touched_canonical_nodes=20))
    assert result["field_state"] == "assessing"
    assert result["node_spread_met"] is False


def test_small_bank_never_declares_weak_or_strong_from_repeat_volume():
    weakish = evaluate_field(
        _evidence(total_question_count=29, evaluable_answer_count=119, evaluable_accuracy=0.55),
        _progress(total_canonical_nodes=15, touched_canonical_nodes=15,
                  state_counts={"repairing": 8, "checking": 4, "stable": 3},
                  field_progress_score=0.2),
    )
    assert weakish["field_state"] == "assessing"
    assert weakish["evidence_sufficient"] is False
    assert weakish["question_supply_sufficient"] is False
    assert "small_bank_supply_limited" in weakish["reasons"]

    strongish = evaluate_field(
        _evidence(total_question_count=58, evaluable_answer_count=72, evaluable_accuracy=0.95),
        _progress(total_canonical_nodes=40, touched_canonical_nodes=40,
                  state_counts={"checking": 2, "repaired": 8, "stable": 30},
                  field_progress_score=0.8),
    )
    assert strongish["field_state"] == "assessing"
    assert strongish["evidence_sufficient"] is False
    assert "small_bank_supply_limited" in strongish["reasons"]


def test_small_bank_safety_keeps_priority_without_ability_classification():
    result = evaluate_field(
        _evidence(total_question_count=29, evaluable_answer_count=119, evaluable_accuracy=0.95),
        _progress(total_canonical_nodes=15, touched_canonical_nodes=15,
                  state_counts={"checking": 5, "stable": 10},
                  field_progress_score=0.7),
        critical_safety_unresolved_count=1,
    )
    assert result["field_state"] == "assessing"
    assert result["strategy_priority_hint"] == "safety"
    assert "small_bank_supply_limited" in result["reasons"]


def test_weak_field_rechecks_every_thirty_questions():
    result = evaluate_field(
        _evidence(evaluable_answer_count=60, evaluable_accuracy=0.60),
        _progress(),
    )
    assert result["field_state"] == "weak"
    assert result["next_evaluation_answer_count"] == 90

    result = evaluate_field(
        _evidence(evaluable_answer_count=91, evaluable_accuracy=0.60),
        _progress(),
    )
    assert result["next_evaluation_answer_count"] == 120


def test_strong_requires_accuracy_and_resolved_node_evidence():
    result = evaluate_field(
        _evidence(evaluable_accuracy=0.85),
        _progress(
            touched_canonical_nodes=50,
            state_counts={
                "unseen": 50,
                "repairing": 2,
                "checking": 8,
                "recheck_due": 5,
                "repaired": 10,
                "stable": 25,
            },
        ),
    )
    assert result["field_state"] == "strong"


def test_safety_keeps_field_weak_even_with_high_accuracy():
    result = evaluate_field(
        _evidence(evaluable_accuracy=0.95),
        _progress(
            touched_canonical_nodes=50,
            state_counts={
                "unseen": 50,
                "repairing": 0,
                "checking": 0,
                "recheck_due": 5,
                "repaired": 10,
                "stable": 35,
            },
        ),
        critical_safety_unresolved_count=1,
    )
    assert result["field_state"] == "weak"
    assert result["strategy_priority_hint"] == "safety"


def test_recovery_is_not_raw_accuracy_only():
    result = evaluate_field(
        _evidence(evaluable_accuracy=0.90, different_question_repair_confirmation_count=2),
        _progress(
            touched_canonical_nodes=50,
            state_counts={
                "unseen": 50,
                "repairing": 2,
                "checking": 8,
                "recheck_due": 5,
                "repaired": 15,
                "stable": 20,
            },
        ),
    )
    assert result["recovery_level"] == "provisional_recovery"


def test_durable_recovery_requires_stability_and_no_active_repair():
    result = evaluate_field(
        _evidence(evaluable_accuracy=0.90, different_question_repair_confirmation_count=4),
        _progress(
            touched_canonical_nodes=50,
            state_counts={
                "unseen": 50,
                "repairing": 0,
                "checking": 5,
                "recheck_due": 5,
                "repaired": 10,
                "stable": 30,
            },
        ),
    )
    assert result["recovery_level"] == "durable_recovery"


def test_overconcentration_marks_strategy_change_without_erasing_weakness():
    result = evaluate_field(
        _evidence(evaluable_answer_count=150, evaluable_accuracy=0.60),
        _progress(field_progress_score=0.42),
        additional_blocks_completed=3,
        previous_progress_score=0.40,
    )
    assert result["field_state"] == "weak"
    assert result["strategy_change_candidate"] is True
    assert result["strategy_priority_hint"] == "strategy_change_candidate"
