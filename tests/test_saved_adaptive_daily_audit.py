import os
from datetime import datetime, timezone

os.environ.setdefault("OPENAI_API_KEY", "x")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "x")
os.environ.setdefault("CHANNEL_SECRET", "x")

import database
from app import app
from database import get_latest_adaptive_daily_learning_event, set_supporter_link
from goukaku_ui import create_supporter_token
from pilot_diagnostics import build_saved_adaptive_daily_audit


NOW = datetime(2026, 9, 1, tzinfo=timezone.utc)
AUDIT = {
    "selection_reason": "repairing",
    "selection_group": "repair",
    "selection_score": 900,
    "repair_evidence_quality": "strong",
    "recent_question_repeat": False,
    "recent_cooldown_bypassed": False,
}


def _result(number, **overrides):
    result = {"question_id": f"Q{number}", "learning_source": "adaptive_daily", **AUDIT}
    result.update(overrides)
    return result


def setup_function():
    database._local_learning_events.clear()
    database._local_question_attempts.clear()
    database._local_supporter_links.clear()


def test_latest_adaptive_daily_excludes_other_learning_sources():
    database._local_learning_events.update({
        "adaptive-old": {"user_id": "learner", "mode": "study", "answered_count": 1,
                         "correct_count": 0, "answered_at": NOW, "question_results": [_result(1)]},
        "random-new": {"user_id": "learner", "mode": "study", "answered_count": 1,
                       "correct_count": 1, "answered_at": NOW.replace(hour=1),
                       "question_results": [{"question_id": "Q2", "learning_source": "random"}]},
    })
    assert get_latest_adaptive_daily_learning_event("learner")["event_key"] == "adaptive-old"
    assert get_latest_adaptive_daily_learning_event("other") is None


def test_saved_audit_summarizes_all_30_without_recalculation():
    results = [_result(number) for number in range(1, 31)]
    results[2]["recent_question_repeat"] = True
    results[4]["recent_cooldown_bypassed"] = True
    audit = build_saved_adaptive_daily_audit({
        "mode": "study", "answered_at": NOW, "question_results": results,
    })
    assert audit["question_count"] == audit["unique_question_count"] == 30
    assert audit["audit_fields_complete"] is True
    assert audit["recent_repeat_count"] == audit["cooldown_bypass_count"] == 1
    assert audit["recent_repeat_question_ids"] == ["Q3"]
    assert audit["cooldown_bypass_question_ids"] == ["Q5"]


def test_missing_audit_field_is_fail_and_empty_is_safe():
    incomplete = _result(1)
    incomplete.pop("selection_score")
    audit = build_saved_adaptive_daily_audit({"question_results": [incomplete]})
    assert audit["audit_fields_complete"] is False
    assert audit["results"][0]["missing_audit_fields"] == ["selection_score"]
    assert build_saved_adaptive_daily_audit(None)["exists"] is False


def test_supporter_route_displays_persisted_fields_and_keeps_simulation():
    results = [_result(number) for number in range(1, 31)]
    results[0]["recent_question_repeat"] = True
    database._local_learning_events["adaptive"] = {
        "user_id": "learner", "mode": "study", "answered_count": 30,
        "correct_count": 0, "answered_at": NOW,
        "question_results": results,
    }
    before = dict(database._local_learning_events)
    set_supporter_link("supporter", "learner")
    token = create_supporter_token("supporter")
    response = app.test_client().get(
        f"/supporter/pilot-diagnostics?token={token}&learner_user_id=learner"
    )
    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "実出題 adaptive_daily 監査" in html
    assert "audit fields complete:</b> PASS" in html
    assert "selection_reason: repairing" in html
    assert "recent repeats: 1" in html
    assert html.count('class="saved-adaptive-audit-item"') == 30
    assert "最新のおすすめ30問シミュレーション" in html
    assert database._local_learning_events == before
