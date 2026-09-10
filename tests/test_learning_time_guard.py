from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from learning_time_guard import (
    estimate_active_learning_seconds,
    install_learning_time_guard,
    parse_learning_time_event_key,
    parse_web_recommendation_time_event_key,
)


def _attempt(session_id, answered_at, suffix="1"):
    return {
        "event_key": f"{session_id}:{suffix}",
        "answered_at": answered_at,
    }


def _web_attempt(session_id, answered_at, suffix="1"):
    return {
        "event_key": f"web-recommendation:{session_id}:{suffix}",
        "answered_at": answered_at,
    }


def test_parse_learning_time_event_key_reads_session_and_start_epoch():
    parsed = parse_learning_time_event_key("123:1789031570.7290385")
    assert parsed is not None
    session_id, started_at = parsed
    assert session_id == "123"
    assert started_at.tzinfo == timezone.utc
    assert abs(started_at.timestamp() - 1789031570.7290385) < 0.001


def test_parse_web_recommendation_time_event_key():
    assert (
        parse_web_recommendation_time_event_key(
            "web-recommendation:abc_DEF-123:time"
        )
        == "abc_DEF-123"
    )
    assert parse_web_recommendation_time_event_key("web-recommendation::time") is None
    assert parse_web_recommendation_time_event_key("ordinary:123.0") is None


def test_estimate_counts_normal_answer_gaps_but_not_trailing_idle():
    start = datetime(2026, 9, 10, 9, 0, tzinfo=timezone.utc)
    attempts = [
        _attempt("session", start + timedelta(minutes=8), "1"),
        _attempt("session", start + timedelta(minutes=15), "2"),
        _attempt("session", start + timedelta(minutes=24), "3"),
    ]

    seconds = estimate_active_learning_seconds(
        attempts,
        session_id="session",
        active_started_at=start,
        interval_ended_at=start + timedelta(hours=5),
        max_activity_gap_seconds=30 * 60,
    )

    assert seconds == 24 * 60


def test_estimate_caps_long_idle_gap_before_answer_activity():
    start = datetime(2026, 9, 10, 9, 0, tzinfo=timezone.utc)
    attempts = [
        _attempt("session", start + timedelta(hours=4, minutes=30), "1"),
        _attempt("session", start + timedelta(hours=4, minutes=38), "2"),
    ]

    seconds = estimate_active_learning_seconds(
        attempts,
        session_id="session",
        active_started_at=start,
        interval_ended_at=start + timedelta(hours=8),
        max_activity_gap_seconds=30 * 60,
    )

    assert seconds == 38 * 60


def test_estimate_supports_explicit_web_event_prefix():
    start = datetime(2026, 9, 10, 9, 0, tzinfo=timezone.utc)
    attempts = [
        _web_attempt("web1", start + timedelta(minutes=4), "1"),
        _web_attempt("web1", start + timedelta(minutes=11), "2"),
        _web_attempt("other", start + timedelta(minutes=20), "1"),
    ]

    seconds = estimate_active_learning_seconds(
        attempts,
        session_id="web1",
        active_started_at=start,
        interval_ended_at=start + timedelta(minutes=40),
        event_key_prefix="web-recommendation:web1:",
    )

    assert seconds == 11 * 60


def test_estimate_returns_zero_when_session_has_no_answer_evidence():
    start = datetime(2026, 9, 10, 9, 0, tzinfo=timezone.utc)
    attempts = [_attempt("other-session", start + timedelta(minutes=5))]

    assert estimate_active_learning_seconds(
        attempts,
        session_id="session",
        active_started_at=start,
        interval_ended_at=start + timedelta(hours=18),
    ) == 0


def test_guard_persists_evidence_time_instead_of_raw_wall_clock(monkeypatch):
    start = datetime(2026, 9, 10, 9, 0, tzinfo=timezone.utc)
    end = start + timedelta(hours=18)
    calls = []

    def original_add(user_id, elapsed_seconds, recorded_at=None, event_key=None):
        calls.append((user_id, elapsed_seconds, recorded_at, event_key))
        return True

    legacy = SimpleNamespace(
        add_learning_time=original_add,
        study_sessions={"user": {"session_id": "session"}},
        web_recommendation_sessions={},
    )
    database = SimpleNamespace(
        get_question_attempts=lambda user_id, start_at=None: [
            _attempt("session", start + timedelta(minutes=12), "1"),
            _attempt("session", start + timedelta(minutes=20), "2"),
        ]
    )
    monkeypatch.delenv("LT_LEARNING_ACTIVITY_GAP_CAP_SECONDS", raising=False)

    install_learning_time_guard(legacy, database)
    result = legacy.add_learning_time(
        "user",
        18 * 60 * 60,
        recorded_at=end,
        event_key=f"session:{start.timestamp()}",
    )

    assert result is True
    assert len(calls) == 1
    assert calls[0][1] == 20 * 60
    assert calls[0][2] == end


