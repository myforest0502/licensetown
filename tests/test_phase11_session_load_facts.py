from datetime import datetime, timedelta, timezone

import pytest

from phase11_session_load_facts import (
    build_same_day_session_load_evidence_line,
    build_same_day_session_load_facts,
)


def _attempt(index, *, correct, question_id=None, answered_at=None):
    return {
        "id": index,
        "attempt_position": (index - 1) % 5 + 1,
        "question_id": question_id or f"Q{index}",
        "is_correct": correct,
        "confidence": 1,
        "answered_at": answered_at or datetime(2026, 9, 6, 0, 0, tzinfo=timezone.utc) + timedelta(minutes=index),
    }


def test_reconstructs_real_use_shape_without_making_fatigue_verdict():
    # Four 50-question cumulative same-day blocks: 78%, 78%, 74%, 68%.
    block_correct = [39, 39, 37, 34]
    rows = []
    for block_index, correct_count in enumerate(block_correct):
        for offset in range(50):
            index = block_index * 50 + offset + 1
            # 148 unique questions followed by 52 repeats.
            question_id = f"Q{index}" if index <= 148 else f"Q{index - 148}"
            rows.append(_attempt(index, correct=offset < correct_count, question_id=question_id))

    facts = build_same_day_session_load_facts(
        rows,
        as_of=datetime(2026, 9, 6, 12, 0, tzinfo=timezone.utc),
    )

    assert facts["answered_count"] == 200
    assert facts["correct_count"] == 149
    assert facts["accuracy_percent"] == 74.5
    assert facts["unique_question_count"] == 148
    assert facts["repeat_attempt_count"] == 52
    assert [block["accuracy_percent"] for block in facts["blocks"]] == [78.0, 78.0, 74.0, 68.0]
    assert facts["leading_to_trailing_full_block_accuracy_delta_pp"] == -10.0
    assert facts["block_scope"] == "same_day_cumulative"
    assert facts["max_inter_attempt_gap_minutes"] == 1.0
    assert facts["diagnostic_only"] is True
    assert "may span long breaks" in facts["policy_note"]
    assert "prior answer state" in facts["policy_note"]


def test_repeat_accuracy_is_split_by_previous_answer_state():
    rows = [
        _attempt(1, correct=False, question_id="Q1"),
        _attempt(2, correct=True, question_id="Q2"),
        _attempt(3, correct=True, question_id="Q1"),
        _attempt(4, correct=False, question_id="Q2"),
        _attempt(5, correct=False, question_id="Q3"),
        _attempt(6, correct=False, question_id="Q3"),
        _attempt(7, correct=True, question_id="Q4"),
        _attempt(8, correct=True, question_id="Q4"),
    ]

    facts = build_same_day_session_load_facts(
        rows,
        as_of=datetime(2026, 9, 6, 12, 0, tzinfo=timezone.utc),
        block_size=4,
    )

    assert facts["first_attempt_count"] == 4
    assert facts["first_attempt_accuracy_percent"] == 50.0
    assert facts["repeat_attempt_count"] == 4
    assert facts["repeat_accuracy_percent"] == 50.0
    assert facts["repeat_after_wrong_count"] == 2
    assert facts["wrong_to_correct_count"] == 1
    assert facts["wrong_to_wrong_count"] == 1
    assert facts["repeat_after_wrong_accuracy_percent"] == 50.0
    assert facts["repeat_after_correct_count"] == 2
    assert facts["correct_to_correct_count"] == 1
    assert facts["correct_to_wrong_count"] == 1
    assert facts["repeat_after_correct_accuracy_percent"] == 50.0


def test_long_break_is_reported_without_turning_it_into_a_session_or_fatigue_rule():
    rows = [
        _attempt(1, correct=True, answered_at=datetime(2026, 9, 5, 23, 6, tzinfo=timezone.utc)),
        _attempt(2, correct=True, answered_at=datetime(2026, 9, 5, 23, 16, tzinfo=timezone.utc)),
        _attempt(3, correct=False, answered_at=datetime(2026, 9, 6, 4, 38, tzinfo=timezone.utc)),
        _attempt(4, correct=True, answered_at=datetime(2026, 9, 6, 4, 41, tzinfo=timezone.utc)),
    ]

    facts = build_same_day_session_load_facts(
        rows,
        as_of=datetime(2026, 9, 6, 8, 0, tzinfo=timezone.utc),
        block_size=2,
    )

    assert facts["answered_count"] == 4
    assert facts["study_span_minutes"] == 335.0
    assert facts["max_inter_attempt_gap_minutes"] == 322.0
    assert facts["largest_inter_attempt_gaps_minutes"] == [322.0, 10.0, 3.0]
    assert facts["block_scope"] == "same_day_cumulative"
    assert "one continuous session" in facts["policy_note"]


def test_supporter_evidence_line_contains_only_compact_non_identifying_facts():
    line = build_same_day_session_load_evidence_line({
        "date_jst": "2026-09-06",
        "answered_count": 200,
        "accuracy_percent": 74.5,
        "unique_question_count": 148,
        "first_attempt_accuracy_percent": 70.3,
        "repeat_attempt_count": 52,
        "repeat_accuracy_percent": 86.5,
        "repeat_after_wrong_count": 11,
        "wrong_to_correct_count": 6,
        "wrong_to_wrong_count": 5,
        "repeat_after_wrong_accuracy_percent": 54.5,
        "study_span_minutes": 490.0,
        "max_inter_attempt_gap_minutes": 322.0,
        "leading_to_trailing_full_block_accuracy_delta_pp": -10.0,
        "block_scope": "same_day_cumulative",
        "user_id": "must-not-leak",
        "supporter_token": "must-not-leak",
    })

    assert line.startswith("same_day_load=date:2026-09-06,answers:200,accuracy:74.5")
    assert "repeat_after_wrong:11,wrong_to_correct:6,wrong_to_wrong:5" in line
    assert "repeat_after_wrong_accuracy:54.5" in line
    assert "max_gap_minutes:322.0" in line
    assert "block_scope:same_day_cumulative" in line
    assert "must-not-leak" not in line
    assert "user_id" not in line
    assert "supporter_token" not in line
    assert build_same_day_session_load_evidence_line(None).startswith(
        "same_day_load=date:none,answers:0,accuracy:none"
    )


def test_excludes_other_jst_days_and_keeps_partial_block_without_delta():
    rows = [
        _attempt(1, correct=True, answered_at=datetime(2026, 9, 5, 14, 59, tzinfo=timezone.utc)),
        _attempt(2, correct=True, answered_at=datetime(2026, 9, 5, 15, 1, tzinfo=timezone.utc)),
        _attempt(3, correct=False, answered_at=datetime(2026, 9, 5, 15, 2, tzinfo=timezone.utc)),
    ]

    facts = build_same_day_session_load_facts(
        rows,
        as_of=datetime(2026, 9, 6, 1, 0, tzinfo=timezone.utc),
        block_size=50,
    )

    assert facts["answered_count"] == 2
    assert facts["correct_count"] == 1
    assert facts["blocks"][0]["answered_count"] == 2
    assert facts["leading_to_trailing_full_block_accuracy_delta_pp"] is None


def test_rejects_non_positive_block_size():
    with pytest.raises(ValueError, match="block_size must be positive"):
        build_same_day_session_load_facts([], block_size=0)
