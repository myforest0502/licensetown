"""Knowledge Node学習履歴Schemaの⑤-A境界を検証する。"""

from __future__ import annotations

import inspect

import database


class RecordingCursor:
    def __init__(self, executed):
        self.executed = executed

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def execute(self, query, params=None):
        self.executed.append((" ".join(query.split()), params))


class RecordingConnection:
    def __init__(self, executed):
        self.executed = executed

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def cursor(self):
        return RecordingCursor(self.executed)


def run_init(monkeypatch, times=1):
    executed = []
    monkeypatch.setattr(database, "database_is_available", lambda: True)
    monkeypatch.setattr(
        database,
        "get_db_connection",
        lambda: RecordingConnection(executed),
    )
    for _ in range(times):
        database.init_database()
    return executed


def table_ddl(executed, table_name):
    prefix = f"CREATE TABLE IF NOT EXISTS {table_name} "
    matches = [query for query, _params in executed if query.startswith(prefix)]
    assert len(matches) == 1
    return matches[0]


def test_node_learning_schema_has_formal_tables_constraints_and_indexes(monkeypatch):
    executed = run_init(monkeypatch)
    queries = [query for query, _params in executed]

    migrations = table_ddl(executed, "schema_migrations")
    assert "version TEXT PRIMARY KEY" in migrations
    assert "applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()" in migrations

    attempts = table_ddl(executed, "question_attempts")
    for column in (
        "event_key TEXT NOT NULL",
        "user_id TEXT NOT NULL",
        "question_id TEXT NOT NULL",
        "knowledge_node_id TEXT NOT NULL",
        "mode TEXT NOT NULL",
        "selected_answers JSONB NOT NULL",
        "is_correct BOOLEAN NOT NULL",
        "confidence SMALLINT",
        "answered_at TIMESTAMPTZ NOT NULL",
        "attempt_position SMALLINT NOT NULL",
    ):
        assert column in attempts
    assert "UNIQUE (event_key, attempt_position)" in attempts
    assert "CHECK (question_id ~ '^Q[1-9][0-9]{0,3}$')" in attempts
    assert "CHECK (knowledge_node_id ~ '^KN[0-9]{4}$')" in attempts
    assert "CHECK (confidence IS NULL OR confidence BETWEEN 1 AND 3)" in attempts
    assert "CHECK (attempt_position >= 1)" in attempts

    node_state = table_ddl(executed, "user_node_state")
    assert "PRIMARY KEY (user_id, knowledge_node_id)" in node_state
    assert "DEFAULT 'unseen'" in node_state
    for column in (
        "first_seen_at TIMESTAMPTZ",
        "last_seen_at TIMESTAMPTZ",
        "last_correct_at TIMESTAMPTZ",
        "last_incorrect_at TIMESTAMPTZ",
        "last_question_id TEXT",
        "next_review_at TIMESTAMPTZ",
        "last_error_type TEXT",
        "updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()",
    ):
        assert column in node_state
    for state in ("unseen", "checking", "repairing", "repaired", "stable", "recheck_due"):
        assert f"'{state}'" in node_state
    for counter in (
        "attempt_count",
        "correct_count",
        "incorrect_count",
        "confident_wrong_count",
        "consecutive_correct",
        "repair_confirmation_count",
    ):
        assert f"{counter} INTEGER NOT NULL DEFAULT 0" in node_state
        assert f"CHECK ({counter} >= 0)" in node_state
    assert "last_question_id ~ '^Q[1-9][0-9]{0,3}$'" in node_state
    for error_type in (
        "knowledge_gap",
        "misconception",
        "calculation_method",
        "reading_overthinking",
        "uncertain_recall",
        "application_failure",
    ):
        assert f"'{error_type}'" in node_state

    for index_ddl in (
        "CREATE INDEX IF NOT EXISTS question_attempts_user_date_idx "
        "ON question_attempts (user_id, answered_at DESC)",
        "CREATE INDEX IF NOT EXISTS question_attempts_user_question_date_idx "
        "ON question_attempts (user_id, question_id, answered_at DESC)",
        "CREATE INDEX IF NOT EXISTS question_attempts_user_node_date_idx "
        "ON question_attempts (user_id, knowledge_node_id, answered_at DESC)",
        "CREATE INDEX IF NOT EXISTS user_node_state_user_state_idx "
        "ON user_node_state (user_id, state)",
        "CREATE INDEX IF NOT EXISTS user_node_state_user_review_idx "
        "ON user_node_state (user_id, next_review_at)",
        "CREATE INDEX IF NOT EXISTS user_node_state_user_last_seen_idx "
        "ON user_node_state (user_id, last_seen_at DESC)",
    ):
        assert index_ddl in queries


def test_node_learning_schema_init_and_version_registration_are_idempotent(monkeypatch):
    executed = run_init(monkeypatch, times=2)
    queries = [query for query, _params in executed]

    for table in ("schema_migrations", "question_attempts", "user_node_state"):
        assert sum(
            query.startswith(f"CREATE TABLE IF NOT EXISTS {table} ")
            for query in queries
        ) == 2
    migration_inserts = [
        (query, params)
        for query, params in executed
        if query.startswith("INSERT INTO schema_migrations")
    ]
    assert migration_inserts == [
        (
            "INSERT INTO schema_migrations (version) VALUES (%s) "
            "ON CONFLICT (version) DO NOTHING",
            (database.NODE_LEARNING_SCHEMA_VERSION,),
        ),
        (
            "INSERT INTO schema_migrations (version) VALUES (%s) "
            "ON CONFLICT (version) DO NOTHING",
            (database.NODE_LEARNING_SCHEMA_VERSION,),
        ),
    ]
    assert database.NODE_LEARNING_SCHEMA_VERSION == "2026_08_node_learning_state_v1"
    assert not any("DROP " in query or "TRUNCATE " in query for query in queries)


def test_existing_tables_are_retained_and_phase_b_writes_are_not_connected(monkeypatch):
    executed = run_init(monkeypatch)
    queries = [query for query, _params in executed]
    for table in (
        "user_profiles",
        "learning_events",
        "learning_time_totals",
        "learning_time_events",
        "supporter_links",
    ):
        assert any(f"CREATE TABLE IF NOT EXISTS {table}" in query for query in queries)

    record_source = inspect.getsource(database.record_learning_batch)
    assert "question_attempts" not in record_source
    assert "user_node_state" not in record_source


def test_init_without_database_url_keeps_local_fallback(monkeypatch):
    monkeypatch.setattr(database, "database_is_available", lambda: False)

    def unexpected_connection():
        raise AssertionError("DB connection must not be opened without DATABASE_URL")

    monkeypatch.setattr(database, "get_db_connection", unexpected_connection)
    database.init_database()
