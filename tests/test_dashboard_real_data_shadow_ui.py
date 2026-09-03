from datetime import datetime, timezone
import os

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "test-token")
os.environ.setdefault("CHANNEL_SECRET", "test-secret")

import goukaku_ui
from question_bank import get_question_tag


def _attempt(user_id="shadow-ui-user", question_id="Q269"):
    return {
        "user_id": user_id,
        "question_id": question_id,
        "knowledge_node_id": get_question_tag(question_id)["knowledge_node_id"],
        "is_correct": True,
        "confidence": 1,
        "selected_answers": ["1"],
        "answer_status": "answered",
        "answered_at": datetime(2026, 9, 3, tzinfo=timezone.utc),
        "event_key": "shadow-ui",
        "attempt_position": 1,
    }


def test_shadow_flag_defaults_off_and_does_not_add_attempt_read(monkeypatch):
    monkeypatch.delenv("ENABLE_DASHBOARD_REAL_DATA_SHADOW", raising=False)
    monkeypatch.delenv("ENABLE_FIELD_PROGRESS_UI", raising=False)
    monkeypatch.delenv("ENABLE_OVERALL_PROGRESS_UI", raising=False)
    monkeypatch.delenv("ENABLE_PHASE12_GUIDANCE_PREVIEW", raising=False)
    monkeypatch.setattr(
        goukaku_ui,
        "get_question_attempts",
        lambda *_: (_ for _ in ()).throw(AssertionError("unexpected read")),
    )
    dashboard = goukaku_ui.build_dashboard("shadow-off-user")
    assert dashboard["dashboard_real_data_shadow_enabled"] is False
    assert dashboard["dashboard_real_data_shadow"] is None


def test_shadow_enabled_reuses_single_attempt_evidence_progress_pipeline(monkeypatch):
    monkeypatch.setenv("ENABLE_DASHBOARD_REAL_DATA_SHADOW", "true")
    monkeypatch.setenv("ENABLE_FIELD_PROGRESS_UI", "true")
    monkeypatch.setenv("ENABLE_OVERALL_PROGRESS_UI", "true")
    monkeypatch.delenv("ENABLE_PHASE12_GUIDANCE_PREVIEW", raising=False)

    calls = []
    attempt = _attempt()
    monkeypatch.setattr(
        goukaku_ui,
        "get_question_attempts",
        lambda user_id: calls.append(user_id) or [dict(attempt, user_id=user_id)],
    )
    captured = {}

    def fake_shadow(attempts, evidence=None, progress=None, **kwargs):
        captured["attempts"] = attempts
        captured["evidence"] = evidence
        captured["progress"] = progress
        captured["kwargs"] = kwargs
        return {
            "status": "dashboard_real_data_shadow_v0.1",
            "shadow_only": True,
            "recommendation_intent": {"exact_question_ids": None},
        }

    monkeypatch.setattr(goukaku_ui, "build_dashboard_real_data_shadow", fake_shadow)
    dashboard = goukaku_ui.build_dashboard("shadow-ui-user")

    assert calls == ["shadow-ui-user"]
    assert dashboard["dashboard_real_data_shadow_enabled"] is True
    assert dashboard["dashboard_real_data_shadow"]["shadow_only"] is True
    assert captured["attempts"][0]["user_id"] == "shadow-ui-user"
    assert captured["evidence"] is not None
    assert captured["progress"] is not None
    assert captured["kwargs"]["legacy_overall_progress_percent"] == dashboard["overall_progress"]
    assert captured["kwargs"]["legacy_weak_fields"] == dashboard["weak_fields"]
    assert dashboard["field_progress_ui_enabled"] is True
    assert dashboard["overall_progress_ui_enabled"] is True


def test_shadow_does_not_replace_legacy_recommendation(monkeypatch):
    monkeypatch.setenv("ENABLE_DASHBOARD_REAL_DATA_SHADOW", "true")
    monkeypatch.delenv("ENABLE_FIELD_PROGRESS_UI", raising=False)
    monkeypatch.delenv("ENABLE_OVERALL_PROGRESS_UI", raising=False)
    monkeypatch.delenv("ENABLE_PHASE12_GUIDANCE_PREVIEW", raising=False)
    monkeypatch.setattr(goukaku_ui, "get_question_attempts", lambda user_id: [_attempt(user_id=user_id)])

    def fake_shadow(*args, **kwargs):
        return {
            "status": "dashboard_real_data_shadow_v0.1",
            "shadow_only": True,
            "recommendation_intent": {
                "target_field": "SHADOW_ONLY_FIELD",
                "exact_question_ids": None,
            },
        }

    monkeypatch.setattr(goukaku_ui, "build_dashboard_real_data_shadow", fake_shadow)
    dashboard = goukaku_ui.build_dashboard("shadow-ui-user")
    assert dashboard["dashboard_real_data_shadow"]["recommendation_intent"]["target_field"] == "SHADOW_ONLY_FIELD"
    assert all(
        not item or item[0] != "SHADOW_ONLY_FIELD"
        for item in dashboard["recommended_study"]
    )
