from datetime import datetime, timedelta, timezone

from field_evidence import build_field_evidence
from question_bank import get_category_small, get_question_tag


BASE = datetime(2026, 9, 2, tzinfo=timezone.utc)


def attempt(q, correct, confidence, minute, *, status="answered"):
    return {
        "user_id": "u",
        "question_id": q,
        "knowledge_node_id": get_question_tag(q)["knowledge_node_id"],
        "selected_answers": [] if status == "unknown" else ["A"],
        "answer_status": status,
        "is_correct": correct,
        "confidence": confidence,
        "answered_at": BASE + timedelta(minutes=minute),
        "event_key": f"e-{minute}",
        "attempt_position": 1,
    }


def field(report, q="Q1"):
    field_id = get_category_small(q)
    return next(item for item in report["fields"] if item["field_id"] == field_id)


def test_unknown_counts_as_raw_exposure_but_not_evaluable_answer():
    item = field(build_field_evidence([
        attempt("Q1", False, None, 1, status="unknown"),
    ]))
    assert item["question_answer_count"] == 1
    assert item["unknown_answer_count"] == 1
    assert item["question_correct_count"] == 0
    assert item["question_accuracy"] == 0.0
    assert item["evaluable_answer_count"] == 0
    assert item["evaluable_correct_count"] == 0
    assert item["evaluable_accuracy"] is None


def test_evaluable_accuracy_excludes_unknown_from_denominator():
    item = field(build_field_evidence([
        attempt("Q1", True, 1, 1),
        attempt("Q1", False, 2, 2),
        attempt("Q1", False, None, 3, status="unknown"),
    ]))
    assert item["question_answer_count"] == 3
    assert item["question_correct_count"] == 1
    assert item["question_accuracy"] == 1 / 3
    assert item["unknown_answer_count"] == 1
    assert item["evaluable_answer_count"] == 2
    assert item["evaluable_correct_count"] == 1
    assert item["evaluable_accuracy"] == 0.5


def test_extra_unknown_does_not_change_evaluable_accuracy():
    baseline = field(build_field_evidence([
        attempt("Q1", True, 1, 1),
        attempt("Q1", False, 2, 2),
    ]))
    with_unknown = field(build_field_evidence([
        attempt("Q1", True, 1, 1),
        attempt("Q1", False, 2, 2),
        attempt("Q1", False, None, 3, status="unknown"),
        attempt("Q1", False, None, 4, status="unknown"),
    ]))
    assert baseline["evaluable_answer_count"] == 2
    assert with_unknown["evaluable_answer_count"] == 2
    assert baseline["evaluable_accuracy"] == with_unknown["evaluable_accuracy"] == 0.5
    assert baseline["question_accuracy"] != with_unknown["question_accuracy"]


def test_existing_raw_accuracy_semantics_remain_compatible():
    item = field(build_field_evidence([
        attempt("Q1", True, 1, 1),
        attempt("Q1", False, None, 2, status="unknown"),
    ]))
    assert item["question_answer_count"] == 2
    assert item["question_correct_count"] == 1
    assert item["question_accuracy"] == 0.5
    assert item["evaluable_answer_count"] == 1
    assert item["evaluable_correct_count"] == 1
    assert item["evaluable_accuracy"] == 1.0


def test_empty_field_has_zero_evaluable_counts_and_no_evaluable_accuracy():
    empty_report = build_field_evidence([])
    empty_field = empty_report["fields"][0]
    assert empty_field["evaluable_answer_count"] == 0
    assert empty_field["evaluable_correct_count"] == 0
    assert empty_field["evaluable_accuracy"] is None
