from datetime import datetime, timedelta, timezone
import os
import random

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "test-token")
os.environ.setdefault("CHANNEL_SECRET", "test-secret")

import adaptive_question_selector as selector
import app
import short_term_repeat_guard as guard
from question_bank import select_questions_by_category, select_random_questions
from question_equivalence import canonicalize_question_evidence_id


NOW = datetime(2026, 9, 10, 12, tzinfo=timezone.utc)


def attempt(question_id, node_id="KN0001", *, answered_at=NOW):
    return {
        "user_id": "learner",
        "question_id": question_id,
        "knowledge_node_id": node_id,
        "is_correct": False,
        "confidence": 1,
        "answer_status": "answered",
        "answered_at": answered_at,
    }


def questions(count):
    return [
        {
            "id": f"Q{number}",
            "question": f"問題{number}",
            "choices": {key: key for key in "ABCDE"},
            "answer": "A",
            "explanation": "解説",
        }
        for number in range(1, count + 1)
    ]


def test_guard_blocks_same_evidence_but_allows_same_node_different_question(monkeypatch):
    monkeypatch.setattr(guard, "derive_all_user_node_states", lambda *_a, **_k: [
        {"canonical_node_id": "KN0003", "state": "repairing"}
    ])
    blocked = guard.blocked_short_term_evidence_ids([attempt("Q3", "KN0003")], as_of=NOW)
    assert guard.is_short_term_repeat_blocked("Q3", blocked)
    assert not guard.is_short_term_repeat_blocked("Q1565", blocked)


def test_guard_allows_old_same_evidence_only_when_formal_recheck_is_due(monkeypatch):
    monkeypatch.setattr(guard, "derive_all_user_node_states", lambda *_a, **_k: [
        {"canonical_node_id": "KN0003", "state": "recheck_due"}
    ])
    old_attempt = attempt(
        "Q3", "KN0003", answered_at=NOW - timedelta(days=3, seconds=1)
    )
    assert guard.blocked_short_term_evidence_ids([old_attempt], as_of=NOW) == set()


def test_due_node_does_not_reopen_evidence_attempted_less_than_three_days_ago(monkeypatch):
    monkeypatch.setattr(guard, "derive_all_user_node_states", lambda *_a, **_k: [
        {"canonical_node_id": "KN0003", "state": "recheck_due"}
    ])
    recent_attempt = attempt(
        "Q3", "KN0003", answered_at=NOW - timedelta(minutes=10)
    )
    blocked = guard.blocked_short_term_evidence_ids([recent_attempt], as_of=NOW)
    assert blocked == {"Q3"}


def test_due_node_with_mixed_evidence_keeps_only_recent_evidence_blocked(monkeypatch):
    monkeypatch.setattr(guard, "derive_all_user_node_states", lambda *_a, **_k: [
        {"canonical_node_id": "KN0003", "state": "recheck_due"}
    ])
    attempts = [
        attempt("Q3", "KN0003", answered_at=NOW - timedelta(days=7)),
        attempt("Q1565", "KN0003", answered_at=NOW - timedelta(minutes=5)),
    ]
    blocked = guard.blocked_short_term_evidence_ids(attempts, as_of=NOW)
    assert "Q3" not in blocked
    assert "Q1565" in blocked


def test_exact_repeat_equivalent_is_blocked_together(monkeypatch):
    monkeypatch.setattr(guard, "derive_all_user_node_states", lambda *_a, **_k: [
        {"canonical_node_id": "KN1387", "state": "repairing"}
    ])
    blocked = guard.blocked_short_term_evidence_ids(
        [attempt("Q1585", "KN0659")], as_of=NOW
    )
    assert guard.is_short_term_repeat_blocked("Q1411", blocked)
    assert guard.is_short_term_repeat_blocked("Q1585", blocked)


def test_random_and_category_selection_never_duplicate_exact_evidence():
    random.seed(305)
    random_questions = select_random_questions(200)
    random_evidence = [
        canonicalize_question_evidence_id(str(question["id"]))
        for question in random_questions
    ]
    assert len(random_evidence) == len(set(random_evidence))

    category_questions = select_questions_by_category(8, 30, exclude_ids={"Q1"})
    category_evidence = [
        canonicalize_question_evidence_id(str(question["id"]))
        for question in category_questions
    ]
    assert len(category_evidence) == len(set(category_evidence))


