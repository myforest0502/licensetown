import copy
from datetime import date, datetime, timedelta, timezone
import os
from types import SimpleNamespace

import pytest

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "test-token")
os.environ.setdefault("CHANNEL_SECRET", "test-secret")

import app as app_module
import database
from database import (
    calculate_learning_streak,
    get_learning_activity,
    record_learning_batch,
    set_supporter_link,
    user_names,
)
from goukaku_ui import build_dashboard, create_supporter_token
from supporter_report import build_supporter_report


def clear_local_data():
    database._local_learning_events.clear()
    database._local_learning_seconds.clear()
    database._local_learning_time_events.clear()
    database._local_supporter_links.clear()


@pytest.mark.parametrize(
    ("offsets", "expected"),
    [
        ([0], 1),                    # 今日だけ
        ([1], 1),                    # 昨日だけ、今日はまだ未学習
        ([1, 0], 2),                 # 昨日＋今日
        ([2, 1, 0], 3),              # 3日連続
        ([2, 1], 2),                 # 一昨日＋昨日、今日はまだ未学習
        ([2], 0),                    # 一昨日だけ
        ([4, 3, 2, 0], 1),           # 3日連続後に1日空けて再開
        ([0, 0, 0], 1),              # 同じ日の複数学習
    ],
)
def test_calculate_learning_streak_calendar_rules(offsets, expected):
    today = date(2026, 8, 20)
    active_dates = [today - timedelta(days=offset) for offset in offsets]
    assert calculate_learning_streak(active_dates, today) == expected


def test_learning_streak_uses_asia_tokyo_calendar_boundary(monkeypatch):
    clear_local_data()
    monkeypatch.setattr(database, "database_is_available", lambda: False)
    user_id = "jst-boundary-user"
    now = datetime(2026, 8, 19, 18, 0, tzinfo=timezone.utc)  # JST 8/20 03:00
    record_learning_batch(
        user_id, "jst-8-19", "study", 5, 3,
        datetime(2026, 8, 18, 15, 30, tzinfo=timezone.utc),  # JST 8/19 00:30
    )
    record_learning_batch(
        user_id, "jst-8-20", "nekketsu", 5, 4,
        datetime(2026, 8, 19, 15, 30, tzinfo=timezone.utc),  # JST 8/20 00:30
    )

    activity = get_learning_activity(user_id, now=now)
    assert activity["streak_days"] == 2
    assert [day["answered_count"] for day in activity["daily"]][-2:] == [5, 5]


def test_personal_and_supporter_dashboards_share_the_same_streak(monkeypatch):
    clear_local_data()
    monkeypatch.setattr(database, "database_is_available", lambda: False)
    user_id = "same-streak-learner"
    now = datetime.now(timezone.utc)
    record_learning_batch(user_id, "same-streak-1", "study", 5, 3, now - timedelta(days=1))
    record_learning_batch(user_id, "same-streak-2", "nekketsu", 5, 4, now)

    personal = build_dashboard(user_id)
    supporter = build_supporter_report(user_id)
    assert personal["streak_days"] == 2
    assert supporter["streak_days"] == personal["streak_days"]


def test_supporter_refresh_is_read_only_for_learning_data(monkeypatch):
    clear_local_data()
    monkeypatch.setattr(database, "database_is_available", lambda: False)
    supporter_id = "streak-supporter"
    learner_id = "streak-learner"
    user_names[learner_id] = "学習者"
    set_supporter_link(supporter_id, learner_id)
    record_learning_batch(
        learner_id, "read-only-streak", "study", 5, 3,
        datetime.now(timezone.utc) - timedelta(days=1),
    )
    before = (
        copy.deepcopy(database._local_learning_events),
        copy.deepcopy(database._local_learning_seconds),
        copy.deepcopy(database._local_learning_time_events),
    )
    token = create_supporter_token(supporter_id)
    client = app_module.app.test_client()

    for _ in range(2):
        response = client.get(f"/supporter?token={token}&learner_user_id={learner_id}")
        assert response.status_code == 200
        assert "継続" in response.get_data(as_text=True)

    after = (
        database._local_learning_events,
        database._local_learning_seconds,
        database._local_learning_time_events,
    )
    assert after == before


def test_home_and_consultation_without_learning_do_not_create_streak(monkeypatch):
    clear_local_data()
    monkeypatch.setattr(database, "database_is_available", lambda: False)

    class LineApi:
        def reply_message(self, *_args, **_kwargs):
            return None

    monkeypatch.setattr(app_module, "line_bot_api", LineApi())
    user_id = "non-learning-actions-user"

    def send(text):
        app_module.handle_text_message(SimpleNamespace(
            message=SimpleNamespace(text=text),
            source=SimpleNamespace(user_id=user_id),
            reply_token="reply-token",
        ))

    send("ホームに戻る")
    send("相談する")
    activity = get_learning_activity(user_id)
    assert activity["streak_days"] == 0
    assert activity["weekly_learning_days"] == 0
    assert activity["weekly_answers"] == 0
