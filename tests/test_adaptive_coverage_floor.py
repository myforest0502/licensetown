import random
from datetime import datetime, timezone

import adaptive_question_selector as selector


NOW = datetime(2026, 9, 12, tzinfo=timezone.utc)


def _attempt(qid, node, correct, *, confidence=2, minute=0):
    return {
        "user_id": "u",
        "question_id": qid,
        "knowledge_node_id": node,
        "is_correct": correct,
        "confidence": confidence,
        "answer_status": "answered",
        "answered_at": NOW,
        "event_key": f"e-{qid}-{minute}",
        "attempt_position": 1,
    }


def _install_bank(monkeypatch, specs):
    ids = tuple(specs)
    monkeypatch.setattr(selector, "question_ids", lambda: ids)
    monkeypatch.setattr(selector, "get_category_small", lambda qid: specs[qid][0])
    monkeypatch.setattr(selector, "get_question_tag", lambda qid: {
        "knowledge_node_id": specs[qid][1],
        "safety": specs[qid][2],
    })


def test_exploration_floor_uses_distinct_lowest_coverage_fields(monkeypatch):
    specs = {}
    q = 1
    for field_id in range(1, 7):
        for node_index in range(1, 5):
            specs[f"Q{q}"] = (field_id, f"F{field_id}N{node_index}", "none")
            q += 1
    _install_bank(monkeypatch, specs)

    attempts = []
    # Field node coverage before this session:
    # F1=0/4, F2=1/4, F3=2/4, F4=3/4, F5=3/4, F6=4/4.
    for field_id, seen_nodes in ((2, 1), (3, 2), (4, 3), (5, 3), (6, 4)):
        field_qids = [qid for qid, spec in specs.items() if spec[0] == field_id]
        for qid in field_qids[:seen_nodes]:
            attempts.append(_attempt(qid, specs[qid][1], True, confidence=1))

    selected = selector.select_node_adaptive_questions(
        attempts,
        question_count=5,
        learning_intent="exploration",
        rng=random.Random(7),
        as_of=NOW,
    )

    assert len(selected) == 5
    selected_fields = [item["category_small"] for item in selected]
    assert selected_fields[:3] == [1, 2, 3]
    assert set(selected_fields) == {1, 2, 3, 4, 5}
    assert all(item["priority_group"] == "exploration" for item in selected)


def test_safety_repair_stays_first_while_exploration_uses_low_coverage_field(monkeypatch):
    specs = {
        "Q1": (1, "F1N1", "none"),
        "Q2": (1, "F1N2", "none"),
        "Q3": (2, "F2N1", "none"),
        "Q4": (2, "F2N2", "none"),
        "Q5": (3, "F3N1", "none"),
        "Q6": (3, "F3N2", "none"),
        "Q7": (4, "F4N1", "none"),
        "Q8": (4, "F4N2", "none"),
        "Q9": (5, "F5N1", "none"),
        "Q10": (5, "F5N2", "none"),
        "Q11": (6, "SAFE", "critical"),
        "Q12": (6, "SAFE", "critical"),
    }
    _install_bank(monkeypatch, specs)
    monkeypatch.setattr(
        selector,
        "classify_repair_confirmation",
        lambda old, new: "same_question" if old == new else "different_question_strong",
    )

    attempts = [
        _attempt("Q11", "SAFE", False, confidence=2),
        _attempt("Q3", "F2N1", True, confidence=1),
        _attempt("Q4", "F2N2", True, confidence=1),
        _attempt("Q5", "F3N1", True, confidence=1),
        _attempt("Q6", "F3N2", True, confidence=1),
        _attempt("Q7", "F4N1", True, confidence=1),
        _attempt("Q8", "F4N2", True, confidence=1),
        _attempt("Q9", "F5N1", True, confidence=1),
        _attempt("Q10", "F5N2", True, confidence=1),
    ]

    selected = selector.select_node_adaptive_questions(
        attempts,
        question_count=6,
        rng=random.Random(11),
        as_of=NOW,
    )

    assert selected[0]["question_id"] == "Q12"
    assert selected[0]["priority_reason"] == "safety_wrong"
    exploration = [item for item in selected if item["priority_group"] == "exploration"]
    assert exploration
    assert exploration[0]["category_small"] == 1
