from pathlib import Path


def test_product_copy_assets_are_loaded_after_dashboard_assets():
    root = Path(__file__).resolve().parents[1]
    base = (root / "templates" / "goukaku" / "base.html").read_text(encoding="utf-8")
    assert "dashboard-product-copy-v01.css" in base
    assert "dashboard-product-copy-v01.js" in base
    assert base.index("dashboard-progress-trend-v06.js") < base.index("dashboard-product-copy-v01.js")


def test_product_copy_explains_paid_dashboard_meaning_and_next_actions():
    root = Path(__file__).resolve().parents[1]
    js = (root / "static" / "goukaku" / "dashboard-product-copy-v01.js").read_text(encoding="utf-8")
    assert "この到達度が示していること" in js
    assert "今の次の一手" in js
    assert "LTの判断" in js
    assert "この段階を抜ける条件" in js
    assert "なぜ今ここを優先するのか" in js
    assert "今日これをやる理由" in js
    assert "今日終えたら" in js
    assert "この7日間をLTはこう見ています" in js
    assert "学習範囲・修復・定着" in js


def test_paid_route_compares_current_progress_with_recommended_pace():
    root = Path(__file__).resolve().parents[1]
    base = (root / "templates" / "goukaku" / "base.html").read_text(encoding="utf-8")
    js = (root / "static" / "goukaku" / "dashboard-product-copy-v01.js").read_text(encoding="utf-8")
    css = (root / "static" / "goukaku" / "dashboard-product-copy-v01.css").read_text(encoding="utf-8")

    assert "LT_ROUTE_SNAPSHOT" in base
    assert "daysUntilExam" in base
    assert "totalAnswers" in base
    assert "uniqueAnsweredQuestions" in base
    assert "ROUTE_ANCHORS" in js
    assert "interpolateRecommendedProgress" in js
    assert "equivalentDaysRemaining" in js
    assert "この時点の推奨" in js
    assert "推奨ルートとの位置" in js
    assert "合格確率ではありません" in js
    assert "lt-route-pace-panel" in css
