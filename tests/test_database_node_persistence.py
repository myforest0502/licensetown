"""⑤-Bの1問単位回答保存とNode基本集計を検証する。"""

from __future__ import annotations

import copy
import json
import os
from datetime import datetime, timezone

import pytest

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "test-token")
os.environ.setdefault("CHANNEL_SECRET", "test-secret")

import app as bot_app
import database
from question_bank import QuestionBankError, get_quiz_question


def result(question_id, node_id, is_correct, confidence=None, answers=None):
    return {
        "question_id": question_id,
        "knowledge_node_id": node_id,
        "selected_answers": answers or ["1"],
        "is_correct": is_correct,
        "confidence": confidence,
    }


def clear_local_node_data():
    database._local_learning_events.clear()
    database._local_question_attempts.clear()
    database._local_user_node_states.clear()


def test_local_attempts_node_aggregation_idempotency_history_and_reset(monkeypatch):
    monkeypatch.setattr(database, "database_is_available", lambda: False)
    clear_local_node_data()
    timestamp = datetime(2026, 8, 28, 1, 2, tzinfo=timezone.utc)
    results = [
        result("Q1", "KN0001", True, 2, ["B"]),
        result("Q2", "KN0002", False, 1, ["A"]),
        result("Q3", "KN0001", True, None, ["C"]),
    ]

    assert database.record_learning_batch(
        "local-user", "local:1", "study", 3, 2, timestamp, results
    )
    assert not database.record_learning_batch(
        "local-user", "local:1", "study", 3, 2, timestamp, results
    )

    attempts = database.get_question_attempts("local-user")
    assert [item["attempt_position"] for item in attempts] == [1, 2, 3]
    assert all(item["answered_at"] == timestamp for item in attempts)
    assert attempts[0]["knowledge_node_id"] == "KN0001"
    assert attempts[0]["selected_answers"] == ["B"]
    assert attempts[2]["confidence"] is None

    states = {
        item["knowledge_node_id"]: item
        for item in database.get_user_node_states("local-user")
    }
    assert states["KN0001"]["state"] == "checking"
    assert states["KN0001"]["attempt_count"] == 2
    assert states["KN0001"]["correct_count"] == 2
    assert states["KN0001"]["incorrect_count"] == 0
    assert states["KN0001"]["consecutive_correct"] == 2
    assert states["KN0002"]["state"] == "repairing"
    assert states["KN0002"]["confident_wrong_count"] == 1

    assert database.record_learning_batch(
        "local-user", "local:2", "study", 1, 0, timestamp,
        [result("Q4", "KN0001", False, 2)],
    )
    state = {
        item["knowledge_node_id"]: item
        for item in database.get_user_node_states("local-user")
    }["KN0001"]
    assert state["state"] == "repairing"
    assert state["attempt_count"] == 3
    assert state["correct_count"] == 2
    assert state["incorrect_count"] == 1
    assert state["consecutive_correct"] == 0

    history = database.get_question_history("local-user")
    assert len(history) == 4
    assert history[0]["knowledge_node_id"] == "KN0001"
    assert history[0]["timestamp"] == timestamp

    database.reset_user_profile("local-user")
    assert database.get_question_attempts("local-user") == []
    assert database.get_user_node_states("local-user") == []
    assert database.get_question_history("local-user") == []


def test_legacy_question_results_remain_compatible_without_attempt_backfill(monkeypatch):
    monkeypatch.setattr(database, "database_is_available", lambda: False)
    clear_local_node_data()
    legacy = [{
        "question_id": "Q1",
        "selected_answers": ["B"],
        "is_correct": True,
        "confidence": 2,
    }]
    assert database.record_learning_batch(
        "legacy-user", "legacy:1", "study", 1, 1,
        question_results=legacy,
    )
    assert database.get_question_attempts("legacy-user") == []
    assert database.get_user_node_states("legacy-user") == []
    assert database.get_question_history("legacy-user")[0]["question_id"] == "Q1"

    partial = [dict(legacy[0], knowledge_node_id="KN0001"), dict(legacy[0])]
    with pytest.raises(ValueError, match="missing knowledge_node_id"):
        database.record_learning_batch(
            "legacy-user", "partial:1", "study", 2, 2,
            question_results=partial,
        )
    assert "partial:1" not in database._local_learning_events


def test_confirmed_batch_rejects_missing_formal_knowledge_node_id(monkeypatch):
    monkeypatch.setattr(database, "database_is_available", lambda: False)
    clear_local_node_data()
    question = get_quiz_question("Q1")
    answer = "".join(question["accepted_answer_sets"][0])
    session = {
        "session_id": "missing-node-session",
        "current_set": 1,
        "questions_per_set": 1,
        "questions": [question],
        "all_answers": {1: {"answer": answer, "confidence": "2"}},
        "mode": "study",
    }
    monkeypatch.setattr(bot_app, "get_question_tag", lambda _question_id: {})

    with pytest.raises(QuestionBankError, match="Knowledge Node ID not found"):
        bot_app.record_confirmed_learning_batch("missing-node-user", session)
    assert database._local_learning_events == {}
    assert database._local_question_attempts == []


class TransactionDatabase:
    def __init__(self, fail_attempt_position=None):
        self.events = set()
        self.attempts = []
        self.states = {}
        self.fail_attempt_position = fail_attempt_position
        self.rollback_count = 0

    def connect(self):
        return TransactionConnection(self)


