from __future__ import annotations

from datetime import datetime, timezone

import database
from qualifications.pt.learning_writer import PTLearningWriter


NOW = datetime(2026, 9, 12, tzinfo=timezone.utc)


class Cursor:
    def __init__(self):
        self.calls = []
        self.rowcount = 1

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, sql, params=()):
        self.calls.append((" ".join(sql.split()), params))
        self.rowcount = 1


class Connection:
    def __init__(self, cursor):
        self.cursor_obj = cursor

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def cursor(self):
        return self.cursor_obj


def _result():
    return [{
        "question_id": "Q1",
        "knowledge_node_id": "KN0001",
        "selected_answers": [1],
        "is_correct": False,
        "confidence": 1,
    }]


def test_writer_uses_explicit_pt_identity_and_qualified_conflict_targets(monkeypatch):
    cursor = Cursor()
    monkeypatch.setattr(database, "database_is_available", lambda: True)
    monkeypatch.setattr(database, "get_db_connection", lambda: Connection(cursor))

    writer = PTLearningWriter()
    assert writer.record_learning_batch(
        "learner",
        "session:1",
        "study",
        1,
        0,
        answered_at=NOW,
        question_results=_result(),
    ) is True

    event_sql, event_params = cursor.calls[0]
    attempt_sql, attempt_params = cursor.calls[1]
    node_sql, node_params = cursor.calls[2]

    assert "qualification_id" in event_sql
    assert "ON CONFLICT (qualification_id, event_key) DO NOTHING" in event_sql
    assert event_params[0] == "pt"

    assert "INSERT INTO question_attempts ( qualification_id" in attempt_sql
    assert attempt_params[0] == "pt"

    assert "qualification_id" in node_sql
    assert "ON CONFLICT ( qualification_id, user_id, knowledge_node_id ) DO UPDATE" in node_sql
    assert node_params[0] == "pt"


def test_duplicate_event_returns_false_before_attempt_or_node_writes(monkeypatch):
    cursor = Cursor()

    def execute(sql, params=()):
        cursor.calls.append((" ".join(sql.split()), params))
        cursor.rowcount = 0

    cursor.execute = execute
    monkeypatch.setattr(database, "database_is_available", lambda: True)
    monkeypatch.setattr(database, "get_db_connection", lambda: Connection(cursor))

    assert PTLearningWriter().record_learning_batch(
        "learner", "session:1", "study", 1, 0, question_results=_result()
    ) is False
    assert len(cursor.calls) == 1


def test_local_fallback_delegates_to_legacy_writer_exactly(monkeypatch):
    calls = []
    monkeypatch.setattr(database, "database_is_available", lambda: False)
    monkeypatch.setattr(
        database,
        "record_learning_batch",
        lambda **kwargs: calls.append(kwargs) or True,
    )

    result = PTLearningWriter().record_learning_batch(
        "learner",
        "session:1",
        "study",
        1,
        1,
        answered_at=NOW,
        question_results=_result(),
    )

    assert result is True
    assert calls == [{
        "user_id": "learner",
        "event_key": "session:1",
        "mode": "study",
        "answered_count": 1,
        "correct_count": 1,
        "answered_at": NOW,
        "question_results": _result(),
    }]


def test_activity_event_reuses_qualified_batch_writer(monkeypatch):
    writer = PTLearningWriter()
    calls = []
    monkeypatch.setattr(
        writer,
        "record_learning_batch",
        lambda **kwargs: calls.append(kwargs) or True,
    )

    assert writer.record_activity_event(
        "learner", "recommendation_plan", {"goal": 5}, occurred_at=NOW
    ) is True
    assert len(calls) == 1
    assert calls[0]["mode"] == "recommendation_plan"
    assert calls[0]["answered_count"] == 0
    assert calls[0]["question_results"] == {
        "activity_type": "recommendation_plan",
        "goal": 5,
    }
