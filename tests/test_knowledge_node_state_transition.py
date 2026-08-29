from datetime import datetime, timedelta, timezone

from knowledge_node_state_transition import (
    derive_all_user_node_states,
    derive_knowledge_node_state,
    derive_state_timeline,
    is_recheck_due,
)
from scripts.simulate_knowledge_node_state_transitions import (
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


def state(*items):
    return derive_knowledge_node_state(items)["state"]


def test_unseen():
    assert derive_knowledge_node_state([], "KN1080")["state"] == "unseen"


def test_first_correct_is_checking():
    assert state(attempt("u", "KN1080", "Q1091", True, 1, 1)) == "checking"


def test_first_wrong_is_repairing():
    assert state(attempt("u", "KN1080", "Q1091", False, 2, 1)) == "repairing"


def test_same_question_wrong_then_correct_stays_repairing():
    assert state(
        attempt("u", "KN1080", "Q1091", False, 2, 1),
        attempt("u", "KN1080", "Q1091", True, 1, 2),
    ) == "repairing"


def test_different_question_confidence_two_correct_does_not_repair():
    assert state(
        attempt("u", "KN1080", "Q1091", False, 2, 1),
        attempt("u", "KN1518", "Q1544", True, 2, 2),
    ) == "repairing"


def test_different_question_confidence_one_correct_repairs():
    result = derive_knowledge_node_state([
        attempt("u", "KN0268", "Q269", False, 2, 1),
        attempt("u", "KN0268", "Q361", True, 1, 2),
    ])
    assert result["state"] == "repaired"
    assert result["confident_correct_after_wrong_count"] == 1


def test_same_day_additional_confident_correct_never_becomes_stable():
    assert state(
        attempt("u", "KN0268", "Q269", False, 2, 1),
        attempt("u", "KN0268", "Q361", True, 1, 2),
        attempt("u", "KN0268", "Q361", True, 1, 3),
    ) == "repaired"


def test_stable_then_wrong_returns_to_repairing():
    assert state(
        attempt("u", "KN0268", "Q269", False, 2, 1),
        attempt("u", "KN0268", "Q361", True, 1, 2),
        attempt("u", "KN0268", "Q269", False, 1, 4),
    ) == "repairing"


def test_cross_question_wrong_is_repairing():
    result = derive_knowledge_node_state([
        attempt("u", "KN1080", "Q1091", False, 2, 1),
        attempt("u", "KN1518", "Q1544", False, 2, 2),
    ])
    assert result["evidence_level"] == "CROSS_QUESTION_WRONG"
    assert result["state"] == "repairing"


def test_cross_question_confident_wrong_is_repairing():
    result = derive_knowledge_node_state([
        attempt("u", "KN1080", "Q1091", False, 2, 1),
        attempt("u", "KN1518", "Q1544", False, 1, 2),
    ])
    assert result["evidence_level"] == "CROSS_QUESTION_CONFIDENT_WRONG"
    assert result["state"] == "repairing"


def test_aliases_are_canonicalized_and_users_are_not_mixed():
    records = derive_all_user_node_states([
        attempt("a", "KN0268", "Q269", False, 2, 1),
        attempt("a", "KN0268", "Q361", True, 1, 2),
        attempt("b", "KN0268", "Q361", True, 1, 3),
    ])
    assert len(records) == 2
    assert {item["canonical_node_id"] for item in records} == {"KN0268"}
    assert sorted(item["state"] for item in records) == ["checking", "repaired"]


def test_timeline_has_no_future_leakage():
    timeline = derive_state_timeline([
        attempt("u", "KN0268", "Q269", False, 2, 1),
        attempt("u", "KN0268", "Q361", True, 1, 2),
    ])
    assert [item["state"] for item in timeline] == ["repairing", "repaired"]


def test_recheck_due_intervals_are_state_specific():
    assert is_recheck_due("stable", NOW, NOW + timedelta(days=30))
    assert is_recheck_due("repaired", NOW, NOW + timedelta(days=7))
    report = build_report([])
    assert report["state_counts"]["recheck_due"] == 0
    assert report["recheck_due_policy"]["implemented_in_production"] is True


def test_repaired_becomes_due_but_never_stable_from_time_alone():
    history = [
        attempt("u", "KN0268", "Q269", False, 2, 1),
        attempt("u", "KN0268", "Q361", True, 1, 2),
    ]
    assert derive_knowledge_node_state(history, as_of=NOW + timedelta(days=31))["state"] == "recheck_due"


def test_different_question_with_same_demand_is_weak_and_does_not_repair():
    assert state(
        attempt("u", "KN1080", "Q1091", False, 2, 1),
        attempt("u", "KN1518", "Q1544", True, 1, 2),
    ) == "repairing"


def test_different_question_confidence_three_correct_does_not_repair():
    assert state(
        attempt("u", "KN0268", "Q269", False, 2, 1),
        attempt("u", "KN0268", "Q361", True, 3, 2),
    ) == "repairing"


def test_unknown_answer_is_wrong_evidence():
    item = attempt("u", "KN0001", "Q1", True, None, 1)
    item["answer_status"] = "unknown"
    assert derive_knowledge_node_state([item])["state"] == "repairing"


def test_repaired_then_unknown_returns_to_repairing():
    unknown = attempt("u", "KN0268", "Q269", True, None, 3)
    unknown["answer_status"] = "unknown"
    assert state(
        attempt("u", "KN0268", "Q269", False, 2, 1),
        attempt("u", "KN0268", "Q361", True, 1, 2),
        unknown,
    ) == "repairing"


def test_simulation_reports_kn1080_and_raw_unseen_slots_anonymously():
    report = build_report([
        attempt("secret-user", "KN1080", "Q1091", False, 2, 1),
        attempt("secret-user", "KN1518", "Q1544", False, 2, 2),
    ])
    assert report["state_counts"]["repairing"] == 1
    assert report["attempted_raw_node_slots"] == 2
    assert report["unseen_raw_node_slots"] == report["registry_node_count"] - 2
    assert report["kn1080"][0]["state"] == "repairing"
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


def test_simulation_loader_is_select_only():
    connection = ReadOnlyConnection()
    assert load_attempts_read_only(connection) == []
    sql, params = connection.cursor_instance.statements[0]
    assert sql.startswith("SELECT ")
    assert params is None
    assert all(word not in sql.upper() for word in (
        "INSERT", "UPDATE", "DELETE", "TRUNCATE", "ALTER", "CREATE", "DROP",
    ))
