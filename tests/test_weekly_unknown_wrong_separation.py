from datetime import datetime, timedelta, timezone

import database

NOW = datetime(2026, 9, 2, 0, 0, tzinfo=timezone.utc)


def row(q, *, selected, correct, confidence, hour=0, status=None):
    item = {
        "user_id": "u",
        "question_id": q,
        "selected_answers": selected,
        "is_correct": correct,
        "confidence": confidence,
        "answered_at": NOW - timedelta(hours=hour),
    }
    if status is not None:
        item["answer_status"] = status
    return item


def assert_semantics(result):
    assert result["unknown_question_ids"] == ["Q1", "Q4"]
    assert result["wrong_question_ids"] == ["Q2", "Q3", "Q4"]
    assert result["confident_wrong_question_ids"] == ["Q3"]


def test_local_weekly_history_separates_unknown_from_evaluable_wrong(monkeypatch):
    monkeypatch.setattr(database, "DATABASE_URL", None)
    monkeypatch.setattr(database, "_local_question_attempts", [
        row("Q1", selected=[], correct=False, confidence=None, hour=1, status="unknown"),
        row("Q2", selected=[2], correct=False, confidence=2, hour=2, status="answered"),
        row("Q3", selected=[3], correct=False, confidence=1, hour=3, status="answered"),
        row("Q4", selected=[], correct=False, confidence=None, hour=4, status="unknown"),
        row("Q4", selected=[1], correct=False, confidence=2, hour=5, status="answered"),
    ])
    result = database.get_weekly_question_history("u", now=NOW)
    assert_semantics(result)


def test_db_weekly_history_uses_same_attempt_level_semantics(monkeypatch):
    rows = [
        ("Q1", [], False, None, NOW - timedelta(hours=1)),
        ("Q2", [2], False, 2, NOW - timedelta(hours=2)),
        ("Q3", [3], False, 1, NOW - timedelta(hours=3)),
        ("Q4", [], False, None, NOW - timedelta(hours=4)),
        ("Q4", [1], False, 2, NOW - timedelta(hours=5)),
    ]

    class Cursor:
        def __enter__(self): return self
        def __exit__(self, *_args): return False
        def execute(self, _sql, _args): pass
        def fetchall(self): return rows

    class Connection:
        def __enter__(self): return self
        def __exit__(self, *_args): return False
        def cursor(self): return Cursor()

    monkeypatch.setattr(database, "database_is_available", lambda: True)
    monkeypatch.setattr(database, "get_db_connection", lambda: Connection())
    result = database.get_weekly_question_history("u", now=NOW)
    assert_semantics(result)
