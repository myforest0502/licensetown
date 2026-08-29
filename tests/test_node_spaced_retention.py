from datetime import datetime, timedelta, timezone

import knowledge_node_state_transition as transition


BASE = datetime(2026, 1, 1, tzinfo=timezone.utc)


def item(q, correct, confidence, day, unknown=False):
    return {"user_id": "u", "question_id": q, "knowledge_node_id": "KN0001",
            "is_correct": correct, "confidence": confidence,
            "answer_status": "unknown" if unknown else "answered",
            "attempted_at": BASE + timedelta(days=day), "event_key": f"e-{day}-{q}",
            "attempt_position": 1}


def strong_classifier(old, new):
    return "same_question" if old == new else "different_question_strong"


def repaired_history():
    return [item("Q1", False, 2, 0), item("Q2", True, 1, 1)]


def test_repaired_due_at_seven_days_not_six(monkeypatch):
    monkeypatch.setattr(transition, "classify_repair_confirmation", strong_classifier)
    history = repaired_history()
    assert transition.derive_knowledge_node_state(history, as_of=BASE + timedelta(days=7))["state"] == "repaired"
    result = transition.derive_knowledge_node_state(history, as_of=BASE + timedelta(days=8))
    assert result["state"] == "recheck_due"
    assert result["next_review_at"] == BASE + timedelta(days=8)


def test_due_checks_require_strong_confident_different_question(monkeypatch):
    monkeypatch.setattr(transition, "classify_repair_confirmation", strong_classifier)
    base = repaired_history()
    assert transition.derive_knowledge_node_state(base + [item("Q2", True, 1, 8)])["state"] == "recheck_due"
    assert transition.derive_knowledge_node_state(base + [item("Q3", True, 2, 8)])["state"] == "recheck_due"
    assert transition.derive_knowledge_node_state(base + [item("Q3", True, 3, 8)])["state"] == "recheck_due"
    assert transition.derive_knowledge_node_state(base + [item("Q3", True, 1, 8)])["state"] == "stable"


def test_due_wrong_or_unknown_returns_to_repairing(monkeypatch):
    monkeypatch.setattr(transition, "classify_repair_confirmation", strong_classifier)
    base = repaired_history()
    assert transition.derive_knowledge_node_state(base + [item("Q3", False, 2, 8)])["state"] == "repairing"
    assert transition.derive_knowledge_node_state(base + [item("Q3", False, None, 8, True)])["state"] == "repairing"


def test_stable_due_at_thirty_days_and_can_reconfirm(monkeypatch):
    monkeypatch.setattr(transition, "classify_repair_confirmation", strong_classifier)
    stable = repaired_history() + [item("Q3", True, 1, 8)]
    assert transition.derive_knowledge_node_state(stable, as_of=BASE + timedelta(days=37))["state"] == "stable"
    assert transition.derive_knowledge_node_state(stable, as_of=BASE + timedelta(days=38))["state"] == "recheck_due"
    assert transition.derive_knowledge_node_state(stable + [item("Q4", True, 1, 38)])["state"] == "stable"
    assert transition.derive_knowledge_node_state(stable + [item("Q4", False, 1, 38)])["state"] == "repairing"
