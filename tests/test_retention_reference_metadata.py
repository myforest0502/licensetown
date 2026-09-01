from datetime import datetime, timedelta, timezone

import knowledge_node_state_transition as transition
from knowledge_node_repair_evidence import DIFFERENT_QUESTION_STRONG, DIFFERENT_QUESTION_WEAK


BASE = datetime(2026, 9, 1, tzinfo=timezone.utc)


def attempt(q, *, correct, confidence, when, unknown=False):
    return {
        "id": int(when.total_seconds()) + 1,
        "event_key": f"e-{q}-{when.total_seconds()}",
        "user_id": "u",
        "question_id": q,
        "knowledge_node_id": "KN0268",
        "selected_answers": [] if unknown else ["A"],
        "answer_status": "unknown" if unknown else "answered",
        "is_correct": correct,
        "confidence": confidence,
        "answered_at": BASE + when,
        "attempt_position": 1,
    }


def classifier(strong_pairs):
    strong_pairs = set(strong_pairs)

    def classify(old, new):
        return DIFFERENT_QUESTION_STRONG if (old, new) in strong_pairs else DIFFERENT_QUESTION_WEAK

    return classify


def test_unseen_has_no_retention_reference():
    result = transition.derive_knowledge_node_state([], canonical_node_id="KN0268")
    assert result["state"] == "unseen"
    assert result["retention_reference_question_id"] is None


def test_repaired_state_exposes_strong_confirmation_as_retention_reference(monkeypatch):
    monkeypatch.setattr(
        transition,
        "classify_repair_confirmation",
        classifier({("Q1", "Q2")}),
    )
    result = transition.derive_knowledge_node_state([
        attempt("Q1", correct=False, confidence=2, when=timedelta()),
        attempt("Q2", correct=True, confidence=1, when=timedelta(minutes=1)),
    ])
    assert result["state"] == "repaired"
    assert result["retention_reference_question_id"] == "Q2"


def test_time_only_recheck_due_preserves_retention_reference(monkeypatch):
    monkeypatch.setattr(
        transition,
        "classify_repair_confirmation",
        classifier({("Q1", "Q2")}),
    )
    result = transition.derive_knowledge_node_state(
        [
            attempt("Q1", correct=False, confidence=2, when=timedelta()),
            attempt("Q2", correct=True, confidence=1, when=timedelta(minutes=1)),
        ],
        as_of=BASE + timedelta(days=8),
    )
    assert result["state"] == "recheck_due"
    assert result["retention_reference_question_id"] == "Q2"


def test_successful_retention_check_updates_reference_to_new_question(monkeypatch):
    monkeypatch.setattr(
        transition,
        "classify_repair_confirmation",
        classifier({("Q1", "Q2"), ("Q2", "Q3")}),
    )
    result = transition.derive_knowledge_node_state([
        attempt("Q1", correct=False, confidence=2, when=timedelta()),
        attempt("Q2", correct=True, confidence=1, when=timedelta(minutes=1)),
        attempt("Q3", correct=True, confidence=1, when=timedelta(days=8)),
    ])
    assert result["state"] == "stable"
    assert result["retention_reference_question_id"] == "Q3"


def test_weak_due_correct_keeps_existing_retention_reference(monkeypatch):
    monkeypatch.setattr(
        transition,
        "classify_repair_confirmation",
        classifier({("Q1", "Q2")}),
    )
    result = transition.derive_knowledge_node_state([
        attempt("Q1", correct=False, confidence=2, when=timedelta()),
        attempt("Q2", correct=True, confidence=1, when=timedelta(minutes=1)),
        attempt("QWEAK", correct=True, confidence=1, when=timedelta(days=8)),
    ])
    assert result["state"] == "recheck_due"
    assert result["retention_reference_question_id"] == "Q2"


def test_failed_due_wrong_clears_retention_reference(monkeypatch):
    monkeypatch.setattr(
        transition,
        "classify_repair_confirmation",
        classifier({("Q1", "Q2")}),
    )
    result = transition.derive_knowledge_node_state([
        attempt("Q1", correct=False, confidence=2, when=timedelta()),
        attempt("Q2", correct=True, confidence=1, when=timedelta(minutes=1)),
        attempt("Q3", correct=False, confidence=2, when=timedelta(days=8)),
    ])
    assert result["state"] == "repairing"
    assert result["retention_reference_question_id"] is None


def test_failed_due_unknown_clears_retention_reference(monkeypatch):
    monkeypatch.setattr(
        transition,
        "classify_repair_confirmation",
        classifier({("Q1", "Q2")}),
    )
    result = transition.derive_knowledge_node_state([
        attempt("Q1", correct=False, confidence=2, when=timedelta()),
        attempt("Q2", correct=True, confidence=1, when=timedelta(minutes=1)),
        attempt("Q3", correct=False, confidence=None, when=timedelta(days=8), unknown=True),
    ])
    assert result["state"] == "repairing"
    assert result["retention_reference_question_id"] is None
