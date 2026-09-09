from datetime import datetime, timedelta, timezone

from knowledge_node_state_transition import derive_knowledge_node_state


NOW = datetime(2026, 9, 9, 0, 0, tzinfo=timezone.utc)


def attempt(question, correct, confidence, at, *, node="KN0268", status="answered"):
    return {
        "id": int(at.timestamp()),
        "event_key": f"event-{question}-{int(at.timestamp())}",
        "user_id": "learner",
        "question_id": question,
        "knowledge_node_id": node,
        "is_correct": correct,
        "confidence": confidence,
        "answer_status": status,
        "attempted_at": at,
        "attempt_position": 1,
    }


def repaired_history():
    return [
        attempt("Q269", False, 2, NOW),
        attempt("Q361", True, 1, NOW + timedelta(minutes=1)),
    ]


def test_repair_confirmation_schedules_day3_not_day7():
    history = repaired_history()
    repaired_at = NOW + timedelta(minutes=1)

    before = derive_knowledge_node_state(
        history, as_of=repaired_at + timedelta(days=2, hours=23)
    )
    assert before["state"] == "repaired"
    assert before["retention_stage"] == "repair_confirmed"
    assert before["retention_checkpoint"] == "day3"
    assert before["next_review_at"] == repaired_at + timedelta(days=3)

    due = derive_knowledge_node_state(
        history, as_of=repaired_at + timedelta(days=3)
    )
    assert due["state"] == "recheck_due"
    assert due["retention_checkpoint"] == "day3"


def test_day3_day7_day30_successes_reach_stable():
    repaired_at = NOW + timedelta(minutes=1)
    day3 = repaired_at + timedelta(days=3)
    day7 = repaired_at + timedelta(days=7)
    day30 = repaired_at + timedelta(days=30)

    history = repaired_history()
    history.append(attempt("Q269", True, 1, day3))
    after_day3 = derive_knowledge_node_state(history, as_of=day3)
    assert after_day3["state"] == "repaired"
    assert after_day3["retention_stage"] == "day3_passed"
    assert after_day3["retention_checkpoint"] == "day7"
    assert after_day3["next_review_at"] == day7

    history.append(attempt("Q361", True, 1, day7))
    after_day7 = derive_knowledge_node_state(history, as_of=day7)
    assert after_day7["state"] == "repaired"
    assert after_day7["retention_stage"] == "day7_passed"
    assert after_day7["retention_checkpoint"] == "day30"
    assert after_day7["next_review_at"] == day30

    history.append(attempt("Q269", True, 1, day30))
    after_day30 = derive_knowledge_node_state(history, as_of=day30)
    assert after_day30["state"] == "stable"
    assert after_day30["retention_stage"] == "durable"
    assert after_day30["retention_checkpoint"] is None
    assert after_day30["next_review_at"] is None


def test_one_late_correct_cannot_skip_multiple_retention_checkpoints():
    repaired_at = NOW + timedelta(minutes=1)
    late = repaired_at + timedelta(days=31)
    history = repaired_history() + [attempt("Q269", True, 1, late)]

    result = derive_knowledge_node_state(history, as_of=late)
    assert result["state"] == "recheck_due"
    assert result["retention_stage"] == "day3_passed"
    assert result["retention_checkpoint"] == "day7"


def test_wrong_at_retention_checkpoint_starts_new_repair_cycle():
    repaired_at = NOW + timedelta(minutes=1)
    day3 = repaired_at + timedelta(days=3)
    history = repaired_history() + [attempt("Q269", False, 1, day3)]

    result = derive_knowledge_node_state(history, as_of=day3)
    assert result["state"] == "repairing"
    assert result["retention_stage"] is None
    assert result["retention_checkpoint"] is None
    assert result["next_review_at"] is None


def test_same_question_correct_does_not_confirm_initial_repair():
    history = [
        attempt("Q269", False, 2, NOW),
        attempt("Q269", True, 1, NOW + timedelta(minutes=1)),
    ]
    result = derive_knowledge_node_state(history)
    assert result["state"] == "repairing"
    assert result["retention_stage"] is None
