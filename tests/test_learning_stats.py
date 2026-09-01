from datetime import datetime, timedelta, timezone
import os

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "test-token")
os.environ.setdefault("CHANNEL_SECRET", "test-secret")

import app as app_module
import database
from app import app, record_confirmed_learning_batch
from database import (
    add_learning_time,
    get_field_learning_summary,
    get_learning_activity,
    get_learning_summary,
    get_question_attempts,
    record_learning_batch,
    reset_user_profile,
)
from goukaku_ui import create_dashboard_token
from question_bank import get_category_small, get_quiz_question, is_answer_correct


def clear_local_stats():
    database._local_learning_events.clear()
    database._local_question_attempts.clear()
    database._local_user_node_states.clear()
    database._local_learning_seconds.clear()
    database._local_learning_time_events.clear()


def test_learning_summary_combines_study_and_heat_without_duplicates():
    clear_local_stats()
    user_id = "stats-user"
    now = datetime.now(timezone.utc)
    assert record_learning_batch(user_id, "study-session:1", "study", 5, 3, now)
    assert not record_learning_batch(user_id, "study-session:1", "study", 5, 3, now)
    assert record_learning_batch(user_id, "heat-session:1", "nekketsu", 5, 4, now)
    add_learning_time(user_id, 125)

    summary = get_learning_summary(user_id, now=now)
    assert summary == {
        "total_answers": 10,
        "correct_answers": 7,
        "average_accuracy": 70,
        "last_7_days_accuracy": 70,
        "today_progress": 10,
        "study_minutes": 2,
    }


def test_recent_accuracy_and_complete_reset():
    clear_local_stats()
    user_id = "recent-user"
    now = datetime.now(timezone.utc)
    record_learning_batch(user_id, "old:1", "study", 5, 5, now - timedelta(days=8))
    record_learning_batch(user_id, "recent:1", "study", 5, 2, now)
    assert get_learning_summary(user_id, now=now)["last_7_days_accuracy"] == 40

    reset_user_profile(user_id)
    assert get_learning_summary(user_id, now=now)["total_answers"] == 0


def test_confirmed_batch_and_signed_dashboard_render_real_values():
    clear_local_stats()
    user_id = "dashboard-user"
    questions = [get_quiz_question(f"Q{number}") for number in range(1, 6)]
    correct_answers = [
        "".join(question["accepted_answer_sets"][0])
        for question in questions
    ]
    session = {
        "session_id": "dashboard-session",
        "current_set": 1,
        "questions_per_set": 5,
        "questions": questions,
        "all_answers": {
            number: {"answer": answer}
            for number, answer in enumerate(
                [correct_answers[0], correct_answers[1], "X", "X", correct_answers[4]],
                1,
            )
        },
        "mode": "study",
    }
    assert record_confirmed_learning_batch(user_id, session)
    assert not record_confirmed_learning_batch(user_id, session)

    token = create_dashboard_token(user_id)
    response = app.test_client().get(f"/goukaku-no-michi?token={token}")
    text = response.get_data(as_text=True)
    assert response.status_code == 200
    assert ">5<small>問</small>" in text
    assert text.count(">60<small>%</small>") >= 2
    assert "おすすめ進捗 0 / 10問" in text
    assert "KN0001" not in text


def test_question_results_store_formal_single_multi_either_and_null_confidence():
    clear_local_stats()
    user_id = "question-results-user"
    questions = [
        get_quiz_question("Q1"),
        get_quiz_question("Q521"),
        get_quiz_question("Q551"),
        get_quiz_question("Q2"),
        get_quiz_question("Q3"),
    ]
    wrong_q2_answer = next(
        label for label in "ABCDE"
        if not is_answer_correct(questions[3], label)
    )
    answers = {
        1: {"answer": "B", "confidence": "2"},
        2: {"answer": "DB", "confidence": "1"},
        3: {"answer": "B"},
        4: {"answer": wrong_q2_answer, "confidence": "3"},
        5: {
            "answer": "".join(questions[4]["accepted_answer_sets"][0]),
            "confidence": "1",
        },
    }
    session = {
        "session_id": "question-results-session",
        "current_set": 1,
        "questions_per_set": 5,
        "questions": questions,
        "all_answers": answers,
        "mode": "study",
    }

    assert record_confirmed_learning_batch(user_id, session)
    event = database._local_learning_events["question-results-session:1"]
    results = event["question_results"]

    assert len(results) == 5
    assert results[0] == {
        "question_id": "Q1",
        "knowledge_node_id": "KN0001",
        "selected_answers": ["B"],
        "is_correct": True,
        "confidence": 2,
        "answer_status": "answered",
    }
    assert results[1] == {
        "question_id": "Q521",
        "knowledge_node_id": "KN0513",
        "selected_answers": ["2", "4"],
        "is_correct": True,
        "confidence": 1,
        "answer_status": "answered",
    }
    assert results[2] == {
        "question_id": "Q551",
        "knowledge_node_id": "KN0543",
        "selected_answers": ["2"],
        "is_correct": True,
        "confidence": None,
        "answer_status": "answered",
    }
    assert results[3]["is_correct"] is False
    assert all(isinstance(item["selected_answers"], list) for item in results)
    assert event["answered_count"] == 5
    assert event["correct_count"] == sum(item["is_correct"] for item in results)
    assert len(database._local_question_attempts) == 5
    assert all(
        item["knowledge_node_id"].startswith("KN")
        for item in database._local_question_attempts
    )