class TransactionConnection:
    def __init__(self, target):
        self.target = target

    def __enter__(self):
        self.events = copy.deepcopy(self.target.events)
        self.attempts = copy.deepcopy(self.target.attempts)
        self.states = copy.deepcopy(self.target.states)
        return self

    def __exit__(self, exc_type, _exc, _traceback):
        if exc_type is not None:
            self.target.rollback_count += 1
            return False
        self.target.events = self.events
        self.target.attempts = self.attempts
        self.target.states = self.states
        return False

    def cursor(self):
        return TransactionCursor(self)


class TransactionCursor:
    def __init__(self, connection):
        self.connection = connection
        self.rowcount = 0

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def execute(self, query, params):
        sql = " ".join(query.split())
        if sql.startswith("INSERT INTO learning_events"):
            event_key = params[0]
            if event_key in self.connection.events:
                self.rowcount = 0
            else:
                self.connection.events.add(event_key)
                self.rowcount = 1
            return

        if sql.startswith("INSERT INTO question_attempts"):
            attempt_position = params[9]
            if attempt_position == self.connection.target.fail_attempt_position:
                raise RuntimeError("attempt insert failed")
            self.connection.attempts.append({
                "event_key": params[0],
                "user_id": params[1],
                "question_id": params[2],
                "knowledge_node_id": params[3],
                "mode": params[4],
                "selected_answers": json.loads(params[5]),
                "is_correct": params[6],
                "confidence": params[7],
                "answered_at": params[8],
                "attempt_position": attempt_position,
            })
            self.rowcount = 1
            return

        if sql.startswith("INSERT INTO user_node_state"):
            (
                user_id, node_id, initial_state, correct, incorrect,
                confident_wrong, consecutive, first_seen, last_seen,
                last_correct, last_incorrect, question_id,
            ) = params
            key = (user_id, node_id)
            state = self.connection.states.get(key)
            if state is None:
                state = {
                    "state": initial_state,
                    "attempt_count": 0,
                    "correct_count": 0,
                    "incorrect_count": 0,
                    "confident_wrong_count": 0,
                    "consecutive_correct": 0,
                    "repair_confirmation_count": 0,
                    "first_seen_at": first_seen,
                    "next_review_at": None,
                    "last_error_type": None,
                }
                self.connection.states[key] = state
            state["attempt_count"] += 1
            state["correct_count"] += correct
            state["incorrect_count"] += incorrect
            state["confident_wrong_count"] += confident_wrong
            state["consecutive_correct"] = (
                0 if incorrect else state["consecutive_correct"] + consecutive
            )
            if incorrect:
                state["state"] = "repairing"
            state["last_seen_at"] = last_seen
            state["last_question_id"] = question_id
            if last_correct is not None:
                state["last_correct_at"] = last_correct
            if last_incorrect is not None:
                state["last_incorrect_at"] = last_incorrect
            self.rowcount = 1
            return

        raise AssertionError(f"Unexpected SQL: {sql}")


def test_database_batch_is_atomic_idempotent_and_preserves_state_fields(monkeypatch):
    fake = TransactionDatabase()
    monkeypatch.setattr(database, "database_is_available", lambda: True)
    monkeypatch.setattr(database, "get_db_connection", fake.connect)
    timestamp = datetime(2026, 8, 28, 2, 3, tzinfo=timezone.utc)
    results = [
        result("Q1", "KN0001", True, 2),
        result("Q2", "KN0001", False, 1),
        result("Q3", "KN0002", True, None),
    ]

    assert database.record_learning_batch(
        "db-user", "db:1", "study", 3, 2, timestamp, results
    )
    assert not database.record_learning_batch(
        "db-user", "db:1", "study", 3, 2, timestamp, results
    )
    assert fake.events == {"db:1"}
    assert len(fake.attempts) == 3
    assert [item["attempt_position"] for item in fake.attempts] == [1, 2, 3]
    assert all(item["answered_at"] == timestamp for item in fake.attempts)

    node1 = fake.states[("db-user", "KN0001")]
    assert node1["state"] == "repairing"
    assert node1["attempt_count"] == 2
    assert node1["correct_count"] == 1
    assert node1["incorrect_count"] == 1
    assert node1["confident_wrong_count"] == 1
    assert node1["consecutive_correct"] == 0
    assert fake.states[("db-user", "KN0002")]["state"] == "checking"

    node1["repair_confirmation_count"] = 7
    node1["next_review_at"] = "keep-review"
    node1["last_error_type"] = "knowledge_gap"
    assert database.record_learning_batch(
        "db-user", "db:2", "study", 1, 1, timestamp,
        [result("Q4", "KN0001", True, 3)],
    )
    node1 = fake.states[("db-user", "KN0001")]
    assert node1["state"] == "repairing"
    assert node1["consecutive_correct"] == 1
    assert node1["repair_confirmation_count"] == 7
    assert node1["next_review_at"] == "keep-review"
    assert node1["last_error_type"] == "knowledge_gap"


def test_database_failure_rolls_back_learning_event_attempts_and_state(monkeypatch):
    fake = TransactionDatabase(fail_attempt_position=2)
    monkeypatch.setattr(database, "database_is_available", lambda: True)
    monkeypatch.setattr(database, "get_db_connection", fake.connect)

    try:
        database.record_learning_batch(
            "db-user", "db:rollback", "study", 2, 1,
            question_results=[
                result("Q1", "KN0001", True, 2),
                result("Q2", "KN0002", False, 1),
            ],
        )
    except RuntimeError as exc:
        assert str(exc) == "attempt insert failed"
    else:
        raise AssertionError("Expected transaction failure")

    assert fake.rollback_count == 1
    assert fake.events == set()
    assert fake.attempts == []
    assert fake.states == {}
