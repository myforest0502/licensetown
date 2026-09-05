from datetime import datetime, timezone
from pathlib import Path

from recommendation_daily_summary import build_today_recommendation_summary


def test_recommendation_daily_summary_counts_only_today_recommendation_questions():
    now = datetime(2026, 9, 5, 10, 0, tzinfo=timezone.utc)
    rows = [
        ([
            {"learning_source": "dashboard_recommendation", "is_correct": True},
            {"learning_source": "dashboard_recommendation", "is_correct": True},
            {"learning_source": "dashboard_recommendation", "is_correct": False},
        ], datetime(2026, 9, 5, 9, 0, tzinfo=timezone.utc)),
        ([
            {"learning_source": "manual", "is_correct": True},
            {"learning_source": "dashboard_recommendation", "is_correct": False},
        ], datetime(2026, 9, 5, 9, 30, tzinfo=timezone.utc)),
        ([
            {"learning_source": "dashboard_recommendation", "is_correct": True},
        ], datetime(2026, 9, 4, 9, 0, tzinfo=timezone.utc)),
    ]

    summary = build_today_recommendation_summary(
        "user",
        now=now,
        question_result_rows=rows,
    )

    assert summary == {
        "recommendation_today_answered": 4,
        "recommendation_today_correct": 2,
        "recommendation_today_incorrect": 2,
    }


def test_dashboard_card_uses_recommendation_specific_counts():
    root = Path(__file__).resolve().parents[1]
    base = (root / "templates" / "goukaku" / "base.html").read_text(encoding="utf-8")
    js = (root / "static" / "goukaku" / "recommendation-daily-summary.js").read_text(encoding="utf-8")

    assert "dashboard.recommendation_today_answered" in base
    assert "dashboard.recommendation_today_correct" in base
    assert "dashboard.today_progress" not in base
    assert "lt_today_row.correct_count" not in base
    assert "今日の目標${goal}問" in js
    assert "達成！" in js
    assert "未達（あと${remaining}問）" in js
    assert "正解：${correct}問" in js
    assert "誤答：${incorrect}問" in js
    assert "answered - correct" in js
