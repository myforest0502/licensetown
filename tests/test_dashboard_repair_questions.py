"""Repair-questions CTA is authenticated, separate and evidence-preserving."""
import os
from pathlib import Path

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "test-token")
os.environ.setdefault("CHANNEL_SECRET", "test-secret")

import app as app_module


def test_repair_questions_start_uses_server_selected_repair_intent(monkeypatch):
    monkeypatch.setattr(app_module, "dashboard_user_id", lambda token: "learner" if token == "valid" else None)
    monkeypatch.setattr(app_module, "current_user_catchup", lambda *_args: {"active": True})
    calls = []

    def fake_start(*args, **kwargs):
        calls.append((args, kwargs))
        return "safe-session", True

    monkeypatch.setattr(app_module, "create_web_recommendation_session", fake_start)
    client = app_module.app.test_client()
    response = client.post("/goukaku-no-michi/recommendation/start", json={
        "token": "valid",
        "source": "repair_questions",
        "count": 10,
        "field": "攻撃者が指定した分野",  # no client-controlled field selection
        "intent": "exploration",
    })
    assert response.status_code == 200
    assert response.json["redirect_url"] == "/goukaku-no-michi/learning/safe-session"
    assert calls == [(
        ("learner", None, 10, "valid"),
        {"learning_intent": "repair", "session_kind": "dashboard_repair"},
    )]


def test_repair_questions_is_fail_closed_on_auth_and_count(monkeypatch):
    monkeypatch.setattr(app_module, "dashboard_user_id", lambda token: "learner" if token == "valid" else None)
    monkeypatch.setattr(app_module, "current_user_catchup", lambda *_args: {"active": True})
    monkeypatch.setattr(
        app_module, "create_web_recommendation_session",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("Must not start")),
    )
    client = app_module.app.test_client()
    for payload, expected in [
        ({"source": "repair_questions", "token": "invalid", "count": 10}, 403),
        ({"source": "repair_questions", "token": "valid", "count": 30}, 400),
        ({"source": "repair_questions", "token": "valid", "count": "10"}, 400),
        ({"source": "repair_questions", "token": "valid", "count": 0}, 400),
    ]:
        assert client.post("/goukaku-no-michi/recommendation/start", json=payload).status_code == expected


def test_repair_entry_is_visible_only_while_behind_and_uses_normal_web_flow():
    root = Path(__file__).resolve().parents[1]
    template = (root / "templates/goukaku/home.html").read_text(encoding="utf-8")
    script = (root / "static/goukaku/dashboard-product-copy-v01.js").read_text(encoding="utf-8")
    client_script = (root / "static/goukaku/goukaku.js").read_text(encoding="utf-8")
    base = (root / "templates/goukaku/base.html").read_text(encoding="utf-8")
    assert "修復問題を10問始める" in template
    assert 'data-recommendation-source="repair_questions"' in template
    assert 'data-repair-question-card' in template
    assert "repairCard.hidden = !catchup.active" in script
    assert 'data-repair-question-card' in template
    assert "currentFinish" in script and "overall.progress_raw" in script
    assert "button.dataset.recommendationSource === 'repair_questions'" in client_script
    assert "!structuredNavigation && await liffReady" in client_script
    assert "{% if not read_only and not learner_preview %}" in template
    assert "20261027-repair-questions1" in base
    assert "合格確率" not in template.split("lt-repair-card", 1)[1].split("</section>", 1)[0]


def test_repair_session_reuse_isolated_from_normal_recommendation():
    src = Path(__file__).resolve().parents[1] / "app.py"
    app_source = src.read_text(encoding="utf-8")
    assert 'and session.get("session_kind") == session_kind' in app_source
    assert '"session_kind": session_kind' in app_source
    assert '"learning_source": "dashboard_recommendation"' in app_source
    assert '"repair_questions_mode": session.get("session_kind") == "dashboard_repair"' in app_source



def test_repair_only_selector_does_not_pad_with_new_topics():
    # An untouched learner must not receive exploration Qs mislabeled as repair.
    import pytest
    from adaptive_question_selector import build_node_adaptive_session
    from question_bank import QuestionAvailabilityError

    with pytest.raises(QuestionAvailabilityError):
        build_node_adaptive_session(
            [], question_count=10, learning_intent="repair", strict_repair=True,
        )
