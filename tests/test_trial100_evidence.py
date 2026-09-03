from datetime import date

import pytest

from trial100_evidence import normalize_trial100_record


def _record(**overrides):
    record = {
        "user_id": "learner-1",
        "test_date": "2026-09-03",
        "source_version": "trial100-2026-09-a",
        "total_questions": 100,
        "correct_count": 72,
        "completion_status": "completed",
        "duration_minutes": 155,
    }
    record.update(overrides)
    return record


def test_completed_100_question_attempt_within_160_minutes_is_full_format():
    result = normalize_trial100_record(_record())
    assert result["timed_full_format"] is True
    assert result["score_rate"] == 0.72
    assert result["supportive"] is False


def test_supportive_is_never_inferred_from_score():
    result = normalize_trial100_record(_record(correct_count=100))
    assert result["supportive"] is False
    explicit = normalize_trial100_record(_record(correct_count=100, supportive=True))
    assert explicit["supportive"] is True


def test_over_time_limit_is_recorded_but_not_full_format():
    result = normalize_trial100_record(_record(duration_minutes=161))
    assert result["timed_full_format"] is False
    assert result["correct_count"] == 72


def test_missing_duration_is_not_claimed_as_timed_full_format():
    result = normalize_trial100_record(_record(duration_minutes=None))
    assert result["timed_full_format"] is False


def test_incomplete_attempt_is_not_full_format_even_with_time_recorded():
    result = normalize_trial100_record(_record(completion_status="incomplete", duration_minutes=120))
    assert result["timed_full_format"] is False


def test_non_100_question_ordinary_aggregate_cannot_be_full_format():
    result = normalize_trial100_record(_record(total_questions=30, correct_count=25, duration_minutes=40))
    assert result["timed_full_format"] is False


def test_source_version_is_required_for_auditable_trial_identity():
    with pytest.raises(ValueError, match="source_version"):
        normalize_trial100_record(_record(source_version=""))


def test_score_bounds_are_validated():
    with pytest.raises(ValueError, match="correct_count"):
        normalize_trial100_record(_record(correct_count=101))
    with pytest.raises(ValueError, match="correct_count"):
        normalize_trial100_record(_record(correct_count=-1))


def test_supportive_requires_boolean_not_truthy_string():
    with pytest.raises(ValueError, match="supportive"):
        normalize_trial100_record(_record(supportive="yes"))


def test_optional_breakdowns_are_preserved_without_interpretation():
    result = normalize_trial100_record(_record(
        test_date=date(2026, 9, 3),
        field_breakdown={"神経医学": {"correct": 8, "total": 10}},
        review_summary={"confident_wrong": 2},
    ))
    assert result["test_date"] == "2026-09-03"
    assert result["field_breakdown"]["神経医学"]["correct"] == 8
    assert result["review_summary"]["confident_wrong"] == 2
