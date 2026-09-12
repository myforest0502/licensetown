from unittest.mock import MagicMock

import database
from qualifications.pt.learning_store import PTLearningHistoryStore


def db_context_with_fetches(*rows):
    cursor = MagicMock()
    cursor.fetchone.side_effect = rows
    connection = MagicMock()
    connection.cursor.return_value.__enter__.return_value = cursor
    context = MagicMock()
    context.__enter__.return_value = connection
    return context, cursor


def test_true_qualified_state_short_circuits_learning_evidence(monkeypatch):
    context, cursor = db_context_with_fetches((True,))
    monkeypatch.setattr(database, "database_is_available", lambda: True)
    monkeypatch.setattr(database, "get_db_connection", lambda: context)

    assert PTLearningHistoryStore().is_initial_assessment_completed("learner") is True
    assert cursor.execute.call_count == 1


def test_false_qualified_state_preserves_existing_pt_learning_evidence(monkeypatch):
    context, cursor = db_context_with_fetches((False,), (True,))
    monkeypatch.setattr(database, "database_is_available", lambda: True)
    monkeypatch.setattr(database, "get_db_connection", lambda: context)

    assert PTLearningHistoryStore().is_initial_assessment_completed("learner") is True
    assert cursor.execute.call_count == 2
    evidence_sql = cursor.execute.call_args_list[1].args[0]
    evidence_params = cursor.execute.call_args_list[1].args[1]
    assert "qualification_id = %s" in evidence_sql
    assert "answered_count > 0" in evidence_sql
    assert evidence_params == ("learner", "pt")


def test_false_state_without_pt_learning_evidence_remains_incomplete(monkeypatch):
    context, cursor = db_context_with_fetches((False,), (False,))
    monkeypatch.setattr(database, "database_is_available", lambda: True)
    monkeypatch.setattr(database, "get_db_connection", lambda: context)

    assert PTLearningHistoryStore().is_initial_assessment_completed("learner") is False
    assert cursor.execute.call_count == 2


def test_missing_state_with_pt_learning_evidence_remains_backward_compatible(monkeypatch):
    context, cursor = db_context_with_fetches(None, (True,))
    monkeypatch.setattr(database, "database_is_available", lambda: True)
    monkeypatch.setattr(database, "get_db_connection", lambda: context)

    assert PTLearningHistoryStore().is_initial_assessment_completed("learner") is True
    assert cursor.execute.call_count == 2
