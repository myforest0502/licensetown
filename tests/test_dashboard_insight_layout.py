from pathlib import Path


def test_dashboard_density_uses_guidance_column_and_compact_lower_insights():
    root = Path(__file__).resolve().parents[1]
    js = (root / "static" / "goukaku" / "dashboard-meaning-cards.js").read_text(encoding="utf-8")
    css = (root / "static" / "goukaku" / "dashboard-meaning-cards.css").read_text(encoding="utf-8")

    assert "const guidanceStack = document.querySelector('.guidance-stack')" in js
    assert "guidanceStack.appendChild(stateCard)" in js
    assert "guidanceStack.appendChild(weeklyCard)" in js
    assert "study-profile-card" in js
    assert "learner-nav-details-duplicated" in js
    assert ".learning-position-card{grid-column:1/-1" in css
    assert "height:auto" in css
    assert ".study-profile-grid{display:grid!important;grid-template-columns:repeat(4" in css
    assert "@media(max-width:700px)" in css
