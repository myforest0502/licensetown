import os

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "test-token")
os.environ.setdefault("CHANNEL_SECRET", "test-secret")

import app as app_module
import goukaku_ui


def _navigation():
    return {
        "headline": "まだ見ていない範囲を広げよう",
        "summary": "まだ十分に確認できていない分野を増やしていこう。",
        "today_action": {
            "field": "神経医学",
            "count": 10,
            "learning_intent": "exploration",
            "reason_code": "coverage_expand",
            "reason": "まだ確認が足りない分野を広げよう。",
            "button_label": "今日の学習を始める",
        },
        "attention_items": [
            {
                "field": "神経医学",
                "label": "まだ確認が足りない",
                "message": "まだ確認が足りない分野を広げよう。",
                "proven_weakness": False,
            }
        ],
        "stable_areas": [],
        "repair_areas": [],
        "coverage_gaps": [
            {
                "field": "心理学",
                "coverage": 0.1,
                "message": "まだ確認できていない内容があります。弱いと決まったわけではありません。",
            }
        ],
        "retention_message": "時間を空けた再確認の記録は、これから増えていきます。",
        "trial100_message": "本番形式の確認はまだ十分に記録されていません。",
        "safety_attention": False,
        "trace": {
            "readiness_status": "building_coverage",
            "recommendation_reason_code": "coverage_expand",
        },
    }


def _dashboard(nav=True):
    data = {
        "current_date": goukaku_ui.tokyo_today(),
        "exam_date": None,
        "days_until_exam": None,
        "overall_progress": 0,
        "total_answers": 100,
        "study_minutes": 0,
        "last_7_days_accuracy": 80,
        "average_accuracy": 80,
        "streak_days": 1,
        "field_stats": [],
        "field_progress_ui_enabled": False,
        "field_progress_fields": [],
        "overall_progress_ui_enabled": False,
        "overall_progress_preview": None,
        "phase12_guidance_preview_enabled": False,
        "phase12_guidance_preview": None,
        "weak_fields": [],
        "weak_analysis_message": "",
        "recommended_study": [("神経医学", 10)],
        "recommendation_reason": "legacy",
        "recommendation_progress": 0,
        "recommendation_goal": 10,
        "next_reward_answers": 10,
        "reward_interval": 10,
        "reward_progress": 0,
        "today_goal": 30,
        "today_progress": 0,
        "gensan_comment": "おう。",
        "learner_navigation_enabled": nav,
        "learner_navigation": _navigation() if nav else None,
    }
    return data


def test_home_enables_learner_navigation_for_authenticated_learner(monkeypatch):
    calls = []
    monkeypatch.setattr(goukaku_ui, "dashboard_user_id", lambda token: "learner" if token else None)
    monkeypatch.setattr(
        goukaku_ui,
        "build_dashboard",
        lambda user_id=None, include_learner_navigation=False: calls.append((user_id, include_learner_navigation)) or _dashboard(),
    )
    monkeypatch.setattr(goukaku_ui, "record_activity_event", lambda *args, **kwargs: None)
    response = app_module.app.test_client().get("/goukaku-no-michi?token=ok")
    text = response.get_data(as_text=True)
    assert response.status_code == 200
    assert calls == [("learner", True)]
    assert "現在地" in text
    assert "今日やること" in text
    assert "今日の学習を始める" in text
    assert 'data-recommendation-source="learner_navigation"' in text
    assert "coverage_expand" in text  # internal trace exists only in data attr for validation, not visible copy
    assert "Phase11" not in text
    assert "STRONG" not in text


def test_learner_data_routes_fail_closed_and_keep_signed_token_navigation(monkeypatch):
    client = app_module.app.test_client()
    for path in (
        "/goukaku-no-michi",
        "/goukaku-no-michi/subjects",
        "/goukaku-no-michi/footprints",
        "/goukaku-no-michi/learning",
    ):
        assert client.get(path).status_code == 403
        assert client.get(f"{path}?token=invalid").status_code == 403

    token = goukaku_ui.create_dashboard_token("learner")
    monkeypatch.setattr(goukaku_ui, "record_activity_event", lambda *args, **kwargs: None)
    home = client.get(f"/goukaku-no-michi?token={token}")
    assert home.status_code == 200
    text = home.get_data(as_text=True)
    assert f"/goukaku-no-michi/subjects?token={token}" in text
    assert f"/goukaku-no-michi/footprints?token={token}" in text
    assert client.get(f"/goukaku-no-michi/subjects?token={token}").status_code == 200
    assert client.get(f"/goukaku-no-michi/footprints?token={token}").status_code == 200


