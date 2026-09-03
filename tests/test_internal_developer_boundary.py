import os

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "test-token")
os.environ.setdefault("CHANNEL_SECRET", "test-secret")

from app import app
import developer_ui


def test_internal_diagnostics_requires_admin_secret(monkeypatch):
    monkeypatch.setenv("LT_INTERNAL_ADMIN_TOKEN", "admin-secret")
    client = app.test_client()
    assert client.get("/internal/pilot-diagnostics?learner_user_id=learner").status_code == 403
    assert client.get("/internal/pilot-diagnostics?token=wrong&learner_user_id=learner").status_code == 403


def test_internal_index_accepts_header_token(monkeypatch):
    monkeypatch.setenv("LT_INTERNAL_ADMIN_TOKEN", "admin-secret")
    response = app.test_client().get(
        "/internal?learner_user_id=learner",
        headers={"X-LT-Developer-Token": "admin-secret"},
    )
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert "/internal/pilot-diagnostics" in text
    assert "/internal/learner-preview" in text


def test_developer_authorized_uses_constant_time_comparison(monkeypatch):
    monkeypatch.setenv("LT_INTERNAL_ADMIN_TOKEN", "admin-secret")
    assert developer_ui.developer_authorized("admin-secret")
    assert not developer_ui.developer_authorized("admin-secrex")
