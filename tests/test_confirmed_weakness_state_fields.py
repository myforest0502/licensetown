from datetime import datetime, timedelta, timezone

from knowledge_node_state_transition import derive_knowledge_node_state

NOW = datetime(2026, 9, 1, tzinfo=timezone.utc)


def attempt(q, correct, confidence=2, *, minute=0, status="answered"):
    return {
        "user_id": "u",
        "question_id": q,
        "knowledge_node_id": "KN0001",
        "is_correct": correct,
        "confidence": confidence,
        "answer_status": status,
        "answered_at": NOW + timedelta(minutes=minute),
        "event_key": f"e-{minute}",
        "attempt_position": 1,
    }


def test_unknown_only_is_repair_trigger_but_not_confirmed_weakness():
    state = derive_knowledge_node_state([
        attempt("Q1", False, None, status="unknown"),
    ])
    assert state["state"] == "repairing"
    assert state["unknown_attempt_count"] == 1
    assert state["evaluable_wrong_question_count"] == 0
    assert state["confirmed_weakness_evidence_level"] == "NO_WRONG_EVIDENCE"


def test_two_unknowns_do_not_create_confirmed_repeated_weakness():
    state = derive_knowledge_node_state([
        attempt("Q1", False, None, minute=1, status="unknown"),
        attempt("Q2", False, None, minute=2, status="unknown"),
    ])
    assert state["state"] == "repairing"
    assert state["unknown_attempt_count"] == 2
    assert state["evaluable_wrong_question_count"] == 0
    assert state["confirmed_weakness_evidence_level"] == "NO_WRONG_EVIDENCE"


def test_real_wrong_plus_unknown_counts_one_evaluable_wrong_question():
    state = derive_knowledge_node_state([
        attempt("Q1", False, 2, minute=1),
        attempt("Q2", False, None, minute=2, status="unknown"),
    ])
    assert state["state"] == "repairing"
    assert state["unknown_attempt_count"] == 1
    assert state["evaluable_wrong_question_count"] == 1
    assert state["confirmed_weakness_evidence_level"] == "SINGLE_WRONG"


def test_real_cross_question_wrong_remains_confirmed():
    state = derive_knowledge_node_state([
        attempt("Q1", False, 2, minute=1),
        attempt("Q2", False, 2, minute=2),
    ])
    assert state["unknown_attempt_count"] == 0
    assert state["evaluable_wrong_question_count"] == 2
    assert state["confirmed_weakness_evidence_level"] == "CROSS_QUESTION_WRONG"


def test_legacy_evidence_fields_are_preserved_for_unknown_compatibility():
    state = derive_knowledge_node_state([
        attempt("Q1", False, None, status="unknown"),
    ])
    assert "evidence_level" in state
    assert "wrong_question_count" in state
    assert state["wrong_question_count"] >= state["evaluable_wrong_question_count"]
