from datetime import datetime, timedelta, timezone
import os

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "test-token")
os.environ.setdefault("CHANNEL_SECRET", "test-secret")

import database
from app import app, record_confirmed_learning_batch
from database import add_learning_time, get_learning_summary, record_learning_batch, reset_user_profile
from goukaku_ui import create_dashboard_token
from question_bank import get_quiz_question, is_answer_correct


def clear_local_stats():
    database._local_learning_events.clear()
    database._local_learning_seconds.clear()


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
    questions = [{"answer": answer} for answer in ["A", "B", "C", "D", "E"]]
    session = {
        "session_id": "dashboard-session",
        "current_set": 1,
        "questions_per_set": 5,
        "questions": questions,
        "all_answers": {
            number: {"answer": answer}
            for number, answer in enumerate(["A", "B", "X", "X", "E"], 1)
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
    assert "5 / 30問" in text


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
        "selected_answers": ["B"],
        "is_correct": True,
        "confidence": 2,
    }
    assert results[1] == {
        "question_id": "Q521",
        "selected_answers": ["2", "4"],
        "is_correct": True,
        "confidence": 1,
    }
    assert results[2] == {
        "question_id": "Q551",
        "selected_answers": ["2"],
        "is_correct": True,
        "confidence": None,
    }
    assert results[3]["is_correct"] is False
    assert all(isinstance(item["selected_answers"], list) for item in results)
    assert event["answered_count"] == 5
    assert event["correct_count"] == sum(item["is_correct"] for item in results)


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
