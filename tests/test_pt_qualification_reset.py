from __future__ import annotations

import database
from qualifications.pt.learning_store import PTLearningHistoryStore


class FakeCursor:
    def __init__(self):
        self.calls = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, sql, params=()):
        self.calls.append((" ".join(sql.split()), params))


class FakeConnection:
    def __init__(self, cursor):
        self._cursor = cursor

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def cursor(self):
        return self._cursor


def test_pt_reset_deletes_only_qualified_learning_state_in_production(monkeypatch):
    store = PTLearningHistoryStore()
    cursor = FakeCursor()
    monkeypatch.setattr(database, "database_is_available", lambda: True)
    monkeypatch.setattr(database, "get_db_connection", lambda: FakeConnection(cursor))

    store.reset_qualification_state("user-1")

    qualified_tables = {
        "question_attempts",
        "user_node_state",
        "learning_events",
        "learning_time_events",
        "qualification_learning_time_totals",
        "qualification_user_state",
        "paused_quiz_sessions",
        "web_learning_sessions",
    }
    qualified_calls = cursor.calls[: len(qualified_tables)]
    assert len(qualified_calls) == len(qualified_tables)
    assert all("qualification_id = %s" in sql for sql, _ in qualified_calls)
    assert all(params == ("user-1", "pt") for _, params in qualified_calls)
    assert {
        next(table for table in qualified_tables if f"FROM {table}" in sql)
        for sql, _ in qualified_calls
    } == qualified_tables

    assert cursor.calls[-2] == (
        "DELETE FROM learning_time_totals WHERE user_id = %s",
        ("user-1",),
    )
    profile_sql, profile_params = cursor.calls[-1]
    assert profile_sql.startswith("UPDATE user_profiles SET initial_assessment_completed = FALSE")
    assert profile_params == ("user-1",)
    assert not any("DELETE FROM user_profiles" in sql for sql, _ in cursor.calls)


def test_pt_reset_local_fallback_clears_learning_state_only(monkeypatch):
    store = PTLearningHistoryStore()
    monkeypatch.setattr(database, "database_is_available", lambda: False)
    monkeypatch.setattr(
        database,
        "_local_learning_events",
        {"event": {"user_id": "user-1"}, "other": {"user_id": "other"}},
    )
    monkeypatch.setattr(database, "_local_learning_seconds", {"user-1": 120, "other": 60})
    monkeypatch.setattr(
        database,
        "_local_learning_time_events",
        [{"user_id": "user-1"}, {"user_id": "other"}],
    )
    monkeypatch.setattr(
        database,
        "_local_question_attempts",
        [{"user_id": "user-1"}, {"user_id": "other"}],
    )
    monkeypatch.setattr(
        database,
        "_local_user_node_states",
        {("user-1", "KN1"): {}, ("other", "KN2"): {}},
    )
    monkeypatch.setattr(
        database,
        "_local_initial_assessment_completed",
        {"user-1", "other"},
    )

    store.reset_qualification_state("user-1")

    assert list(database._local_learning_events) == ["other"]
    assert database._local_learning_seconds == {"other": 60}
    assert database._local_learning_time_events == [{"user_id": "other"}]
    assert database._local_question_attempts == [{"user_id": "other"}]
    assert database._local_user_node_states == {("other", "KN2"): {}}
    assert database._local_initial_assessment_completed == {"other"}
