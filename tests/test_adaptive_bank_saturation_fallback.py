from datetime import datetime, timedelta, timezone
import random

import adaptive_question_selector as selector
from question_equivalence import canonicalize_question_evidence_id


def install_bank(monkeypatch, count):
    ids = tuple(f"Q{i}" for i in range(1, count + 1))
    monkeypatch.setattr(selector, "question_ids", lambda: ids)
    monkeypatch.setattr(selector, "get_question_tag", lambda q: {
        "knowledge_node_id": f"KN{int(q[1:]):04d}",
        "safety": "none",
    })
    monkeypatch.setattr(selector, "get_category_small", lambda _q: 1)
    monkeypatch.setattr(selector, "get_quiz_question", lambda q: {"id": q})
    return ids


def old_attempt(qid, index, *, days=4):
    now = datetime.now(timezone.utc)
    return {
        "user_id": "learner",
        "question_id": qid,
        "knowledge_node_id": f"KN{int(qid[1:]):04d}",
        "is_correct": True,
        "confidence": 1,
        "answer_status": "answered",
        "answered_at": now - timedelta(days=days, minutes=1000-index),
        "event_key": f"e-{index}",
        "attempt_position": 1,
    }


def test_saturated_bank_uses_old_spaced_evidence_instead_of_stopping(monkeypatch):
    ids = install_bank(monkeypatch, 70)
    attempts = [old_attempt(qid, i) for i, qid in enumerate(ids, start=1)]
    audit = {}

    questions = selector.build_node_adaptive_session(
        attempts, 30, rng=random.Random(901), audit_out=audit
    )

    selected = [q["id"] for q in questions]
    selected_evidence = [canonicalize_question_evidence_id(q) for q in selected]
    assert len(selected) == 30
    assert len(selected_evidence) == len(set(selected_evidence)) == 30
    assert all(audit[q]["selection_reason"] == "spaced_repeat_fallback" for q in selected)
    assert all(audit[q]["recent_cooldown_bypassed"] is False for q in selected)


def test_spaced_fallback_keeps_three_day_floor_when_older_supply_is_enough(monkeypatch):
    ids = install_bank(monkeypatch, 70)
    now = datetime.now(timezone.utc)
    attempts = []
    for i, qid in enumerate(ids, start=1):
        row = old_attempt(qid, i)
        if i <= 35:
            row["answered_at"] = now - timedelta(hours=12)
        attempts.append(row)
    audit = {}

    questions = selector.build_node_adaptive_session(
        attempts, 30, rng=random.Random(902), audit_out=audit
    )

    selected = {q["id"] for q in questions}
    assert len(selected) == 30
    assert not selected.intersection(set(ids[:35]))
    assert all(audit[q]["selection_reason"] == "spaced_repeat_fallback" for q in selected)


def test_recent_questions_are_last_resort_instead_of_stopping(monkeypatch):
    ids = install_bank(monkeypatch, 70)
    now = datetime.now(timezone.utc)
    attempts = []
    for i, qid in enumerate(ids, start=1):
        row = old_attempt(qid, i)
        row["answered_at"] = now - timedelta(hours=12, minutes=1000-i)
        attempts.append(row)
    audit = {}

    questions = selector.build_node_adaptive_session(
        attempts, 30, rng=random.Random(904), audit_out=audit
    )

    selected = [q["id"] for q in questions]
    assert len(selected) == 30
    assert len(selected) == len(set(selected))
    assert all(audit[q]["selection_reason"] == "emergency_repeat_fallback" for q in selected)


def test_fresh_supply_still_wins_before_any_spaced_repeat(monkeypatch):
    ids = install_bank(monkeypatch, 70)
    attempts = [old_attempt(qid, i) for i, qid in enumerate(ids[:40], start=1)]
    audit = {}

    questions = selector.build_node_adaptive_session(
        attempts, 30, rng=random.Random(903), audit_out=audit
    )

    selected = {q["id"] for q in questions}
    assert selected == set(ids[40:])
    assert all(audit[q]["selection_reason"] != "spaced_repeat_fallback" for q in selected)
