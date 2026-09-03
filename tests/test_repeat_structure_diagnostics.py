import os
from datetime import datetime, timedelta, timezone

os.environ.setdefault("OPENAI_API_KEY", "x")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "x")
os.environ.setdefault("CHANNEL_SECRET", "x")

import database
import pilot_diagnostics
from app import app
from database import get_learning_events_by_event_keys
from goukaku_ui import create_dashboard_token
from pilot_diagnostics import build_repeat_structure_audit


NOW = datetime(2026, 9, 2, 12, tzinfo=timezone.utc)
AUDIT = {
    "selection_reason": "repairing",
    "selection_group": "repair",
    "selection_score": 850,
    "repair_evidence_quality": "same_question",
    "recent_question_repeat": True,
    "recent_cooldown_bypassed": False,
}


def attempt(q, hour, *, event=None, node=None, user="learner", status="answered"):
    return {
        "event_key": event or f"event-{q}-{hour}",
        "user_id": user,
        "question_id": q,
        "knowledge_node_id": node or f"KN{int(q[1:]):04d}",
        "mode": "study",
        "selected_answers": [] if status == "unknown" else ["A"],
        "answer_status": status,
        "is_correct": False,
        "confidence": None if status == "unknown" else 2,
        "answered_at": NOW + timedelta(hours=hour),
        "attempt_position": 1,
    }


def event(key, q, source="adaptive_daily", **audit):
    result = {"question_id": q, "learning_source": source, **audit}
    return {"event_key": key, "user_id": "learner", "question_results": [result]}


def setup_function():
    database._local_question_attempts.clear()
    database._local_learning_events.clear()
    database._local_supporter_links.clear()


def test_total_unique_and_repeat_counts_include_unknown_attempts():
    attempts = [attempt(f"Q{i}", i) for i in range(1, 9)]
    attempts += [attempt("Q1", 9), attempt("Q2", 10, status="unknown")]
    audit = build_repeat_structure_audit(attempts, [])
    assert audit["total_attempts"] == 10
    assert audit["unique_questions"] == 8
    assert audit["repeat_occurrences"] == audit["same_question_repeats"] == 2
    assert audit["unknown_attempts"] == 1


def test_same_canonical_node_different_question_is_not_same_q_repeat():
    attempts = [
        attempt("Q1", 0, node="KN0597"),
        attempt("Q2", 1, node="KN0807"),
    ]
    audit = build_repeat_structure_audit(attempts, [])
    assert audit["same_question_repeats"] == 0
    assert audit["same_node_different_question_confirmations"] == 1


def test_repeat_categories_follow_saved_recent_metadata_matrix_and_never_call_selector(monkeypatch):
    attempts = []
    events = []
    cases = [
        ("Q1", "justified", {**AUDIT, "recent_question_repeat": True, "recent_cooldown_bypassed": True}),
        ("Q2", "recent-repair", {**AUDIT, "recent_question_repeat": True, "recent_cooldown_bypassed": False, "selection_group": "repair"}),
        ("Q3", "recent-checking", {**AUDIT, "recent_question_repeat": True, "recent_cooldown_bypassed": False, "selection_group": "checking"}),
        ("Q4", "spaced-checking", {**AUDIT, "recent_question_repeat": False, "recent_cooldown_bypassed": False, "selection_group": "checking"}),
        ("Q5", "spaced-uncertain", {**AUDIT, "recent_question_repeat": False, "recent_cooldown_bypassed": False, "selection_reason": "uncertain_correct", "selection_group": "checking"}),
        ("Q6", "spaced-recheck", {**AUDIT, "recent_question_repeat": False, "recent_cooldown_bypassed": False, "selection_reason": "recheck_due", "selection_group": "checking"}),
        ("Q7", "spaced-repair", {**AUDIT, "recent_question_repeat": False, "recent_cooldown_bypassed": False, "selection_group": "repair"}),
        ("Q8", "inconsistent", {**AUDIT, "recent_question_repeat": False, "recent_cooldown_bypassed": True}),
        ("Q9", "random", None),
        ("Q10", "missing", "missing"),
    ]
    for index, (q, key, metadata) in enumerate(cases):
        attempts.extend([attempt(q, index * 2), attempt(q, index * 2 + 1, event=key)])
        if metadata is None:
            events.append(event(key, q, "random"))
        elif metadata != "missing":
            events.append(event(key, q, "adaptive_daily", **metadata))

    monkeypatch.setattr(
        pilot_diagnostics,
        "select_node_adaptive_questions",
        lambda *_a, **_k: (_ for _ in ()).throw(AssertionError("selector called")),
    )
    audit = build_repeat_structure_audit(attempts, events)
    assert audit["category_counts"] == {
        "justified_cooldown_bypass": 1,
        "adaptive_spaced_repeat": 4,
        "adaptive_unexplained_repeat": 2,
        "adaptive_metadata_inconsistent": 1,
        "nonadaptive_repeat": 1,
        "audit_metadata_unavailable": 1,
    }
    assert audit["nonadaptive_modes"] == {"random": 1}
    assert [item["question_id"] for item in audit["unexplained_repeats"]] == ["Q2", "Q3"]


