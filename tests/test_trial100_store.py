from __future__ import annotations

import pytest

import trial100_store


def _record(**overrides):
    record = {
        "user_id": "trial100-user",
        "test_date": "2026-09-04",
        "source_version": "trial100-v1",
        "total_questions": 100,
        "correct_count": 78,
        "completion_status": "completed",
        "duration_minutes": 155,
        "supportive": False,
        "field_breakdown": {"内科学": {"answered": 10, "correct": 7}},
        "review_summary": {"note": "paper test"},
    }
    record.update(overrides)
    return record


def setup_function():
    trial100_store._local_trial100_attempts.clear()


def teardown_function():
    trial100_store._local_trial100_attempts.clear()


def test_save_and_read_local_trial100_record(monkeypatch):
    monkeypatch.setattr(trial100_store.database, "database_is_available", lambda: False)

    saved = trial100_store.save_trial100_record(_record(), recorded_by="supporter")
    rows = trial100_store.get_trial100_records("trial100-user")

    assert saved["score_rate"] == 0.78
    assert saved["timed_full_format"] is True
    assert saved["supportive"] is False
    assert saved["recorded_by"] == "supporter"
    assert rows == [saved]


def test_duplicate_identity_is_rejected_locally(monkeypatch):
    monkeypatch.setattr(trial100_store.database, "database_is_available", lambda: False)
    trial100_store.save_trial100_record(_record())

    with pytest.raises(ValueError, match="duplicate Trial100 record"):
        trial100_store.save_trial100_record(_record(correct_count=80))


def test_store_uses_evidence_validation_before_persistence(monkeypatch):
    monkeypatch.setattr(trial100_store.database, "database_is_available", lambda: False)

    with pytest.raises(ValueError, match="correct_count"):
        trial100_store.save_trial100_record(_record(correct_count=101))

    assert trial100_store.get_trial100_records("trial100-user") == []


def test_records_are_returned_newest_first(monkeypatch):
    monkeypatch.setattr(trial100_store.database, "database_is_available", lambda: False)
    trial100_store.save_trial100_record(_record(test_date="2026-08-01", source_version="aug"))
    trial100_store.save_trial100_record(_record(test_date="2026-09-01", source_version="sep"))

    rows = trial100_store.get_trial100_records("trial100-user")

    assert [item["source_version"] for item in rows] == ["sep", "aug"]


def test_missing_user_returns_empty_without_db_access(monkeypatch):
    monkeypatch.setattr(trial100_store.database, "database_is_available", lambda: True)
    monkeypatch.setattr(
        trial100_store.database,
        "get_db_connection",
        lambda: (_ for _ in ()).throw(AssertionError("DB should not be opened")),
    )

    assert trial100_store.get_trial100_records("") == []
