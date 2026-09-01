from datetime import datetime, timedelta, timezone

import knowledge_node_state_transition as transition
from knowledge_node_repair_evidence import DIFFERENT_QUESTION_STRONG, DIFFERENT_QUESTION_WEAK
from knowledge_node_weakness_evidence import (
    CROSS_QUESTION_CONFIDENT_WRONG,
    CROSS_QUESTION_WRONG,
    NO_WRONG_EVIDENCE,
    SINGLE_WRONG,
)
from phase11_active_weakness import build_active_repair_weakness


BASE = datetime(2026, 9, 1, tzinfo=timezone.utc)


def attempt(q, *, correct, confidence, minute=0, days=0, unknown=False):
    return {
        "id": days * 1000 + minute + 1,
        "event_key": f"e-{q}-{days}-{minute}",
        "user_id": "u",
        "question_id": q,
        "knowledge_node_id": "KN0268",
        "selected_answers": [] if unknown else ["A"],
        "answer_status": "unknown" if unknown else "answered",
        "is_correct": correct,
        "confidence": confidence,
        "answered_at": BASE + timedelta(days=days, minutes=minute),
        "attempt_position": 1,
    }


def classifier(strong_pairs):
    strong_pairs = set(strong_pairs)

    def classify(old, new):
        return DIFFERENT_QUESTION_STRONG if (old, new) in strong_pairs else DIFFERENT_QUESTION_WEAK

    return classify


def test_completed_repair_has_no_active_weakness(monkeypatch):
    monkeypatch.setattr(
        transition,
        "classify_repair_confirmation",
        classifier({("Q1", "Q2")}),
    )
    attempts = [
        attempt("Q1", correct=False, confidence=2),
        attempt("Q2", correct=True, confidence=1, minute=1),
    ]
    assert build_active_repair_weakness(attempts) == {}


def test_unknown_only_current_cycle_is_unresolved_but_not_confirmed_weakness():
    facts = build_active_repair_weakness([
        attempt("Q1", correct=False, confidence=None, unknown=True),
    ])["KN0268"]
    assert facts["active_repair_cycle_attempt_count"] == 1
    assert facts["active_unknown_attempt_count"] == 1
    assert facts["active_evaluable_wrong_attempt_count"] == 0
    assert facts["active_weakness_evidence_level"] == NO_WRONG_EVIDENCE


def test_one_current_cycle_wrong_is_single_wrong():
    facts = build_active_repair_weakness([
        attempt("Q1", correct=False, confidence=2),
    ])["KN0268"]
    assert facts["active_evaluable_wrong_question_count"] == 1
    assert facts["active_weakness_evidence_level"] == SINGLE_WRONG


def test_two_current_cycle_wrong_questions_are_cross_question_wrong():
    facts = build_active_repair_weakness([
        attempt("Q1", correct=False, confidence=2),
        attempt("Q2", correct=False, confidence=3, minute=1),
    ])["KN0268"]
    assert facts["active_evaluable_wrong_question_count"] == 2
    assert facts["active_weakness_evidence_level"] == CROSS_QUESTION_WRONG


def test_current_cycle_confident_cross_wrong_is_confident(monkeypatch):
    facts = build_active_repair_weakness([
        attempt("Q1", correct=False, confidence=1),
        attempt("Q2", correct=False, confidence=2, minute=1),
    ])["KN0268"]
    assert facts["active_has_confident_wrong"] is True
    assert facts["active_confident_wrong_count"] == 1
    assert facts["active_weakness_evidence_level"] == CROSS_QUESTION_CONFIDENT_WRONG


def test_old_cross_wrong_does_not_leak_after_completed_repair_and_new_single_wrong(monkeypatch):
    monkeypatch.setattr(
        transition,
        "classify_repair_confirmation",
        classifier({("Q1", "Q3"), ("Q2", "Q3")}),
    )
    attempts = [
        attempt("Q1", correct=False, confidence=2),
        attempt("Q2", correct=False, confidence=1, minute=1),
        attempt("Q3", correct=True, confidence=1, minute=2),
        attempt("Q4", correct=False, confidence=2, minute=3),
    ]
    facts = build_active_repair_weakness(attempts)["KN0268"]
    assert facts["active_evaluable_wrong_question_count"] == 1
    assert facts["active_has_confident_wrong"] is False
    assert facts["active_weakness_evidence_level"] == SINGLE_WRONG


def test_old_cross_wrong_does_not_revive_from_new_unknown(monkeypatch):
    monkeypatch.setattr(
        transition,
        "classify_repair_confirmation",
        classifier({("Q1", "Q3"), ("Q2", "Q3")}),
    )
    attempts = [
        attempt("Q1", correct=False, confidence=2),
        attempt("Q2", correct=False, confidence=1, minute=1),
        attempt("Q3", correct=True, confidence=1, minute=2),
        attempt("Q4", correct=False, confidence=None, minute=3, unknown=True),
    ]
    facts = build_active_repair_weakness(attempts)["KN0268"]
    assert facts["active_evaluable_wrong_attempt_count"] == 0
    assert facts["active_has_confident_wrong"] is False
    assert facts["active_weakness_evidence_level"] == NO_WRONG_EVIDENCE


def test_failed_due_recheck_uses_only_new_cycle(monkeypatch):
    monkeypatch.setattr(
        transition,
        "classify_repair_confirmation",
        classifier({("Q1", "Q2")}),
    )
    attempts = [
        attempt("Q1", correct=False, confidence=1),
        attempt("Q2", correct=True, confidence=1, minute=1),
        attempt("Q3", correct=False, confidence=2, days=8),
    ]
    facts = build_active_repair_weakness(attempts)["KN0268"]
    assert facts["active_evaluable_wrong_question_count"] == 1
    assert facts["active_has_confident_wrong"] is False
    assert facts["active_weakness_evidence_level"] == SINGLE_WRONG
