"""Catch-up is real repair-only study, not cosmetic schedule manipulation."""
import os

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "test-token")
os.environ.setdefault("CHANNEL_SECRET", "test-secret")

import app as app_module
from licensetown.pt import catchup_mode as mode

FIXTURE = {
    "progress_raw": 0.25,
    "total_unique_canonical_nodes": 1532,
    "state_counts": {
        "unseen": 0, "checking": 740, "repairing": 700,
        "repaired": 80, "recheck_due": 12, "stable": 0,
    },
}


def test_threshold_and_persistent_lifecycle_until_exact_zero():
    # At day 117 current 25% is ~13 days behind on the existing strict curve.
    status = mode.calculate_catchup_status(117, FIXTURE)
    assert status["lag_days"] >= 10
    assert status["active"]
    assert 10 <= status["daily_goal"] <= 60
    assert status["daily_goal"] % 10 == 0

    # 9->1 days must remain locked once the learner entered repair mode.
    nine_days_behind = {**FIXTURE, "progress_raw": .275}
    status = mode.calculate_catchup_status(117, nine_days_behind, was_active=True)
    assert 0 < status["lag_days"] < 10
    assert status["active"]
    assert not mode.calculate_catchup_status(117, nine_days_behind)["active"]

    # The exact zero-lag threshold reopens normal learning.
    zero_lag = {**FIXTURE, "progress_raw": .32}
    status = mode.calculate_catchup_status(117, zero_lag, was_active=True)
    assert status["lag_days"] == 0
    assert status["active"] is False


def test_catchup_transition_is_persisted_without_fake_question_results(monkeypatch):
    observed = []
    monkeypatch.setattr(mode, "_latest_transition", lambda _user: "catchup_started")
    import database
    monkeypatch.setattr(database, "record_activity_event",
                        lambda user_id, typ, meta: observed.append((user_id, typ, meta)))
    recovered = mode.get_catchup_status(
        "learner", 117, {**FIXTURE, "progress_raw": .32},
        record_transition=True,
    )
    assert recovered["active"] is False
    assert [event[1] for event in observed] == ["catchup_recovered"]


def test_repair_start_is_exclusive_and_normal_resumes_at_zero(monkeypatch):
    monkeypatch.setattr(app_module, "dashboard_user_id",
                        lambda token: "learner" if token == "signed" else None)
    monkeypatch.setattr(app_module, "current_user_catchup",
                        lambda user_id: {"active": True})
    observed = []
    monkeypatch.setattr(app_module, "create_web_recommendation_session",
                        lambda *args, **kwargs: (observed.append((args, kwargs)) or ("test-s", True)))
    client = app_module.app.test_client()
    normal = client.post("/goukaku-no-michi/recommendation/start", json={
        "token": "signed", "source": "learner_navigation",
        "field": "解剖学", "count": 10,
    })
    assert normal.status_code == 409
    assert not observed
    special = client.post("/goukaku-no-michi/recommendation/start", json={
        "token": "signed", "source": "repair_questions", "count": 10,
    })
    assert special.status_code == 200
    assert observed[0][1]["session_kind"] == "dashboard_repair"

    monkeypatch.setattr(app_module, "current_user_catchup",
                        lambda user_id: {"active": False})
    outdated_repair = client.post("/goukaku-no-michi/recommendation/start", json={
        "token": "signed", "source": "repair_questions", "count": 10,
    })
    assert outdated_repair.status_code == 409


def test_catchup_ui_disables_all_other_learning_buttons_and_preserves_gensan():
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    base = (root / "templates/goukaku/base.html").read_text(encoding="utf-8")
    css = (root / "static/goukaku/dashboard-product-copy-v01.css").read_text(encoding="utf-8")
    approved = (root / "static/goukaku/dashboard-approved-layout-v01.js").read_text(encoding="utf-8")
    view = (root / "templates/goukaku/home.html").read_text(encoding="utf-8")
    assert 'catchup: {{ dashboard.catchup' in base
    assert "lt-catchup-only" in base and "lt-catchup-only" in css
    assert "button:not(.lt-repair-button)" in css
    assert "move(top, repairCard)" in approved
    assert "修復問題を10問始める" in view
    assert "今日の目標は" in view



def test_line_study_start_is_repair_only_during_catchup(monkeypatch):
    from question_bank import get_quiz_question

    monkeypatch.setattr(app_module, "get_question_attempts", lambda _user: [])
    monkeypatch.setattr(app_module, "current_user_catchup", lambda *_args, **_kwargs: {"active": True})
    selectors = []

    def repair_selector(attempts, question_count, **kwargs):
        selectors.append((question_count, kwargs))
        return [get_quiz_question(f"Q{i}") for i in range(1, 11)]

    monkeypatch.setattr(mode, "select_wrong_question_session", repair_selector)
    app_module.start_quiz("line-catchup-test-user", session_kind="adaptive_daily", question_count=30)
    session = app_module.study_sessions.pop("line-catchup-test-user")
    assert session["question_count"] == 10
    assert session["session_kind"] == "catchup_repair_line"
    assert selectors[0][0] == 10
    assert selectors[0][1]["audit_out"] == {}



