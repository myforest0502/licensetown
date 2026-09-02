from datetime import datetime, timedelta, timezone

from pilot_diagnostics import build_saved_adaptive_daily_audit

NOW = datetime(2026, 9, 2, tzinfo=timezone.utc)
AUDIT_FIELDS = {
    "selection_reason": "unseen",
    "selection_group": "exploration",
    "selection_score": 310,
    "repair_evidence_quality": None,
    "recent_question_repeat": False,
    "recent_cooldown_bypassed": False,
}


def result(q):
    return {"question_id": q, "learning_source": "adaptive_daily", **AUDIT_FIELDS}


def events(set_numbers=(1, 2, 3, 4, 5, 6), *, session_ids=None, key_builder=None, question_ids=None):
    session_ids = session_ids or ["session"] * len(set_numbers)
    question_ids = question_ids or [f"Q{i}" for i in range(1, 31)]
    batches = []
    cursor = 0
    for index, set_no in enumerate(set_numbers):
        ids = question_ids[cursor:cursor + 5]
        cursor += 5
        key = (
            key_builder(index, set_no)
            if key_builder is not None
            else f"{session_ids[index]}:{set_no}"
        )
        batches.append({
            "event_key": key,
            "user_id": "u",
            "mode": "study",
            "answered_at": NOW + timedelta(minutes=index),
            "question_results": [result(q) for q in ids],
        })
    return batches


def test_valid_one_to_six_session_is_complete():
    audit = build_saved_adaptive_daily_audit(events())
    assert audit["session_complete"] is True
    assert audit["session_status"] == "complete"
    assert audit["parsed_set_numbers"] == [1, 2, 3, 4, 5, 6]
    assert audit["event_key_parse_failure_count"] == 0


def test_invalid_set_sequence_is_incomplete():
    audit = build_saved_adaptive_daily_audit(events((1, 2, 3, 4, 5, 7)))
    assert audit["session_complete"] is False
    assert audit["session_status"] == "set_sequence_invalid"


def test_duplicate_set_suffix_is_incomplete():
    audit = build_saved_adaptive_daily_audit(events((1, 2, 3, 4, 5, 5)))
    assert audit["session_status"] == "set_sequence_invalid"


def test_mixed_session_ids_are_incomplete():
    audit = build_saved_adaptive_daily_audit(events(session_ids=["a", "a", "a", "b", "b", "b"]))
    assert audit["session_status"] == "mixed_session_ids"


def test_missing_separator_is_unparseable():
    audit = build_saved_adaptive_daily_audit(events(key_builder=lambda i, n: "bad" if i == 2 else f"s:{n}"))
    assert audit["session_status"] == "event_key_unparseable"
    assert audit["event_key_parse_failure_count"] == 1


def test_nonnumeric_suffix_is_unparseable():
    audit = build_saved_adaptive_daily_audit(events(key_builder=lambda i, n: "s:x" if i == 2 else f"s:{n}"))
    assert audit["session_status"] == "event_key_unparseable"


def test_zero_suffix_is_unparseable():
    audit = build_saved_adaptive_daily_audit(events(key_builder=lambda i, n: "s:0" if i == 0 else f"s:{n}"))
    assert audit["session_status"] == "event_key_unparseable"


def test_five_events_are_event_count_incomplete():
    audit = build_saved_adaptive_daily_audit(events((1, 2, 3, 4, 5)))
    assert audit["session_status"] == "event_count_incomplete"


def test_29_result_rows_are_question_count_incomplete():
    ids = [f"Q{i}" for i in range(1, 30)]
    audit = build_saved_adaptive_daily_audit(events(question_ids=ids))
    assert audit["session_status"] == "question_count_incomplete"


def test_duplicate_question_ids_are_incomplete():
    ids = [f"Q{i}" for i in range(1, 30)] + ["Q29"]
    audit = build_saved_adaptive_daily_audit(events(question_ids=ids))
    assert audit["question_count"] == 30
    assert audit["unique_question_count"] == 29
    assert audit["session_status"] == "duplicate_question_ids"


def test_audit_metadata_completeness_is_separate_from_session_completion():
    batches = events()
    del batches[0]["question_results"][0]["selection_reason"]
    audit = build_saved_adaptive_daily_audit(batches)
    assert audit["session_complete"] is True
    assert audit["session_status"] == "complete"
    assert audit["audit_fields_complete"] is False
