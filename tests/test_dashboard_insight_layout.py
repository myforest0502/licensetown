from pathlib import Path


def test_dashboard_density_uses_two_column_insight_and_footer_stacks():
    root = Path(__file__).resolve().parents[1]
    js = (root / "static" / "goukaku" / "dashboard-meaning-cards.js").read_text(encoding="utf-8")
    css = (root / "static" / "goukaku" / "dashboard-meaning-cards.css").read_text(encoding="utf-8")

    assert "const guidanceStack = document.querySelector('.guidance-stack')" in js
    assert "guidanceStack.appendChild(stateCard)" in js
    assert "phase-profile-grid" in js
    assert "phaseProfileGrid.appendChild(phase)" in js
    assert "phaseProfileGrid.appendChild(profileCard)" in js
    assert "dashboard-footer-left" in js
    assert "footerLeft.appendChild(nextCheckCard)" in js
    assert "footer.appendChild(weeklyCard)" in js
    assert "study-profile-card" in js
    assert "learner-nav-details-duplicated" in js

    assert ".phase-profile-grid{grid-column:1/-1;display:grid" in css
    assert ".dashboard-footer-cards{display:grid" in css
    assert ".dashboard-footer-left{display:grid" in css
    assert ".study-profile-grid{display:grid!important;grid-template-columns:1fr" in css
    assert "@media(max-width:700px)" in css


def test_paid_first_view_uses_width_and_adds_detail_density():
    root = Path(__file__).resolve().parents[1]
    css = (root / "static" / "goukaku" / "goukaku-product-first-view-v01.css").read_text(encoding="utf-8")
    js = (root / "static" / "goukaku" / "dashboard-meaning-cards.js").read_text(encoding="utf-8")

    assert "grid-template-columns: repeat(12" in css
    assert "grid-column: 1 / span 7" in css
    assert "grid-column: 8 / -1" in css
    assert "font-size: 16px" in css
    assert ".learner-current-detail-grid" in css
    assert ".learner-today-summary" in css
    assert "learner-current-detail-grid" in js
    assert "安定していること" in js
    assert "いま修復していること" in js
    assert "まだ確認したいこと" in js
    assert "learner-today-summary" in js
    assert "優先分野" in js
    assert "今の状態" in js
    assert "今日の学習量" in js
