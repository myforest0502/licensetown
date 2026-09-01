import os
from pathlib import Path

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "test-token")
os.environ.setdefault("CHANNEL_SECRET", "test-secret")

import goukaku_ui
from app import app
from goukaku_ui import create_dashboard_token


def _disable_other_previews(monkeypatch):
    monkeypatch.delenv("ENABLE_FIELD_PROGRESS_UI", raising=False)
    monkeypatch.delenv("ENABLE_OVERALL_PROGRESS_UI", raising=False)


def test_flag_defaults_off_and_adds_no_attempt_read(monkeypatch):
    _disable_other_previews(monkeypatch)
    monkeypatch.delenv("ENABLE_PHASE12_GUIDANCE_PREVIEW", raising=False)
    monkeypatch.setattr(
        goukaku_ui,
        "get_question_attempts",
        lambda *_: (_ for _ in ()).throw(AssertionError("unexpected read")),
    )
    dashboard = goukaku_ui.build_dashboard("phase12-off-user")
    assert dashboard["phase12_guidance_preview_enabled"] is False
    assert dashboard["phase12_guidance_preview"] is None


def test_flag_on_builds_shadow_preview_without_replacing_current_guidance(monkeypatch):
    _disable_other_previews(monkeypatch)
    monkeypatch.delenv("ENABLE_PHASE12_GUIDANCE_PREVIEW", raising=False)
    before = goukaku_ui.build_dashboard("phase12-guidance-user")
    calls = []
    monkeypatch.setenv("ENABLE_PHASE12_GUIDANCE_PREVIEW", "true")
    monkeypatch.setattr(goukaku_ui, "get_question_attempts", lambda user: calls.append(user) or [])
    after = goukaku_ui.build_dashboard("phase12-guidance-user")
    assert calls == ["phase12-guidance-user"]
    assert after["phase12_guidance_preview_enabled"] is True
    assert after["phase12_guidance_preview"]["reason"]
    assert after["recommended_study"] == before["recommended_study"]
    assert after["recommendation_reason"] == before["recommendation_reason"]


def test_phase12_reuses_single_attempt_read_with_existing_previews(monkeypatch):
    monkeypatch.setenv("ENABLE_PHASE12_GUIDANCE_PREVIEW", "true")
    monkeypatch.setenv("ENABLE_FIELD_PROGRESS_UI", "true")
    monkeypatch.setenv("ENABLE_OVERALL_PROGRESS_UI", "true")
    calls = []
    monkeypatch.setattr(goukaku_ui, "get_question_attempts", lambda user: calls.append(user) or [])
    dashboard = goukaku_ui.build_dashboard("shared-phase12-user")
    assert calls == ["shared-phase12-user"]
    assert dashboard["phase12_guidance_preview_enabled"]
    assert dashboard["field_progress_ui_enabled"]
    assert dashboard["overall_progress_ui_enabled"]


def test_owner_sees_additive_preview_and_existing_action_route(monkeypatch):
    _disable_other_previews(monkeypatch)
    monkeypatch.setenv("ENABLE_PHASE12_GUIDANCE_PREVIEW", "true")
    monkeypatch.setattr(goukaku_ui, "get_question_attempts", lambda *_: [])
    token = create_dashboard_token("phase12-owner")
    response = app.test_client().get(f"/goukaku-no-michi?token={token}")
    text = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "次にやること Preview" in text
    assert "今日のおすすめ学習" in text
    assert "data-phase12-action" in text
    assert "現在は検証中の案内です。通常のおすすめ学習はこれまでどおり利用できます。" in text


def test_supporter_preview_is_read_only_and_has_no_action(monkeypatch):
    _disable_other_previews(monkeypatch)
    monkeypatch.setenv("ENABLE_PHASE12_GUIDANCE_PREVIEW", "true")
    monkeypatch.setattr(goukaku_ui, "get_question_attempts", lambda *_: [])
    monkeypatch.setattr(goukaku_ui, "authorized_supporter_learner", lambda *_: ("supporter", "learner"))
    response = app.test_client().get("/supporter/goukaku-no-michi?token=test")
    text = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "次にやること Preview" in text
    assert "閲覧専用" in text
    assert "data-phase12-action" not in text


def test_missing_or_invalid_dashboard_token_never_reads_or_exposes_preview(monkeypatch):
    _disable_other_previews(monkeypatch)
    monkeypatch.setenv("ENABLE_PHASE12_GUIDANCE_PREVIEW", "true")
    monkeypatch.setattr(
        goukaku_ui,
        "get_question_attempts",
        lambda *_: (_ for _ in ()).throw(AssertionError("unexpected read")),
    )
    for query in ("", "?token=invalid"):
        text = app.test_client().get(f"/goukaku-no-michi{query}").get_data(as_text=True)
        assert "phase12-guidance-preview" not in text


def test_preview_css_is_scoped_and_responsive():
    css = (Path(__file__).resolve().parents[1] / "static" / "goukaku" / "goukaku.css").read_text(encoding="utf-8")
    assert ".phase12-guidance-preview{" in css
    assert ".phase12-state-summary{" in css
    assert "@media(max-width:700px){.phase12-state-summary" in css