def test_guard_web_recommendation_uses_answer_evidence_not_raw_wall_clock(monkeypatch):
    start = datetime(2026, 9, 10, 9, 0, tzinfo=timezone.utc)
    end = start + timedelta(hours=4)
    calls = []

    def original_add(user_id, elapsed_seconds, recorded_at=None, event_key=None):
        calls.append((user_id, elapsed_seconds, recorded_at, event_key))
        return True

    legacy = SimpleNamespace(
        add_learning_time=original_add,
        study_sessions={},
        web_recommendation_sessions={
            "web1": {
                "user_id": "user",
                "started_at": start.timestamp(),
                "completed": True,
            }
        },
    )
    database = SimpleNamespace(
        get_question_attempts=lambda user_id, start_at=None: [
            _web_attempt("web1", start + timedelta(minutes=10), "1"),
            _web_attempt("web1", start + timedelta(minutes=22), "2"),
            _web_attempt("web1", start + timedelta(hours=3), "3"),
            _web_attempt("web1", start + timedelta(hours=3, minutes=8), "4"),
        ]
    )
    monkeypatch.delenv("LT_LEARNING_ACTIVITY_GAP_CAP_SECONDS", raising=False)

    install_learning_time_guard(legacy, database)
    assert legacy.add_learning_time(
        "user",
        4 * 60 * 60,
        recorded_at=end,
        event_key="web-recommendation:web1:time",
    ) is True

    assert len(calls) == 1
    # 10m + 12m + capped 30m + 8m = 60m. Raw 4h and the trailing 52m idle
    # after the last answer are not counted.
    assert calls[0][1] == 60 * 60
    assert calls[0][3] == "web-recommendation:web1:time"


def test_guard_web_recommendation_falls_closed_if_session_identity_is_missing(monkeypatch):
    start = datetime(2026, 9, 10, 9, 0, tzinfo=timezone.utc)
    calls = []
    legacy = SimpleNamespace(
        add_learning_time=lambda *args, **kwargs: calls.append((args, kwargs)) or True,
        study_sessions={},
        web_recommendation_sessions={},
    )
    database = SimpleNamespace(get_question_attempts=lambda *args, **kwargs: [])
    monkeypatch.delenv("LT_LEARNING_ACTIVITY_GAP_CAP_SECONDS", raising=False)

    install_learning_time_guard(legacy, database)
    assert legacy.add_learning_time(
        "user",
        3 * 60 * 60,
        recorded_at=start + timedelta(hours=3),
        event_key="web-recommendation:missing:time",
    ) is True
    assert len(calls) == 1
    assert calls[0][0][1] == 30 * 60


def test_guard_does_not_persist_abandoned_session_without_answers(monkeypatch):
    start = datetime(2026, 9, 10, 9, 0, tzinfo=timezone.utc)
    calls = []
    legacy = SimpleNamespace(
        add_learning_time=lambda *args, **kwargs: calls.append((args, kwargs)) or True,
        study_sessions={"user": {"session_id": "session"}},
        web_recommendation_sessions={},
    )
    database = SimpleNamespace(get_question_attempts=lambda *args, **kwargs: [])
    monkeypatch.delenv("LT_LEARNING_ACTIVITY_GAP_CAP_SECONDS", raising=False)

    install_learning_time_guard(legacy, database)
    assert legacy.add_learning_time(
        "user",
        6 * 60 * 60,
        recorded_at=start + timedelta(hours=6),
        event_key=f"session:{start.timestamp()}",
    ) is True
    assert calls == []


def test_guard_preserves_legacy_session_without_formal_id_but_caps_it(monkeypatch):
    start = datetime(2026, 9, 10, 9, 0, tzinfo=timezone.utc)
    calls = []
    legacy = SimpleNamespace(
        add_learning_time=lambda *args, **kwargs: calls.append((args, kwargs)) or True,
        study_sessions={"user": {"active_started_at": start.timestamp()}},
        web_recommendation_sessions={},
    )
    database = SimpleNamespace(get_question_attempts=lambda *args, **kwargs: [])
    monkeypatch.delenv("LT_LEARNING_ACTIVITY_GAP_CAP_SECONDS", raising=False)

    install_learning_time_guard(legacy, database)
    assert legacy.add_learning_time(
        "user",
        120,
        recorded_at=start + timedelta(minutes=2),
        event_key=f"user:{start.timestamp()}",
    ) is True
    assert len(calls) == 1
    assert calls[0][0][1] == 120


def test_guard_is_idempotent(monkeypatch):
    calls = []
    legacy = SimpleNamespace(
        add_learning_time=lambda *args, **kwargs: calls.append((args, kwargs)) or True,
        study_sessions={},
        web_recommendation_sessions={},
    )
    database = SimpleNamespace(get_question_attempts=lambda *args, **kwargs: [])
    monkeypatch.delenv("LT_LEARNING_ACTIVITY_GAP_CAP_SECONDS", raising=False)

    install_learning_time_guard(legacy, database)
    first = legacy.add_learning_time
    install_learning_time_guard(legacy, database)
    assert legacy.add_learning_time is first
