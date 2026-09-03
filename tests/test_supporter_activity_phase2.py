from datetime import datetime, timedelta, timezone
import os
from types import SimpleNamespace

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "test-token")
os.environ.setdefault("CHANNEL_SECRET", "test-secret")

import app as app_module
import database
import goukaku_ui as goukaku_ui_module
from app import app, record_confirmed_learning_batch
from database import (
    get_latest_activity_day_summary,
    record_activity_event,
    record_learning_batch,
)
from goukaku_ui import build_dashboard, create_dashboard_token, create_supporter_token
from question_bank import CATEGORY_NAMES, get_category_small, get_quiz_question, question_ids


def clear_activity_data():
    database._local_learning_events.clear()
    database._local_question_attempts.clear()
    database._local_user_node_states.clear()
    database._local_supporter_links.clear()


def question_for_field(field_name):
    category = next(key for key, name in CATEGORY_NAMES.items() if name == field_name)
    return next(q_id for q_id in question_ids() if get_category_small(q_id) == category)


def answer_result(question_id, correct=True, source=None, with_node=False):
    item = {
        "question_id": question_id,
        "selected_answers": ["1"],
        "is_correct": correct,
        "confidence": 1,
        "answer_status": "answered",
    }
    if source:
        item["learning_source"] = source
    if with_node:
        item["knowledge_node_id"] = "KN0001"
    return item


def test_recommendation_plan_progress_complete_from_any_learning_route():
    clear_activity_data()
    now = datetime(2026, 9, 1, 3, 0, tzinfo=timezone.utc)
    field_name = "人間発達学"
    q_id = question_for_field(field_name)
    assert record_activity_event(
        "learner", "recommendation_plan", {"field": field_name, "goal": 10}, now
    )
    record_learning_batch(
        "learner", "normal-ten", "study", 10, 10, now,
        [answer_result(q_id, source="manual") for _ in range(10)],
    )

    activity = get_latest_activity_day_summary("learner")

    assert activity["recommendation"] == {
        "field": field_name, "goal": 10, "progress": 10, "completed": True,
    }
    assert activity["learning_sources"]["normal"] == 10


def test_recommendation_plan_incomplete_and_other_field_does_not_count():
    clear_activity_data()
    now = datetime(2026, 9, 1, 3, 0, tzinfo=timezone.utc)
    field_name = "人間発達学"
    target_q = question_for_field(field_name)
    other_q = question_for_field("解剖学")
    record_activity_event(
        "learner", "recommendation_plan", {"field": field_name, "goal": 10}, now
    )
    record_learning_batch(
        "learner", "target-three", "study", 3, 2, now,
        [answer_result(target_q, source="dashboard_recommendation") for _ in range(3)],
    )
    activity = get_latest_activity_day_summary("learner")
    assert activity["recommendation"]["progress"] == 3
    assert activity["recommendation"]["completed"] is False

    clear_activity_data()
    record_activity_event(
        "learner", "recommendation_plan", {"field": field_name, "goal": 10}, now
    )
    record_learning_batch(
        "learner", "other-ten", "study", 10, 5, now,
        [answer_result(other_q, source="adaptive_daily") for _ in range(10)],
    )
    activity = get_latest_activity_day_summary("learner")
    assert activity["recommendation"]["progress"] == 0
    assert activity["recommendation"]["completed"] is False


def test_learning_source_breakdown_keeps_legacy_unknown():
    clear_activity_data()
    now = datetime(2026, 9, 1, 3, 0, tzinfo=timezone.utc)
    q_id = question_for_field("解剖学")
    cases = [
        ("heat", "nekketsu", None, 5),
        ("adaptive", "study", "adaptive_daily", 30),
        ("recommend", "study", "dashboard_recommendation", 10),
        ("legacy", "study", None, 4),
    ]
    for key, mode, source, count in cases:
        record_learning_batch(
            "learner", key, mode, count, 0, now,
            [answer_result(q_id, False, source=source) for _ in range(count)],
        )

    sources = get_latest_activity_day_summary("learner")["learning_sources"]

    assert sources["nekketsu"] == 5
    assert sources["normal"] == 30
    assert sources["recommendation"] == 10
    assert sources["legacy"] == 4


def test_consultation_activity_is_daily_idempotent_and_contains_no_message():
    clear_activity_data()
    now = datetime(2026, 9, 1, 3, 0, tzinfo=timezone.utc)
    assert record_activity_event("learner", "consultation", occurred_at=now)
    assert not record_activity_event("learner", "consultation", occurred_at=now)

    events = list(database._local_learning_events.values())
    assert len(events) == 1
    assert events[0]["question_results"] == {"activity_type": "consultation"}
    assert "相談本文" not in str(events[0])


def test_latest_activity_can_be_today_consultation_while_latest_learning_is_yesterday():
    clear_activity_data()
    today = datetime(2026, 9, 1, 3, 0, tzinfo=timezone.utc)
    yesterday = today - timedelta(days=1)
    q_id = question_for_field("解剖学")
    record_learning_batch(
        "learner", "yesterday", "study", 1, 1, yesterday,
        [answer_result(q_id, source="manual")],
    )
    record_activity_event("learner", "consultation", occurred_at=today)

    activity = get_latest_activity_day_summary("learner")

    assert activity["date"] == today.astimezone(database.ZoneInfo("Asia/Tokyo")).date().isoformat()
    assert activity["has_problem_learning"] is False
    assert activity["consultation_used"] is True


def test_plan_only_is_not_latest_activity():
    clear_activity_data()
    record_activity_event(
        "learner", "recommendation_plan", {"field": "人間発達学", "goal": 10}
    )
    assert get_latest_activity_day_summary("learner")["has_activity"] is False


