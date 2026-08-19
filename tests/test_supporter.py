from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
import time

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "test-token")
os.environ.setdefault("CHANNEL_SECRET", "test-secret")

import database
from app import app
from database import (
    add_learning_time,
    deactivate_supporter_link,
    get_learning_summary,
    get_supported_learner_ids,
    record_learning_batch,
    reset_user_profile,
    set_supporter_link,
    user_names,
)
from goukaku_ui import create_supporter_token
from question_bank import get_category_small
from supporter_report import build_supporter_report
import goukaku_ui as goukaku_module


def clear_local_data():
    database._local_learning_events.clear()
    database._local_learning_seconds.clear()
    database._local_learning_time_events.clear()
    database._local_supporter_links.clear()
    user_names.pop("supporter-user", None)
    user_names.pop("learner-user", None)
    user_names.pop("other-learner", None)


def result(question_id, correct):
    return {
        "question_id": question_id,
        "selected_answers": ["1"],
        "is_correct": correct,
        "confidence": None,
    }


def test_supporter_link_is_unique_revocable_and_preserved_when_learner_resets():
    clear_local_data()
    assert set_supporter_link("supporter-user", "learner-user")
    assert not set_supporter_link("supporter-user", "learner-user")
    assert get_supported_learner_ids("supporter-user") == ["learner-user"]
    assert deactivate_supporter_link("supporter-user", "learner-user")
    assert get_supported_learner_ids("supporter-user") == []

    set_supporter_link("supporter-user", "learner-user")
    reset_user_profile("learner-user")
    assert get_supported_learner_ids("supporter-user") == ["learner-user"]


def test_supporter_reset_preserves_link_and_learner_learning_history():
    clear_local_data()
    now = datetime.now(timezone.utc)
    set_supporter_link("supporter-user", "learner-user")
    record_learning_batch(
        "learner-user", "learner-history", "study", 5, 3, now,
        [result("Q1", True)] * 5,
    )
    add_learning_time("learner-user", 600, now, "learner-time")

    reset_user_profile("supporter-user")

    assert get_supported_learner_ids("supporter-user") == ["learner-user"]
    learner_summary = get_learning_summary("learner-user", now=now)
    assert learner_summary["total_answers"] == 5
    assert learner_summary["study_minutes"] == 10


def test_learner_reset_clears_own_learning_data_but_preserves_supporter_link():
    clear_local_data()
    now = datetime.now(timezone.utc)
    set_supporter_link("supporter-user", "learner-user")
    record_learning_batch(
        "learner-user", "learner-reset-history", "study", 5, 3, now,
        [result("Q1", True)] * 5,
    )
    add_learning_time("learner-user", 600, now, "learner-reset-time")

    reset_user_profile("learner-user")

    assert get_supported_learner_ids("supporter-user") == ["learner-user"]
    learner_summary = get_learning_summary("learner-user", now=now)
    assert learner_summary["total_answers"] == 0
    assert learner_summary["study_minutes"] == 0


def test_supporter_report_aggregates_only_learning_metrics():
    clear_local_data()
    now = datetime.now(timezone.utc)
    q1 = "Q1"
    q2 = next(
        f"Q{number}" for number in range(2, 1565)
        if get_category_small(f"Q{number}") != get_category_small(q1)
    )
    record_learning_batch(
        "learner-user", "support-yesterday", "study", 2, 1,
        now - timedelta(days=1), [result(q1, True), result(q1, False)],
    )
    record_learning_batch(
        "learner-user", "support-today", "nekketsu", 3, 2,
        now, [result(q1, True), result(q2, True), result(q2, False)],
    )
    add_learning_time("learner-user", 600, now - timedelta(days=1), "support-time-1")
    add_learning_time("learner-user", 900, now, "support-time-2")

    report = build_supporter_report("learner-user")
    assert report["today"]["answered_count"] == 3
    assert report["today"]["correct_count"] == 2
    assert report["today"]["accuracy"] == 67
    assert report["today"]["study_minutes"] == 15
    assert report["weekly_learning_days"] == 2
    assert report["weekly_answers"] == 5
    assert report["weekly_accuracy"] == 60
    assert report["weekly_study_minutes"] == 25
    assert report["streak_days"] == 2
    assert len(report["today_fields"]) == 2
    assert len(report["fields"]) == 2


