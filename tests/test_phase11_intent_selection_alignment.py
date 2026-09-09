from datetime import datetime, timedelta, timezone

import knowledge_node_state_transition as transition
import phase11_intent_selection_alignment as audit
from knowledge_node_repair_evidence import (
    DIFFERENT_QUESTION_STRONG,
    DIFFERENT_QUESTION_WEAK,
    SAME_QUESTION,
)


BASE = datetime(2026, 9, 1, tzinfo=timezone.utc)


def attempt(q, *, correct, confidence, day, event, position=1):
    return {
        "id": day * 100 + position,
        "event_key": event,
        "user_id": "learner",
        "question_id": q,
        "knowledge_node_id": "KN0001",
        "selected_answers": ["1"],
        "answer_status": "answered",
        "is_correct": correct,
        "confidence": confidence,
        "answered_at": BASE + timedelta(days=day, minutes=position),
        "attempt_position": position,
    }


def event(event_key, q, *, reason="recheck_due", repair_quality=None, recent=False, bypass=False):
    return {
        "event_key": event_key,
        "question_results": [{
            "question_id": q,
            "selection_reason": reason,
            "selection_group": "checking",
            "selection_score": 700,
            "repair_evidence_quality": repair_quality,
            "recent_question_repeat": recent,
            "recent_cooldown_bypassed": bypass,
        }],
    }


def classifier(strong_pairs):
    strong_pairs = set(strong_pairs)

    def classify(old, new):
        if old == new:
            return SAME_QUESTION
        return DIFFERENT_QUESTION_STRONG if (old, new) in strong_pairs else DIFFERENT_QUESTION_WEAK

    return classify


def install(monkeypatch, strong_pairs):
    classify = classifier(strong_pairs)
    monkeypatch.setattr(transition, "classify_repair_confirmation", classify)
    monkeypatch.setattr(audit, "classify_repair_confirmation", classify)


def repaired_history():
    return [
        attempt("Q1", correct=False, confidence=2, day=0, event="old:1"),
        attempt("Q2", correct=True, confidence=1, day=1, event="repair:1"),
    ]


def test_recheck_exact_q_strong_vs_retention_reference_is_aligned(monkeypatch):
    install(monkeypatch, {("Q1", "Q2"), ("Q2", "Q3")})
    history = repaired_history() + [
        attempt("Q3", correct=True, confidence=1, day=8, event="session:1")
    ]
    result = audit.build_phase11_intent_selection_alignment(
        history,
        [event("session:1", "Q3", repair_quality=DIFFERENT_QUESTION_WEAK)],
    )
    assert result["saved_recheck_selection_count"] == 1
    assert result["evaluable_recheck_selection_count"] == 1
    assert result["aligned_recheck_selection_count"] == 1
    assert result["misaligned_recheck_selection_count"] == 0
    assert result["strong_retention_q_count"] == 1
    assert result["alignment_status"] == "pass"
    # Important J5 fact: saved generic repair quality may disagree with the
    # retention-reference-specific quality; retention reference is authoritative here.
    assert result["details"][0]["saved_repair_evidence_quality"] == DIFFERENT_QUESTION_WEAK
    assert result["details"][0]["retention_evidence_quality"] == DIFFERENT_QUESTION_STRONG


def test_recheck_exact_q_weak_vs_retention_reference_is_misaligned(monkeypatch):
    install(monkeypatch, {("Q1", "Q2")})
    history = repaired_history() + [
        attempt("Q3", correct=True, confidence=1, day=8, event="session:1")
    ]
    result = audit.build_phase11_intent_selection_alignment(
        history,
        [event("session:1", "Q3", repair_quality=DIFFERENT_QUESTION_STRONG)],
    )
    assert result["evaluable_recheck_selection_count"] == 1
    assert result["aligned_recheck_selection_count"] == 0
    assert result["misaligned_recheck_selection_count"] == 1
    assert result["weak_retention_q_count"] == 1
    assert result["alignment_status"] == "blocked"


def test_recheck_same_reference_question_is_misaligned(monkeypatch):
    install(monkeypatch, {("Q1", "Q2")})
    history = repaired_history() + [
        attempt("Q2", correct=True, confidence=1, day=8, event="session:1")
    ]
    result = audit.build_phase11_intent_selection_alignment(
        history,
        [event("session:1", "Q2", recent=True, bypass=True)],
    )
    assert result["same_question_retention_q_count"] == 1
    assert result["misaligned_recheck_selection_count"] == 1
    assert result["recent_repeat_recheck_count"] == 1
    assert result["cooldown_bypass_recheck_count"] == 1
    assert result["alignment_status"] == "blocked"


def test_saved_recheck_is_open_when_answer_time_state_is_not_due(monkeypatch):
    install(monkeypatch, {("Q1", "Q2"), ("Q2", "Q3")})
    # Repair is confirmed on day 1; day 3 is still before the day-3 checkpoint.
    history = repaired_history() + [
        attempt("Q3", correct=True, confidence=1, day=3, event="session:1")
    ]
    result = audit.build_phase11_intent_selection_alignment(
        history,
        [event("session:1", "Q3")],
    )
    assert result["saved_recheck_selection_count"] == 1
    assert result["evaluable_recheck_selection_count"] == 0
    assert result["not_evaluable_recheck_selection_count"] == 1
    assert result["alignment_status"] == "open"


def test_non_recheck_saved_rows_are_not_claimed_as_j5_evidence(monkeypatch):
    install(monkeypatch, {("Q1", "Q2"), ("Q2", "Q3")})
    history = repaired_history() + [
        attempt("Q3", correct=True, confidence=1, day=8, event="session:1")
    ]
    result = audit.build_phase11_intent_selection_alignment(
        history,
        [event("session:1", "Q3", reason="checking")],
    )
    assert result["saved_recheck_selection_count"] == 0
    assert result["alignment_status"] == "open"


def test_evidence_line_is_aggregate_and_non_identifying(monkeypatch):
    install(monkeypatch, {("Q1", "Q2"), ("Q2", "Q3")})
    history = repaired_history() + [
        attempt("Q3", correct=True, confidence=1, day=8, event="session:1")
    ]
    result = audit.build_phase11_intent_selection_alignment(
        history,
        [event("session:1", "Q3")],
    )
    result["user_id"] = "must-not-leak"
    line = audit.build_intent_selection_alignment_evidence_line(result)
    assert line.startswith("intent_selection_alignment=status:pass,saved_recheck:1")
    assert "must-not-leak" not in line
    assert "learner" not in line
    assert "Q2" not in line and "Q3" not in line