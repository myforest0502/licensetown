import os

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "test-token")
os.environ.setdefault("CHANNEL_SECRET", "test-secret")

import database
from database import record_learning_batch
from goukaku_ui import build_dashboard


def _clear_local_history():
    database._local_learning_events.clear()
    database._local_question_attempts.clear()


def test_learner_navigation_enables_formal_field_progress_without_preview_flag(monkeypatch):
    monkeypatch.delenv("ENABLE_FIELD_PROGRESS_UI", raising=False)
    _clear_local_history()
    record_learning_batch(
        "formal-field-progress-user",
        "formal-field-progress-event",
        "study",
        1,
        1,
        question_results=[
            {
                "question_id": "Q1",
                "selected_answers": ["1"],
                "is_correct": True,
                "confidence": 1,
            }
        ],
    )

    dashboard = build_dashboard(
        "formal-field-progress-user",
        include_learner_navigation=True,
    )

    assert dashboard["learner_navigation_enabled"] is True
    assert dashboard["field_progress_ui_enabled"] is True
    assert dashboard["field_progress_fields"]
    assert all("progress_percent" in field for field in dashboard["field_progress_fields"])
    assert all("accuracy_label" in field for field in dashboard["field_progress_fields"])
    _clear_local_history()


def test_legacy_non_learner_dashboard_keeps_field_preview_disabled_by_default(monkeypatch):
    monkeypatch.delenv("ENABLE_FIELD_PROGRESS_UI", raising=False)
    _clear_local_history()

    dashboard = build_dashboard("legacy-field-progress-user")

    assert dashboard["learner_navigation_enabled"] is False
    assert dashboard["field_progress_ui_enabled"] is False
    assert dashboard["field_progress_fields"] == []
    _clear_local_history()
