from datetime import datetime, timedelta, timezone

import knowledge_node_state_transition as transition
import phase11_retention_outcome_audit as audit
from knowledge_node_repair_evidence import (
    DIFFERENT_QUESTION_STRONG,
    DIFFERENT_QUESTION_WEAK,
    SAME_QUESTION,
)


BASE = datetime(2026, 9, 1, tzinfo=timezone.utc)


def attempt(q, *, correct, confidence, day, minute=0, unknown=False):
    return {
        "id": day * 100 + minute + 1,
        "event_key": f"e-{day}-{minute}-{q}",
        "user_id": "learner",
        "question_id": q,
        "knowledge_node_id": "KN0001",
        "selected_answers": [] if unknown else ["1"],
        "answer_status": "unknown" if unknown else "answered",
        "is_correct": correct,
        "confidence": confidence,
        "answered_at": BASE + timedelta(days=day, minutes=minute),
        "attempt_position": 1,
    }


def classifier(strong_pairs):
    strong_pairs = set(strong_pairs)

    def classify(old, new):
        if old == new:
            return SAME_QUESTION
        return DIFFERENT_QUESTION_STRONG if (old, new) in strong_pairs else DIFFERENT_QUESTION_WEAK

    return classify


def install_classifier(monkeypatch, strong_pairs):
    classify = classifier(strong_pairs)
    monkeypatch.setattr(transition, "classify_repair_confirmation", classify)
    monkeypatch.setattr(audit, "classify_repair_confirmation", classify)


def repaired_history():
    return [
        attempt("Q1", correct=False, confidence=2, day=0),
        attempt("Q2", correct=True, confidence=1, day=1),
    ]


def test_captures_hidden_repaired_to_due_to_stable_review(monkeypatch):
    install_classifier(monkeypatch, {("Q1", "Q2"), ("Q2", "Q3")})
    history = repaired_history() + [attempt("Q3", correct=True, confidence=1, day=8)]

    # Prefix timeline jumps directly repaired -> stable; the audit must still
    # recover the due-before-attempt retention event.
    assert [item["state"] for item in transition.derive_state_timeline(history)] == [
        "repairing", "repaired", "stable"
    ]
    result = audit.build_retention_outcome_audit(history)
    assert result["review_attempt_count"] == 1
    assert result["stable_count"] == 1
    assert result["strong_evidence_count"] == 1
    review = result["reviews"][0]
    assert review["outcome"] == "stable"
    assert review["retention_reference_question_id"] == "Q2"
    assert review["question_id"] == "Q3"
    assert review["hours_after_due"] == 0.0


def test_due_wrong_is_recorded_as_repairing(monkeypatch):
    install_classifier(monkeypatch, {("Q1", "Q2")})
    result = audit.build_retention_outcome_audit(
        repaired_history() + [attempt("Q3", correct=False, confidence=2, day=8)]
    )
    assert result["review_attempt_count"] == 1
    assert result["repairing_count"] == 1
    assert result["reviews"][0]["outcome"] == "repairing"


def test_due_weak_correct_remains_due(monkeypatch):
    install_classifier(monkeypatch, {("Q1", "Q2")})
    result = audit.build_retention_outcome_audit(
        repaired_history() + [attempt("Q3", correct=True, confidence=1, day=8)]
    )
    assert result["review_attempt_count"] == 1
    assert result["still_due_count"] == 1
    assert result["weak_evidence_count"] == 1


def test_before_due_attempt_is_not_retention_review(monkeypatch):
    install_classifier(monkeypatch, {("Q1", "Q2"), ("Q2", "Q3")})
    result = audit.build_retention_outcome_audit(
        repaired_history() + [attempt("Q3", correct=True, confidence=1, day=7)]
    )
    assert result["review_attempt_count"] == 0


def test_evidence_line_excludes_identity_and_question_ids(monkeypatch):
    install_classifier(monkeypatch, {("Q1", "Q2"), ("Q2", "Q3")})
    result = audit.build_retention_outcome_audit(
        repaired_history() + [attempt("Q3", correct=True, confidence=1, day=8)]
    )
    result["user_id"] = "must-not-leak"
    line = audit.build_retention_outcome_evidence_line(result)
    assert line.startswith("retention_outcomes=reviews:1,stable:1")
    assert "must-not-leak" not in line
    assert "learner" not in line
    assert "Q1" not in line and "Q2" not in line and "Q3" not in line
