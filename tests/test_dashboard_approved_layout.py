from pathlib import Path


def test_approved_layout_assets_are_loaded_last():
    base = Path("templates/goukaku/base.html").read_text(encoding="utf-8")
    assert "dashboard-approved-layout-v01.css" in base
    assert "dashboard-approved-layout-v01.js" in base
    assert base.rfind("dashboard-approved-layout-v01.js") > base.rfind("dashboard-product-copy-v01.js")


def test_route_is_promoted_immediately_after_top_summary():
    js = Path("static/goukaku/dashboard-approved-layout-v01.js").read_text(encoding="utf-8")
    assert "overallCard?.insertAdjacentElement('afterend', routeCard)" in js
    assert "routeCard?.insertAdjacentElement('afterend', learnerNavigation)" in js


def test_all_paid_dashboard_sections_are_preserved_and_distributed():
    js = Path("static/goukaku/dashboard-approved-layout-v01.js").read_text(encoding="utf-8")
    required = [
        ".subject-card",
        ".strategy-note-card",
        ".learning-position-card",
        ".gensan-card",
        ".knowledge-state-card",
        ".study-profile-card",
        ".state-progress-card",
        ".weekly-learning-card",
        ".footprint-card",
        ".next-check-card",
    ]
    for selector in required:
        assert selector in js


def test_formal_gensan_asset_is_reasserted():
    home = Path("templates/goukaku/home.html").read_text(encoding="utf-8")
    js = Path("static/goukaku/dashboard-approved-layout-v01.js").read_text(encoding="utf-8")
    assert "images/characters/gensan_main.png" in home
    assert "/static/images/characters/gensan_main.png" in js