def test_small_category_shortage_uses_non_recent_global_fallback_without_repeat():
    blocked = {f"Q{number}" for number in range(1, 31)}
    selected = select_questions_by_category(14, 30, exclude_ids=blocked)
    evidence = [
        canonicalize_question_evidence_id(str(question["id"]))
        for question in selected
    ]
    assert len(selected) == 30
    assert len(evidence) == len(set(evidence))
    assert not (set(evidence) & blocked)


def test_seven_consecutive_thirty_question_random_sessions_have_no_evidence_repeat(monkeypatch):
    monkeypatch.setattr(guard, "derive_all_user_node_states", lambda items, **_k: [
        {"canonical_node_id": item["knowledge_node_id"], "state": "checking"}
        for item in items
    ])
    history = []
    selected_evidence = set()
    random.seed(304)
    for _set_number in range(7):
        blocked = guard.blocked_short_term_evidence_ids(history, as_of=NOW)
        selected = select_random_questions(30, exclude_ids=blocked)
        evidence = {
            canonicalize_question_evidence_id(str(question["id"]))
            for question in selected
        }
        assert not (selected_evidence & evidence)
        selected_evidence.update(evidence)
        history.extend(
            attempt(str(question["id"]), f"KN{index:04d}")
            for index, question in enumerate(selected, start=len(history) + 1)
        )
    assert len(selected_evidence) == 210


def test_random_and_category_routes_pass_formal_attempt_guard_including_nekketsu(monkeypatch):
    previous = attempt("Q1")
    monkeypatch.setattr(app, "get_question_attempts", lambda _user_id: [previous])
    monkeypatch.setattr(
        guard,
        "derive_all_user_node_states",
        lambda *_a, **_k: [{"canonical_node_id": "KN0001", "state": "repairing"}],
    )
    calls = []

    def random_selector(count, *, exclude_ids=()):
        calls.append(("random", set(exclude_ids)))
        return questions(count)

    def category_selector(category, count, *, exclude_ids=()):
        calls.append((category, set(exclude_ids)))
        return questions(count)

    monkeypatch.setattr(app, "select_random_questions", random_selector)
    monkeypatch.setattr(app, "select_category_questions", category_selector)
    monkeypatch.setattr(app, "format_quiz_messages", lambda _questions: ["quiz"])

    app.user_modes["random-user"] = "nekketsu"
    app.start_quiz("random-user")
    app.quiz_category_selections["category-user"] = {"category_small": 8}
    app.user_modes["category-user"] = "nekketsu"
    app.start_quiz("category-user")

    assert calls == [("random", {"Q1"}), (8, {"Q1"})]


def test_adaptive_fallback_reuses_question_attempts_as_formal_truth(monkeypatch):
    previous = attempt("Q1")
    received = []
    monkeypatch.setattr(app, "ENABLE_NODE_ADAPTIVE_RECOMMENDATION", False)
    monkeypatch.setattr(app, "get_question_attempts", lambda _user_id: [previous])
    monkeypatch.setattr(
        guard,
        "derive_all_user_node_states",
        lambda *_a, **_k: [{"canonical_node_id": "KN0001", "state": "repairing"}],
    )
    monkeypatch.setattr(
        app,
        "build_daily_session",
        lambda history, count, **kwargs: received.append((history, kwargs["exclude_ids"]))
        or questions(count),
    )
    monkeypatch.setattr(app, "format_quiz_messages", lambda _questions: ["quiz"])

    app.start_quiz("fallback-user", session_kind="adaptive_daily")

    assert received == [([previous], {"Q1"})]


def test_adaptive_session_boundary_applies_guard_for_web_style_direct_call(monkeypatch):
    previous = attempt("Q1")
    received = []
    monkeypatch.setattr(
        guard,
        "recent_short_term_evidence_ids",
        lambda _attempts, **_kwargs: {"Q1"},
    )
    monkeypatch.setattr(
        selector,
        "select_node_adaptive_questions",
        lambda attempts, count, **kwargs: received.append(set(kwargs["exclude_ids"]))
        or [{"question_id": "Q2"}],
    )
    monkeypatch.setattr(selector, "get_quiz_question", lambda q: {"id": q})

    result = selector.build_node_adaptive_session([previous], 1)

    assert received == [{"Q1"}]
    assert result == [{"id": "Q2"}]


def test_initial_assessment_runtime_reads_attempts_for_repeat_guard(monkeypatch):
    monkeypatch.setattr(app, "get_question_attempts", lambda _user_id: [])
    monkeypatch.setattr(app, "build_initial_assessment", lambda count: questions(count))
    monkeypatch.setattr(app, "format_quiz_messages", lambda _questions: ["quiz"])
    assert app.start_quiz("initial-user", session_kind="initial_assessment", question_count=10) == ["quiz"]
