from datetime import datetime, timedelta, timezone
import os

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "test-token")
os.environ.setdefault("CHANNEL_SECRET", "test-secret")

import database
from app import app, record_confirmed_learning_batch
from database import add_learning_time, get_learning_summary, record_learning_batch, reset_user_profile
from goukaku_ui import create_dashboard_token


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
