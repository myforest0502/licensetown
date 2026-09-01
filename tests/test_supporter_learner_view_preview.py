import os

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "test-token")
os.environ.setdefault("CHANNEL_SECRET", "test-secret")

from app import app
import goukaku_ui
from goukaku_ui import create_dashboard_token, create_supporter_token


PREVIEW_PATH = "/supporter/goukaku-no-michi/learner-preview"


def _authorize(monkeypatch, learner_id="learner-user"):
    monkeypatch.setattr(
        goukaku_ui,
        "get_supported_learner_ids",
        lambda supporter_id: [learner_id] if supporter_id == "supporter-user" else [],
    )
    return create_supporter_token("supporter-user")


def _preview(client, token, learner_id="learner-user"):
    return client.get(
        f"{PREVIEW_PATH}?token={token}&learner_user_id={learner_id}"
    )


def test_authorized_supporter_gets_inert_learner_visual_preview(monkeypatch):
    token = _authorize(monkeypatch)
    calls = []
    original = goukaku_ui.build_dashboard
    monkeypatch.setattr(
        goukaku_ui,
        "build_dashboard",
        lambda learner_id: calls.append(learner_id) or original(learner_id),
    )
    response = _preview(app.test_client(), token)
    text = response.get_data(as_text=True)
    assert response.status_code == 200
    assert calls == ["learner-user"]
    assert "本人画面プレビュー（操作はできません）" in text
    assert "今日のおすすめ学習" in text
    assert "チャレンジする！" in text
    assert "あなたの足跡を見る" in text
    for label in ("ホームに戻る", "勉強する", "相談する", "熱血モード"):
        assert label in text
    assert 'class="page-content dashboard-grid learner-preview-mode" inert' in text


def test_invalid_token_and_unrelated_learner_are_forbidden(monkeypatch):
    token = _authorize(monkeypatch)
    client = app.test_client()
    assert _preview(client, "invalid").status_code == 403
    assert _preview(client, token, "other-learner").status_code == 403


def test_preview_contains_no_live_action_or_learner_token(monkeypatch):
    token = _authorize(monkeypatch)
    text = _preview(app.test_client(), token).get_data(as_text=True)
    assert "data-recommendation-start-url" not in text
    assert "data-line-message" not in text
    assert "data-dashboard-token" not in text
    assert create_dashboard_token("learner-user") not in text
    assert "/goukaku-no-michi/learning" not in text
    assert "/goukaku-no-michi/footprints" not in text
    assert "learner-preview-inert" in text


def test_preview_never_records_recommendation_activity(monkeypatch):
    token = _authorize(monkeypatch)
    monkeypatch.setattr(
        goukaku_ui,
        "record_activity_event",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("write attempted")),
    )
    assert _preview(app.test_client(), token).status_code == 200


def test_existing_learner_and_supporter_modes_remain_distinct(monkeypatch):
    token = _authorize(monkeypatch)
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


def test_supporter_top_separates_monitoring_and_learner_preview(monkeypatch):
    token = _authorize(monkeypatch)
    response = app.test_client().get(
        f"/supporter?token={token}&learner_user_id=learner-user"
    )
    text = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "見守り用 合格への道" in text
    assert "閲覧専用" in text
    assert "本人画面プレビュー" in text
    assert "表示確認用・操作不可" in text
    assert PREVIEW_PATH in text


def test_phase12_card_is_visible_but_action_is_inert(monkeypatch):
    token = _authorize(monkeypatch)
    monkeypatch.setenv("ENABLE_PHASE12_GUIDANCE_PREVIEW", "true")
    monkeypatch.setattr(goukaku_ui, "get_question_attempts", lambda *_: [])
    text = _preview(app.test_client(), token).get_data(as_text=True)
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