def test_unknown_answer_is_distinct_in_learning_events_attempts_and_local_fallback():
    clear_local_stats()
    user_id = "unknown-answer-user"
    questions = [get_quiz_question(f"Q{number}") for number in range(1, 6)]
    answers = app_module.parse_quiz_answers(
        "A1 B2 0 D1 E2", expected_numbers=set(range(1, 6))
    )
    session = {
        "session_id": "unknown-answer-session",
        "current_set": 1,
        "questions_per_set": 5,
        "questions": questions,
        "all_answers": answers,
        "mode": "study",
    }
    assert record_confirmed_learning_batch(user_id, session)

    result = database._local_learning_events["unknown-answer-session:1"]["question_results"][2]
    assert result["selected_answers"] == []
    assert result["confidence"] is None
    assert result["answer_status"] == "unknown"
    assert result["is_correct"] is False
    assert all(
        item["answer_status"] == "answered"
        for index, item in enumerate(
            database._local_learning_events["unknown-answer-session:1"]["question_results"]
        )
        if index != 2
    )

    attempt = get_question_attempts(user_id)[2]
    assert attempt["selected_answers"] == []
    assert attempt["confidence"] is None
    assert attempt["answer_status"] == "unknown"
    assert attempt["is_correct"] is False


def test_question_results_duplicate_resume_home_and_reset_are_safe():
    clear_local_stats()
    user_id = "question-results-lifecycle-user"
    questions = [get_quiz_question(f"Q{number}") for number in range(1, 6)]
    answers = {
        number: {
            "answer": "".join(question["accepted_answer_sets"][0]),
            "confidence": "1",
        }
        for number, question in enumerate(questions, 1)
    }
    session = {
        "session_id": "lifecycle-session",
        "current_set": 1,
        "questions_per_set": 5,
        "questions": questions,
        "all_answers": answers,
        "mode": "study",
        "status": "waiting_for_continue",
    }
    app_module = __import__("app")
    app_module.study_sessions[user_id] = session

    assert record_confirmed_learning_batch(user_id, session)
    assert not record_confirmed_learning_batch(user_id, session)
    assert len(database._local_learning_events) == 1
    assert app_module.pause_quiz_session(user_id)
    assert app_module.resume_quiz_session(user_id) is session
    assert len(database._local_learning_events) == 1

    app_module.study_sessions.pop(user_id, None)
    assert len(database._local_learning_events) == 1
    reset_user_profile(user_id)
    assert database._local_learning_events == {}


def test_database_migration_adds_nullable_jsonb_without_recreating_table():
    source = (__import__("pathlib").Path(database.__file__)).read_text(encoding="utf-8")
    assert "ADD COLUMN IF NOT EXISTS question_results JSONB" in source
    assert "DROP TABLE" not in source


def _question_ids_for_different_categories():
    first_id = "Q1"
    first_category = get_category_small(first_id)
    second_id = next(
        f"Q{number}" for number in range(2, 1592)
        if get_category_small(f"Q{number}") != first_category
    )
    return first_id, second_id


def test_field_summary_counts_repeats_categories_recent_and_legacy_rows():
    clear_local_stats()
    user_id = "field-summary-user"
    now = datetime.now(timezone.utc)
    q1, q2 = _question_ids_for_different_categories()
    category1 = get_category_small(q1)
    category2 = get_category_small(q2)
    record_learning_batch(user_id, "legacy", "study", 5, 5, now, question_results=None)
    record_learning_batch(
        user_id, "old-detail", "study", 1, 0, now - timedelta(days=8),
        question_results=[{"question_id": q1, "selected_answers": ["1"], "is_correct": False, "confidence": None}],
    )
    record_learning_batch(
        user_id, "recent-detail", "nekketsu", 3, 2, now,
        question_results=[
            {"question_id": q1, "selected_answers": ["2"], "is_correct": True, "confidence": 2},
            {"question_id": q1, "selected_answers": ["1"], "is_correct": False, "confidence": 1},
            {"question_id": q2, "selected_answers": ["3"], "is_correct": True, "confidence": 3},
        ],
    )

    fields = {item["category_small"]: item for item in get_field_learning_summary(user_id, now=now)}
    assert len(fields) == 18
    assert fields[category1]["answered_count"] == 3
    assert fields[category1]["correct_count"] == 1
    assert fields[category1]["accuracy"] == 33
    assert fields[category1]["recent_7d_answered_count"] == 2
    assert fields[category1]["recent_7d_correct_count"] == 1
    assert fields[category1]["recent_7d_accuracy"] == 50
    assert fields[category2]["answered_count"] == 1
    assert fields[category2]["accuracy"] == 100
    assert get_learning_summary(user_id, now=now)["total_answers"] == 9

    unlearned = next(item for item in fields.values() if item["answered_count"] == 0)
    assert unlearned["learned"] is False
    assert unlearned["accuracy"] is None
    assert unlearned["recent_7d_accuracy"] is None


