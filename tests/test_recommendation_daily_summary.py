from pathlib import Path


def test_recommendation_daily_summary_uses_today_answered_correct_and_wrong_counts():
    root = Path(__file__).resolve().parents[1]
    base = (root / "templates" / "goukaku" / "base.html").read_text(encoding="utf-8")
    js = (root / "static" / "goukaku" / "recommendation-daily-summary.js").read_text(encoding="utf-8")

    assert "dashboard.today_progress" in base
    assert "lt_today_row.correct_count" in base
    assert "今日の目標${goal}問" in js
    assert "達成！" in js
    assert "未達（あと${remaining}問）" in js
    assert "正解：${correct}問" in js
    assert "誤答：${incorrect}問" in js
    assert "answered - correct" in js