def test_supporter_route_requires_signed_active_link_and_cannot_switch_learner():
    clear_local_data()
    user_names["learner-user"] = "対象学習者"
    user_names["other-learner"] = "閲覧禁止学習者"
    set_supporter_link("supporter-user", "learner-user")
    client = app.test_client()
    token = create_supporter_token("supporter-user")

    assert client.get("/supporter").status_code == 403
    assert client.get("/supporter?token=invalid").status_code == 403
    assert client.get(f"/supporter?token={token}tampered").status_code == 403
    assert client.get(
        f"/supporter?token={create_supporter_token('unlinked-supporter')}"
    ).status_code == 403

    response = client.get(
        f"/supporter?token={token}&learner_user_id=other-learner"
    )
    text = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "対象学習者" in text
    assert "閲覧禁止学習者" not in text
    assert "相談内容や私的な会話は表示されません" in text

    deactivate_supporter_link("supporter-user", "learner-user")
    assert client.get(f"/supporter?token={token}").status_code == 403


def test_expired_supporter_token_is_rejected(monkeypatch):
    clear_local_data()
    set_supporter_link("supporter-user", "learner-user")
    current_time = time.time()
    monkeypatch.setattr(time, "time", lambda: current_time - (31 * 24 * 60 * 60))
    expired_token = create_supporter_token("supporter-user")
    monkeypatch.setattr(time, "time", lambda: current_time)

    assert app.test_client().get(
        f"/supporter?token={expired_token}"
    ).status_code == 403


def test_supporter_implementation_does_not_access_consultation_data():
    source = Path(__import__("supporter_report").__file__).read_text(encoding="utf-8")
    assert "consultation_contexts" not in source
    assert "conversation" not in source
    assert "get_learning_summary" in source
    assert "get_learning_activity" in source
    assert "get_field_learning_summary" in source


def test_supporter_page_displays_weak_top3_and_recommendation(monkeypatch):
    clear_local_data()
    set_supporter_link("supporter-user", "learner-user")
    report = {
        "today": {"answered_count": 5, "correct_count": 3, "accuracy": 60, "study_minutes": 12},
        "today_studied": True,
        "today_fields": [{"name": "生理学", "answered_count": 5, "accuracy": 60}],
        "weekly_learning_days": 2,
        "weekly_answers": 10,
        "weekly_study_minutes": 25,
        "weekly_accuracy": 60,
        "streak_days": 2,
        "fields": [{"name": "生理学", "answered_count": 10, "accuracy": 60}],
        "weak_fields": [{"name": "生理学", "reason": "正答率60%"}],
        "weak_analysis_message": "",
        "recommended_study": [("生理学", 10)],
        "comment": "継続できています。",
    }
    monkeypatch.setattr(goukaku_module, "build_supporter_report", lambda _user_id: report)
    token = create_supporter_token("supporter-user")
    text = app.test_client().get(f"/supporter?token={token}").get_data(as_text=True)
    assert "苦手分野 TOP3" in text
    assert "正答率60%" in text
    assert "今日のおすすめ" in text
    assert "10問の学習がおすすめです" in text
    assert "3</b><small>正解" in text


def test_supporter_table_initialization_is_idempotent_and_non_destructive():
    source = Path(database.__file__).read_text(encoding="utf-8")
    assert "CREATE TABLE IF NOT EXISTS supporter_links" in source
    assert "UNIQUE (supporter_user_id, learner_user_id)" in source
    assert "CREATE INDEX IF NOT EXISTS supporter_links_supporter_active_idx" in source
    assert "DROP TABLE" not in source
    assert "TRUNCATE" not in source