def test_legacy_weak_field_action_is_removed_from_formal_learner_path(monkeypatch):
    dashboard = _dashboard()
    dashboard["weak_fields"] = [
        {"name": "内科学", "reason": "要強化", "score": 40},
    ]
    monkeypatch.setattr(goukaku_ui, "dashboard_user_id", lambda token: "learner")
    monkeypatch.setattr(goukaku_ui, "build_dashboard", lambda *args, **kwargs: dashboard)
    monkeypatch.setattr(goukaku_ui, "record_activity_event", lambda *args, **kwargs: None)

    text = app_module.app.test_client().get("/goukaku-no-michi?token=ok").get_data(as_text=True)

    assert "/goukaku-no-michi/learning?" not in text
    assert "Ver.1では選択内容の確認まで利用できます" not in text
    assert "今日の学習ナビで確認" in text
    assert 'data-recommendation-source="learner_navigation"' in text


def test_formal_overall_reuses_single_learner_navigation_attempt_read(monkeypatch):
    calls = []
    monkeypatch.delenv("ENABLE_OVERALL_PROGRESS_UI", raising=False)
    monkeypatch.delenv("ENABLE_FIELD_PROGRESS_UI", raising=False)
    monkeypatch.setattr(
        goukaku_ui,
        "get_question_attempts",
        lambda user_id: calls.append(user_id) or [],
    )

    dashboard = goukaku_ui.build_dashboard("learner", include_learner_navigation=True)

    assert calls == ["learner"]
    assert dashboard["overall_progress_ui_enabled"] is True
    assert dashboard["overall_progress_preview"] is not None


def test_supporter_view_does_not_enable_learner_navigation(monkeypatch):
    calls = []
    monkeypatch.setattr(goukaku_ui, "authorized_supporter_learner", lambda *args: ("supporter", "learner"))
    monkeypatch.setattr(goukaku_ui, "user_names", {"learner": "学習者"})
    monkeypatch.setattr(
        goukaku_ui,
        "build_dashboard",
        lambda user_id=None, include_learner_navigation=False: calls.append((user_id, include_learner_navigation)) or _dashboard(nav=False),
    )
    response = app_module.app.test_client().get("/supporter/goukaku-no-michi?token=ok")
    assert response.status_code == 200
    assert calls == [("learner", False)]
    assert "今日の学習ナビ" not in response.get_data(as_text=True)


def test_navigation_cta_rejects_stale_or_tampered_intent(monkeypatch):
    monkeypatch.setattr(app_module, "dashboard_user_id", lambda token: "learner")
    monkeypatch.setattr(
        app_module,
        "build_dashboard",
        lambda user_id, include_learner_navigation=False: _dashboard(),
    )
    client = app_module.app.test_client()
    response = client.post(
        "/goukaku-no-michi/recommendation/start",
        json={
            "token": "ok",
            "field": "神経医学",
            "count": 10,
            "source": "learner_navigation",
            "intent": "repair",
            "reason": "coverage_expand",
        },
    )
    assert response.status_code == 409


def test_navigation_cta_accepts_validated_intent_then_uses_central_session_creator(monkeypatch):
    calls = []
    monkeypatch.setattr(app_module, "dashboard_user_id", lambda token: "learner")
    monkeypatch.setattr(
        app_module,
        "build_dashboard",
        lambda user_id, include_learner_navigation=False: _dashboard(),
    )
    monkeypatch.setattr(
        app_module,
        "create_web_recommendation_session",
        lambda user_id, category_small, question_count, token: calls.append((user_id, category_small, question_count, token)) or ("session-1", True),
    )
    response = app_module.app.test_client().post(
        "/goukaku-no-michi/recommendation/start",
        json={
            "token": "ok",
            "field": "神経医学",
            "count": 10,
            "source": "learner_navigation",
            "intent": "exploration",
            "reason": "coverage_expand",
        },
    )
    assert response.status_code == 200
    assert response.get_json()["redirect_url"] == "/goukaku-no-michi/learning/session-1"
    assert len(calls) == 1


def test_javascript_forces_structured_web_post_for_learner_navigation():
    from pathlib import Path

    js = (Path(__file__).resolve().parents[1] / "static" / "goukaku" / "goukaku.js").read_text(encoding="utf-8")
    assert "recommendationSource === 'learner_navigation'" in js
    assert "!structuredNavigation && await liffReady" in js
    assert "recommendationIntent" in js
    assert "recommendationReason" in js
