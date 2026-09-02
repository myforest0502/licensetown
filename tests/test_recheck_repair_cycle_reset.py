from datetime import datetime, timedelta, timezone

import knowledge_node_state_transition as transition
from knowledge_node_repair_cycle import current_repair_cycle
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
    normalized = {tuple(pair) for pair in strong_pairs}

    def classify(old, new):
        return (
            DIFFERENT_QUESTION_STRONG
            if (old, new) in normalized
            else DIFFERENT_QUESTION_WEAK
        )

    return classify


def repaired_history():
    return [
        attempt("QOLD", correct=False, confidence=2, when=timedelta()),
        attempt("QREPAIR", correct=True, confidence=1, when=timedelta(minutes=1)),
    ]


def test_failed_due_wrong_resets_old_repair_reference(monkeypatch):
    monkeypatch.setattr(
        transition,
        "classify_repair_confirmation",
        classifier({("QOLD", "QREPAIR"), ("QOLD", "QCANDIDATE")}),
    )
    failed = attempt("QNEW", correct=False, confidence=2, when=timedelta(days=8))
    candidate = attempt(
        "QCANDIDATE", correct=True, confidence=1, when=timedelta(days=8, minutes=1)
    )
    history = repaired_history() + [failed, candidate]
    result = transition.derive_knowledge_node_state(history)
    assert result["state"] == "repairing"
    assert [item["question_id"] for item in current_repair_cycle(history)] == [
        "QNEW", "QCANDIDATE"
    ]


def test_candidate_strong_against_new_failed_recheck_can_repair(monkeypatch):
    monkeypatch.setattr(
        transition,
        "classify_repair_confirmation",
        classifier({("QOLD", "QREPAIR"), ("QNEW", "QCANDIDATE")}),
    )
    failed = attempt("QNEW", correct=False, confidence=2, when=timedelta(days=8))
    candidate = attempt(
        "QCANDIDATE", correct=True, confidence=1, when=timedelta(days=8, minutes=1)
    )
    result = transition.derive_knowledge_node_state(repaired_history() + [failed, candidate])
    assert result["state"] == "repaired"


def test_failed_due_unknown_starts_new_repair_cycle(monkeypatch):
    monkeypatch.setattr(
        transition,
        "classify_repair_confirmation",
        classifier({("QOLD", "QREPAIR")}),
    )
    unknown = attempt(
        "QUNKNOWN", correct=False, confidence=None, when=timedelta(days=8), unknown=True
    )
    history = repaired_history() + [unknown]
    result = transition.derive_knowledge_node_state(history)
    assert result["state"] == "repairing"
    assert [item["question_id"] for item in current_repair_cycle(history)] == ["QUNKNOWN"]


def test_successful_due_recheck_still_goes_stable(monkeypatch):
    monkeypatch.setattr(
        transition,
        "classify_repair_confirmation",
        classifier({("QOLD", "QREPAIR"), ("QREPAIR", "QRETENTION")}),
    )
    retention = attempt(
        "QRETENTION", correct=True, confidence=1, when=timedelta(days=8)
    )
    result = transition.derive_knowledge_node_state(repaired_history() + [retention])
    assert result["state"] == "stable"


def test_same_or_weak_due_correct_remains_due(monkeypatch):
    monkeypatch.setattr(
        transition,
        "classify_repair_confirmation",
        classifier({("QOLD", "QREPAIR")}),
    )
    retention = attempt(
        "QWEAK", correct=True, confidence=1, when=timedelta(days=8)
    )
    result = transition.derive_knowledge_node_state(repaired_history() + [retention])
    assert result["state"] == "recheck_due"
