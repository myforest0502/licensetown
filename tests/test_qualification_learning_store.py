"""Regression coverage for qualification-scoped learner-history adapters."""

from datetime import datetime, timezone

import pytest

import database
from qualifications.common.learning_store_registry import (
    LearningHistoryStoreNotConfigured,
    get_learning_history_store,
)
from qualifications.pt.learning_store import PTLearningHistoryStore


NOW = datetime(2026, 9, 11, tzinfo=timezone.utc)


def test_pt_learning_store_is_available_and_stable():
    first = get_learning_history_store("pt")
    second = get_learning_history_store("pt")
    assert isinstance(first, PTLearningHistoryStore)
    assert first is second
    assert first.qualification_id == "pt"


def test_takken_learning_store_is_not_allowed_to_fall_back_to_pt():
    with pytest.raises(
        LearningHistoryStoreNotConfigured,
        match="not configured for qualification: takken",
    ):
        get_learning_history_store("takken")


def test_unknown_qualification_fails_closed():
    with pytest.raises(KeyError):
        get_learning_history_store("unknown")


def test_pt_adapter_delegates_question_attempt_reads_exactly(monkeypatch):
    store = get_learning_history_store("pt")
    sentinel = [{"question_id": "Q1"}]
    calls = []

    def fake(user_id, start_at=None):
        calls.append((user_id, start_at))
        return sentinel

    monkeypatch.setattr(database, "get_question_attempts", fake)
    assert store.get_question_attempts("user-1", start_at=NOW) is sentinel
    assert calls == [("user-1", NOW)]


def test_pt_adapter_delegates_history_and_assessment_state(monkeypatch):
    store = get_learning_history_store("pt")
    history = [{"question_id": "Q2"}]
    marked = []

    monkeypatch.setattr(database, "get_question_history", lambda user_id: history)
    monkeypatch.setattr(database, "is_initial_assessment_completed", lambda user_id: user_id == "done")
    monkeypatch.setattr(database, "mark_initial_assessment_completed", lambda user_id: marked.append(user_id))

    assert store.get_question_history("user-1") is history
    assert store.is_initial_assessment_completed("done") is True
    assert store.is_initial_assessment_completed("not-yet") is False
    assert store.mark_initial_assessment_completed("user-1") is None
    assert marked == ["user-1"]
