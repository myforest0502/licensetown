from datetime import datetime, timezone
from pathlib import Path

import dashboard_progress_trend as trend


def test_progress_history_reconstructs_seven_daily_points(monkeypatch):
    monkeypatch.setattr(
        trend,
        "build_field_evidence",
        lambda attempts, as_of=None: {"attempt_count": len(attempts)},
    )
    monkeypatch.setattr(
        trend,
        "build_field_progress",
        lambda evidence: {
            "overall": {"overall_progress_score": evidence["attempt_count"] / 100}
        },
    )
    attempts = [
        {
            "user_id": "u1",
            "question_id": "Q1",
            "answered_at": datetime(2026, 9, 5, 1, tzinfo=timezone.utc),
        },
        {
            "user_id": "u1",
            "question_id": "Q2",
            "answered_at": datetime(2026, 9, 6, 1, tzinfo=timezone.utc),
        },
    ]
    points = trend.build_overall_progress_history_7d(
        attempts,
        now=datetime(2026, 9, 7, 0, tzinfo=timezone.utc),
    )
    assert len(points) == 7
    assert points[-1]["label"] == "9/7"
    assert points[-1]["progress"] == 2.0
    assert points[-3]["progress"] == 1.0


def test_progress_trend_assets_are_loaded_and_align_position_card():
    root = Path(__file__).resolve().parents[1]
    base = (root / "templates" / "goukaku" / "base.html").read_text(encoding="utf-8")
    css = (root / "static" / "goukaku" / "dashboard-progress-trend-v06.css").read_text(encoding="utf-8")
    js = (root / "static" / "goukaku" / "dashboard-progress-trend-v06.js").read_text(encoding="utf-8")

    assert "overallProgress" in base
    assert "dashboard-progress-trend-v06.css" in base
    assert "dashboard-progress-trend-v06.js" in base
    assert "margin-top:auto!important" in css
    assert "weekly-progress-line" in css
    assert "知識の仕上がり" in js
    assert "回答数" in js
    assert "学習範囲・修復・再確認・定着" in js


def test_authenticated_owner_history_uses_exact_original_calculation(monkeypatch):
    from app import app
    from goukaku_ui import create_dashboard_token

    seen = []
    points = [{"date": "2026-10-31", "label": "10/31", "progress": 24.7}]

    def fake_history(user_id):
        seen.append(user_id)
        return points

    monkeypatch.setattr(trend, "_history_for_user", fake_history)
    token = create_dashboard_token("owner-progress-history")
    client = app.test_client()

    assert client.get("/goukaku-no-michi?trend_only=1").status_code == 403
    response = client.get(
        f"/goukaku-no-michi?token={token}&trend_only=1"
    )
    assert response.status_code == 200
    assert response.get_json() == {"overallProgress": points}
    assert seen == ["owner-progress-history"]
    assert response.headers["Cache-Control"] == "no-store"


def test_progress_trend_wrapper_defers_only_authenticated_page_and_keeps_values(monkeypatch):
    from flask import Flask
    from types import SimpleNamespace

    web = Flask(__name__)
    web.add_url_rule("/goukaku-no-michi", endpoint="goukaku_ui.home", view_func=lambda: "")
    calls = []
    points = [{"date": "2026-10-31", "label": "10/31", "progress": 33.3}]
    monkeypatch.setattr(trend, "_history_for_user", lambda uid: calls.append(uid) or points)

    original = lambda user_id, **_kw: {"overall_progress_ui_enabled": True}
    fake = SimpleNamespace(build_dashboard=original)
    legacy = SimpleNamespace(build_dashboard=original)
    trend.install_dashboard_progress_trend(legacy, fake)

    with web.test_request_context("/goukaku-no-michi"):
        result = fake.build_dashboard("learner")
    assert result["overall_progress_history_async"] is True
    assert result["overall_progress_history_7d"] == []
    assert calls == []

    # Standalone/non-page callers retain the original full trend calculation.
    result = fake.build_dashboard("learner")
    assert result["overall_progress_history_7d"] == points
    assert calls == ["learner"]


def test_progress_trend_async_frontend_has_loading_and_fallback():
    root = Path(__file__).resolve().parents[1]
    base = (root / "templates" / "goukaku" / "base.html").read_text(encoding="utf-8")
    js = (root / "static" / "goukaku" / "dashboard-progress-trend-v06.js").read_text(encoding="utf-8")
    assert "overallProgressAsync" in base
    assert "trend_only" in js
    assert "drawExactTrend(data.overallProgress)" in js
    assert "進捗" in js or "知識の仕上がり" in js
    assert "推移グラフを取得できませんでした" in js
