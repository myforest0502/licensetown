import random
from datetime import datetime, timedelta, timezone

import adaptive_question_selector as selector

NOW = datetime(2026, 8, 29, tzinfo=timezone.utc)


def attempt(q, node, correct, confidence=2, *, minute=0, status="answered"):
    return {
        "user_id": "u",
        "question_id": q,
        "knowledge_node_id": node,
        "is_correct": correct,
        "confidence": confidence,
        "answer_status": status,
        "answered_at": NOW + timedelta(minutes=minute),
        "event_key": f"e-{minute}",
        "attempt_position": 1,
    }


def custom_bank(monkeypatch, node_by_q, safety_by_node=None):
    safety_by_node = safety_by_node or {}
    monkeypatch.setattr(selector, "question_ids", lambda: tuple(node_by_q))
    monkeypatch.setattr(selector, "get_question_tag", lambda q: {
        "knowledge_node_id": node_by_q[q],
        "safety": safety_by_node.get(node_by_q[q], "none"),
    })


def test_safety_unknown_only_uses_unresolved_reason_and_preserves_priority(monkeypatch):
    node_by_q = {"Q1": "KN0001"}
    node_by_q.update({f"Q{i}": f"KN{i:04d}" for i in range(2, 45)})
    custom_bank(monkeypatch, node_by_q, {"KN0001": "moderate"})
    selected = selector.select_node_adaptive_questions([
        attempt("Q1", "KN0001", False, None, status="unknown")
    ], 10, rng=random.Random(101))
    node = next(item for item in selected if item["canonical_node_id"] == "KN0001")
    assert node["priority_reason"] == "safety_unresolved"
    assert node["priority_group"] == "repair"
    assert node["unknown_evidence"] is True
    assert node["recent_question_repeat"] is True
    assert node["recent_cooldown_bypassed"] is True


def test_safety_real_wrong_stays_safety_wrong_even_with_unknown(monkeypatch):
    node_by_q = {"Q1": "KN0001", "Q2": "KN0001"}
    node_by_q.update({f"Q{i}": f"KN{i:04d}" for i in range(3, 45)})
    custom_bank(monkeypatch, node_by_q, {"KN0001": "critical"})
    selected = selector.select_node_adaptive_questions([
        attempt("Q1", "KN0001", False, 2, minute=1),
        attempt("Q2", "KN0001", False, None, status="unknown", minute=2),
    ], 10, rng=random.Random(102))
    node = next(item for item in selected if item["canonical_node_id"] == "KN0001")
    assert node["priority_reason"] == "safety_wrong"


def test_safety_unknown_prefers_nonrecent_same_node_alternate_without_bypass(monkeypatch):
    node_by_q = {"Q1": "KN0001", "Q2": "KN0001"}
    node_by_q.update({f"Q{i}": f"KN{i:04d}" for i in range(3, 45)})
    custom_bank(monkeypatch, node_by_q, {"KN0001": "moderate"})
    monkeypatch.setattr(selector, "classify_repair_confirmation", lambda old, new: (
        "same_question" if old == new else "different_question_weak"
    ))
    selected = selector.select_node_adaptive_questions([
        attempt("Q1", "KN0001", False, None, status="unknown")
    ], 10, rng=random.Random(103))
    node = next(item for item in selected if item["canonical_node_id"] == "KN0001")
    assert node["question_id"] == "Q2"
    assert node["priority_reason"] == "safety_unresolved"
    assert node["recent_question_repeat"] is False
    assert node["recent_cooldown_bypassed"] is False


def test_non_safety_unknown_remains_repairing_and_cannot_use_safety_exception(monkeypatch):
    node_by_q = {"Q1": "KN0001"}
    node_by_q.update({f"Q{i}": f"KN{i:04d}" for i in range(2, 45)})
    custom_bank(monkeypatch, node_by_q)
    selected = selector.select_node_adaptive_questions([
        attempt("Q1", "KN0001", False, None, status="unknown")
    ], 10, rng=random.Random(104))
    assert not any(item["question_id"] == "Q1" for item in selected)


def test_priority_fallback_keeps_legacy_mock_contract():
    summary = {
        "wrong_questions": {"Q1"},
        "correct_questions": set(),
        "confident_wrong": False,
        "uncertain_correct": False,
        "unknown": False,
    }
    assert selector._priority("repairing", summary, "moderate")[1] == "safety_wrong"
