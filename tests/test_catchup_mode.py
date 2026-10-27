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

    monkeypatch.setattr(app_module, "build_node_adaptive_session", repair_selector)
    app_module.start_quiz("line-catchup-test-user", session_kind="adaptive_daily", question_count=30)
    session = app_module.study_sessions.pop("line-catchup-test-user")
    assert session["question_count"] == 10
    assert session["session_kind"] == "catchup_repair_line"
    assert selectors[0][0] == 10
    assert selectors[0][1]["learning_intent"] == "repair"
    assert selectors[0][1]["strict_repair"] is True
