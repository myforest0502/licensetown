"""Roadmap 6 acceptance tests for deterministic different-question repair."""

import random
from datetime import datetime, timedelta, timezone

import adaptive_question_selector as selector
import knowledge_node_state_transition as transition


NOW = datetime(2026, 8, 30, tzinfo=timezone.utc)


def attempt(question_id, correct, confidence, minute, *, unknown=False):
    return {
        "user_id": "learner",
        "question_id": question_id,
        "knowledge_node_id": "KN0001",
        "is_correct": correct,
        "confidence": confidence,
        "answer_status": "unknown" if unknown else "answered",
        "answered_at": NOW + timedelta(minutes=minute),
        "event_key": f"event-{minute}",
        "attempt_position": 1,
    }


def evidence(previous, candidate):
    if previous == candidate:
        return "same_question"
    return "different_question_weak" if candidate == "Q2" else "different_question_strong"


def derived_state(monkeypatch, *history):
    monkeypatch.setattr(transition, "classify_repair_confirmation", evidence)
    return transition.derive_knowledge_node_state(history)["state"]


def test_scenarios_a_to_e_wrong_repair_confirmation(monkeypatch):
    wrong = attempt("Q1", False, 2, 1)
    assert derived_state(monkeypatch, wrong) == "repairing"
    assert derived_state(monkeypatch, wrong, attempt("Q1", True, 1, 2)) == "repairing"
    assert derived_state(monkeypatch, wrong, attempt("Q2", True, 1, 2)) == "repairing"
    assert derived_state(monkeypatch, wrong, attempt("Q3", True, 2, 2)) == "repairing"
    assert derived_state(monkeypatch, wrong, attempt("Q3", True, 3, 2)) == "repairing"
    assert derived_state(monkeypatch, wrong, attempt("Q3", True, 1, 2)) == "repaired"


def test_scenarios_f_to_h_unknown_and_regression(monkeypatch):
    unknown = attempt("Q1", False, None, 1, unknown=True)
    repaired = [unknown, attempt("Q3", True, 1, 2)]
    assert derived_state(monkeypatch, *repaired) == "repaired"
    assert derived_state(monkeypatch, *repaired, attempt("Q4", False, 2, 3)) == "repairing"
    assert derived_state(
        monkeypatch, *repaired, attempt("Q4", False, None, 3, unknown=True)
    ) == "repairing"


def fake_selector_bank(monkeypatch):
    question_ids = tuple(f"Q{i}" for i in range(1, 61))
    monkeypatch.setattr(selector, "question_ids", lambda: question_ids)
    monkeypatch.setattr(selector, "get_question_tag", lambda question_id: {
        "knowledge_node_id": "KN0001" if int(question_id[1:]) <= 3 else f"KN{int(question_id[1:]):04d}",
        "safety": "none",
    })


def test_selector_prefers_strong_then_weak_and_avoids_same_question(monkeypatch):
    fake_selector_bank(monkeypatch)
    monkeypatch.setattr(selector, "classify_repair_confirmation", evidence)
    selected = selector.select_node_adaptive_questions(
        [attempt("Q1", False, 2, 1)], 30, rng=random.Random(6)
    )
    node_items = [item for item in selected if item["canonical_node_id"] == "KN0001"]
    assert node_items[0]["question_id"] == "Q3"
    assert node_items[0]["strong_repair_confirmation"] is True
    assert all(item["question_id"] != "Q1" for item in node_items)
    assert len(node_items) <= 2
    assert len(selected) == len({item["question_id"] for item in selected}) == 30
    assert any(item["priority_group"] == "exploration" for item in selected)


def test_selector_falls_back_when_no_strong_question_exists(monkeypatch):
    fake_selector_bank(monkeypatch)
    monkeypatch.setattr(selector, "classify_repair_confirmation", lambda old, new: (
        "same_question" if old == new else "different_question_weak"
    ))
    selected = selector.select_node_adaptive_questions(
        [attempt("Q1", False, 2, 1)], 30, rng=random.Random(7)
    )
    node_items = [item for item in selected if item["canonical_node_id"] == "KN0001"]
    assert node_items
    assert any(item["question_id"] in {"Q2", "Q3"} for item in node_items)
    assert all(item["strong_repair_confirmation"] is False for item in node_items)
    assert len(selected) == len({item["question_id"] for item in selected}) == 30