def test_incomplete_boolean_audit_values_are_unavailable_not_selector_failures():
    attempts = [attempt("Q1", 0), attempt("Q1", 1, event="partial")]
    events = [event(
        "partial",
        "Q1",
        "adaptive_daily",
        **{**AUDIT, "recent_question_repeat": None, "recent_cooldown_bypassed": False},
    )]
    audit = build_repeat_structure_audit(attempts, events)
    assert audit["category_counts"]["audit_metadata_unavailable"] == 1
    assert audit["unexplained_repeat_count"] == 0


def test_elapsed_buckets_use_non_overlapping_24_hour_and_7_day_boundaries():
    attempts = [
        attempt("Q1", 0), attempt("Q1", 23),
        attempt("Q2", 0), attempt("Q2", 24),
        attempt("Q3", 0), attempt("Q3", 24 * 7),
    ]
    audit = build_repeat_structure_audit(attempts, [])
    assert audit["distance_counts"] == {
        "under_24h": 1,
        "one_to_under_seven_days": 1,
        "seven_days_or_more": 1,
        "unknown": 0,
    }


def test_learning_event_helper_is_select_only(monkeypatch):
    class Cursor:
        def __init__(self): self.sql = ""; self.args = None
        def __enter__(self): return self
        def __exit__(self, *_args): return False
        def execute(self, sql, args): self.sql = " ".join(sql.split()); self.args = args
        def fetchall(self): return []
    class Connection:
        def __init__(self): self.cursor_value = Cursor()
        def __enter__(self): return self
        def __exit__(self, *_args): return False
        def cursor(self): return self.cursor_value

    connection = Connection()
    monkeypatch.setattr(database, "database_is_available", lambda: True)
    monkeypatch.setattr(database, "get_db_connection", lambda: connection)
    assert get_learning_events_by_event_keys("learner", {"e2", "e1"}) == []
    assert connection.cursor_value.sql.startswith("SELECT ")
    assert connection.cursor_value.args == ("learner", ["e1", "e2"])
    assert not any(word in connection.cursor_value.sql.upper() for word in (
        "INSERT", "UPDATE", "DELETE", "TRUNCATE", "ALTER", "CREATE", "DROP",
    ))


def test_internal_diagnostics_renders_repeat_section_but_learner_page_does_not(monkeypatch):
    first = attempt("Q1", 0)
    repeated = attempt("Q1", 1, event="adaptive-repeat")
    database._local_question_attempts.extend([first, repeated])
    database._local_learning_events["adaptive-repeat"] = {
        "user_id": "learner",
        "mode": "study",
        "answered_count": 1,
        "correct_count": 0,
        "answered_at": repeated["answered_at"],
        "question_results": [{
            "question_id": "Q1", "learning_source": "adaptive_daily",
            **{**AUDIT, "selection_group": "exploration", "selection_reason": "safety_wrong"},
        }],
    }
    monkeypatch.setenv("LT_INTERNAL_ADMIN_TOKEN", "admin-secret")
    client = app.test_client()
    response = client.get(
        "/internal/pilot-diagnostics?token=admin-secret&learner_user_id=learner&period=7"
    )
    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Repeat構造監査" in html
    assert "adaptive説明不能recent repeat 1" in html
    assert "Q1（KN0001）" in html
    assert "reason safety_wrong" in html
    learner_html = client.get(
        f"/goukaku-no-michi?token={create_dashboard_token('learner')}"
    ).get_data(as_text=True)
    assert "Repeat構造監査" not in learner_html
