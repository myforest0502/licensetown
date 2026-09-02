from datetime import datetime, timedelta, timezone

import field_evidence
import knowledge_node_state_transition as transition
from field_evidence import build_field_evidence
from question_bank import get_category_small, get_question_tag


BASE = datetime(2026, 8, 30, tzinfo=timezone.utc)


def attempt(q, node, correct, confidence, minute, *, status="answered", user="u"):
    return {
        "user_id": user,
        "question_id": q,
        "knowledge_node_id": node,
        "is_correct": correct,
        "confidence": confidence,
        "selected_answers": [] if status == "unknown" else ["1"],
        "answer_status": status,
        "answered_at": BASE + timedelta(minutes=minute),
        "event_key": f"e-{minute}",
        "attempt_position": 1,
    }


def by_field(report, field_id):
    return next(item for item in report["fields"] if item["field_id"] == field_id)


def test_empty_user_returns_all_fields_and_formal_totals():
    report = build_field_evidence([])
    assert report["status"] == "evidence_only"
    assert report["official_mastery_score"] is None
    assert report["field_count"] == len(report["fields"]) == 18
    assert report["question_total"] == sum(x["total_question_count"] for x in report["fields"]) == 1640
    assert report["canonical_node_total"] == 1509
    assert report["multi_field_node_count"] == 14
    assert report["canonical_node_membership_total"] > report["canonical_node_total"]
    assert all(x["attempted_canonical_node_count"] == 0 for x in report["fields"])
    assert all(x["unseen_node_count"] == x["total_canonical_node_count"] for x in report["fields"])


def test_single_answer_and_confidence_unknown_evidence():
    node = get_question_tag("Q1")["knowledge_node_id"]
    field_id = get_category_small("Q1")
    report = build_field_evidence([
        attempt("Q1", node, True, 1, 1),
        attempt("Q1", node, True, 2, 2),
        attempt("Q1", node, True, 3, 3),
        attempt("Q1", node, False, None, 4, status="unknown"),
    ])
    item = by_field(report, field_id)
    assert item["answered_unique_question_count"] == 1
    assert item["question_coverage"]["status"] == "candidate_metric"
    assert item["confidence_counts"] == {"1": 1, "2": 1, "3": 1}
    assert item["unknown_answer_count"] == 1
    assert item["repairing_node_count"] == 1


def test_unknown_attempts_do_not_create_field_repeated_weakness():
    field_id = get_category_small("Q1091")
    report = build_field_evidence([
        attempt("Q1091", "KN1080", False, None, 1, status="unknown"),
        attempt("Q1091", "KN1080", False, None, 2, status="unknown"),
        attempt("Q1544", "KN1518", False, None, 3, status="unknown"),
    ])
    item = by_field(report, field_id)
    assert item["unknown_answer_count"] == 3
    assert item["question_answer_count"] == 3
    assert item["repeated_weakness_evidence_count"] == 0
    assert "REPEATED_SAME_QUESTION_WRONG" not in item["repeated_weakness_evidence_levels"]
    assert "CROSS_QUESTION_WRONG" not in item["repeated_weakness_evidence_levels"]


def test_real_wrong_plus_unknown_does_not_become_repeated_field_weakness():
    field_id = get_category_small("Q1091")
    report = build_field_evidence([
        attempt("Q1091", "KN1080", False, 2, 1),
        attempt("Q1544", "KN1518", False, None, 2, status="unknown"),
    ])
    item = by_field(report, field_id)
    assert item["unknown_answer_count"] == 1
    assert item["question_answer_count"] == 2
    assert item["repeated_weakness_evidence_count"] == 0


def test_two_real_wrong_attempts_still_create_field_repeated_weakness():
    node = get_question_tag("Q1")["knowledge_node_id"]
    field_id = get_category_small("Q1")
    report = build_field_evidence([
        attempt("Q1", node, False, 2, 1),
        attempt("Q1", node, False, 2, 2),
    ])
    item = by_field(report, field_id)
    assert item["unknown_answer_count"] == 0
    assert item["question_answer_count"] == 2
    assert item["repeated_weakness_evidence_count"] == 1
    assert item["repeated_weakness_evidence_levels"]["REPEATED_SAME_QUESTION_WRONG"] == 1


