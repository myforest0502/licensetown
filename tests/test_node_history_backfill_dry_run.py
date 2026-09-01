"""⑤-C1 legacy Node-history backfill dry-run tests."""

from __future__ import annotations

import importlib.util
from datetime import datetime, timedelta, timezone
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "backfill_node_learning_history.py"
SPEC = importlib.util.spec_from_file_location("node_backfill_dry_run", SCRIPT)
backfill = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(backfill)


NOW = datetime(2026, 8, 28, 3, 0, tzinfo=timezone.utc)


def resolver(question_id):
    number = int(question_id[1:])
    return {"knowledge_node_id": f"KN{number:04d}"}


def event(results, *, event_key="event:1", answered=None, correct=None, user="user-a"):
    return {
        "event_key": event_key,
        "user_id": user,
        "mode": "study",
        "answered_count": len(results) if answered is None else answered,
        "correct_count": sum(item.get("is_correct") is True for item in results)
        if correct is None else correct,
        "answered_at": NOW,
        "question_results": results,
    }


def result(question_id="Q1", correct=True, confidence=2, answers=None):
    return {
        "question_id": question_id,
        "selected_answers": ["B"] if answers is None else answers,
        "is_correct": correct,
        "confidence": confidence,
    }


def expected_attempt(**overrides):
    value = {
        "event_key": "event:1",
        "user_id": "user-a",
        "question_id": "Q1",
        "knowledge_node_id": "KN0001",
        "mode": "study",
        "selected_answers": ["B"],
        "is_correct": True,
        "confidence": 2,
        "answered_at": NOW,
        "attempt_position": 1,
    }
    value.update(overrides)
    return value


def test_normal_history_becomes_candidate_and_joins_formal_node():
    report, candidates = backfill.audit_learning_history(
        [event([result()])], [], resolver
    )
    assert report["total_learning_events"] == 1
    assert report["events_with_question_results"] == 1
    assert report["events_without_question_results"] == 0
    assert report["total_attempt_candidates"] == 1
    assert report["resolved_knowledge_node_id"] == 1
    assert report["new_attempt_candidates"] == 1
    assert report["affected_users"] == 1
    assert report["apply_eligible"] is True
    assert candidates == [expected_attempt()]


def test_missing_question_invalid_confidence_and_count_mismatches_are_reported():
    results = [
        {"selected_answers": ["A"], "is_correct": True, "confidence": 7},
        result("Q1606", False, None),
    ]
    report, candidates = backfill.audit_learning_history(
        [event(results, answered=3, correct=2)], [], resolver
    )
    assert report["missing_question_id"] == 1
    assert report["out_of_range_question_id"] == 1
    assert report["invalid_confidence"] == 1
    assert report["confidence_null"] == 1
    assert report["answered_count_mismatches"] == 1
    assert report["correct_count_mismatches"] == 1
    assert report["apply_eligible"] is False
    assert candidates == []


def test_missing_node_is_correct_selected_answers_and_bad_json_are_audited():
    no_node = lambda _question_id: {}
    raw = event([{"question_id": "Q1", "confidence": None}])
    bad_json = event([], event_key="event:2")
    bad_json["question_results"] = "{not-json"
    report, _ = backfill.audit_learning_history([raw, bad_json], [], no_node)
    assert report["unresolved_knowledge_node_id"] == 1
    assert report["missing_is_correct"] == 1
    assert report["missing_selected_answers"] == 1
    assert report["json_decode_errors"] == 1
    assert report["apply_eligible"] is False


def test_existing_attempt_exact_match_and_conflict_are_distinguished():
    history = [event([result()])]
    matched, candidates = backfill.audit_learning_history(
        history, [expected_attempt()], resolver
    )
    assert matched["existing_matched"] == 1
    assert matched["new_attempt_candidates"] == 0
    assert matched["existing_conflicts"] == 0
    assert matched["inserted"] == 0
    assert matched["skipped"] == 1
    assert candidates == []

    conflict, candidates = backfill.audit_learning_history(
        history, [expected_attempt(is_correct=False)], resolver
    )
    assert conflict["existing_matched"] == 0
    assert conflict["existing_conflicts"] == 1
    assert conflict["apply_eligible"] is False
    assert candidates == []


def test_audit_is_idempotent_and_does_not_mutate_inputs():
    events = [event([result(), result("Q2", False, 1)])]
    existing = [expected_attempt()]
    events_before = repr(events)
    existing_before = repr(existing)
    first = backfill.audit_learning_history(events, existing, resolver)
    second = backfill.audit_learning_history(events, existing, resolver)
    assert first == second
    assert repr(events) == events_before
    assert repr(existing) == existing_before


class ReadOnlyCursor:
    def __init__(self, queries):
        self.queries = queries
        self.rows = []

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def execute(self, query):
        sql = " ".join(query.split())
        self.queries.append(sql)
        assert sql.upper().startswith("SELECT ")
        if "FROM learning_events" in sql:
            self.rows = [(
                "event:1", "user-a", "study", 1, 1, NOW, [result()],
            )]
        else:
            self.rows = []

    def fetchall(self):
        return list(self.rows)


class ReadOnlyConnection:
    def __init__(self):
        self.queries = []

    def cursor(self):
        return ReadOnlyCursor(self.queries)


def test_dry_run_snapshot_issues_select_only(monkeypatch):
    connection = ReadOnlyConnection()
    monkeypatch.setattr(backfill, "get_question_tag", resolver)
    report = backfill.run_dry_run(connection)
    assert report["new_attempt_candidates"] == 1
    assert len(connection.queries) == 2
    assert all(query.upper().startswith("SELECT ") for query in connection.queries)


def test_apply_flag_is_rejected_before_database_access(monkeypatch, capsys):
    monkeypatch.setattr(
        backfill,
        "run_dry_run",
        lambda: (_ for _ in ()).throw(AssertionError("DB must not be accessed")),
    )
    assert backfill.main(["--apply"]) == 2
    assert "requires --confirm" in capsys.readouterr().out


def test_rebuild_node_state_uses_full_ordered_attempt_history():
    attempts = [
        expected_attempt(answered_at=NOW, is_correct=True, confidence=2),
        expected_attempt(
            event_key="event:2", question_id="Q2", answered_at=NOW + timedelta(minutes=1),
            attempt_position=1, is_correct=False, confidence=1,
        ),
        expected_attempt(
            event_key="event:3", question_id="Q3", answered_at=NOW + timedelta(minutes=2),
            attempt_position=1, is_correct=True, confidence=None,
        ),
        expected_attempt(
            event_key="event:4", user_id="user-b", question_id="Q4",
            knowledge_node_id="KN0002", answered_at=NOW, attempt_position=1,
            is_correct=False, confidence=3,
        ),
    ]
    states = {
        (item["user_id"], item["knowledge_node_id"]): item
        for item in backfill.rebuild_user_node_states(attempts)
    }
    first = states[("user-a", "KN0001")]
    assert first["state"] == "checking"
    assert first["attempt_count"] == 3
    assert first["correct_count"] == 2
    assert first["incorrect_count"] == 1
    assert first["confident_wrong_count"] == 1
    assert first["consecutive_correct"] == 1
    assert first["last_question_id"] == "Q3"
    assert first["repair_confirmation_count"] == 0
    assert first["next_review_at"] is None
    second = states[("user-b", "KN0002")]
    assert second["state"] == "repairing"
    assert second["consecutive_correct"] == 0
