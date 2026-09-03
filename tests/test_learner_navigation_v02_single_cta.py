from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_learner_navigation_v02_styles_are_loaded():
    base = (ROOT / "templates/goukaku/base.html").read_text(encoding="utf-8")
    assert "goukaku/learner-navigation-v02.css" in base
    assert "20260903-single-cta1" in base


def test_learner_navigation_hides_only_duplicate_legacy_guidance_cards():
    css = (ROOT / "static/goukaku/learner-navigation-v02.css").read_text(encoding="utf-8")
    assert ".dashboard-grid>.learner-navigation~.learning-overview .guidance-stack>.weak-card" in css
    assert ".dashboard-grid>.learner-navigation~.learning-overview .guidance-stack>.recommend-card" in css
    assert ".gensan-card" not in css
