from pathlib import Path


def test_paid_dashboard_v05_assets_are_loaded_after_existing_layout_assets():
    root = Path(__file__).resolve().parents[1]
    base = (root / "templates" / "goukaku" / "base.html").read_text(encoding="utf-8")
    assert "dashboard-layout-v05.css" in base
    assert "dashboard-layout-v07.css" in base
    assert "dashboard-layout-v05.js" in base
    assert base.index("dashboard-meaning-cards.js") < base.index("dashboard-layout-v05.js")
    assert base.index("dashboard-progress-trend-v06.css") < base.index("dashboard-layout-v07.css")


def test_paid_dashboard_v05_recomposes_story_into_balanced_columns():
    root = Path(__file__).resolve().parents[1]
    js = (root / "static" / "goukaku" / "dashboard-layout-v05.js").read_text(encoding="utf-8")
    css = (root / "static" / "goukaku" / "dashboard-layout-v05.css").read_text(encoding="utf-8")
    balance_css = (root / "static" / "goukaku" / "dashboard-layout-v07.css").read_text(encoding="utf-8")

    assert "dashboard-story-layout" in js
    assert "left.appendChild(subjectCard)" in js
    assert "stateProgressCard" in js
    assert "strategyCard" in js
    assert "left.appendChild(stateProgressCard)" in js
    assert "left.appendChild(strategyCard)" in js
    assert "left.appendChild(phaseCard)" in js
    assert "right.appendChild(guidanceStack)" in js
    assert "guidanceStack.appendChild(profileCard)" in js
    assert "weekly-learning-card-full" in js
    assert "dashboard-footer-compact" in js

    assert "grid-template-columns:minmax(0,1.04fr) minmax(0,.96fr)" in css
    assert ".dashboard-story-right .guidance-stack>*" in css
    assert ".weekly-learning-card-full{grid-column:1/-1" in css
    assert ".dashboard-footer-cards.dashboard-footer-compact" in css
    assert "@media(max-width:1000px)" in css

    assert ".dashboard-story-layout{align-items:start}" in balance_css
    assert ".dashboard-story-left>.learning-position-card{margin-top:0!important}" in balance_css
