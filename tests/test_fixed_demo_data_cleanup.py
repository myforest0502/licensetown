from datetime import datetime, timedelta, timezone
import os

import pytest

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "test-token")
os.environ.setdefault("CHANNEL_SECRET", "test-secret")

import goukaku_ui
from app import app
from dashboard_settings import (
    SYSTEM_DEFAULT_EXAM_DATE,
    get_daily_question_goal,
    get_effective_exam_date,
    get_reward_progress,
    tokyo_today,
)
from goukaku_ui import create_dashboard_token
from learning_milestones import build_learning_milestones


def _attempt(index, *, user_id="learner", timestamp=None):
    return {
        "user_id": user_id,
        "question_id": f"Q{index}",
        "answered_at": timestamp or datetime(2026, 1, 1, index % 24, tzinfo=timezone.utc),
        "event_key": f"event-{index:04d}",
        "attempt_position": index,
    }


def test_dashboard_settings_have_safe_defaults_and_jst_boundary(monkeypatch):
    monkeypatch.delenv("DEFAULT_EXAM_DATE", raising=False)
    monkeypatch.delenv("DEFAULT_DAILY_QUESTION_GOAL", raising=False)
    assert get_effective_exam_date() == SYSTEM_DEFAULT_EXAM_DATE
    assert get_daily_question_goal() == 30
    assert tokyo_today(datetime(2026, 8, 30, 15, 30, tzinfo=timezone.utc)).isoformat() == "2026-08-31"


def test_explicit_unset_exam_date_and_invalid_goal_are_safe(monkeypatch):
    monkeypatch.setenv("DEFAULT_EXAM_DATE", "")
    monkeypatch.setenv("DEFAULT_DAILY_QUESTION_GOAL", "invalid")
    assert get_effective_exam_date() is None
    assert get_daily_question_goal() == 30
    dashboard = goukaku_ui.build_dashboard()
    assert dashboard["exam_date"] is None
    assert dashboard["days_until_exam"] is None


@pytest.mark.parametrize(
    ("answers", "next_answers", "progress"),
    [(0, 100, 0), (99, 1, 99), (100, 100, 0), (101, 99, 1)],
)
def test_reward_interval_is_centralized_without_changing_behavior(answers, next_answers, progress):
    result = get_reward_progress(answers)
    assert result == {
        "reward_interval": 100,
        "next_reward_answers": next_answers,
        "reward_progress": progress,
    }


def test_milestones_use_exact_attempt_timestamps_and_jst_dates():
    first = datetime(2026, 8, 30, 15, 30, tzinfo=timezone.utc)
    attempts = [_attempt(i, timestamp=first + timedelta(minutes=i - 1)) for i in range(1, 101)]
    events = build_learning_milestones(attempts)
    assert [event["event_type"] for event in events] == ["learning_started", "answers_100"]
    assert events[0]["occurred_at"] == first
    assert events[0]["display_date"] == "2026年08月31日"
    assert events[1]["occurred_at"] == attempts[99]["answered_at"]


def test_milestones_do_not_infer_unverifiable_events_or_thresholds():
    events = build_learning_milestones([_attempt(i) for i in range(1, 100)])
    assert [event["event_type"] for event in events] == ["learning_started"]
    assert not ({"first_repaired", "first_stable", "streak_7"} & {e["event_type"] for e in events})
    assert build_learning_milestones([]) == []


@pytest.mark.parametrize(("count", "event_type"), [(500, "answers_500"), (1000, "answers_1000")])
def test_answer_milestones_require_the_exact_saved_attempt_threshold(count, event_type):
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    attempts = [_attempt(i, timestamp=start + timedelta(minutes=i)) for i in range(1, count + 1)]
    events = build_learning_milestones(attempts)
    assert event_type in {event["event_type"] for event in events}
    assert next(event for event in events if event["event_type"] == event_type)["occurred_at"] == attempts[-1]["answered_at"]


def test_milestones_reject_mixed_users():
    with pytest.raises(ValueError, match="one user"):
        build_learning_milestones([_attempt(1, user_id="a"), _attempt(2, user_id="b")])


def test_first_repaired_and_stable_use_exact_formal_transition_timestamps():
    start = datetime(2026, 6, 1, tzinfo=timezone.utc)
    history = [
        {**_attempt(269, timestamp=start), "knowledge_node_id": "KN0268", "is_correct": False, "confidence": 2},
        {**_attempt(361, timestamp=start + timedelta(days=1)), "knowledge_node_id": "KN0268", "is_correct": True, "confidence": 1},
        {**_attempt(269, timestamp=start + timedelta(days=9)), "knowledge_node_id": "KN0268", "is_correct": True, "confidence": 1},
    ]
    events = {event["event_type"]: event for event in build_learning_milestones(history)}
    assert events["first_repaired"]["occurred_at"] == start + timedelta(days=1)
    assert events["first_stable"]["occurred_at"] == start + timedelta(days=9)


def test_footprints_use_token_user_real_attempts_and_preserve_return_token(monkeypatch):
    token = create_dashboard_token("footprint-user")
    timestamp = datetime(2026, 8, 20, 1, 0, tzinfo=timezone.utc)
    seen = []

    def fake_attempts(user_id):
        seen.append(user_id)
        return [_attempt(1, user_id=user_id, timestamp=timestamp)]

    monkeypatch.setattr(goukaku_ui, "get_question_attempts", fake_attempts)
    text = app.test_client().get(
        f"/goukaku-no-michi/footprints?token={token}"
    ).get_data(as_text=True)
    assert seen == ["footprint-user"]
    assert "学習を始めました" in text
    assert "2026年08月20日" in text
    assert f"/goukaku-no-michi?token={token}" in text


def test_dashboard_footprint_link_preserves_dashboard_token():
    token = create_dashboard_token("footprint-link-user")
    text = app.test_client().get(f"/goukaku-no-michi?token={token}").get_data(as_text=True)
    assert f"/goukaku-no-michi/footprints?token={token}" in text
