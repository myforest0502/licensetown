"""Regression coverage for qualification-scoped learner-history adapters."""

from datetime import datetime, timezone

import pytest

import database
from qualifications.common.learning_store_registry import (
    LearningHistoryStoreNotConfigured,
    get_learning_history_store,
)
from qualifications.pt.learning_store import PTLearningHistoryStore


NOW = datetime(2026, 9, 11, tzinfo=timezone.utc)


class FakeCursor:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []
        self.current = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, sql, params=()):
        self.calls.append((" ".join(sql.split()), params))
        self.current = self.responses.pop(0) if self.responses else []

    def fetchall(self):
        return list(self.current or [])

    def fetchone(self):
        if not self.current:
            return None
        return self.current[0]


class FakeConnection:
    def __init__(self, cursor):
        self._cursor = cursor

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def cursor(self):
        return self._cursor


def test_pt_learning_store_is_available_and_stable():
    first = get_learning_history_store("pt")
    second = get_learning_history_store("pt")
    assert isinstance(first, PTLearningHistoryStore)
    assert first is second
    assert first.qualification_id == "pt"


def test_takken_learning_store_is_not_allowed_to_fall_back_to_pt():
    with pytest.raises(
        LearningHistoryStoreNotConfigured,
        match="not configured for qualification: takken",
    ):
        get_learning_history_store("takken")


def test_unknown_qualification_fails_closed():
    with pytest.raises(KeyError):
        get_learning_history_store("unknown")


def test_pt_adapter_preserves_legacy_local_fallback(monkeypatch):
    store = get_learning_history_store("pt")
    sentinel = [{"question_id": "Q1"}]
    calls = []

    monkeypatch.setattr(database, "database_is_available", lambda: False)

    def fake(user_id, start_at=None):
        calls.append((user_id, start_at))
        return sentinel

    monkeypatch.setattr(database, "get_question_attempts", fake)
    assert store.get_question_attempts("user-1", start_at=NOW) is sentinel
    assert calls == [("user-1", NOW)]


def test_pt_attempt_reads_require_explicit_pt_scope(monkeypatch):
    store = get_learning_history_store("pt")
    row = (
        "event:1", "user-1", "Q1", "KN0001", "study", [1], True, 1,
        NOW, 1,
    )
    cursor = FakeCursor([[row]])
    monkeypatch.setattr(database, "database_is_available", lambda: True)
    monkeypatch.setattr(database, "get_db_connection", lambda: FakeConnection(cursor))

    attempts = store.get_question_attempts("user-1", start_at=NOW)

    assert attempts[0]["question_id"] == "Q1"
    assert attempts[0]["answer_status"] == "answered"
    sql, params = cursor.calls[0]
    assert "qualification_id = %s" in sql
    assert params == ("user-1", "pt", NOW)


def test_pt_history_reads_require_explicit_pt_scope(monkeypatch):
    store = get_learning_history_store("pt")
    cursor = FakeCursor([[
        ([{"question_id": "Q2", "is_correct": False}], NOW),
    ]])
    monkeypatch.setattr(database, "database_is_available", lambda: True)
    monkeypatch.setattr(database, "get_db_connection", lambda: FakeConnection(cursor))

    history = store.get_question_history("user-1")

    assert history == [{"question_id": "Q2", "is_correct": False, "timestamp": NOW}]
    sql, params = cursor.calls[0]
    assert "qualification_id = %s" in sql
    assert params == ("user-1", "pt")


def test_pt_assessment_state_reads_and_writes_qualified_row(monkeypatch):
    store = get_learning_history_store("pt")
    read_cursor = FakeCursor([[(True,)]])
    monkeypatch.setattr(database, "database_is_available", lambda: True)
    monkeypatch.setattr(database, "get_db_connection", lambda: FakeConnection(read_cursor))

    assert store.is_initial_assessment_completed("user-1") is True
    sql, params = read_cursor.calls[0]
    assert "qualification_user_state" in sql
    assert "qualification_id = %s" in sql
    assert params == ("user-1", "pt")

    write_cursor = FakeCursor([[]])
    monkeypatch.setattr(database, "get_db_connection", lambda: FakeConnection(write_cursor))
    legacy_marked = []
    monkeypatch.setattr(
        database, "mark_initial_assessment_completed", legacy_marked.append
    )

    assert store.mark_initial_assessment_completed("user-1") is None
    sql, params = write_cursor.calls[0]
    assert "qualification_user_state" in sql
    assert params == ("user-1", "pt")
    assert legacy_marked == ["user-1"]
