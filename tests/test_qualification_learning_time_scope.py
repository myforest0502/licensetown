"""Regression coverage for PT qualification-scoped learning-time totals."""

from types import SimpleNamespace

from qualification_learning_time_scope import install_pt_learning_time_scope


class Cursor:
    def __init__(self):
        self.calls = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, sql, params=()):
        self.calls.append((" ".join(sql.split()), params))


class Connection:
    def __init__(self, cursor):
        self._cursor = cursor

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def cursor(self):
        return self._cursor


def test_successful_pt_time_addition_is_mirrored_once():
    calls = []
    legacy = SimpleNamespace(
        add_learning_time=lambda *args, **kwargs: calls.append((args, kwargs)) or True
    )
    cursor = Cursor()
    database = SimpleNamespace(
        database_is_available=lambda: True,
        get_db_connection=lambda: Connection(cursor),
    )

    install_pt_learning_time_scope(legacy, database)
    assert legacy.add_learning_time("user-1", 90, event_key="event-1") is True

    assert len(calls) == 1
    assert len(cursor.calls) == 1
    sql, params = cursor.calls[0]
    assert "qualification_learning_time_totals" in sql
    assert "ON CONFLICT (user_id, qualification_id)" in sql
    assert params == ("user-1", "pt", 90.0)


def test_duplicate_rejected_by_legacy_recorder_is_not_mirrored():
    legacy = SimpleNamespace(add_learning_time=lambda *args, **kwargs: False)
    cursor = Cursor()
    database = SimpleNamespace(
        database_is_available=lambda: True,
        get_db_connection=lambda: Connection(cursor),
    )

    install_pt_learning_time_scope(legacy, database)
    assert legacy.add_learning_time("user-1", 90, event_key="duplicate") is False
    assert cursor.calls == []


def test_local_fallback_preserves_legacy_result_without_scoped_db_write():
    sentinel = object()
    legacy = SimpleNamespace(add_learning_time=lambda *args, **kwargs: sentinel)
    database = SimpleNamespace(database_is_available=lambda: False)

    install_pt_learning_time_scope(legacy, database)
    assert legacy.add_learning_time("user-1", 12) is sentinel


def test_installer_is_idempotent():
    legacy = SimpleNamespace(add_learning_time=lambda *args, **kwargs: True)
    database = SimpleNamespace(database_is_available=lambda: False)

    install_pt_learning_time_scope(legacy, database)
    first = legacy.add_learning_time
    install_pt_learning_time_scope(legacy, database)

    assert legacy.add_learning_time is first
