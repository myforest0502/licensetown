from datetime import datetime, timedelta, timezone

from companion_record import build_companion_record


NOW = datetime(2026, 9, 9, tzinfo=timezone.utc)


def attempt(question, correct, confidence, minute, *, status="answered", node="KN0268"):
    return {
        "id": minute + 1,
        "event_key": f"event-{minute}",
        "user_id": "learner",
        "question_id": question,
        "knowledge_node_id": node,
        "is_correct": correct,
        "confidence": confidence,
        "answer_status": status,
        "attempted_at": NOW + timedelta(minutes=minute),
        "attempt_position": 1,
    }


def wrong_pattern(*history):
    record = build_companion_record(history)
    return record["episodes"][0]["wrong_pattern"]


def test_confident_wrong_is_explicit_observable_pattern():
    pattern = wrong_pattern(attempt("Q269", False, 1, 1))
    assert pattern["code"] == "confident_wrong"
    assert pattern["basis"] == "wrong_with_confidence_1"


def test_unknown_answer_is_not_guessed_as_knowledge_failure():
    pattern = wrong_pattern(attempt("Q269", False, None, 1, status="unknown"))
    assert pattern["code"] == "unknown_answer"
    assert pattern["basis"] == "answer_status_unknown"


def test_repeated_cross_question_wrong_is_distinguished():
    pattern = wrong_pattern(
        attempt("Q269", False, 2, 1),
        attempt("Q361", False, 2, 2),
    )
    assert pattern["code"] == "repeated_cross_question_wrong"


def test_wrong_after_repair_is_retention_regression():
    record = build_companion_record([
        attempt("Q269", False, 2, 1),
        attempt("Q361", True, 1, 2),
        attempt("Q269", False, 1, 3),
    ])
    episode = record["episodes"][0]
    assert episode["wrong_pattern"]["code"] == "retention_regression"
    assert episode["events"][-1]["event"] == "regression_detected"


def test_wrong_pattern_contract_does_not_claim_hidden_psychology():
    record = build_companion_record([attempt("Q269", False, 2, 1)])
    assert record["wrong_pattern_semantics"] == "observable_evidence_not_psychological_diagnosis"
