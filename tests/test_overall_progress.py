from datetime import datetime, timezone
import os

import pytest

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "test-token")
os.environ.setdefault("CHANNEL_SECRET", "test-secret")

from app import app
import database
from database import (
    add_learning_time,
    calculate_overall_progress,
    get_learning_summary,
    get_unique_answered_question_count,
    record_learning_batch,
    set_supporter_link,
)
from goukaku_ui import build_dashboard, create_dashboard_token, create_supporter_token


def clear_local_data():
    database._local_learning_events.clear()
    database._local_learning_seconds.clear()
    database._local_learning_time_events.clear()
    database._local_supporter_links.clear()


def result(question_id):
    return {
        "question_id": question_id,
        "selected_answers": ["1"],
        "is_correct": True,
        "confidence": 1,
    }


@pytest.mark.parametrize(
    ("study_minutes", "total_answers", "unique_questions", "expected"),
    [
        (0, 0, 0, 0),
        (5 * 60, 60, 60, 1),
        (250 * 60, 1500, 800, 50),
        (500 * 60, 3000, 300, 55),
        (500 * 60, 3000, 1000, 100),
        (1000 * 60, 6000, 1564, 100),
        (500 * 60, 0, 0, 0),
        (0, 3000, 1000, 0),
    ],
)
def test_overall_progress_v1_formula(
    study_minutes, total_answers, unique_questions, expected
):
    assert calculate_overall_progress(
        study_minutes, total_answers, unique_questions
    ) == expected


def test_unique_question_count_deduplicates_repeated_answers(monkeypatch):
    clear_local_data()
    monkeypatch.setattr(database, "database_is_available", lambda: False)
    user_id = "repeat-question-user"
    repeated = [result("Q1") for _ in range(100)]
    record_learning_batch(
        user_id, "repeat-100", "study", 100, 100,
        datetime.now(timezone.utc), repeated,
    )

    assert get_learning_summary(user_id)["total_answers"] == 100
    assert get_unique_answered_question_count(user_id) == 1

    record_learning_batch(
        user_id, "repeat-and-new", "nekketsu", 3, 3,
        datetime.now(timezone.utc), [result("Q1"), result("Q2"), result("Q2")],
    )
    assert get_learning_summary(user_id)["total_answers"] == 103
    assert get_unique_answered_question_count(user_id) == 2


def seed_sixty_question_progress(user_id):
    now = datetime.now(timezone.utc)
    record_learning_batch(
        user_id, "sixty-unique", "study", 60, 44, now,
        [result(f"Q{number}") for number in range(1, 61)],
    )
    add_learning_time(user_id, 5 * 60 * 60, now, "five-hours")


def test_dashboard_calculates_progress_below_one_hundred_answers(monkeypatch):
    clear_local_data()
    monkeypatch.setattr(database, "database_is_available", lambda: False)
    user_id = "overall-dashboard-user"
    seed_sixty_question_progress(user_id)

    dashboard = build_dashboard(user_id)
    assert dashboard["total_answers"] == 60
    assert dashboard["study_minutes"] == 300
    assert dashboard["unique_answered_questions"] == 60
    assert dashboard["overall_progress"] == 1
    assert dashboard["phase"] == "foundation"


def test_personal_uses_formal_progress_while_readonly_keeps_safe_legacy_copy(monkeypatch):
    clear_local_data()
    monkeypatch.setattr(database, "database_is_available", lambda: False)
    learner_id = "overall-learner"
    supporter_id = "overall-supporter"
    seed_sixty_question_progress(learner_id)
    set_supporter_link(supporter_id, learner_id)
    client = app.test_client()

    personal = client.get(
        f"/goukaku-no-michi?token={create_dashboard_token(learner_id)}"
    ).get_data(as_text=True)
    readonly = client.get(
        "/supporter/goukaku-no-michi"
        f"?token={create_supporter_token(supporter_id)}"
        f"&learner_user_id={learner_id}"
    ).get_data(as_text=True)

    assert "合格への到達度" in personal
    assert "必要な知識をどこまで学習・修復・定着できたか" in personal
    assert "合格確率ではなく" in personal
    assert "総合到達度" not in personal
    assert "LTで記録された学習時間と問題演習量から算出" not in personal

    assert 'class="ring" style="--value:1"' in readonly
    assert "目標学習量まで あと 99%" in readonly
    assert "合格ラインまで" not in readonly
    assert "LTで記録された学習時間と問題演習量から算出" in readonly
    assert "合格を保証する数値ではありません" in readonly
    assert "閲覧専用" in readonly


def test_dashboard_data_reuses_one_connection_and_question_result_fetch(monkeypatch):
    connection = object()
    opened = []
    question_rows = [([result("Q1")], datetime.now(timezone.utc))]

    class ConnectionContext:
        def __enter__(self):
            opened.append(connection)
            return connection

        def __exit__(self, *_args):
            return False

    monkeypatch.setattr(database, "database_is_available", lambda: True)
    monkeypatch.setattr(database, "get_db_connection", lambda: ConnectionContext())
    monkeypatch.setattr(
        database,
        "_get_question_result_rows",
        lambda user_id, received: question_rows if received is connection else None,
    )
    monkeypatch.setattr(
        database,
        "get_learning_summary",
        lambda user_id, _connection=None: {"total_answers": 1}
        if _connection is connection else None,
    )
    monkeypatch.setattr(
        database,
        "get_learning_activity",
        lambda user_id, _connection=None: {"streak_days": 1}
        if _connection is connection else None,
    )
    monkeypatch.setattr(
        database,
        "get_field_learning_summary",
        lambda user_id, _connection=None, _question_result_rows=None: ["fields"]
        if _connection is connection and _question_result_rows is question_rows else None,
    )
    monkeypatch.setattr(
        database,
        "get_unique_answered_question_count",
        lambda user_id, _connection=None, _question_result_rows=None: 1
        if _connection is connection and _question_result_rows is question_rows else None,
    )

    data = database.get_dashboard_learning_data("one-connection-user")
    assert len(opened) == 1
    assert data == {
        "summary": {"total_answers": 1},
        "activity": {"streak_days": 1},
        "fields": ["fields"],
        "unique_question_count": 1,
    }
