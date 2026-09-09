from pathlib import Path


def test_approved_layout_assets_are_loaded_last():
    base = Path("templates/goukaku/base.html").read_text(encoding="utf-8")
    assert "dashboard-approved-layout-v01.css" in base
    assert "dashboard-approved-layout-v01.js" in base
    assert base.rfind("dashboard-approved-layout-v01.js") > base.rfind("dashboard-product-copy-v01.js")


def test_top_half_matches_reference_hierarchy():
    js = Path("static/goukaku/dashboard-approved-layout-v01.js").read_text(encoding="utf-8")
    css = Path("static/goukaku/dashboard-approved-layout-v01.css").read_text(encoding="utf-8")
    assert "dashboard-reference-top-split" in js
    assert "move(topLeft, dateCard)" in js
    assert "move(topLeft, attentionCard)" in js
    assert "move(topRight, overallCard)" in js
    assert "move(top, summaryGrid)" in js
    assert "move(top, learnerNavigation)" in js
    assert "move(top, routeCard)" in js
    assert "grid-template-columns:minmax(0,58%) minmax(0,42%)" in css


def test_lower_half_matches_reference_grid_and_preserves_every_card():
    js = Path("static/goukaku/dashboard-approved-layout-v01.js").read_text(encoding="utf-8")
    css = Path("static/goukaku/dashboard-approved-layout-v01.css").read_text(encoding="utf-8")
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
    for area in [
        '"subjects gensan"',
        '"subjects knowledge"',
        '"subjects profile"',
        '"subjects retention"',
        '"strategy weekly"',
        '"position weekly"',
        '"footprints checkpoint"',
    ]:
        assert area in css


def test_formal_gensan_asset_is_reasserted():
    home = Path("templates/goukaku/home.html").read_text(encoding="utf-8")
    js = Path("static/goukaku/dashboard-approved-layout-v01.js").read_text(encoding="utf-8")
    assert "images/characters/gensan_main.png" in home
    assert "/static/images/characters/gensan_main.png" in js
