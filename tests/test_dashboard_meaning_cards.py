from pathlib import Path


def test_dashboard_lower_cards_have_distinct_user_facing_roles():
    root = Path(__file__).resolve().parents[1]
    base = (root / "templates" / "goukaku" / "base.html").read_text(encoding="utf-8")
    js = (root / "static" / "goukaku" / "dashboard-meaning-cards.js").read_text(encoding="utf-8")

    assert "dashboard-meaning-cards.css" in base
    assert "dashboard-meaning-cards.js" in base
    assert "LT_WEEKLY_LEARNING_SNAPSHOT" in base
    assert "dashboard.weekly_learning_days" in base
    assert "dashboard.weekly_answers" in base
    assert "dashboard.weekly_correct" in base
    assert "dashboard.weekly_study_minutes" in base
    assert "dashboard.daily" in base

    assert "🧭 学習の現在地" in js
    assert "ここでは「今日何問やるか」ではなく" in js
    assert "🔧 知識の確認状況" in js
    assert "📊 直近7日間の学習記録" in js
    assert "weekly-period" in js
    assert "🗂 今の学習カルテ" in js
    assert ".reward-card, .target-progress-card" in js
    assert "phase12-preview-action" in js
    assert ".remove()" in js


def test_weekly_card_is_factual_and_does_not_duplicate_advice():
    root = Path(__file__).resolve().parents[1]
    js = (root / "static" / "goukaku" / "dashboard-meaning-cards.js").read_text(encoding="utf-8")

    weekly_section = js.split("const weeklyCard = document.createElement('article');", 1)[1]
    weekly_markup = weekly_section.split("let profileCard", 1)[0]
    assert "直近7日間" in weekly_markup
    assert "学習した日" in weekly_markup
    assert "回答" in weekly_markup
    assert "正答率" in weekly_markup
    assert "今日は" not in weekly_markup
    assert "おすすめ学習を始める" not in weekly_markup
    assert "源さん" not in weekly_markup
