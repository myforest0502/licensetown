"""⑤-C2 safe apply tests using an in-memory transactional fake DB."""

from __future__ import annotations

import copy
import importlib.util
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "backfill_node_learning_history.py"
SPEC = importlib.util.spec_from_file_location("node_backfill_apply", SCRIPT)
backfill = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(backfill)


NOW = datetime(2026, 8, 28, 4, 0, tzinfo=timezone.utc)


def resolver(question_id):
    return {"knowledge_node_id": f"KN{int(question_id[1:]):04d}"}


def result(question_id="Q1", correct=True, confidence=2):
    return {
        "question_id": question_id,
        "selected_answers": ["B"],
        "is_correct": correct,
        "confidence": confidence,
    }


def event(event_key="legacy:1", results=None, user_id="user-a", answered_at=NOW):
    values = [result()] if results is None else results
    return {
        "event_key": event_key,
        "user_id": user_id,
        "mode": "study",
        "answered_count": len(values),
        "correct_count": sum(item.get("is_correct") is True for item in values),
        "answered_at": answered_at,
        "question_results": values,
    }


def attempt(event_key="legacy:1", question_id="Q1", correct=True, confidence=2,
            user_id="user-a", answered_at=NOW, position=1):
    return {
        "event_key": event_key,
        "user_id": user_id,
        "question_id": question_id,
        "knowledge_node_id": f"KN{int(question_id[1:]):04d}",
        "mode": "study",
        "selected_answers": ["B"],
        "is_correct": correct,
        "confidence": confidence,
        "answered_at": answered_at,
        "attempt_position": position,
    }


class MemoryConnection:
    def __init__(self, events=None, attempts=None, states=None, fail_state_insert=False):
        self.events = copy.deepcopy(events or [])
        self.attempts = copy.deepcopy(attempts or [])
        self.states = copy.deepcopy(states or {})
        self.fail_state_insert = fail_state_insert
        self.write_statements = []
        self.rollback_count = 0
        self.commit_count = 0
        self._snapshot = None

    def __enter__(self):
        self._snapshot = copy.deepcopy((self.events, self.attempts, self.states))
        return self

    def __exit__(self, exc_type, _exc, _traceback):
        if exc_type is not None:
            self.events, self.attempts, self.states = self._snapshot
            self.rollback_count += 1
            return False
        self.commit_count += 1
        return False

    def cursor(self):
        return MemoryCursor(self)


class MemoryCursor:
    def __init__(self, connection):
        self.connection = connection
        self.rows = []
        self.one = None

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def execute(self, query, params=None):
        sql = " ".join(query.split())
        self.rows = []
        self.one = None
        if sql.startswith("SELECT event_key, user_id, mode"):
            self.rows = [tuple(item[column] for column in backfill.LEARNING_EVENT_COLUMNS)
                         for item in self.connection.events]
            return
        if sql.startswith("SELECT event_key, user_id, question_id"):
            self.rows = [tuple(item[column] for column in backfill.ATTEMPT_COLUMNS)
                         for item in self.connection.attempts]
            return
        if sql.startswith("SELECT COUNT(*) FROM user_node_state"):
            users = set(params[0])
            self.one = (sum(key[0] in users for key in self.connection.states),)
            return

        self.connection.write_statements.append(sql.split()[0].upper())
        if sql.startswith("INSERT INTO question_attempts"):
            key = (params[0], params[9])
            if any((item["event_key"], item["attempt_position"]) == key
                   for item in self.connection.attempts):
                self.one = None
                return
            self.connection.attempts.append({
                "event_key": params[0], "user_id": params[1],
                "question_id": params[2], "knowledge_node_id": params[3],
                "mode": params[4], "selected_answers": __import__("json").loads(params[5]),
                "is_correct": params[6], "confidence": params[7],
                "answered_at": params[8], "attempt_position": params[9],
            })
            self.one = (len(self.connection.attempts),)
            return
        if sql.startswith("DELETE FROM user_node_state"):
            users = set(params[0])
            self.connection.states = {
                key: value for key, value in self.connection.states.items()
                if key[0] not in users
            }
            return
        if sql.startswith("INSERT INTO user_node_state"):
            if self.connection.fail_state_insert:
                raise RuntimeError("state insert failed")
            state = {
                "user_id": params[0], "knowledge_node_id": params[1],
                "state": params[2], "attempt_count": params[3],
                "correct_count": params[4], "incorrect_count": params[5],
                "confident_wrong_count": params[6], "consecutive_correct": params[7],
                "repair_confirmation_count": 0, "first_seen_at": params[8],
                "last_seen_at": params[9], "last_correct_at": params[10],
                "last_incorrect_at": params[11], "last_question_id": params[12],
                "next_review_at": None, "last_error_type": None,
            }
            self.connection.states[(params[0], params[1])] = state
            return
        raise AssertionError(f"Unexpected SQL: {sql}")

    def fetchall(self):
        return list(self.rows)

    def fetchone(self):
        return self.one


