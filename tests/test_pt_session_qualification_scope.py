"""Regression coverage for explicit PT scope in durable session stores."""

import pytest

from durable_paused_session import PausedSessionStore
from durable_web_learning_session import WebLearningSessionStore


class Cursor:
    def __init__(self, rows=None):
        self.calls = []
        self.rows = rows or []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, sql, params=()):
        self.calls.append((" ".join(sql.split()), params))

    def fetchone(self):
        return self.rows[0] if self.rows else None

    def fetchall(self):
        return list(self.rows)


class Connection:
    def __init__(self, cursor):
        self._cursor = cursor

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def cursor(self):
        return self._cursor


class Database:
    def __init__(self, cursor):
        self.cursor = cursor

    @staticmethod
    def database_is_available():
        return True

    def get_db_connection(self):
        return Connection(self.cursor)


def paused_session(**extra):
    return {
        "status": "paused",
        "all_answers": {},
        **extra,
    }


def web_session(**extra):
    return {
        "user_id": "user-1",
        "dashboard_token": "token",
        "question_count": 1,
        "questions": [{"id": "Q1"}],
        "current_index": 0,
        **extra,
    }


def test_paused_store_writes_explicit_pt_scope():
    cursor = Cursor()
    store = PausedSessionStore(Database(cursor))

    assert store.save("user-1", paused_session()) is True
    sql, params = cursor.calls[0]
    assert "qualification_id" in sql
    assert params[0:2] == ("user-1", "pt")


def test_paused_store_load_and_delete_filter_pt_scope():
    cursor = Cursor()
    store = PausedSessionStore(Database(cursor))
    store.load("user-1")
    store.delete("user-1")

    load_sql, load_params = cursor.calls[0]
    delete_sql, delete_params = cursor.calls[1]
    assert "qualification_id = %s" in load_sql
    assert load_params == ("user-1", "pt")
    assert "qualification_id = %s" in delete_sql
    assert delete_params == ("user-1", "pt")


def test_paused_store_rejects_cross_qualification_payload():
    store = PausedSessionStore(Database(Cursor()))
    with pytest.raises(ValueError, match="qualification mismatch"):
        store.save("user-1", paused_session(qualification_id="takken"))


def test_web_store_writes_and_reads_explicit_pt_scope():
    cursor = Cursor()
    store = WebLearningSessionStore(Database(cursor))

    assert store.save("sid", web_session()) is True
    cleanup_sql, cleanup_params = cursor.calls[0]
    insert_sql, insert_params = cursor.calls[1]
    assert "qualification_id = %s" in cleanup_sql
    assert cleanup_params == ("pt",)
    assert "qualification_id" in insert_sql
    assert insert_params[0:3] == ("sid", "user-1", "pt")

    cursor.calls.clear()
    store.load("sid")
    sql, params = cursor.calls[0]
    assert "qualification_id = %s" in sql
    assert params == ("sid", "pt")


def test_web_store_rejects_cross_qualification_payload():
    store = WebLearningSessionStore(Database(Cursor()))
    with pytest.raises(ValueError, match="qualification mismatch"):
        store.save("sid", web_session(qualification_id="takken"))
