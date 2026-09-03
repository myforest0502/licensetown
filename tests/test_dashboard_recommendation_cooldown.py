from datetime import datetime, timezone

from adaptive_question_selector import build_node_adaptive_session
from question_bank import get_category_small, get_question_tag, question_ids


def _find_category_with_questions(min_count=12):
    groups = {}
    for qid in question_ids():
        groups.setdefault(get_category_small(qid), []).append(qid)
    category_small, ids = next(
        (category, ids)
        for category, ids in sorted(groups.items())
        if len(ids) >= min_count
    )
    return category_small, ids


def _attempt(question_id, *, user_id="dashboard-cooldown-user"):
    return {
        "user_id": user_id,
        "question_id": question_id,
        "knowledge_node_id": get_question_tag(question_id)["knowledge_node_id"],
        "is_correct": True,
        "confidence": 1,
        "answer_status": "answered",
        "answered_at": datetime(2026, 9, 3, 0, 0, tzinfo=timezone.utc),
    }


def test_category_scoped_adaptive_session_avoids_recent_exact_question_when_alternatives_exist():
    category_small, ids = _find_category_with_questions()
    recent_id = ids[0]
    audit = {}
    selected = build_node_adaptive_session(
        [_attempt(recent_id)],
        question_count=10,
        category_small=category_small,
        audit_out=audit,
    )
    selected_ids = [str(item["id"]) for item in selected]
    assert len(selected_ids) == 10
    assert recent_id not in selected_ids
    assert all(get_category_small(qid) == category_small for qid in selected_ids)
    assert all(audit[qid]["recent_question_repeat"] is False for qid in selected_ids)
    assert all(audit[qid]["recent_cooldown_bypassed"] is False for qid in selected_ids)


def test_category_scoped_selector_keeps_exact_q_selection_centralized():
    category_small, ids = _find_category_with_questions()
    attempts = [_attempt(ids[0]), _attempt(ids[1])]
    selected = build_node_adaptive_session(
        attempts,
        question_count=5,
        category_small=category_small,
    )
    assert len(selected) == 5
    assert all(get_category_small(str(item["id"])) == category_small for item in selected)