def test_confirm_mismatch_and_ineligible_audit_write_nothing():
    connection = MemoryConnection(events=[event()])
    with pytest.raises(backfill.BackfillSafetyError, match="confirmation mismatch"):
        backfill.run_apply("WRONG", connection)
    assert connection.write_statements == []
    assert connection.attempts == []
    assert connection.rollback_count == 1

    broken = event()
    broken["answered_count"] = 2
    connection = MemoryConnection(events=[broken])
    with pytest.raises(backfill.BackfillSafetyError, match="not apply eligible"):
        backfill.run_apply("BACKFILL_1_ATTEMPTS", connection)
    assert connection.write_statements == []
    assert connection.attempts == []


def test_normal_apply_rebuilds_state_and_keeps_learning_events_unchanged():
    events = [event(results=[result("Q1", True, 2), result("Q2", False, 1)])]
    before = copy.deepcopy(events)
    connection = MemoryConnection(events=events)
    report = backfill.run_apply("BACKFILL_2_ATTEMPTS", connection)
    assert report["inserted"] == 2
    assert report["skipped"] == 0
    assert report["conflicts"] == 0
    assert report["question_attempts_total"] == 2
    assert report["rebuilt_state_rows"] == 2
    assert report["learning_events_unchanged"] is True
    assert connection.events == before
    assert connection.states[("user-a", "KN0001")]["state"] == "checking"
    node2 = connection.states[("user-a", "KN0002")]
    assert node2["state"] == "repairing"
    assert node2["confident_wrong_count"] == 1
    assert connection.commit_count == 1


def test_existing_match_is_skipped_and_existing_conflict_stops():
    connection = MemoryConnection(events=[event()], attempts=[attempt()])
    report = backfill.run_apply("BACKFILL_0_ATTEMPTS", connection)
    assert report["inserted"] == 0
    assert report["skipped"] == 1
    assert len(connection.attempts) == 1

    conflicting = attempt(correct=False)
    connection = MemoryConnection(events=[event()], attempts=[conflicting])
    with pytest.raises(backfill.BackfillSafetyError, match="not apply eligible"):
        backfill.run_apply("BACKFILL_0_ATTEMPTS", connection)
    assert connection.write_statements == []
    assert connection.attempts == [conflicting]


def test_failure_rolls_back_attempt_and_state_changes():
    original_state = {("user-a", "KN9999"): {"state": "stable"}}
    connection = MemoryConnection(
        events=[event()], states=original_state, fail_state_insert=True
    )
    with pytest.raises(RuntimeError, match="state insert failed"):
        backfill.run_apply("BACKFILL_1_ATTEMPTS", connection)
    assert connection.attempts == []
    assert connection.states == original_state
    assert connection.rollback_count == 1


def test_new_node_history_coexists_and_all_user_attempts_rebuild_state():
    events = [
        event("legacy:1", [result("Q1", False, 1)], answered_at=NOW),
        event("new:1", [result("Q1", True, 3)], answered_at=NOW + timedelta(minutes=1)),
    ]
    existing_new = attempt(
        "new:1", "Q1", True, 3, answered_at=NOW + timedelta(minutes=1)
    )
    connection = MemoryConnection(events=events, attempts=[existing_new])
    report = backfill.run_apply("BACKFILL_1_ATTEMPTS", connection)
    assert report["inserted"] == 1
    assert report["skipped"] == 1
    state = connection.states[("user-a", "KN0001")]
    assert state["attempt_count"] == 2
    assert state["correct_count"] == 1
    assert state["incorrect_count"] == 1
    assert state["state"] == "checking"
    assert state["consecutive_correct"] == 1


def test_second_apply_is_idempotent_and_state_is_identical():
    connection = MemoryConnection(events=[event()])
    first = backfill.run_apply("BACKFILL_1_ATTEMPTS", connection)
    first_attempts = copy.deepcopy(connection.attempts)
    first_states = copy.deepcopy(connection.states)
    second = backfill.run_apply("BACKFILL_0_ATTEMPTS", connection)
    assert first["inserted"] == 1
    assert second["inserted"] == 0
    assert second["skipped"] == 1
    assert connection.attempts == first_attempts
    assert connection.states == first_states
    assert connection.events == [event()]
