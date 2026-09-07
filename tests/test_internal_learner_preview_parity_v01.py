from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_wsgi_rebinds_developer_ui_dashboard_builder_after_composition():
    text = (ROOT / "wsgi.py").read_text(encoding="utf-8")
    assert "import developer_ui as developer_ui_module" in text
    assert "developer_ui_module.build_dashboard = goukaku_module.build_dashboard" in text
    assert "include_learner_navigation=True" in text
    assert "developer_ui_module.build_dashboard = _build_full_developer_preview_dashboard" in text