def test_personal_dashboard_records_one_plan_but_supporter_dashboard_records_none(monkeypatch):
    clear_activity_data()
    dashboard = build_dashboard()
    dashboard.update({
        "recommended_study": [("人間発達学", 10)],
        "recommendation_reason": "test",
        "recommendation_progress": 0,
        "recommendation_goal": 10,
    })
    monkeypatch.setattr(goukaku_ui_module, "build_dashboard", lambda user_id, **kwargs: dashboard)
    token = create_dashboard_token("learner")
    client = app.test_client()

    assert client.get(f"/goukaku-no-michi?token={token}").status_code == 200
    assert client.get(f"/goukaku-no-michi?token={token}").status_code == 200
    assert len(database._local_learning_events) == 1

    database.set_supporter_link("supporter", "learner")
    supporter_token = create_supporter_token("supporter")
    before = len(database._local_learning_events)
    assert client.get(
        f"/supporter/goukaku-no-michi?token={supporter_token}&learner_user_id=learner"
    ).status_code == 200
    assert len(database._local_learning_events) == before


def test_learning_source_extra_key_does_not_change_attempt_or_node_processing():
    clear_activity_data()
    item = answer_result("Q1", source="adaptive_daily", with_node=True)
    assert record_learning_batch("learner", "source-key", "study", 1, 1, question_results=[item])
    assert len(database._local_question_attempts) == 1
    assert len(database._local_user_node_states) == 1
    assert "learning_source" not in database._local_question_attempts[0]


def test_record_confirmed_batch_persists_session_kind():
    clear_activity_data()
    question = get_quiz_question("Q1")
    answer = "".join(question["accepted_answer_sets"][0])
    session = {
        "session_id": "source-session",
        "current_set": 1,
        "questions_per_set": 1,
        "questions": [question],
        "all_answers": {1: {"answer": answer, "confidence": "1"}},
        "mode": "study",
        "session_kind": "initial_assessment",
    }
    assert record_confirmed_learning_batch("learner", session)
    result = database._local_learning_events["source-session:1"]["question_results"][0]
    assert result["learning_source"] == "initial_assessment"


def test_actual_chat_message_records_only_consultation_fact(monkeypatch):
    clear_activity_data()
    user_id = "chat-phase2-user"
    app_module.user_modes[user_id] = "chat"
    app_module.user_states[user_id] = "consultation_input"
    monkeypatch.setattr(app_module, "create_text_response", lambda *_args: "返答")
    monkeypatch.setattr(app_module, "reply_consultation_response", lambda *_args: None)
    event = SimpleNamespace(
        source=SimpleNamespace(user_id=user_id),
        message=SimpleNamespace(text="保存してはいけない相談本文"),
        reply_token="reply",
    )

    app_module.handle_text_message(event)
    app_module.handle_text_message(event)

    events = [event for event in database._local_learning_events.values() if event["mode"] == "consultation"]
    assert len(events) == 1
    assert "保存してはいけない相談本文" not in str(events)
    app_module.consultation_contexts.pop(user_id, None)
    app_module.user_modes.pop(user_id, None)
    app_module.user_states.pop(user_id, None)


def test_entering_consultation_without_message_does_not_record_activity(monkeypatch):
    clear_activity_data()
    user_id = "chat-entry-only-user"
    monkeypatch.setattr(app_module, "reply_consultation_start", lambda *_args: None)
    event = SimpleNamespace(
        source=SimpleNamespace(user_id=user_id),
        message=SimpleNamespace(text="相談する"),
        reply_token="reply",
    )

    app_module.handle_text_message(event)

    assert not any(
        item["mode"] == "consultation"
        for item in database._local_learning_events.values()
    )
    app_module.consultation_contexts.pop(user_id, None)
    app_module.user_modes.pop(user_id, None)


def test_supporter_html_shows_activity_breakdown_without_consultation_text():
    clear_activity_data()
    now = datetime.now(timezone.utc)
    q_id = question_for_field("人間発達学")
    record_activity_event(
        "learner", "recommendation_plan", {"field": "人間発達学", "goal": 10}, now
    )
    record_learning_batch(
        "learner", "recommend-three", "study", 3, 2, now,
        [answer_result(q_id, index < 2, "dashboard_recommendation") for index in range(3)],
    )
    record_activity_event("learner", "consultation", occurred_at=now)
    database.set_supporter_link("supporter", "learner")
    token = create_supporter_token("supporter")

    text = app.test_client().get(f"/supporter?token={token}").get_data(as_text=True)

    assert "人間発達学 3 / 10問" in text
    assert "未完了" in text
    assert "おすすめ学習経由" in text
    assert "相談モード" in text
    assert "利用あり" in text
    assert "保存してはいけない相談本文" not in text


def test_latest_activity_database_path_uses_existing_learning_events(monkeypatch):
    answered_at = datetime(2026, 9, 1, 3, 0, tzinfo=timezone.utc)
    q_id = question_for_field("解剖学")

    class FakeCursor:
        def __init__(self):
            self.query = ""

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def execute(self, query, _params):
            self.query = " ".join(query.split())

        def fetchone(self):
            return (answered_at,)

        def fetchall(self):
            return [
                (
                    "study", 1, 1, answered_at,
                    [answer_result(q_id, source="adaptive_daily")],
                )
            ]

    class FakeConnection:
        def cursor(self):
            return FakeCursor()

    monkeypatch.setattr(database, "DATABASE_URL", "postgresql://configured")

    activity = get_latest_activity_day_summary("learner", _connection=FakeConnection())

    assert activity["has_activity"] is True
    assert activity["has_problem_learning"] is True
    assert activity["learning_sources"]["normal"] == 1
