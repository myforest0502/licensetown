from datetime import datetime, timedelta, timezone

from knowledge_node_weakness_evidence import derive_repeated_weakness_evidence
from scripts.simulate_repeated_cross_question_weakness import (
    build_report,
    load_attempts_read_only,
)


NOW = datetime(2026, 8, 29, tzinfo=timezone.utc)


def attempt(user, node, question, correct, confidence, minute):
    return {
        "id": minute + 1,
        "event_key": f"event-{user}-{minute}",
        "user_id": user,
        "question_id": question,
        "knowledge_node_id": node,
        "is_correct": correct,
        "confidence": confidence,
        "attempted_at": NOW + timedelta(minutes=minute),
        "attempt_position": 1,
    }


def one(*attempts):
    result = derive_repeated_weakness_evidence(attempts)
    assert len(result) == 1
    assert "user_id" not in result[0]
    return result[0]


def test_one_question_one_wrong_is_single_wrong():
    assert one(attempt("u", "KN1080", "Q1091", False, 2, 1))["evidence_level"] == "SINGLE_WRONG"


def test_same_question_twice_wrong_is_not_cross_question():
    item = one(
        attempt("u", "KN1080", "Q1091", False, 2, 1),
        attempt("u", "KN1518", "Q1091", False, 1, 2),
    )
    assert item["evidence_level"] == "REPEATED_SAME_QUESTION_WRONG"
    assert item["wrong_question_count"] == 1


def test_kn1080_fixture_is_cross_question_wrong():
    item = one(
        attempt("u", "KN1080", "Q1091", False, 2, 1),
        attempt("u", "KN1518", "Q1544", False, 2, 2),
    )
    assert item["canonical_node_id"] == "KN1080"
    assert item["wrong_question_count"] == 2
    assert item["evidence_level"] == "CROSS_QUESTION_WRONG"


def test_cross_question_confident_wrong_is_stronger():
    item = one(
        attempt("u", "KN1080", "Q1091", False, 2, 1),
        attempt("u", "KN1518", "Q1544", False, 1, 2),
    )
    assert item["evidence_level"] == "CROSS_QUESTION_CONFIDENT_WRONG"
    assert item["confident_wrong_count"] == 1


def test_wrong_then_other_question_correct_is_mixed():
    item = one(
        attempt("u", "KN1080", "Q1091", False, 2, 1),
        attempt("u", "KN1518", "Q1544", True, 1, 2),
    )
    assert item["evidence_level"] == "MIXED_EVIDENCE"


def test_correct_then_other_question_wrong_is_mixed_and_order_independent_input():
    item = one(
        attempt("u", "KN1518", "Q1544", False, 2, 2),
        attempt("u", "KN1080", "Q1091", True, 1, 1),
    )
    assert item["evidence_level"] == "MIXED_EVIDENCE"


def test_attempted_at_controls_first_and_last_wrong_order():
    item = one(
        attempt("u", "KN1518", "Q1544", False, 2, 2),
        attempt("u", "KN1080", "Q1091", False, 2, 1),
    )
    assert item["first_wrong_question_id"] == "Q1091"
    assert item["last_wrong_question_id"] == "Q1544"


def test_users_and_unrelated_nodes_are_not_mixed():
    records = derive_repeated_weakness_evidence([
        attempt("user-a", "KN1080", "Q1091", False, 2, 1),
        attempt("user-b", "KN1518", "Q1544", False, 2, 2),
        attempt("user-a", "KN0597", "Q605", False, 2, 3),
    ])
    assert len(records) == 3
    assert all(item["evidence_level"] == "SINGLE_WRONG" for item in records)


def test_report_counts_levels_and_keeps_kn1080_anonymous():
    report = build_report([
        attempt("secret-user", "KN1080", "Q1091", False, 2, 1),
        attempt("secret-user", "KN1518", "Q1544", False, 2, 2),
    ])
    assert report["evidence_level_counts"]["CROSS_QUESTION_WRONG"] == 1
    assert report["kn1080"][0]["evidence_level"] == "CROSS_QUESTION_WRONG"
    assert "secret-user" not in str(report)


class ReadOnlyCursor:
    def __init__(self):
        self.statements = []

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def execute(self, sql, params=None):
        self.statements.append((" ".join(sql.split()), params))

    def fetchall(self):
        return []


class ReadOnlyConnection:
    def __init__(self):
        self.cursor_instance = ReadOnlyCursor()

    def cursor(self):
        return self.cursor_instance


def test_loader_is_select_only():
    connection = ReadOnlyConnection()
    assert load_attempts_read_only(connection) == []
    sql, params = connection.cursor_instance.statements[0]
    assert sql.startswith("SELECT ")
    assert params is None
    assert all(word not in sql.upper() for word in (
        "INSERT", "UPDATE", "DELETE", "TRUNCATE", "ALTER", "CREATE", "DROP",
    ))
