from pathlib import Path


def test_dashboard_insight_layout_places_position_left_and_state_weekly_right():
    root = Path(__file__).resolve().parents[1]
    js = (root / "static" / "goukaku" / "dashboard-meaning-cards.js").read_text(encoding="utf-8")
    css = (root / "static" / "goukaku" / "dashboard-meaning-cards.css").read_text(encoding="utf-8")

    assert "learning-insight-layout" in js
    assert "learning-insight-right" in js
    assert "layout.appendChild(phase)" in js
    assert "right.appendChild(stateCard)" in js
    assert "right.appendChild(weeklyCard)" in js
    assert ".learning-insight-layout{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr)" in css
    assert ".learning-insight-right{display:grid;grid-template-rows:auto auto" in css
    assert "@media(max-width:700px)" in css