def test_wrong_question_retry_queue_clears_one_at_a_time():
    from datetime import datetime, timezone, timedelta
    t = datetime(2026, 10, 27, tzinfo=timezone.utc)
    rows = [
        {"question_id": "Q1", "is_correct": False, "answered_at": t},
        {"question_id": "Q2", "is_correct": False, "answered_at": t},
        {"question_id": "Q3", "is_correct": False, "answered_at": t},
    ]
    assert mode.unresolved_wrong_question_ids(rows) == ("Q1", "Q2", "Q3")
    rows.append({"question_id": "Q2", "is_correct": True, "answered_at": t + timedelta(hours=1)})
    assert mode.unresolved_wrong_question_ids(rows) == ("Q1", "Q3")
    rows.append({"question_id": "Q1", "is_correct": False, "answered_at": t + timedelta(hours=2)})
    assert mode.unresolved_wrong_question_ids(rows) == ("Q1", "Q3")
    rows.append({"question_id": "Q3", "is_correct": True, "answered_at": t + timedelta(hours=3)})
    assert mode.unresolved_wrong_question_ids(rows) == ("Q1",)
    rows.append({"question_id": "Q1", "is_correct": True, "answered_at": t + timedelta(hours=4)})
    assert mode.unresolved_wrong_question_ids(rows) == ()
    rows.append({"question_id": "Q1", "is_correct": False, "answered_at": t + timedelta(hours=5)})
    assert mode.unresolved_wrong_question_ids(rows) == ("Q1",)


def test_only_previous_wrong_questions_are_selected_and_final_block_can_be_short():
    from datetime import datetime, timezone, timedelta
    t = datetime(2026, 10, 27, tzinfo=timezone.utc)
    attempts = [
        {"question_id": "Q1", "is_correct": False, "answered_at": t},
        {"question_id": "Q2", "is_correct": False, "answered_at": t},
        {"question_id": "Q3", "is_correct": False, "answered_at": t},
        {"question_id": "Q4", "is_correct": True, "answered_at": t},
        {"question_id": "Q2", "is_correct": True, "answered_at": t + timedelta(seconds=2)},
    ]
    questions = mode.select_wrong_question_session(attempts, 10)
    assert [q["id"] for q in questions] == ["Q1", "Q3"]
    import pytest
    from question_bank import QuestionAvailabilityError
    with pytest.raises(QuestionAvailabilityError):
        mode.select_wrong_question_session(
            [{"question_id": "Q2", "is_correct": True, "answered_at": t}], 10
        )


def test_zero_backlog_ends_repair_even_if_formal_schedule_still_lags(monkeypatch):
    from database import record_activity_event
    current = mode.calculate_catchup_status(117, FIXTURE, wrong_question_ids=("Q1", "Q2"))
    assert current["active"]
    assert current["pending_questions"] == 2
    after_one = mode.calculate_catchup_status(
        117, FIXTURE, was_active=True, wrong_question_ids=("Q2",)
    )
    assert after_one["active"] and after_one["pending_questions"] == 1
    complete = mode.calculate_catchup_status(117, FIXTURE, was_active=True, wrong_question_ids=())
    assert complete["lag_days"] >= 10  # formal pace has NOT been manipulated
    assert not complete["active"]
    assert complete["pending_questions"] == 0
    observed = []
    monkeypatch.setattr(mode, "_latest_transition", lambda _id: "catchup_started")
    monkeypatch.setattr("database.record_activity_event", lambda u, k, d: observed.append(k))
    ended = mode.get_catchup_status(
        "learner", 117, FIXTURE, wrong_question_ids=(), record_transition=True
    )
    assert not ended["active"]
    assert ended["just_recovered"] is True
    assert ended["recovery_complete"] is True
    assert observed == ["catchup_recovered"]
    monkeypatch.setattr(mode, "_latest_transition", lambda _id: "catchup_recovered")
    next_visit = mode.get_catchup_status("learner", 117, FIXTURE, wrong_question_ids=())
    assert not next_visit["active"]
    assert next_visit["recovery_complete"] is True
    assert next_visit["just_recovered"] is False


def test_line_partial_last_repair_batch_keeps_exact_question_count(monkeypatch):
    from question_bank import get_quiz_question
    monkeypatch.setattr(app_module, "get_question_attempts", lambda _user: [])
    monkeypatch.setattr(app_module, "current_user_catchup", lambda *_args, **_kw: {"active": True})
    monkeypatch.setattr(
        mode, "select_wrong_question_session",
        lambda *_args, **_kwargs: [get_quiz_question(f"Q{i}") for i in range(1, 8)]
    )
    user = "line-short-repair-queue"
    app_module.start_quiz(user, session_kind="adaptive_daily", question_count=30)
    session = app_module.study_sessions[user]
    assert session["question_count"] == 7
    assert session["total_sets"] == 2
    assert session["expected_numbers"] == [1, 2, 3, 4, 5]
    app_module.start_next_quiz(user)
    assert session["expected_numbers"] == [6, 7]
    assert len(session["questions"]) == 2
    app_module.study_sessions.pop(user)
