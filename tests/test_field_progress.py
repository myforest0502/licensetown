from datetime import datetime, timedelta, timezone

import pytest

import knowledge_node_state_transition as transition
from field_evidence import build_field_evidence
from field_progress import (
    STATE_SCORES,
    build_field_progress,
    calculate_progress_from_state_counts,
)
from question_bank import get_category_small


BASE = datetime(2026, 8, 30, tzinfo=timezone.utc)


def counts(**values):
    return {state: values.get(state, 0) for state in STATE_SCORES}


def progress(**values):
    return calculate_progress_from_state_counts(counts(**values), 100)


@pytest.mark.parametrize(("state", "expected"), [
    ("stable", 0.40),
    ("checking", 0.30),
    ("repaired", 0.70),
    ("recheck_due", 0.60),
    ("repairing", 0.10),
])
def test_spec_cases_a_to_e(state, expected):
    values = {state: 40, "unseen": 60} if state == "stable" else {state: 100}
    assert progress(**values)["progress_score"] == pytest.approx(expected)


def test_spec_case_f_weighted_states():
    result = progress(stable=80, repaired=10, recheck_due=5, checking=3, repairing=2)
    assert result["progress_score"] == pytest.approx((80 + 7 + 3 + 0.9 + 0.2) / 100)


def test_spec_case_g_coverage_times_mastery():
    result = progress(stable=20, unseen=80)
    assert result["node_coverage"] == pytest.approx(0.20)
    assert result["state_mastery"] == pytest.approx(1.00)
    assert result["progress_score"] == pytest.approx(0.20)


def test_spec_case_h_mixed_touched_states():
    result = progress(repairing=70, checking=20, repaired=10)
    assert result["progress_score"] == pytest.approx(0.20)


def attempt(q, node, correct, confidence, day, *, user="u"):
    return {
        "user_id": user, "question_id": q, "knowledge_node_id": node,
        "is_correct": correct, "confidence": confidence,
        "selected_answers": ["1"], "answer_status": "answered",
        "answered_at": BASE + timedelta(days=day),
        "event_key": f"e-{day}-{q}", "attempt_position": 1,
    }


def node_score(report, node_id):
    return next(x for x in report["canonical_node_scores"] if x["canonical_node_id"] == node_id)


def test_cases_i_and_j_use_formal_retention_replay(monkeypatch):
    monkeypatch.setattr(transition, "classify_repair_confirmation", lambda old, new: (
        "same_question" if old == new else "different_question_strong"
    ))
    repaired_history = [
        attempt("Q269", "KN0268", False, 2, 0),
        attempt("Q361", "KN0268", True, 1, 1),
    ]
    repaired = build_field_progress(build_field_evidence(repaired_history, as_of=BASE + timedelta(days=7)))
    due = build_field_progress(build_field_evidence(repaired_history, as_of=BASE + timedelta(days=9)))
    assert node_score(repaired, "KN0268")["state_score"] == 0.70
    assert node_score(due, "KN0268")["state_score"] == 0.60

    retention = attempt("Q3", "KN0268", True, 1, 9)
    stable_history = repaired_history + [retention]
    stable = build_field_progress(build_field_evidence(stable_history))
    failed = build_field_progress(build_field_evidence(
        stable_history + [attempt("Q4", "KN0268", False, 2, 10)]
    ))
    assert node_score(stable, "KN0268")["state_score"] == 1.00
    assert node_score(failed, "KN0268")["state_score"] == 0.10


def test_aliases_are_unique_overall_and_multi_field_memberships_repeat_only_by_field():
    evidence = build_field_evidence([
        attempt("Q1225", "KN1210", False, 2, 0),
        attempt("Q1363", "KN0609", False, 2, 1),
    ])
    report = build_field_progress(evidence)
    assert report["overall"]["total_unique_canonical_nodes"] == 1508
    assert len(report["canonical_node_scores"]) == len({
        x["canonical_node_id"] for x in report["canonical_node_scores"]
    }) == 1508
    assert sum(x["total_canonical_nodes"] for x in report["fields"]) == report["canonical_node_membership_total"]
    assert report["canonical_node_membership_total"] > 1508
    memberships = [x for x in report["fields"] if "KN0609" in next(
        field["multi_field_canonical_node_ids"] for field in evidence["fields"] if field["field_id"] == x["field_id"]
    )]
    assert len(memberships) == 3
    assert sum(x["repairing_node_count"] for x in evidence["fields"] if "KN0609" in x["multi_field_canonical_node_ids"]) == 3


def test_shadow_keeps_accuracy_and_legacy_progress_separate():
    evidence = build_field_evidence([
        attempt("Q269", "KN0268", True, 1, 0),
    ])
    report = build_field_progress(evidence, legacy_overall_progress_percent=4)
    field = next(x for x in report["fields"] if x["field_id"] == get_category_small("Q269"))
    assert field["question_accuracy"] == 1.0
    assert field["field_progress_score"] < field["question_accuracy"]
    assert report["legacy_overall_progress_percent"] == 4
    assert report["overall"]["overall_progress_score"] < 0.01
    assert not report["retention_multiplier_applied"]
    assert not report["confidence_adjustment_applied"]
    assert not report["unknown_answer_adjustment_applied"]
    assert not report["repeated_weakness_adjustment_applied"]
    assert not report["written_evidence_adjustment_applied"]


def test_invalid_state_totals_are_rejected():
    with pytest.raises(ValueError):
        calculate_progress_from_state_counts(counts(stable=1), 100)
