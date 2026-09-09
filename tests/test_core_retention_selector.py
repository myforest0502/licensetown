import random

import adaptive_question_selector as selector


def test_recheck_due_can_bypass_recent_cooldown(monkeypatch):
    node_by_q = {
        "Q1": "KN0001",
        "Q2": "KN0001",
        **{f"Q{i}": f"KN{i:04d}" for i in range(3, 50)},
    }
    monkeypatch.setattr(selector, "question_ids", lambda: tuple(node_by_q))
    monkeypatch.setattr(
        selector,
        "get_question_tag",
        lambda q: {"knowledge_node_id": node_by_q[q], "safety": "none"},
    )
    monkeypatch.setattr(
        selector,
        "derive_all_user_node_states",
        lambda *_args, **_kwargs: [
            {
                "canonical_node_id": "KN0001",
                "state": "recheck_due",
                "due_overdue_days": 0,
            }
        ],
    )
    monkeypatch.setattr(
        selector,
        "classify_repair_confirmation",
        lambda old, new: "same_question" if old == new else "different_question_strong",
    )
    attempts = [
        {
            "user_id": "u",
            "question_id": "Q1",
            "knowledge_node_id": "KN0001",
            "is_correct": False,
            "confidence": 2,
            "answer_status": "answered",
            "answered_at": "2026-09-01T00:00:00+00:00",
            "event_key": "e1",
            "attempt_position": 1,
        },
        {
            "user_id": "u",
            "question_id": "Q2",
            "knowledge_node_id": "KN0001",
            "is_correct": True,
            "confidence": 1,
            "answer_status": "answered",
            "answered_at": "2026-09-01T00:01:00+00:00",
            "event_key": "e2",
            "attempt_position": 1,
        },
    ]

    selected = selector.select_node_adaptive_questions(
        attempts,
        10,
        rng=random.Random(101),
        learning_intent="recheck",
    )
    due_items = [item for item in selected if item["canonical_node_id"] == "KN0001"]
    assert due_items
    assert due_items[0]["priority_reason"] == "recheck_due"
    assert due_items[0]["recent_question_repeat"] is True
    assert due_items[0]["recent_cooldown_bypassed"] is True
