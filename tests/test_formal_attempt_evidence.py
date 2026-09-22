from datetime import datetime, timedelta, timezone

from licensetown.pt.formal_attempt_evidence import (
    PROVISIONAL_REWRITE_LIVE_AT,
    filter_current_formal_evidence,
    is_current_formal_evidence,
)


def _attempt(question_id, answered_at):
    return {"question_id": question_id, "answered_at": answered_at}


def test_pre_rewrite_provisional_attempt_is_not_current_formal_evidence():
    attempt = _attempt(
        "Q2234",
        PROVISIONAL_REWRITE_LIVE_AT - timedelta(seconds=1),
    )
    assert is_current_formal_evidence(attempt) is False


def test_post_rewrite_provisional_attempt_is_current_formal_evidence():
    attempt = _attempt("Q2743", PROVISIONAL_REWRITE_LIVE_AT)
    assert is_current_formal_evidence(attempt) is True


def test_questions_outside_rewritten_range_are_unchanged():
    old = _attempt("Q2000", datetime(2026, 9, 1, tzinfo=timezone.utc))
    future = _attempt("Q3000", datetime(2026, 9, 1, tzinfo=timezone.utc))
    assert is_current_formal_evidence(old) is True
    assert is_current_formal_evidence(future) is True


def test_filter_preserves_raw_objects_only_as_copies_and_drops_old_rewrite_evidence():
    attempts = [
        _attempt("Q100", datetime(2026, 9, 22, tzinfo=timezone.utc)),
        _attempt("Q2234", PROVISIONAL_REWRITE_LIVE_AT - timedelta(hours=1)),
        _attempt("Q2234", PROVISIONAL_REWRITE_LIVE_AT + timedelta(seconds=1)),
    ]
    filtered = filter_current_formal_evidence(attempts)
    assert [row["question_id"] for row in filtered] == ["Q100", "Q2234"]
    assert filtered[0] is not attempts[0]


def test_iso_timestamp_is_supported():
    attempt = _attempt("Q2500", "2026-09-22T13:48:28Z")
    assert is_current_formal_evidence(attempt) is True


def test_missing_timestamp_does_not_destroy_legacy_evidence():
    assert is_current_formal_evidence({"question_id": "Q2500"}) is True
