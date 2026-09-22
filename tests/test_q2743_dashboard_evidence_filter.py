from datetime import timedelta

import licensetown.pt.goukaku_ui as ui
from licensetown.pt.formal_attempt_evidence import PROVISIONAL_REWRITE_LIVE_AT


def _attempt(qid, when):
    return {"question_id": qid, "answered_at": when}


def test_dashboard_bundle_filters_pre_rewrite_attempts_in_local_path(monkeypatch):
    old = _attempt("Q2234", PROVISIONAL_REWRITE_LIVE_AT - timedelta(seconds=1))
    new = _attempt("Q2234", PROVISIONAL_REWRITE_LIVE_AT + timedelta(seconds=1))
    stable = _attempt("Q2000", PROVISIONAL_REWRITE_LIVE_AT - timedelta(days=1))

    monkeypatch.setattr(ui, "database_is_available", lambda: False)
    monkeypatch.setattr(ui, "get_dashboard_learning_data", lambda user_id: {"summary": {}, "activity": {}, "fields": [], "unique_question_count": 0})
    monkeypatch.setattr(ui, "get_question_attempts", lambda user_id: [old, new, stable])
    monkeypatch.setattr(ui, "get_trial100_records", lambda user_id: [])
    monkeypatch.setattr(ui, "get_learning_events", lambda user_id: [])

    bundle = ui._dashboard_read_bundle("user", include_attempts=True)
    assert [row["question_id"] for row in bundle["attempts"]] == ["Q2234", "Q2000"]
    assert bundle["attempts"][0]["answered_at"] == new["answered_at"]


def test_navigation_formal_inputs_filter_production_bundle(monkeypatch):
    old = _attempt("Q2743", PROVISIONAL_REWRITE_LIVE_AT - timedelta(seconds=1))
    new = _attempt("Q2743", PROVISIONAL_REWRITE_LIVE_AT + timedelta(seconds=1))
    stable = _attempt("Q1", PROVISIONAL_REWRITE_LIVE_AT - timedelta(days=30))

    monkeypatch.setattr(ui, "database_is_available", lambda: True)
    monkeypatch.setattr(
        ui,
        "_get_production_learner_navigation_read_bundle",
        lambda user_id: {
            "attempts": [old, new, stable],
            "trial100_records": [{"id": 1}],
            "learning_events": [{"id": 2}],
        },
    )

    bundle = ui.get_learner_navigation_formal_inputs("user")
    assert [row["question_id"] for row in bundle["attempts"]] == ["Q2743", "Q1"]
    assert bundle["trial100_records"] == [{"id": 1}]
    assert bundle["learning_events"] == [{"id": 2}]
