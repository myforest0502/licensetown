from datetime import datetime, timedelta, timezone

import pytest

from knowledge_node_relations import get_node_relations, get_reviewed_node_relations
from prerequisite_diagnosis import (
    SOURCE_CONFIDENT_CORRECT,
    SOURCE_CONFLICT,
    SOURCE_UNSEEN,
    SOURCE_UNSTABLE,
    derive_prerequisite_diagnosis,
    simulate_prerequisite_diagnoses,
)
from scripts.simulate_prerequisite_diagnosis import load_attempts_read_only


NOW = datetime(2026, 8, 29, tzinfo=timezone.utc)
RELATION = get_reviewed_node_relations()[0]


def attempt(node, correct, confidence, minutes, question="Q1", user="user-a", position=1):
    return {
        "id": minutes + 100,
        "event_key": f"event-{minutes:03d}",
        "user_id": user,
        "question_id": question,
        "knowledge_node_id": node,
        "is_correct": correct,
        "confidence": confidence,
        "answered_at": NOW + timedelta(minutes=minutes),
        "attempt_position": position,
    }


def target(minutes=10, confidence=2):
    return attempt(RELATION["target_node_id"], False, confidence, minutes, "Q1209")


@pytest.mark.parametrize(("correct", "confidence", "expected"), [
    (True, 1, SOURCE_CONFIDENT_CORRECT),
    (True, 2, SOURCE_UNSTABLE),
    (True, 3, SOURCE_UNSTABLE),
    (False, 1, SOURCE_CONFLICT),
    (False, 2, SOURCE_UNSTABLE),
    (False, 3, SOURCE_UNSTABLE),
])
def test_source_evidence_classification(correct, confidence, expected):
    source = attempt(RELATION["source_node_id"], correct, confidence, 1, "Q745")
    result = derive_prerequisite_diagnosis(target(), [source], RELATION)
    assert result["source_status"] == expected
    assert result["recommended_backtrack"] is (expected != SOURCE_CONFIDENT_CORRECT)


def test_source_unseen():
    assert derive_prerequisite_diagnosis(target(), [], RELATION)["source_status"] == SOURCE_UNSEEN


def test_confident_correct_followed_by_wrong_uses_latest_evidence():
    history = [
        attempt(RELATION["source_node_id"], True, 1, 1),
        attempt(RELATION["source_node_id"], False, 2, 2),
    ]
    assert derive_prerequisite_diagnosis(target(), history, RELATION)["source_status"] == SOURCE_UNSTABLE


def test_wrong_followed_by_confident_correct_recovers_source_classification():
    history = [
        attempt(RELATION["source_node_id"], False, 1, 1),
        attempt(RELATION["source_node_id"], True, 1, 2),
    ]
    result = derive_prerequisite_diagnosis(target(), history, RELATION)
    assert result["source_status"] == SOURCE_CONFIDENT_CORRECT
    assert not result["recommended_backtrack"]


def test_future_attempt_and_unrelated_nodes_are_ignored():
    history = [
        attempt("KN9998", True, 1, 1),
        attempt(RELATION["source_node_id"], True, 1, 11),
        attempt(RELATION["source_node_id"], True, 1, 1, user="other-user"),
    ]
    result = derive_prerequisite_diagnosis(target(10), history, RELATION)
    assert result["source_status"] == SOURCE_UNSEEN
    assert result["source_question_ids"] == []


def test_medium_transfer_is_not_simulated():
    relations = get_node_relations()
    medium_transfer = next(item for item in relations if item["relation_type"] == "TRANSFER")
    transfer_target = attempt(medium_transfer["target_node_id"], False, 2, 3, "Q246")
    report = simulate_prerequisite_diagnoses([transfer_target], relations)
    assert report["target_node_attempts"] == 0
    assert report["prerequisite_relation_count"] == 12
    assert {item["relation_id"] for item in report["relations"]} == {
        f"KNR{number:04d}" for number in range(1, 14) if number != 4
    }


def test_simulation_is_deterministic_and_reports_relations_in_id_order():
    source = attempt(RELATION["source_node_id"], True, 1, 1, "Q745")
    wrong = target(2)
    relations = list(reversed(get_node_relations()))
    first = simulate_prerequisite_diagnoses([wrong, source], relations)
    second = simulate_prerequisite_diagnoses([source, wrong], relations)
    assert first == second
    assert [item["relation_id"] for item in first["relations"]] == [
        f"KNR{number:04d}" for number in range(1, 14) if number != 4
    ]
    assert first["SOURCE_CONFIDENT_CORRECT"] == 1


def test_expanded_report_includes_zero_activity_relations_and_consistent_totals():
    source = attempt(RELATION["source_node_id"], True, 1, 1, "Q745")
    correct_target = attempt(RELATION["target_node_id"], True, 1, 2, "Q1209")
    wrong_target = target(3)
    report = simulate_prerequisite_diagnoses(
        [wrong_target, source, correct_target],
        get_node_relations(),
    )

    assert report["prerequisite_relation_count"] == 12
    assert len(report["relations"]) == 12
    first = report["relations"][0]
    assert first["target_attempt_count"] == 2
    assert first["target_wrong_count"] == 1
    assert first["recommended_backtrack_true"] == 0
    assert first["recommended_backtrack_false"] == 1
    assert sum(report[status] for status in (
        SOURCE_UNSEEN,
        SOURCE_UNSTABLE,
        SOURCE_CONFIDENT_CORRECT,
        SOURCE_CONFLICT,
    )) == report["prerequisite_evaluable_target_wrong_attempts"]
    assert (
        report["recommended_backtrack_true"]
        + report["recommended_backtrack_false"]
    ) == report["prerequisite_evaluable_target_wrong_attempts"]
    assert all(item["target_attempt_count"] == 0 for item in report["relations"][1:])


class ReadOnlyCursor:
    def __init__(self):
        self.sql = []

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def execute(self, sql, params=None):
        self.sql.append((" ".join(sql.split()), params))

    def fetchall(self):
        return []


class ReadOnlyConnection:
    def __init__(self):
        self.cursor_instance = ReadOnlyCursor()

    def cursor(self):
        return self.cursor_instance


def test_database_loader_issues_select_only_and_does_not_fetch_answers():
    connection = ReadOnlyConnection()
    assert load_attempts_read_only(connection) == []
    assert len(connection.cursor_instance.sql) == 1
    sql, params = connection.cursor_instance.sql[0]
    assert sql.startswith("SELECT ")
    assert params is None
    assert all(token not in sql.upper() for token in ("INSERT", "UPDATE", "DELETE", "DDL", "TRUNCATE"))
    assert "selected_answers" not in sql
