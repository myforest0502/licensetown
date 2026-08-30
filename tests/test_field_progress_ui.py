from datetime import datetime, timezone
import os

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "test-token")
os.environ.setdefault("CHANNEL_SECRET", "test-secret")

import goukaku_ui
from app import app
from field_progress_presentation import build_field_progress_presentation, format_progress_percent
from goukaku_ui import create_dashboard_token
from question_bank import get_question_tag


def _attempt(question_id="Q269", *, user_id="field-progress-ui-user"):
    return {
        "user_id": user_id, "question_id": question_id,
        "knowledge_node_id": get_question_tag(question_id)["knowledge_node_id"],
        "is_correct": True, "confidence": 1, "selected_answers": ["1"],
        "answer_status": "answered",
        "answered_at": datetime(2026, 8, 30, tzinfo=timezone.utc),
        "event_key": "field-progress-ui", "attempt_position": 1,
    }


def test_progress_formatter_keeps_raw_calculation_separate():
    assert format_progress_percent(0) == "0%"
    assert format_progress_percent(0.0049) == "1%未満"
    assert format_progress_percent(0.0149) == "1%"
    assert format_progress_percent(0.015) == "2%"


def test_presentation_has_all_fields_and_low_progress_with_full_accuracy():
    rows = build_field_progress_presentation([_attempt()], legacy_fields=[{
        "name": "基礎運動学", "learned": True, "answered_count": 1, "accuracy": 100,
    }])
    assert len(rows) == 18
    learned = next(item for item in rows if item["answer_count"] == 1)
    assert 0 < learned["progress_raw"] < 0.01
    assert learned["progress_display"] == "1%未満"
    assert learned["coverage_display"] in {"1%未満", "2%"}
    assert learned["accuracy_display"] == "100%"
    unseen = next(item for item in rows if item["answer_count"] == 0)
    assert unseen["progress_display"] == "0%"
    assert unseen["coverage_display"] == "0%"
    assert unseen["accuracy_display"] == "--"


def test_flag_defaults_off_and_does_not_read_attempts(monkeypatch):
    monkeypatch.delenv("ENABLE_FIELD_PROGRESS_UI", raising=False)
    monkeypatch.setattr(goukaku_ui, "get_question_attempts", lambda *_: (_ for _ in ()).throw(AssertionError("unexpected read")))
    dashboard = goukaku_ui.build_dashboard("flag-off-user")
    assert not dashboard["field_progress_ui_enabled"]
    assert dashboard["field_progress_fields"] == []


def test_enabled_dashboard_reads_only_current_user_once(monkeypatch):
    monkeypatch.setenv("ENABLE_FIELD_PROGRESS_UI", "true")
    calls = []
    monkeypatch.setattr(goukaku_ui, "get_question_attempts", lambda user_id: calls.append(user_id) or [_attempt(user_id=user_id)])
    dashboard = goukaku_ui.build_dashboard("isolated-user")
    assert calls == ["isolated-user"]
    assert dashboard["field_progress_ui_enabled"]
    assert len(dashboard["field_progress_fields"]) == 18
    assert "isolated-user" not in str(dashboard["field_progress_fields"])


def test_enabled_home_separates_three_metrics_and_keeps_overall_and_cta(monkeypatch):
    monkeypatch.setenv("ENABLE_FIELD_PROGRESS_UI", "true")
    monkeypatch.setattr(goukaku_ui, "get_question_attempts", lambda *_: [_attempt()])
    token = create_dashboard_token("field-progress-ui-user")
    text = app.test_client().get(f"/goukaku-no-michi?token={token}").get_data(as_text=True)
    assert "学習範囲" in text
    assert "正答率" in text
    assert "1%未満" in text
    assert "総合到達度" in text
    assert "今日のおすすめ学習" in text
    assert "チャレンジする！" in text


def test_supporter_uses_same_read_only_progress_view(monkeypatch):
    monkeypatch.setenv("ENABLE_FIELD_PROGRESS_UI", "true")
    monkeypatch.setattr(goukaku_ui, "get_question_attempts", lambda user_id: [_attempt(user_id=user_id)])
    monkeypatch.setattr(goukaku_ui, "authorized_supporter_learner", lambda *_: ("supporter", "learner"))
    response = app.test_client().get("/supporter/goukaku-no-michi?token=test")
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert "閲覧専用" in text
    assert "学習範囲" in text
    assert "チャレンジする！" not in text


def test_preview_css_is_scoped_and_responsive():
    from pathlib import Path
    css = (Path(__file__).resolve().parents[1] / "static" / "goukaku" / "goukaku.css").read_text(encoding="utf-8")
    assert ".field-progress-row{" in css
    assert ".field-progress-bar{" in css
    assert "@media(max-width:700px){.field-progress-row{" in css


def test_invalid_or_missing_token_does_not_expose_preview_data(monkeypatch):
    monkeypatch.setenv("ENABLE_FIELD_PROGRESS_UI", "true")
    monkeypatch.setattr(goukaku_ui, "get_question_attempts", lambda *_: (_ for _ in ()).throw(AssertionError("unexpected read")))
    for query in ("", "?token=invalid"):
        text = app.test_client().get(f"/goukaku-no-michi{query}").get_data(as_text=True)
        assert "field-progress-row" not in text
