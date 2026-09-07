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
    assert "合格への到達度" in js
    assert "回答数" in js
    assert "学習範囲・修復・再確認・定着" in js
