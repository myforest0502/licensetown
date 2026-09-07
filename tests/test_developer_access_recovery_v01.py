from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_recovery_hub_is_internal_token_protected_and_separate():
    source = (ROOT / "developer_access_recovery.py").read_text(encoding="utf-8")
    assert 'ROUTE = "/internal/recovery"' in source
    assert "require_developer_authorization()" in source
    assert "authorized_supporter_learner" in source
    assert '"site_ui.internal_learner_preview"' in source
    assert '"site_ui.internal_pilot_diagnostics"' in source
    assert '"internal_phase11_gates"' in source


def test_recovery_hub_is_installed_in_production_composition():
    source = (ROOT / "wsgi.py").read_text(encoding="utf-8")
    assert "from developer_access_recovery import install_developer_access_recovery" in source
    assert "install_developer_access_recovery(legacy.app)" in source


def test_recovery_template_has_two_primary_recovery_destinations():
    html = (ROOT / "templates" / "internal" / "recovery.html").read_text(encoding="utf-8")
    assert "本人のリアル画面" in html
    assert "開発者向け画面" in html
    assert "一般の親画面には表示されません" in html
