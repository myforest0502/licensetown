from pathlib import Path


def test_mobile_paid_dashboard_asset_is_loaded():
    root = Path(__file__).resolve().parents[1]
    base = (root / "templates" / "goukaku" / "base.html").read_text(encoding="utf-8")
    assert "dashboard-mobile-paid-v01.css" in base


def test_mobile_paid_dashboard_preserves_full_paid_information():
    root = Path(__file__).resolve().parents[1]
    css = (root / "static" / "goukaku" / "dashboard-mobile-paid-v01.css").read_text(encoding="utf-8")
    assert "@media(max-width:720px)" in css
    assert ".lt-route-pace-panel" in css
    assert ".lt-route-timeline" in css
    assert ".learner-navigation" in css
    assert ".overall-progress-preview" in css
    assert ".weekly-learning-card" in css
    assert "display:none" not in css.replace(".lt-action-flow i:nth-of-type(2){display:none}", "")
