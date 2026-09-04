from __future__ import annotations

import dashboard_read_bundle


def test_local_bundle_preserves_existing_read_contract(monkeypatch):
    learning = {
        "summary": {"total_answers": 5},
        "activity": {"streak_days": 1},
        "fields": [],
        "unique_question_count": 5,
    }
    attempts = [{"question_id": "Q1"}]
    trial100 = [{"source_version": "trial100-v1"}]

    monkeypatch.setattr(
        dashboard_read_bundle.database, "database_is_available", lambda: False
    )
    monkeypatch.setattr(
        dashboard_read_bundle.database,
        "get_dashboard_learning_data",
        lambda user_id: learning,
    )
    monkeypatch.setattr(
        dashboard_read_bundle.database,
        "get_question_attempts",
        lambda user_id: attempts,
    )
    monkeypatch.setattr(
        dashboard_read_bundle,
        "get_trial100_records",
        lambda user_id, **kwargs: trial100,
    )

    result = dashboard_read_bundle.get_dashboard_read_bundle(
        "learner", include_attempts=True, include_trial100=True
    )

    assert result["learning_data"] is learning
    assert result["attempts"] is attempts
    assert result["trial100_records"] is trial100


def test_optional_evidence_reads_are_skipped(monkeypatch):
    monkeypatch.setattr(
        dashboard_read_bundle.database, "database_is_available", lambda: False
    )
    monkeypatch.setattr(
        dashboard_read_bundle.database,
        "get_dashboard_learning_data",
        lambda user_id: {
            "summary": {}, "activity": {}, "fields": [], "unique_question_count": 0
        },
    )
    monkeypatch.setattr(
        dashboard_read_bundle.database,
        "get_question_attempts",
        lambda user_id: (_ for _ in ()).throw(AssertionError("attempt read not expected")),
    )
    monkeypatch.setattr(
        dashboard_read_bundle,
        "get_trial100_records",
        lambda user_id, **kwargs: (_ for _ in ()).throw(
            AssertionError("Trial100 read not expected")
        ),
    )

    result = dashboard_read_bundle.get_dashboard_read_bundle("learner")

    assert result["attempts"] == []
    assert result["trial100_records"] == []


def test_attempt_rows_match_formal_database_shape():
    class Cursor:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def execute(self, sql, params):
            assert "FROM question_attempts" in sql
            assert params == ("learner",)

        def fetchall(self):
            return [
                (
                    "event-1",
                    "learner",
                    "Q1",
                    "KN0001",
                    "study",
                    [],
                    False,
                    None,
                    "2026-09-04T00:00:00+00:00",
                    1,
                )
            ]

    class Connection:
        def cursor(self):
            return Cursor()

    attempts = dashboard_read_bundle._attempts_with_connection(
        "learner", Connection()
    )

    assert attempts[0]["question_id"] == "Q1"
    assert attempts[0]["answer_status"] == "unknown"


def test_learner_navigation_bundle_shares_one_production_connection(monkeypatch):
    connection_obj = object()
    connection_entries = []
    attempts = [{"question_id": "Q1"}]
    trial100 = [{"source_version": "trial100-v1"}]

    class ConnectionContext:
        def __enter__(self):
            connection_entries.append("enter")
            return connection_obj

        def __exit__(self, *args):
            connection_entries.append("exit")
            return False

    monkeypatch.setattr(
        dashboard_read_bundle.database, "database_is_available", lambda: True
    )
    monkeypatch.setattr(
        dashboard_read_bundle.database, "get_db_connection", ConnectionContext
    )
    monkeypatch.setattr(
        dashboard_read_bundle,
        "_attempts_with_connection",
        lambda user_id, conn: attempts if conn is connection_obj else None,
    )
    monkeypatch.setattr(
        dashboard_read_bundle,
        "get_trial100_records",
        lambda user_id, connection=None: trial100 if connection is connection_obj else None,
    )
    monkeypatch.setattr(
        dashboard_read_bundle.database,
        "_get_question_result_rows",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("legacy dashboard aggregates are not part of this read")
        ),
    )

    result = dashboard_read_bundle.get_learner_navigation_read_bundle("learner")

    assert result == {"attempts": attempts, "trial100_records": trial100}
    assert connection_entries == ["enter", "exit"]


def test_learner_navigation_bundle_preserves_local_fallback(monkeypatch):
    attempts = [{"question_id": "Q1"}]
    trial100 = [{"source_version": "trial100-v1"}]
    monkeypatch.setattr(
        dashboard_read_bundle.database, "database_is_available", lambda: False
    )
    monkeypatch.setattr(
        dashboard_read_bundle.database,
        "get_question_attempts",
        lambda user_id: attempts,
    )
    monkeypatch.setattr(
        dashboard_read_bundle,
        "get_trial100_records",
        lambda user_id: trial100,
    )
    monkeypatch.setattr(
        dashboard_read_bundle.database,
        "get_dashboard_learning_data",
        lambda user_id: (_ for _ in ()).throw(
            AssertionError("full dashboard read is not part of the fallback")
        ),
    )

    result = dashboard_read_bundle.get_learner_navigation_read_bundle("learner")

    assert result == {"attempts": attempts, "trial100_records": trial100}
