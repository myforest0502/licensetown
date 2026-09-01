import os
from datetime import datetime, timedelta, timezone

os.environ.setdefault("OPENAI_API_KEY", "x")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "x")
os.environ.setdefault("CHANNEL_SECRET", "x")

import database
from app import app
from database import (
    get_latest_adaptive_daily_learning_event,
    get_latest_adaptive_daily_learning_session_events,
    set_supporter_link,
)
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
    events = [
        {"event_key": f"session-a:{index + 1}", "mode": "study",
         "answered_at": NOW.replace(minute=index), "question_results": results[index * 5:(index + 1) * 5]}
        for index in range(6)
    ]
    audit = build_saved_adaptive_daily_audit(events)
    assert audit["question_count"] == audit["unique_question_count"] == 30
    assert audit["event_count"] == 6 and audit["session_complete"] is True
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
    for index in range(6):
        database._local_learning_events[f"adaptive-session:{index + 1}"] = {
            "user_id": "learner", "mode": "study", "answered_count": 5,
            "correct_count": 0, "answered_at": NOW.replace(minute=index),
            "question_results": results[index * 5:(index + 1) * 5],
        }
    before = dict(database._local_learning_events)
    set_supporter_link("supporter", "learner")
    token = create_supporter_token("supporter")
    response = app.test_client().get(
        f"/supporter/pilot-diagnostics?token={token}&learner_user_id=learner"
    )
    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "最新 adaptive_daily 30問セッション監査" in html
    assert "event数 6" in html and "30問監査完了" in html
    assert "audit fields complete:</b> PASS" in html
    assert "selection_reason: repairing" in html
    assert "recent repeats: 1" in html
    assert html.count('class="saved-adaptive-audit-item"') == 30
    assert "最新のおすすめ30問シミュレーション" in html
    assert database._local_learning_events == before


def test_latest_session_groups_six_batches_without_mixing_other_sessions_or_modes():
    database._local_learning_events["session-old:1"] = {
        "user_id": "learner", "mode": "study", "answered_count": 5,
        "correct_count": 0, "answered_at": NOW - timedelta(days=1),
        "question_results": [_result(number) for number in range(101, 106)],
    }
    for index in range(6):
        database._local_learning_events[f"session-a:{index + 1}"] = {
            "user_id": "learner", "mode": "study", "answered_count": 5,
            "correct_count": 0, "answered_at": NOW.replace(minute=index),
            "question_results": [_result(index * 5 + offset) for offset in range(1, 6)],
        }
    database._local_learning_events["random-session:1"] = {
        "user_id": "learner", "mode": "study", "answered_count": 5,
        "correct_count": 5, "answered_at": NOW.replace(hour=1),
        "question_results": [{"question_id": "Q100", "learning_source": "random"}],
    }
    events = get_latest_adaptive_daily_learning_session_events("learner")
    assert len(events) == 6
    assert {item["event_key"].split(":")[0] for item in events} == {"session-a"}


def test_incomplete_three_batch_session_is_progress_not_complete():
    events = [
        {"event_key": f"session-b:{index + 1}", "mode": "study",
         "answered_at": NOW.replace(minute=index),
         "question_results": [_result(index * 5 + offset) for offset in range(1, 6)]}
        for index in range(3)
    ]
    audit = build_saved_adaptive_daily_audit(events)
    assert audit["event_count"] == 3
    assert audit["question_count"] == audit["unique_question_count"] == 15
    assert audit["session_complete"] is False
