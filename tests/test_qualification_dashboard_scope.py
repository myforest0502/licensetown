from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

from qualification_dashboard_scope import (
    build_pt_weekly_question_history,
    install_pt_dashboard_history_scope,
)
from qualifications.common.learning_store_registry import get_learning_history_store


NOW = datetime(2026, 9, 12, 0, 0, tzinfo=timezone.utc)


def test_weekly_history_uses_pt_store_and_preserves_shape():
    calls = []

    class Store:
        def get_question_attempts(self, user_id, start_at=None):
            calls.append((user_id, start_at))
            return [
                {
                    "question_id": "Q10",
                    "selected_answers": [1],
                    "is_correct": False,
                    "confidence": 1,
                    "answered_at": NOW,
                },
                {
                    "question_id": "Q2",
                    "selected_answers": [],
                    "is_correct": False,
                    "confidence": None,
                    "answer_status": "unknown",
                    "answered_at": NOW,
                },
            ]

    result = build_pt_weekly_question_history(
        "learner", now=NOW, store=Store()
    )

    assert calls and calls[0][0] == "learner"
    assert result["total_attempts"] == 2
    assert result["unique_questions"] == 2
    assert result["attempted_question_ids"] == ["Q2", "Q10"]
    assert result["wrong_question_ids"] == ["Q10"]
    assert result["unknown_question_ids"] == ["Q2"]
    assert result["confident_wrong_question_ids"] == ["Q10"]


def test_install_rebinds_only_dashboard_history_helpers_and_is_idempotent():
    legacy_attempts = lambda user_id: ["legacy"]
    legacy_weekly = lambda user_id: {"legacy": True}
    module = SimpleNamespace(
        get_question_attempts=legacy_attempts,
        get_weekly_question_history=legacy_weekly,
    )

    install_pt_dashboard_history_scope(module)
    first_attempts = module.get_question_attempts
    first_weekly = module.get_weekly_question_history

    store = get_learning_history_store("pt")
    assert first_attempts.__self__ is store
    assert module._pt_dashboard_history_store is store

    install_pt_dashboard_history_scope(module)
    assert module.get_question_attempts is first_attempts
    assert module.get_weekly_question_history is first_weekly