def test_field_summary_is_empty_after_complete_reset():
    clear_local_stats()
    user_id = "field-reset-user"
    record_learning_batch(
        user_id, "field-reset", "study", 1, 1,
        question_results=[{"question_id": "Q1", "selected_answers": ["2"], "is_correct": True, "confidence": 1}],
    )
    assert any(item["learned"] for item in get_field_learning_summary(user_id))
    reset_user_profile(user_id)
    assert all(not item["learned"] for item in get_field_learning_summary(user_id))


def test_learning_activity_uses_real_daily_answers_time_and_streak():
    clear_local_stats()
    user_id = "activity-user"
    now = datetime(2026, 8, 17, 12, tzinfo=timezone.utc)
    record_learning_batch(user_id, "activity-yesterday", "study", 5, 3, now - timedelta(days=1))
    record_learning_batch(user_id, "activity-today", "study", 10, 7, now)
    add_learning_time(user_id, 600, recorded_at=now - timedelta(days=1))
    add_learning_time(user_id, 900, recorded_at=now)

    activity = get_learning_activity(user_id, now=now)
    assert activity["streak_days"] == 2
    assert activity["weekly_study_minutes"] == 25
    assert activity["average_daily_study_minutes"] == 4
    assert [item["answered_count"] for item in activity["daily"]][-2:] == [5, 10]
    assert [item["study_minutes"] for item in activity["daily"]][-2:] == [10, 15]

    reset_user_profile(user_id)
    assert get_learning_activity(user_id, now=now)["weekly_study_minutes"] == 0


def test_learning_time_updates_total_and_daily_event_once_per_finished_interval(monkeypatch):
    clear_local_stats()
    app_module = __import__("app")
    user_id = "time-interval-user"
    session = {"active_started_at": 100.0}
    app_module.study_sessions[user_id] = session
    monkeypatch.setattr(app_module.time, "time", lambda: 220.0)

    app_module.finish_active_learning_time(user_id)
    app_module.finish_active_learning_time(user_id)

    assert get_learning_summary(user_id)["study_minutes"] == 2
    events = [
        event for event in database._local_learning_time_events
        if event["user_id"] == user_id
    ]
    assert len(events) == 1
    assert events[0]["elapsed_seconds"] == 120
    assert "active_started_at" not in session
    app_module.study_sessions.pop(user_id, None)

    assert not add_learning_time(
        user_id,
        120,
        recorded_at=events[0]["recorded_at"],
        event_key=events[0]["event_key"],
    )
    assert get_learning_summary(user_id)["study_minutes"] == 2
    assert len(database._local_learning_time_events) == 1


def test_learning_time_table_initialization_is_idempotent_and_non_destructive(monkeypatch):
    source = (__import__("pathlib").Path(database.__file__)).read_text(encoding="utf-8")
    assert "CREATE TABLE IF NOT EXISTS learning_time_events" in source
    assert "CREATE INDEX IF NOT EXISTS learning_time_events_user_date_idx" in source
    assert "CREATE UNIQUE INDEX IF NOT EXISTS learning_time_events_event_key_idx" in source
    assert "ADD COLUMN IF NOT EXISTS event_key TEXT" in source
    assert "DROP TABLE" not in source
    assert "TRUNCATE" not in source

    executed = []

    class FakeCursor:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def execute(self, query, _params=None):
            executed.append(" ".join(query.split()))

    class FakeConnection:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def cursor(self):
            return FakeCursor()

    monkeypatch.setattr(database, "database_is_available", lambda: True)
    monkeypatch.setattr(database, "get_db_connection", lambda: FakeConnection())
    database.init_database()
    database.init_database()

    create_time_table = [
        query for query in executed
        if "CREATE TABLE IF NOT EXISTS learning_time_events" in query
    ]
    assert len(create_time_table) == 2
    assert all("DROP " not in query and "TRUNCATE " not in query for query in executed)
