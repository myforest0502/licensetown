from datetime import datetime, timedelta, timezone

import pytest

from knowledge_node_relations import get_node_relations, get_reviewed_node_relations
from prerequisite_backtrack import (
    select_prerequisite_backtrack_candidate,
    simulate_prerequisite_backtrack_selection,
)
from prerequisite_diagnosis import (
    SOURCE_CONFIDENT_CORRECT,
    SOURCE_CONFLICT,
    SOURCE_UNSEEN,
    SOURCE_UNSTABLE,
)
from scripts.simulate_prerequisite_backtrack_selection import run_simulation


NOW = datetime(2026, 8, 29, tzinfo=timezone.utc)
RELATION = get_reviewed_node_relations()[0]


def attempt(question, correct, confidence, minute, node=None, user="user-a"):
    return {
        "id": minute + 100,
        "event_key": f"event-{minute:03d}",
        "user_id": user,
        "question_id": question,
        "knowledge_node_id": node or RELATION["source_node_id"],
        "is_correct": correct,
        "confidence": confidence,
        "answered_at": NOW + timedelta(minutes=minute),
        "attempt_position": 1,
    }


def diagnosis(status=SOURCE_UNSTABLE, relation=RELATION):
    return {"relation_id": relation["relation_id"], "source_status": status}


@pytest.mark.parametrize("status", [SOURCE_UNSEEN, SOURCE_UNSTABLE, SOURCE_CONFLICT])
def test_backtrack_statuses_select_source_candidate(status):
    result = select_prerequisite_backtrack_candidate(diagnosis(status), RELATION, [])
    assert result["backtrack"]
    assert result["candidate_question_id"] in RELATION["source_question_ids"]


def test_confident_correct_repairs_target_instead_of_backtracking():
    result = select_prerequisite_backtrack_candidate(
        diagnosis(SOURCE_CONFIDENT_CORRECT), RELATION, []
    )
    assert not result["backtrack"]
    assert result["candidate_question_id"] is None
    assert result["candidate_reason"] == "target_self_repair"


def multi_question_relation():
    relation = dict(RELATION)
    relation["relation_id"] = "KNR9999"
    relation["source_question_ids"] = ["Q40", "Q10", "Q30", "Q20"]
    return relation


def test_source_priority_and_deterministic_question_order():
    relation = multi_question_relation()
    history = [
        attempt("Q10", False, 1, 1),
        attempt("Q20", True, 2, 2),
        attempt("Q30", True, 1, 3),
    ]
    first = select_prerequisite_backtrack_candidate(
        diagnosis(SOURCE_UNSTABLE, relation), relation, reversed(history)
    )
    second = select_prerequisite_backtrack_candidate(
        diagnosis(SOURCE_UNSTABLE, relation), relation, history
    )
    assert first == second
    assert first["candidate_question_id"] == "Q40"
    assert first["candidate_reason"] == "unanswered_source"


@pytest.mark.parametrize(("histories", "expected", "reason"), [
    ({"Q10": (False, 1), "Q20": (True, 2), "Q30": (True, 1)}, "Q10", "previously_wrong_source"),
    ({"Q10": (True, 3), "Q20": (True, 2), "Q30": (True, 1)}, "Q10", "uncertain_or_guessed_correct_source"),
    ({"Q10": (True, 1), "Q20": (True, 1), "Q30": (True, 1)}, "Q10", "confident_correct_source"),
])
def test_answered_source_priority(histories, expected, reason):
    relation = multi_question_relation()
    relation["source_question_ids"] = sorted(histories)
    attempts = [
        attempt(question, correct, confidence, index)
        for index, (question, (correct, confidence)) in enumerate(histories.items(), 1)
    ]
    result = select_prerequisite_backtrack_candidate(
        diagnosis(SOURCE_UNSTABLE, relation), relation, attempts
    )
    assert result["candidate_question_id"] == expected
    assert result["candidate_reason"] == reason


def test_relation_external_questions_are_never_selected():
    result = select_prerequisite_backtrack_candidate(
        diagnosis(), RELATION, [attempt("Q999", False, 1, 1)]
    )
    assert result["candidate_question_id"] in RELATION["source_question_ids"]
    assert result["candidate_question_id"] != "Q999"


def test_bank_coverage_uses_twelve_formal_prerequisites_and_excludes_transfer():
    report = simulate_prerequisite_backtrack_selection([], get_node_relations())
    assert report["bank_coverage"] == {
        "relation_count": 12,
        "relations_with_source_questions": 12,
        "relations_with_target_questions": 12,
        "relations_ready_for_backtrack": 12,
        "source_question_count_distribution": {1: 10, 2: 2},
        "target_question_count_distribution": {1: 12},
    }
    assert len(report["relations"]) == 12
    assert all(item["historical_target_attempts"] == 0 for item in report["relations"])


def test_mip_q386_wrong_selects_q260():
    relation = next(item for item in get_reviewed_node_relations() if item["relation_id"] == "KNR0003")
    source = attempt("Q260", True, 2, 1, relation["source_node_id"])
    target = attempt("Q386", False, 2, 2, relation["target_node_id"])
    report = simulate_prerequisite_backtrack_selection([source, target], [relation])
    example = report["examples"][0]
    assert example["diagnosis"] == SOURCE_UNSTABLE
    assert example["backtrack"]
    assert example["source_candidate_question_id"] == "Q260"


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


def test_simulation_db_access_is_select_only():
    connection = ReadOnlyConnection()
    report = run_simulation(connection)
    assert report["bank_coverage"]["relation_count"] == 12
    assert len(connection.cursor_instance.sql) == 1
    sql, params = connection.cursor_instance.sql[0]
    assert sql.startswith("SELECT ")
    assert params is None
    assert all(word not in sql.upper() for word in (
        "INSERT", "UPDATE", "DELETE", "TRUNCATE", "CREATE", "ALTER", "DROP"
    ))
