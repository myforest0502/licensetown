import os

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "test-token")
os.environ.setdefault("CHANNEL_SECRET", "test-secret")

from app import app
import database
import developer_ui
import goukaku_ui
from goukaku_ui import create_dashboard_token, create_supporter_token


LEGACY_PREVIEW_PATH = "/supporter/goukaku-no-michi/learner-preview"
LEGACY_DIAGNOSTICS_PATH = "/supporter/pilot-diagnostics"
INTERNAL_PREVIEW_PATH = "/internal/learner-preview"
INTERNAL_DIAGNOSTICS_PATH = "/internal/pilot-diagnostics"


def _authorize_supporter(monkeypatch, learner_id="learner-user"):
    monkeypatch.setattr(
        goukaku_ui,
        "get_supported_learner_ids",
        lambda supporter_id: [learner_id] if supporter_id == "supporter-user" else [],
    )
    return create_supporter_token("supporter-user")


def _internal_preview(client, token, learner_id="learner-user"):
    return client.get(
        f"{INTERNAL_PREVIEW_PATH}?token={token}&learner_user_id={learner_id}"
    )


def test_legacy_supporter_developer_routes_are_not_reachable_with_supporter_token(monkeypatch):
    token = _authorize_supporter(monkeypatch)
    client = app.test_client()
    assert client.get(
        f"{LEGACY_PREVIEW_PATH}?token={token}&learner_user_id=learner-user"
    ).status_code == 404
    assert client.get(
        f"{LEGACY_DIAGNOSTICS_PATH}?token={token}&learner_user_id=learner-user"
    ).status_code == 404


def test_internal_console_fails_closed_without_configured_secret(monkeypatch):
    monkeypatch.delenv("LT_INTERNAL_ADMIN_TOKEN", raising=False)
    client = app.test_client()
    assert client.get("/internal").status_code == 404
    assert _internal_preview(client, "anything").status_code == 404


def test_internal_console_rejects_wrong_secret(monkeypatch):
    monkeypatch.setenv("LT_INTERNAL_ADMIN_TOKEN", "admin-secret")
    client = app.test_client()
    assert client.get("/internal?token=wrong").status_code == 403
    assert _internal_preview(client, "wrong").status_code == 403


def test_internal_preview_is_inert_and_uses_developer_secret(monkeypatch):
    monkeypatch.setenv("LT_INTERNAL_ADMIN_TOKEN", "admin-secret")
    calls = []
    original = developer_ui.build_dashboard
    monkeypatch.setattr(
        developer_ui,
        "build_dashboard",
        lambda learner_id: calls.append(learner_id) or original(learner_id),
    )
    response = _internal_preview(app.test_client(), "admin-secret")
    text = response.get_data(as_text=True)
    assert response.status_code == 200
    assert calls == ["learner-user"]
    assert "本人画面プレビュー（操作はできません）" in text
    assert 'class="page-content dashboard-grid learner-preview-mode" inert' in text
    assert "data-recommendation-start-url" not in text
    assert "data-line-message" not in text
    assert "data-dashboard-token" not in text
    assert create_dashboard_token("learner-user") not in text
    assert "/goukaku-no-michi/learning" not in text
    assert "/goukaku-no-michi/footprints" not in text


def test_internal_preview_never_records_recommendation_activity(monkeypatch):
    monkeypatch.setenv("LT_INTERNAL_ADMIN_TOKEN", "admin-secret")
    before = len(database._local_learning_events)
    monkeypatch.setattr(
        goukaku_ui,
        "record_activity_event",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("write attempted")),
    )
    assert _internal_preview(app.test_client(), "admin-secret").status_code == 200
    assert len(database._local_learning_events) == before


def test_supporter_top_does_not_expose_developer_preview_or_diagnostics(monkeypatch):
    token = _authorize_supporter(monkeypatch)
    response = app.test_client().get(
        f"/supporter?token={token}&learner_user_id=learner-user"
    )
    text = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "見守り用 合格への道" in text
    assert "閲覧専用" in text
    assert LEGACY_PREVIEW_PATH not in text
    assert LEGACY_DIAGNOSTICS_PATH not in text
    assert "表示確認用・操作不可" not in text
    assert "開発診断 ›" not in text


def test_existing_learner_and_supporter_modes_remain_distinct(monkeypatch):
    token = _authorize_supporter(monkeypatch)
    client = app.test_client()
    learner_token = create_dashboard_token("learner-user")
    learner = client.get(f"/goukaku-no-michi?token={learner_token}").get_data(as_text=True)
    supporter = client.get(
        f"/supporter/goukaku-no-michi?token={token}&learner_user_id=learner-user"
    ).get_data(as_text=True)
    assert "本人画面プレビュー（操作はできません）" not in learner
    assert "data-line-message" in learner
    assert "閲覧専用" in supporter
    assert "チャレンジする！" not in supporter
    assert "本人画面プレビュー（操作はできません）" not in supporter


def test_phase12_card_is_visible_but_action_is_inert_in_internal_preview(monkeypatch):
    monkeypatch.setenv("LT_INTERNAL_ADMIN_TOKEN", "admin-secret")
    monkeypatch.setenv("ENABLE_PHASE12_GUIDANCE_PREVIEW", "true")
    monkeypatch.setattr(goukaku_ui, "get_question_attempts", lambda *_: [])
    text = _internal_preview(app.test_client(), "admin-secret").get_data(as_text=True)
    assert "次にやること Preview" in text
    assert "phase12-preview-action learner-preview-inert" in text
    assert "data-phase12-action" not in text
    assert "data-recommendation-start-url" not in text


def test_preview_css_is_scoped_to_preview_mode():
    from pathlib import Path

    css = (Path(__file__).resolve().parents[1] / "static" / "goukaku" / "goukaku.css").read_text(encoding="utf-8")
    assert ".learner-preview-banner{" in css
    assert ".learner-preview-mode .learner-preview-inert{" in css
    assert ".learner-preview-mode[inert]{" in css
