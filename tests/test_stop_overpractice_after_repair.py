"""Roadmap 7 acceptance tests: stop high-priority practice after repair."""

import random
from collections import Counter
from datetime import datetime, timedelta, timezone

import adaptive_question_selector as selector
import knowledge_node_state_transition as transition


NOW = datetime(2026, 8, 30, tzinfo=timezone.utc)


def attempt(question_id, node_id, correct, confidence, minute, *, unknown=False):
    return {
        "user_id": "learner",
        "question_id": question_id,
        "knowledge_node_id": node_id,
        "is_correct": correct,
        "confidence": confidence,
        "answer_status": "unknown" if unknown else "answered",
        "answered_at": NOW + timedelta(minutes=minute),
        "event_key": f"event-{minute}",
        "attempt_position": 1,
    }


def strong_classifier(previous, candidate):
    return "same_question" if previous == candidate else "different_question_strong"


def fake_bank(monkeypatch):
    ids = tuple(f"Q{i}" for i in range(1, 61))
    monkeypatch.setattr(selector, "question_ids", lambda: ids)

    def tag(question_id):
        number = int(question_id[1:])
        if number <= 3:
            node = "KN0001"
        elif number <= 5:
            node = "KN0002"
        elif number <= 7:
            node = "KN0003"
        else:
            node = f"KN{number:04d}"
        return {"knowledge_node_id": node, "safety": "none"}

    monkeypatch.setattr(selector, "get_question_tag", tag)
    monkeypatch.setattr(selector, "classify_repair_confirmation", strong_classifier)
    monkeypatch.setattr(transition, "classify_repair_confirmation", strong_classifier)


def selected_by_node(records, node_id):
    return [item for item in records if item["canonical_node_id"] == node_id]


def test_repaired_node_leaves_repair_group_and_frees_capacity(monkeypatch):
    fake_bank(monkeypatch)
    node_b_wrong = attempt("Q4", "KN0002", False, 2, 2)
    node_c_checking = attempt("Q6", "KN0003", True, 1, 3)
    before_history = [attempt("Q1", "KN0001", False, 2, 1), node_b_wrong, node_c_checking]
    before = selector.select_node_adaptive_questions(
        before_history, 30, rng=random.Random(11), as_of=NOW + timedelta(minutes=4)
    )
    assert selected_by_node(before, "KN0001")[0]["priority_group"] == "repair"

    after_history = before_history + [attempt("Q3", "KN0001", True, 1, 4)]
    assert transition.derive_knowledge_node_state(
        [before_history[0], after_history[-1]]
    )["state"] == "repaired"
    after = selector.select_node_adaptive_questions(
        after_history, 30, rng=random.Random(11), as_of=NOW + timedelta(minutes=5)
    )
    node_a_after = selected_by_node(after, "KN0001")
    assert all(item["priority_group"] == "maintenance" for item in node_a_after)
    assert selected_by_node(after, "KN0002")[0]["priority_group"] == "repair"
    assert selected_by_node(after, "KN0003")[0]["priority_group"] == "checking"
    assert any(item["priority_group"] == "exploration" for item in after)
    assert sum(item["priority_group"] == "repair" for item in after) < sum(
        item["priority_group"] == "repair" for item in before
    )
    assert len(after) == len({item["question_id"] for item in after}) == 30
    assert max(Counter(item["canonical_node_id"] for item in after).values()) <= 2


def test_past_wrongs_and_same_day_correct_do_not_repromote_repaired(monkeypatch):
    fake_bank(monkeypatch)
    history = [
        attempt("Q1", "KN0001", False, 1, 1),
        attempt("Q2", "KN0001", False, 2, 2),
        attempt("Q3", "KN0001", True, 1, 3),
        attempt("Q3", "KN0001", True, 1, 4),
    ]
    assert transition.derive_knowledge_node_state(history)["state"] == "repaired"
    selected = selector.select_node_adaptive_questions(
        history, 30, rng=random.Random(12), as_of=NOW + timedelta(minutes=5)
    )
    assert all(
        item["priority_group"] == "maintenance"
        for item in selected_by_node(selected, "KN0001")
    )


def test_new_wrong_or_unknown_returns_repaired_node_to_repair(monkeypatch):
    fake_bank(monkeypatch)
    repaired = [
        attempt("Q1", "KN0001", False, 2, 1),
        attempt("Q3", "KN0001", True, 1, 2),
    ]
    for regression in (
        attempt("Q2", "KN0001", False, 2, 3),
        attempt("Q2", "KN0001", False, None, 3, unknown=True),
    ):
        history = repaired + [regression]
        assert transition.derive_knowledge_node_state(history)["state"] == "repairing"
        selected = selector.select_node_adaptive_questions(
            history, 30, rng=random.Random(13), as_of=NOW + timedelta(minutes=4)
        )
        # The formal state still regresses to repairing, while all three Qs for
        # this Node remain under recent cooldown when enough other Qs exist.
        assert selected_by_node(selected, "KN0001") == []


def test_repaired_returns_as_recheck_due_after_seven_days(monkeypatch):
    fake_bank(monkeypatch)
    history = [
        attempt("Q1", "KN0001", False, 2, 1),
        attempt("Q3", "KN0001", True, 1, 2),
    ]
    as_of = NOW + timedelta(days=8)
    assert transition.derive_knowledge_node_state(history, as_of=as_of)["state"] == "recheck_due"
    selected = selector.select_node_adaptive_questions(
        history, 30, rng=random.Random(14), as_of=as_of
    )
    node_items = selected_by_node(selected, "KN0001")
    assert node_items
    assert node_items[0]["state"] == "recheck_due"
    assert node_items[0]["priority_group"] == "checking"


def test_stable_with_historical_wrongs_remains_maintenance():
    summary = {
        "wrong_questions": {"Q1"}, "correct_questions": {"Q2", "Q3"},
        "confident_wrong": True, "uncertain_correct": False, "unknown": False,
    }
    assert selector._priority("stable", summary, "critical") == (
        100, "stable_maintenance", "maintenance"
    )
