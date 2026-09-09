from datetime import datetime, timedelta, timezone

from companion_record import build_companion_record


NOW = datetime(2026, 9, 1, tzinfo=timezone.utc)


def attempt(user, node, question, correct, confidence, minute, *, answer_status="answered"):
    return {
        "id": minute + 1,
        "event_key": f"event-{user}-{minute}",
        "user_id": user,
        "question_id": question,
        "knowledge_node_id": node,
        "is_correct": correct,
        "confidence": confidence,
        "answer_status": answer_status,
        "attempted_at": NOW + timedelta(minutes=minute),
        "attempt_position": 1,
    }


def test_record_uses_formal_repair_transition_and_is_not_persisted():
    record = build_companion_record([
        attempt("u", "KN0268", "Q269", False, 2, 1),
        attempt("u", "KN0268", "Q361", True, 1, 2),
    ])
    assert record["persisted"] is False
    assert record["authoritative_attempt_source"] == "question_attempts"
    assert record["episode_count"] == 1
    episode = record["episodes"][0]
    assert episode["current_state"] == "repaired"
    assert [item["event"] for item in episode["events"]] == [
        "weakness_detected",
        "repair_confirmed",
    ]


def test_confident_wrong_is_high_priority_reason():
    record = build_companion_record([
        attempt("u", "KN0268", "Q269", False, 1, 1),
    ])
    assert record["episodes"][0]["priority_reason"] == "confident_wrong"


def test_repeated_wrong_reason_uses_existing_formal_evidence():
    record = build_companion_record([
        attempt("u", "KN0268", "Q269", False, 2, 1),
        attempt("u", "KN0268", "Q269", False, 2, 2),
    ])
    assert record["episodes"][0]["priority_reason"] == "repeated_wrong"
    assert record["episodes"][0]["current_state"] == "repairing"


def test_repaired_episode_becomes_recheck_due_from_as_of_without_fake_attempt():
    history = [
        attempt("u", "KN0268", "Q269", False, 2, 1),
        attempt("u", "KN0268", "Q361", True, 1, 2),
    ]
    record = build_companion_record(history, as_of=NOW + timedelta(days=8))
    episode = record["episodes"][0]
    assert episode["current_state"] == "recheck_due"
    assert episode["events"][-1]["event"] == "retention_recheck_due"
    assert episode["events"][-1]["state_after"] == "recheck_due"


def test_regression_after_repair_is_explicit_episode_event():
    record = build_companion_record([
        attempt("u", "KN0268", "Q269", False, 2, 1),
        attempt("u", "KN0268", "Q361", True, 1, 2),
        attempt("u", "KN0268", "Q269", False, 1, 3),
    ])
    episode = record["episodes"][0]
    assert episode["current_state"] == "repairing"
    assert episode["events"][-1]["event"] == "regression_detected"


def test_correct_only_checking_nodes_are_omitted_by_default():
    history = [attempt("u", "KN0268", "Q269", True, 1, 1)]
    assert build_companion_record(history)["episode_count"] == 0
    assert build_companion_record(history, include_checking_only=True)["episode_count"] == 1


def test_multiple_users_are_rejected():
    history = [
        attempt("a", "KN0268", "Q269", False, 2, 1),
        attempt("b", "KN0268", "Q269", False, 2, 2),
    ]
    try:
        build_companion_record(history)
    except ValueError as exc:
        assert "one user" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_exact_official_repeat_cross_node_stays_one_episode():
    # Q1411/Q1585 are reviewed exact official repeats and must share the same
    # derived evidence Node even though their raw historical Nodes differ.
    record = build_companion_record([
        attempt("u", "KN1387", "Q1411", False, 2, 1),
        attempt("u", "KN0659", "Q1585", True, 1, 2),
    ])
    assert record["episode_count"] == 1
    episode = record["episodes"][0]
    assert episode["canonical_node_id"] == "KN1387"
    # Equivalent Q IDs are not strong different-question evidence, so this
    # cannot falsely mark repair as confirmed.
    assert episode["current_state"] == "repairing"
    assert episode["repair_confirmation_count"] == 0
