"""Synthetic unit evidence is not Production acceptance or natural-use data."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys

import pytest

from field_progress import calculate_progress_from_state_counts
from field_learning_target_shadow import build_field_target, build_field_targets
from learning_strategy_shadow import build_learning_strategy


def rows(field_id=1, *, answers=60, accuracy=0.9, counts=None, supply=200, repeated=0, repairs=0, confident_wrong=0):
    counts = counts or {"stable": 100}
    total = sum(counts.values())
    current = calculate_progress_from_state_counts(counts, total)
    evidence = {
        "field_id": field_id, "total_question_count": supply,
        "total_canonical_node_count": total, "state_counts": dict(counts),
        "evaluable_answer_count": answers, "evaluable_accuracy": accuracy,
        "repeated_weakness_evidence_count": repeated,
        "different_question_repair_confirmation_count": repairs,
        "confident_wrong_count": confident_wrong,
    }
    progress = {
        "field_id": field_id, "total_canonical_nodes": total, **current,
        "field_progress_score": current["progress_score"], "state_counts": dict(counts),
    }
    return evidence, progress


def bundles(overrides=None):
    data = [rows(i) for i in range(1, 19)]
    for field_id, pair in (overrides or {}).items():
        data[field_id - 1] = pair
    return {"fields": [pair[0] for pair in data]}, {"fields": [pair[1] for pair in data]}


@pytest.mark.parametrize("answers", [0, 1, 59])
def test_insufficient_answers_never_become_weak_or_strong(answers):
    for accuracy in (0.1, 0.99):
        target = build_field_target(*rows(answers=answers, accuracy=accuracy))
        assert target["field_state"] == "assessing"
        result = build_learning_strategy(*bundles({1: rows(answers=answers, accuracy=accuracy)}))
        row = next(row for row in result["ranked_fields"] if row["field_id"] == 1)
        assert row["priority_components"]["weakness_score"] == 0
        assert row["learning_intent"] == "coverage"


def test_sixty_answers_still_require_canonical_spread():
    target = build_field_target(*rows(counts={"unseen": 80, "repairing": 20}, accuracy=0.1))
    assert target["field_state"] == "assessing"
    assert target["minimum_node_spread"] == 35


@pytest.mark.parametrize("answers,next_count", [(60, 90), (90, 120), (120, 150)])
def test_weak_reassessment_cadence_and_strategy_change(answers, next_count):
    pair = rows(answers=answers, accuracy=0.5, counts={"repairing": 40, "checking": 60})
    target = build_field_target(*pair)
    assert target["field_state"] == "weak"
    assert target["next_evaluation_answer_count"] == next_count
    capped = build_field_target(*pair, context={
        "additional_blocks_completed": 3,
        "previous_progress_score": target["current_progress_score"] - 0.01,
    })
    assert capped["strategy_change_candidate"]
    assert capped["remaining_additional_blocks"] == 0


def test_targets_distinguish_supply_from_classification_and_current_from_goal():
    small = build_field_target(*rows(14, answers=15, counts={"stable": 10}, supply=15))
    large = build_field_target(*rows(18, answers=15, counts={"unseen": 300}, supply=340))
    assert small["minimum_initial_questions"] == 15
    assert small["classification_question_floor"] == 60
    assert small["field_state"] == "assessing"
    assert large["minimum_initial_questions"] == 60
    assert large["minimum_node_spread"] == 60
    assert large["target_progress_score"] > small["target_progress_score"]
    assert small["current_progress_score"] == 1.0


def test_strong_recovery_and_high_weight_maintenance():
    target = build_field_target(*rows(18), context={"days_since_last_field_study": 8})
    assert target["field_state"] == "strong"
    assert target["recovery_level"] == "durable_recovery"
    assert target["maintenance_interval_days"] == 7
    assert target["maintenance_needed"]
    low = build_field_target(*rows(14), context={"days_since_last_field_study": 8})
    assert not low["maintenance_needed"]
    result = build_learning_strategy(*bundles(), context_by_field={18: {"days_since_last_field_study": 8}})
    assert result["recommended_field_id"] == 18
    assert result["learning_intent"] == "maintenance"


def test_provisional_recovery_stays_distinct():
    target = build_field_target(*rows(counts={"repairing": 5, "checking": 45, "repaired": 30, "stable": 20}, repairs=2))
    assert target["recovery_level"] == "provisional_recovery"


def test_incomplete_sixty_answer_first_pass_outranks_ordinary_assessed_field():
    result = build_learning_strategy(*bundles({
        5: rows(5, answers=59, accuracy=0.99, counts={"checking": 59, "unseen": 41}),
        18: rows(18, answers=60, accuracy=0.70, counts={"checking": 60, "unseen": 40}),
    }))
    assert result["recommended_field_id"] == 5
    assert result["learning_intent"] == "coverage"
    assert result["ranked_fields"][0]["initial_question_floor_incomplete"] is True
    assert "initial_question_floor_incomplete" in result["reason_codes"]


def test_confirmed_weakness_outranks_unfinished_coverage():
    result = build_learning_strategy(*bundles({
        14: rows(14, accuracy=0.64, counts={"stable": 80, "checking": 20}),
        18: rows(18, answers=0, accuracy=None, counts={"unseen": 100}),
    }))
    assert result["recommended_field_id"] == 14
    assert result["learning_intent"] == "repair"
    chosen = next(row for row in result["ranked_fields"] if row["field_id"] == 14)
    assert "low_accuracy" in chosen["target"]["evaluation"]["reasons"]


def test_safety_outranks_unfinished_first_pass():
    result = build_learning_strategy(*bundles({
        5: rows(5, answers=59, counts={"checking": 59, "unseen": 41}),
        14: rows(14, answers=60),
    }), context_by_field={14: {
        "critical_safety_unresolved_count": 1,
    }})
    assert result["recommended_field_id"] == 14
    assert result["learning_intent"] == "safety_review"
    assert "critical_safety" in result["reason_codes"]


def test_closest_field_to_sixty_is_finished_first():
    result = build_learning_strategy(*bundles({
        5: rows(5, answers=41, counts={"checking": 41, "unseen": 59}),
        12: rows(12, answers=55, counts={"checking": 55, "unseen": 45}),
        14: rows(14, answers=50, counts={"checking": 50, "unseen": 50}),
    }))
    assert result["recommended_field_id"] == 12
    incomplete = [row for row in result["ranked_fields"] if row["initial_question_floor_incomplete"]]
    assert [row["field_id"] for row in incomplete[:3]] == [12, 14, 5]


def test_repeated_weakness_before_sixty_routes_to_repair_before_plain_coverage():
    result = build_learning_strategy(*bundles({
        5: rows(
            5,
            answers=30,
            accuracy=0.70,
            counts={"repairing": 10, "checking": 20, "unseen": 70},
            repeated=1,
        ),
        12: rows(12, answers=59, counts={"checking": 59, "unseen": 41}),
    }))
    assert result["recommended_field_id"] == 5
    assert result["learning_intent"] == "repair"
    assert result["ranked_fields"][0]["early_repair_signal"] is True
    assert "early_repair_signal" in result["reason_codes"]
    assert "repeated_weakness" in result["reason_codes"]


def test_single_small_repair_signal_does_not_derail_first_pass_coverage():
    result = build_learning_strategy(*bundles({
        5: rows(
            5,
            answers=30,
            accuracy=0.70,
            counts={"repairing": 1, "checking": 29, "unseen": 70},
        ),
        12: rows(12, answers=59, counts={"checking": 59, "unseen": 41}),
    }))
    assert result["recommended_field_id"] == 12
    assert result["learning_intent"] == "coverage"


def test_confident_wrong_before_sixty_routes_to_repair():
    result = build_learning_strategy(*bundles({
        5: rows(
            5,
            answers=20,
            accuracy=0.80,
            counts={"repairing": 1, "checking": 19, "unseen": 80},
            confident_wrong=1,
        ),
        12: rows(12, answers=59, counts={"checking": 59, "unseen": 41}),
    }))
    assert result["recommended_field_id"] == 5
    assert result["learning_intent"] == "repair"
    assert result["ranked_fields"][0]["early_repair_signal"] is True
    assert "confident_wrong" in result["reason_codes"]


def test_concentration_penalty_and_additional_cap_keep_unresolved_field_visible():
    inputs = bundles({18: rows(18, accuracy=0.5)})
    plain = build_learning_strategy(*inputs)
    penalized = build_learning_strategy(*inputs, context_by_field={18: {"consecutive_field_blocks": 3}})
    score = lambda bundle: next(r["priority_score"] for r in bundle["ranked_fields"] if r["field_id"] == 18)
    assert score(penalized) < score(plain)
    capped = build_learning_strategy(*inputs, context_by_field={18: {"additional_blocks_completed": 3}})
    row = next(r for r in capped["ranked_fields"] if r["field_id"] == 18)
    assert row["learning_intent"] == "strategy_change"
    assert row["allocation_candidate"]
    assert "additional_block_cap_reached" in row["reason_codes"]


def test_retention_drop_and_explicit_time_are_explainable():
    pair = rows(18, counts={"recheck_due": 20, "stable": 80})
    far = build_learning_strategy(*bundles({18: pair}), context_by_field={18: {"previous_stable_ratio": 0.9}}, days_to_exam=180)
    near = build_learning_strategy(*bundles({18: pair}), context_by_field={18: {"previous_stable_ratio": 0.9}}, days_to_exam=10)
    assert near["priority_score"] > far["priority_score"]
    assert "stable_ratio_declined" in near["reason_codes"]
    assert "retention_due" in near["reason_codes"]
    assert near["temporal_adjustment"] is False


def test_inputs_unchanged_deterministic_and_all_components_bounded():
    inputs = bundles({1: rows(1, accuracy=0.4, repeated=3), 18: rows(18, answers=0, counts={"unseen": 100})})
    before = deepcopy(inputs)
    result = build_learning_strategy(*inputs)
    assert result == build_learning_strategy(*inputs)
    assert inputs == before
    assert result["shadow_only"] and not result["selection_authority"]
    assert result["recommended_question_count"] == 30
    assert len(result["ranked_fields"]) == 18
    assert not result["time_evidence_available"]
    for row in result["ranked_fields"]:
        assert all(0 <= value <= 1 for value in row["priority_components"].values())
        assert row["shadow_only"] and not row["selection_authority"]
        assert not row["target"]["safety_evidence_available"]
    assert "repeated_weakness" in next(r for r in result["ranked_fields"] if r["field_id"] == 1)["reason_codes"]
    json.dumps(result, allow_nan=False)


def test_empty_supply_or_fully_maintained_fields_defer():
    empty = {i: rows(i, answers=0, counts={"unseen": 0}, supply=0) for i in range(1, 19)}
    for inputs in (bundles(empty), bundles()):
        result = build_learning_strategy(*inputs)
        assert result["recommended_field_id"] is None
        assert result["recommended_question_count"] == 0


def test_missing_duplicate_or_mismatched_fields_are_rejected():
    evidence, progress = bundles()
    with pytest.raises(ValueError):
        build_field_targets({"fields": evidence["fields"][:-1]}, progress)
    with pytest.raises(ValueError):
        build_field_targets({"fields": evidence["fields"] + evidence["fields"][:1]}, progress)
    pair = rows()
    pair[1]["field_id"] = 2
    with pytest.raises(ValueError):
        build_field_target(*pair)


@pytest.mark.parametrize("value", [-1, float("nan"), float("inf"), 1.5])
def test_invalid_counts_rejected(value):
    pair = rows()
    pair[0]["evaluable_answer_count"] = value
    with pytest.raises(ValueError):
        build_field_target(*pair)


def test_formal_evidence_and_progress_bundles_are_accepted():
    # Existing truth adapters run only under CI's empty DATABASE_URL.
    from field_evidence import build_field_evidence
    from field_progress import build_field_progress

    evidence = build_field_evidence([])
    result = build_learning_strategy(evidence, build_field_progress(evidence))
    assert len(result["ranked_fields"]) == 18
    assert all(row["field_state"] == "unassessed" for row in result["ranked_fields"])
    assert result["recommended_field_id"] == 1
    assert result["ranked_fields"][0]["initial_question_floor_incomplete"] is True


def test_fresh_import_cannot_reach_runtime_db_network_or_write():
    script = r'''
import importlib.abc
import os
import sys
blocked = {"app", "wsgi", "database", "field_evidence", "question_bank",
           "adaptive_question_selector", "psycopg", "sqlite3", "openai", "linebot"}
class BlockImports(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split(".")[0] in blocked:
            raise AssertionError(fullname)
def audit(event, args):
    if event == "open":
        _, mode, flags = args
        if (mode and any(c in mode for c in "wax+")) or flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND):
            raise AssertionError("write")
    if event.startswith(("socket.", "subprocess.", "sqlite3.")):
        raise AssertionError(event)
sys.meta_path.insert(0, BlockImports())
sys.addaudithook(audit)
import exam_weight_shadow
import field_learning_target_shadow
import learning_strategy_shadow
assert not blocked.intersection(sys.modules)
'''
    result = subprocess.run([sys.executable, "-B", "-c", script],
                            cwd=Path(__file__).resolve().parents[1],
                            capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr
