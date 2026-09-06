from datetime import datetime, timedelta, timezone

from phase11_repair_effectiveness_facts import (
    build_repair_effectiveness_evidence_line,
    build_same_day_repair_effectiveness_facts,
)


NOW = datetime(2026, 9, 6, 12, 0, tzinfo=timezone.utc)


def _event(minutes, results):
    return {
        "answered_at": NOW - timedelta(minutes=minutes),
        "question_results": results,
    }


def _result(
    q,
    *,
    correct,
    confidence,
    quality,
    node="KN0001",
    source="adaptive_daily",
    group="repair",
    recent=False,
    bypass=False,
):
    return {
        "question_id": q,
        "knowledge_node_id": node,
        "is_correct": correct,
        "confidence": confidence,
        "answer_status": "answered",
        "learning_source": source,
        "selection_group": group,
        "repair_evidence_quality": quality,
        "recent_question_repeat": recent,
        "recent_cooldown_bypassed": bypass,
    }


def test_summarizes_strong_repair_outcomes_without_promoting_state():
    events = [
        _event(30, [
            _result("Q1", correct=True, confidence=1, quality="different_question_strong", node="KN1"),
            _result("Q2", correct=True, confidence=2, quality="different_question_strong", node="KN2"),
            _result("Q3", correct=False, confidence=2, quality="different_question_strong", node="KN3"),
            _result("Q4", correct=True, confidence=1, quality="different_question_weak", node="KN4"),
            _result("Q5", correct=False, confidence=1, quality="same_question", node="KN5"),
        ]),
        _event(20, [
            _result("Q1", correct=True, confidence=1, quality="different_question_strong", node="KN1"),
            _result("Q6", correct=True, confidence=1, quality="different_question_strong", node="KN6", recent=True, bypass=True),
            _result("Q7", correct=True, confidence=1, quality="different_question_strong", source="manual"),
            _result("Q8", correct=True, confidence=1, quality="different_question_strong", group="checking"),
        ]),
    ]

    facts = build_same_day_repair_effectiveness_facts(events, as_of=NOW)

    assert facts["adaptive_repair_attempt_count"] == 7
    assert facts["strong_attempt_count"] == 5
    assert facts["strong_correct_count"] == 4
    assert facts["strong_accuracy_percent"] == 80.0
    assert facts["strong_confident_correct_count"] == 3
    assert facts["formal_confirmation_candidate_count"] == 3
    assert facts["strong_wrong_count"] == 1
    assert facts["strong_distinct_node_count"] == 4
    assert facts["strong_distinct_question_count"] == 4
    assert facts["strong_recent_repeat_count"] == 1
    assert facts["strong_cooldown_bypass_count"] == 1
    assert facts["weak_attempt_count"] == 1
    assert facts["same_question_attempt_count"] == 1
    assert facts["diagnostic_only"] is True
    assert "spaced-retention" in facts["policy_note"]


def test_excludes_other_jst_day_and_handles_json_string_results():
    previous_day = {
        "answered_at": datetime(2026, 9, 5, 14, 59, tzinfo=timezone.utc),
        "question_results": '[{"question_id":"Q1","knowledge_node_id":"KN1","is_correct":true,"confidence":1,"answer_status":"answered","learning_source":"adaptive_daily","selection_group":"repair","repair_evidence_quality":"different_question_strong"}]',
    }
    current_day = {
        "answered_at": datetime(2026, 9, 5, 15, 1, tzinfo=timezone.utc),
        "question_results": '[{"question_id":"Q2","knowledge_node_id":"KN2","is_correct":true,"confidence":1,"answer_status":"answered","learning_source":"adaptive_daily","selection_group":"repair","repair_evidence_quality":"different_question_strong"}]',
    }
    facts = build_same_day_repair_effectiveness_facts(
        [previous_day, current_day],
        as_of=datetime(2026, 9, 6, 1, 0, tzinfo=timezone.utc),
    )
    assert facts["strong_attempt_count"] == 1
    assert facts["formal_confirmation_candidate_count"] == 1


def test_evidence_line_is_compact_and_non_identifying():
    line = build_repair_effectiveness_evidence_line({
        "date_jst": "2026-09-06",
        "adaptive_repair_attempt_count": 45,
        "strong_attempt_count": 35,
        "strong_correct_count": 26,
        "strong_accuracy_percent": 74.3,
        "strong_confident_correct_count": 13,
        "strong_wrong_count": 9,
        "strong_distinct_node_count": 29,
        "strong_distinct_question_count": 29,
        "strong_recent_repeat_count": 0,
        "strong_cooldown_bypass_count": 0,
        "weak_attempt_count": 8,
        "same_question_attempt_count": 2,
        "formal_confirmation_candidate_count": 13,
        "user_id": "must-not-leak",
        "token": "must-not-leak",
    })
    assert line.startswith("repair_effectiveness=date:2026-09-06,adaptive_repair:45,strong:35")
    assert "strong_correct:26,strong_accuracy:74.3,strong_confident_correct:13" in line
    assert "formal_confirmation_candidates:13" in line
    assert "must-not-leak" not in line
    assert "user_id" not in line
    assert "token" not in line
    assert build_repair_effectiveness_evidence_line(None).startswith(
        "repair_effectiveness=date:none,adaptive_repair:0,strong:0"
    )
