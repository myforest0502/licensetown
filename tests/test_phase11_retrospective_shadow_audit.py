import os
from datetime import datetime, timedelta, timezone

os.environ.setdefault("OPENAI_API_KEY", "x")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "x")
os.environ.setdefault("CHANNEL_SECRET", "x")

import database
from database import get_learning_events
from phase11_retrospective_shadow_audit import (
    POLICY_LABEL,
    audit_historical_attempt_coverage,
    build_retrospective_shadow_audit,
)
from question_bank import CATEGORY_NAMES


T0 = datetime(2026, 9, 1, 0, tzinfo=timezone.utc)


def learning_event(key, hour, *, mode="study", answered_count=0, results=None):
    return {
        "event_key": key,
        "user_id": "learner",
        "mode": mode,
        "answered_count": answered_count,
        "correct_count": 0,
        "answered_at": T0 + timedelta(hours=hour),
        "question_results": results,
    }


def attempt(key, hour, q="Q1", position=1, correct=False, confidence=2, status="answered"):
    return {
        "event_key": key,
        "user_id": "learner",
        "question_id": q,
        "knowledge_node_id": "KN0001",
        "mode": "study",
        "selected_answers": [] if status == "unknown" else ["A"],
        "answer_status": status,
        "is_correct": correct,
        "confidence": None if status == "unknown" else confidence,
        "answered_at": T0 + timedelta(hours=hour),
        "attempt_position": position,
    }


def plan(key, hour, field=None, goal=10):
    return learning_event(
        key,
        hour,
        mode="recommendation_plan",
        answered_count=0,
        results={
            "activity_type": "recommendation_plan",
            "field": field or CATEGORY_NAMES[min(CATEGORY_NAMES)],
            "goal": goal,
        },
    )


def setup_function():
    database._local_learning_events.clear()
    database._local_question_attempts.clear()


def test_zero_answer_activity_events_require_no_attempt_rows():
    coverage = audit_historical_attempt_coverage(
        [learning_event("activity", 1, mode="recommendation_plan", answered_count=0, results={})],
        [],
        before=T0 + timedelta(hours=2),
    )
    assert coverage["status"] == "history_coverage_complete"


def test_answered_event_without_list_results_is_incomplete():
    coverage = audit_historical_attempt_coverage(
        [learning_event("e1", 1, answered_count=1, results={"question_id": "Q1"})],
        [attempt("e1", 1)],
        before=T0 + timedelta(hours=2),
    )
    assert coverage["status"] == "history_coverage_incomplete"


def test_missing_attempt_row_is_incomplete():
    event = learning_event(
        "e1", 1, answered_count=1,
        results=[{"question_id": "Q1", "is_correct": False, "confidence": 2}],
    )
    coverage = audit_historical_attempt_coverage([event], [], before=T0 + timedelta(hours=2))
    assert coverage["status"] == "history_coverage_incomplete"


def test_question_or_answer_mismatch_is_unreliable():
    event = learning_event(
        "e1", 1, answered_count=1,
        results=[{"question_id": "Q2", "is_correct": True, "confidence": 2}],
    )
    coverage = audit_historical_attempt_coverage(
        [event], [attempt("e1", 1, q="Q1", correct=False)], before=T0 + timedelta(hours=2)
    )
    assert coverage["status"] == "history_coverage_unreliable"


def test_matching_formal_history_is_complete():
    event = learning_event(
        "e1", 1, answered_count=1,
        results=[{"question_id": "Q1", "is_correct": False, "confidence": 2}],
    )
    coverage = audit_historical_attempt_coverage(
        [event], [attempt("e1", 1)], before=T0 + timedelta(hours=2)
    )
    assert coverage["status"] == "history_coverage_complete"
    assert coverage["matched_formal_attempts"] == 1


def test_replay_uses_stored_baseline_target_and_current_policy_label():
    audit = build_retrospective_shadow_audit([], [plan("plan", 2)])
    assert audit["policy_label"] == POLICY_LABEL
    assert audit["plan_anchor_count"] == 1
    snapshot = audit["snapshots"][0]
    assert snapshot["baseline_target"] == CATEGORY_NAMES[min(CATEGORY_NAMES)]
    assert snapshot["baseline_goal"] == 10
    assert snapshot["baseline_phase"] == "foundation"
    assert snapshot["eligible"] is True


def test_future_attempt_does_not_break_prior_snapshot_coverage():
    audit = build_retrospective_shadow_audit(
        [attempt("future", 3)],
        [plan("plan", 2), learning_event(
            "future", 3, answered_count=1,
            results=[{"question_id": "Q1", "is_correct": False, "confidence": 2}],
        )],
    )
    snapshot = audit["snapshots"][0]
    assert snapshot["historical_formal_attempt_count"] == 0
    assert snapshot["coverage_status"] == "history_coverage_complete"


def test_unknown_matching_history_is_coverage_complete_not_confirmed_weakness():
    event = learning_event(
        "e1", 1, answered_count=1,
        results=[{"question_id": "Q1", "is_correct": False, "confidence": None}],
    )
    unknown = attempt("e1", 1, status="unknown")
    audit = build_retrospective_shadow_audit([unknown], [event, plan("plan", 2)])
    snapshot = audit["snapshots"][0]
    assert snapshot["coverage_status"] == "history_coverage_complete"
    assert snapshot["shadow_reason_code"] not in {"safety_repair", "confident_wrong_cluster", "repeated_wrong_cluster"}


def test_get_learning_events_local_is_chronological_and_read_only():
    database._local_learning_events["later"] = learning_event("later", 2)
    database._local_learning_events["earlier"] = learning_event("earlier", 1)
    rows = get_learning_events("learner")
    assert [row["event_key"] for row in rows] == ["earlier", "later"]
    rows[0]["mode"] = "changed"
    assert database._local_learning_events["earlier"]["mode"] != "changed"
