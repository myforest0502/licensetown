from datetime import datetime, timezone
import os

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "test-token")
os.environ.setdefault("CHANNEL_SECRET", "test-secret")

import goukaku_ui
from app import app
from field_evidence import build_field_evidence
from field_progress import STATE_SCORES, build_field_progress
from goukaku_ui import create_dashboard_token
from overall_progress_presentation import build_overall_progress_presentation
from question_bank import get_question_tag


def _progress(counts):
    total = sum(counts.values())
    score = sum(counts.get(state, 0) * value for state, value in STATE_SCORES.items()) / total if total else 0
    touched = total - counts.get("unseen", 0)
    return {"overall": {
        "total_unique_canonical_nodes": total,
        "touched_unique_canonical_nodes": touched,
        "state_counts": {state: counts.get(state, 0) for state in STATE_SCORES},
        "overall_progress_score": score,
    }}


def _attempt(question_id="Q269", user_id="overall-ui-user"):
    return {
        "user_id": user_id, "question_id": question_id,
        "knowledge_node_id": get_question_tag(question_id)["knowledge_node_id"],
        "is_correct": True, "confidence": 1, "selected_answers": ["1"],
        "answer_status": "answered",
        "answered_at": datetime(2026, 8, 30, tzinfo=timezone.utc),
        "event_key": "overall-ui", "attempt_position": 1,
    }


def test_overall_presentation_state_fixtures_and_ratios():
    cases = [
        ({"unseen": 100}, 0, "0%"),
        ({"stable": 40, "unseen": 60}, 0.4, "40%"),
        ({"repaired": 100}, 0.7, "70%"),
        ({"recheck_due": 100}, 0.6, "60%"),
        ({"repairing": 100}, 0.1, "10%"),
    ]
    for counts, raw, display in cases:
        result = build_overall_progress_presentation(_progress(counts))
        assert result["progress_raw"] == raw
        assert result["progress_display"] == display
    result = build_overall_progress_presentation(_progress({
        "repaired": 2, "recheck_due": 3, "stable": 5, "unseen": 10,
    }))
    assert result["repair_completed_raw"] == 0.5
    assert result["stable_raw"] == 0.25


def test_one_checking_node_is_unique_low_progress():
    progress = build_field_progress(build_field_evidence([_attempt()]))
    result = build_overall_progress_presentation(progress)
    assert result["total_unique_canonical_nodes"] == 1509
    assert result["touched_unique_canonical_nodes"] == 1
    assert 0 < result["progress_raw"] < 0.01
    assert result["progress_display"] == "1%未満"
    assert result["coverage_raw"] == 1 / 1509


def test_flag_off_preserves_legacy_overall_and_has_no_attempt_read(monkeypatch):
    monkeypatch.delenv("ENABLE_OVERALL_PROGRESS_UI", raising=False)
    monkeypatch.delenv("ENABLE_FIELD_PROGRESS_UI", raising=False)
    monkeypatch.setattr(goukaku_ui, "get_question_attempts", lambda *_: (_ for _ in ()).throw(AssertionError("unexpected read")))
    dashboard = goukaku_ui.build_dashboard("overall-flag-off")
    assert not dashboard["overall_progress_ui_enabled"]
    assert dashboard["overall_progress_preview"] is None
    token = create_dashboard_token("overall-flag-off")
    text = app.test_client().get(f"/goukaku-no-michi?token={token}").get_data(as_text=True)
    assert "総合到達度" in text
    assert "合格への到達度" not in text


def test_overall_flag_on_is_independent_and_shares_replay_with_field(monkeypatch):
    calls = []
    monkeypatch.setenv("ENABLE_OVERALL_PROGRESS_UI", "true")
    monkeypatch.setenv("ENABLE_FIELD_PROGRESS_UI", "true")
    monkeypatch.setattr(goukaku_ui, "get_question_attempts", lambda user: calls.append(user) or [_attempt(user_id=user)])
    dashboard = goukaku_ui.build_dashboard("shared-preview-user")
    assert calls == ["shared-preview-user"]
    assert dashboard["overall_progress_ui_enabled"]
    assert dashboard["field_progress_ui_enabled"]
    assert dashboard["overall_progress_preview"]["progress_display"] == "1%未満"
    assert len(dashboard["field_progress_fields"]) == 18
    assert "shared-preview-user" not in str(dashboard["overall_progress_preview"])


def test_overall_preview_renders_for_owner_and_supporter_without_cta_change(monkeypatch):
    monkeypatch.setenv("ENABLE_OVERALL_PROGRESS_UI", "true")
    monkeypatch.delenv("ENABLE_FIELD_PROGRESS_UI", raising=False)
    monkeypatch.setattr(goukaku_ui, "get_question_attempts", lambda user: [_attempt(user_id=user)])
    token = create_dashboard_token("overall-ui-user")
    owner = app.test_client().get(f"/goukaku-no-michi?token={token}").get_data(as_text=True)
    assert "合格への到達度" in owner
    assert "学習範囲" in owner and "修復済み" in owner and "定着" in owner
    assert "チャレンジする！" in owner
    assert "field-progress-row" not in owner
    monkeypatch.setattr(goukaku_ui, "authorized_supporter_learner", lambda *_: ("supporter", "learner"))
    supporter = app.test_client().get("/supporter/goukaku-no-michi?token=test").get_data(as_text=True)
    assert "合格への到達度" in supporter
    assert "閲覧専用" in supporter
    assert "チャレンジする！" not in supporter


def test_invalid_token_does_not_read_or_expose_overall_preview(monkeypatch):
    monkeypatch.setenv("ENABLE_OVERALL_PROGRESS_UI", "true")
    monkeypatch.setattr(goukaku_ui, "get_question_attempts", lambda *_: (_ for _ in ()).throw(AssertionError("unexpected read")))
    for query in ("", "?token=invalid"):
        text = app.test_client().get(f"/goukaku-no-michi{query}").get_data(as_text=True)
        assert "overall-progress-preview" not in text
        assert "総合到達度" in text


def test_overall_preview_css_is_scoped_and_responsive():
    from pathlib import Path
    css = (Path(__file__).resolve().parents[1] / "static" / "goukaku" / "goukaku.css").read_text(encoding="utf-8")
    assert ".overall-progress-metrics{" in css
    assert ".overall-progress-preview .achievement-copy>small{" in css
    assert "@media(max-width:700px){.overall-progress-preview" in css