def test_same_question_does_not_repair_but_strong_different_question_does():
    same = build_field_evidence([
        attempt("Q269", "KN0268", False, 2, 1),
        attempt("Q269", "KN0268", True, 1, 2),
    ])
    field_id = get_category_small("Q269")
    assert by_field(same, field_id)["repairing_node_count"] == 1

    repaired = build_field_evidence([
        attempt("Q269", "KN0268", False, 2, 1),
        attempt("Q361", "KN0268", True, 1, 2),
    ])
    item = by_field(repaired, field_id)
    assert item["repaired_node_count"] == 1
    assert item["retention_target_node_count"] == 1
    assert item["different_question_repair_confirmation_count"] == 1


def test_retention_replay_reports_due_and_stable(monkeypatch):
    history = [
        attempt("Q269", "KN0268", False, 2, 1),
        attempt("Q361", "KN0268", True, 1, 2),
    ]
    field_id = get_category_small("Q269")
    due = build_field_evidence(history, as_of=BASE + timedelta(days=8))
    assert by_field(due, field_id)["recheck_due_node_count"] == 1

    monkeypatch.setattr(transition, "classify_repair_confirmation", lambda old, new: (
        "same_question" if old == new else "different_question_strong"
    ))
    retention_check = attempt("Q3", "KN0268", True, 1, 3)
    retention_check["answered_at"] = BASE + timedelta(days=8)
    stable = build_field_evidence(history + [retention_check])
    item = by_field(stable, field_id)
    assert item["stable_node_count"] == item["retention_target_node_count"] == 1
    assert item["retention_nodes"][0]["next_review_at"] == (BASE + timedelta(days=38)).isoformat()


def test_repeated_weakness_and_canonical_aliases_are_aggregated():
    field_id = get_category_small("Q1091")
    report = build_field_evidence([
        attempt("Q1091", "KN1080", False, 2, 1),
        attempt("Q1544", "KN1518", False, 2, 2),
    ])
    item = by_field(report, field_id)
    assert item["attempted_canonical_node_count"] == 1
    assert item["repairing_node_count"] == 1
    assert item["repeated_weakness_evidence_count"] == 1
    assert item["repeated_weakness_evidence_levels"]["CROSS_QUESTION_WRONG"] == 1


def test_multi_field_nodes_are_explicitly_duplicated_for_evidence():
    multi = next(item for item in build_field_evidence([])["multi_field_nodes"] if item["canonical_node_id"] == "KN0609")
    assert len(multi["field_ids"]) == 3
    report = build_field_evidence([
        attempt("Q1225", "KN1210", False, 2, 1),
    ])
    for field_id in multi["field_ids"]:
        item = by_field(report, field_id)
        assert "KN0609" in item["multi_field_canonical_node_ids"]
        assert item["attempted_canonical_node_count"] == 1
        assert item["repairing_node_count"] == 1
    assert report["multi_field_membership_policy"].startswith("duplicated")


def test_read_only_adapter_uses_attempt_loader_once(monkeypatch):
    calls = []
    monkeypatch.setattr(field_evidence, "get_question_attempts", lambda user_id: calls.append(user_id) or [])
    result = field_evidence.get_user_field_evidence("learner")
    assert calls == ["learner"]
    assert result["field_count"] == 18


def test_mixed_users_are_rejected():
    node = get_question_tag("Q1")["knowledge_node_id"]
    try:
        build_field_evidence([
            attempt("Q1", node, True, 1, 1, user="a"),
            attempt("Q1", node, True, 1, 2, user="b"),
        ])
    except ValueError as exc:
        assert "one user" in str(exc)
    else:
        raise AssertionError("mixed user histories must not be aggregated")
