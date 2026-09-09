from pathlib import Path


def test_weekly_card_fills_right_story_column_instead_of_forcing_blank_row():
    js = Path("static/goukaku/dashboard-layout-v05.js").read_text(encoding="utf-8")
    assert "guidanceStack.appendChild(weeklyCard);" in js
    assert "story.insertAdjacentElement('afterend', weeklyCard);" not in js


def test_dashboard_layout_cache_token_is_bumped():
    base = Path("templates/goukaku/base.html").read_text(encoding="utf-8")
    assert "dashboard-layout-v05.js', v='20260909-v08'" in base
