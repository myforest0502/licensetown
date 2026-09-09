from pathlib import Path


def test_approved_layout_assets_are_loaded_last():
    base = Path("templates/goukaku/base.html").read_text(encoding="utf-8")
    assert "dashboard-approved-layout-v01.css" in base
    assert "dashboard-approved-layout-v01.js" in base
    assert base.rfind("dashboard-approved-layout-v01.js") > base.rfind("dashboard-product-copy-v01.js")


def test_top_half_matches_latest_boss_reference_exact_order():
    js = Path("static/goukaku/dashboard-approved-layout-v01.js").read_text(encoding="utf-8")
    css = Path("static/goukaku/dashboard-approved-layout-v01.css").read_text(encoding="utf-8")
    base = Path("templates/goukaku/base.html").read_text(encoding="utf-8")
    expected = [
        "move(topLeft, dateCard)",
        "move(topLeft, todayCard)",
        "move(topRight, overallCard)",
        "move(top, summaryGrid)",
        "move(top, routeCard)",
        "move(top, currentCard)",
    ]
    positions = [js.index(item) for item in expected]
    assert positions == sorted(positions)
    assert "grid-template-columns:minmax(0,58%) minmax(0,42%)" in css
    assert ".dashboard-reference-source-only" in css
    assert "@media (min-width:701px)" in css
    assert "@media (min-width:701px) and (max-width:1000px)" not in css
    assert "grid-template-columns:repeat(5,minmax(0,1fr))" in css
    assert ".lt-route-pace-note" in css
    assert "dashboard-approved-layout-v01.css', v='20260909-v04'" in base
    assert "dashboard-product-copy-v01.js', v='20260909-v04'" in base


def test_lower_half_remains_frozen_to_previous_approved_reference():
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
    assert "LOWER reference was already approved by Boss. Do not change its composition." in js
    assert "LOWER HALF: frozen to the already approved reference." in css


def test_formal_gensan_asset_is_reasserted():
    home = Path("templates/goukaku/home.html").read_text(encoding="utf-8")
    js = Path("static/goukaku/dashboard-approved-layout-v01.js").read_text(encoding="utf-8")
    assert "images/characters/gensan_main.png" in home
    assert "/static/images/characters/gensan_main.png" in js
