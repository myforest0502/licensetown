from datetime import datetime, timedelta, timezone
import os
import random

import pytest

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "test-token")
os.environ.setdefault("CHANNEL_SECRET", "test-secret")

import adaptive_question_selector as selector
import app
import learning_engine as engine
import short_term_repeat_guard as guard
from question_bank import (
    QUESTION_AVAILABILITY_MESSAGE,
    QuestionAvailabilityError,
    get_category_small,
    get_question_tag,
    question_ids,
    select_questions_by_category,
    select_random_questions,
)
from question_equivalence import canonicalize_question_evidence_id


NOW = datetime(2026, 9, 10, 12, tzinfo=timezone.utc)


class FirstChoiceRandom:
    def shuffle(self, values):
        return None

    def choice(self, values):
        return values[0]


def test_initial_assessment_never_contains_two_raw_ids_for_same_exact_evidence(monkeypatch):
    candidates = ["Q1411", "Q1585"] + [f"Q{i}" for i in range(1, 21)]
    monkeypatch.setattr(engine, "_candidate_ids", lambda *_args, **_kwargs: list(candidates))
    monkeypatch.setattr(
        engine,
        "get_question_tag",
        lambda q_id: {"primary_ability": "KNOW", "level": (int(q_id[1:]) % 4) + 1},
    )
    monkeypatch.setattr(engine, "get_quiz_question", lambda q_id: {"id": q_id})

    selected = engine.build_initial_assessment(10, rng=FirstChoiceRandom())
    selected_ids = [item["id"] for item in selected]
    evidence_ids = [canonicalize_question_evidence_id(q_id) for q_id in selected_ids]

    assert len(selected_ids) == 10
    assert len(evidence_ids) == len(set(evidence_ids))
    assert len({"Q1411", "Q1585"} & set(selected_ids)) == 1


def test_unknown_attempt_time_fails_closed_for_three_day_floor():
    attempts = [{
        "user_id": "learner",
        "question_id": "Q1",
        "knowledge_node_id": "KN0001",
        "is_correct": True,
        "confidence": 1,
        "answer_status": "answered",
    }]

    assert guard.recent_short_term_evidence_ids(attempts, as_of=NOW) == {"Q1"}


def recent_attempt(question_id, *, user_id="learner"):
    return {
        "user_id": user_id,
        "question_id": question_id,
        "knowledge_node_id": get_question_tag(question_id)["knowledge_node_id"],
        "is_correct": True,
        "confidence": 1,
        "answer_status": "answered",
        "answered_at": NOW - timedelta(minutes=1),
    }


def evidence_ids(questions):
    return [
        canonicalize_question_evidence_id(str(question["id"]))
        for question in questions
    ]


def test_random_keeps_thirty_unique_evidence_after_five_hundred_recent_attempts():
    blocked = guard.blocked_short_term_evidence_ids(
        [recent_attempt(f"Q{number}") for number in range(1, 501)],
        as_of=NOW,
    )
    selected = select_random_questions(30, exclude_ids=blocked)
    selected_evidence = evidence_ids(selected)

    assert len(selected) == 30
    assert len(selected_evidence) == len(set(selected_evidence))
    assert not (set(selected_evidence) & blocked)


def test_category_shortage_uses_global_fresh_questions_without_reopening_blocked():
    category = 14
    category_ids = [
        q_id for q_id in question_ids() if get_category_small(q_id) == category
    ]
    blocked = {
        canonicalize_question_evidence_id(q_id) for q_id in category_ids[:-1]
    }
    selected = select_questions_by_category(category, 30, exclude_ids=blocked)
    selected_evidence = evidence_ids(selected)

    assert len(selected) == 30
    assert len(selected_evidence) == len(set(selected_evidence))
    assert not (set(selected_evidence) & blocked)
    assert any(get_category_small(question["id"]) != category for question in selected)


def test_nekketsu_random_and_category_keep_the_same_non_recent_guarantee(monkeypatch):
    attempts = [recent_attempt(f"Q{number}", user_id="nekketsu") for number in range(1, 101)]
    monkeypatch.setattr(app, "get_question_attempts", lambda _user_id: attempts)
    monkeypatch.setattr(app, "format_quiz_messages", lambda _questions: ["quiz"])

    app.user_modes["nekketsu-random"] = "nekketsu"
    app.start_quiz("nekketsu-random")
    random_session = app.study_sessions.pop("nekketsu-random")

    app.user_modes["nekketsu-category"] = "nekketsu"
    app.quiz_category_selections["nekketsu-category"] = {"category_small": 14}
    app.start_quiz("nekketsu-category")
    category_session = app.study_sessions.pop("nekketsu-category")

    blocked = guard.recent_short_term_evidence_ids(attempts, as_of=NOW)
    for session in (random_session, category_session):
        selected_evidence = evidence_ids(session["all_questions"])
        assert len(selected_evidence) == 30
        assert len(selected_evidence) == len(set(selected_evidence))
        assert not (set(selected_evidence) & blocked)


def test_adaptive_daily_keeps_thirty_unique_after_large_recent_histories():
    for history_size in (100, 500):
        attempts = [
            recent_attempt(f"Q{number}", user_id=f"adaptive-{history_size}")
            for number in range(1, history_size + 1)
        ]
        selected = selector.build_node_adaptive_session(
            attempts, 30, rng=random.Random(history_size)
        )
        selected_evidence = evidence_ids(selected)
        blocked = guard.recent_short_term_evidence_ids(attempts, as_of=NOW)

        assert len(selected) == 30
        assert len(selected_evidence) == len(set(selected_evidence))
        assert not (set(selected_evidence) & blocked)


def test_category_intent_adaptive_relaxes_to_global_non_blocked_supply():
    category = 14
    category_ids = [
        q_id for q_id in question_ids() if get_category_small(q_id) == category
    ]
    attempts = [
        recent_attempt(q_id, user_id="web-category") for q_id in category_ids[:-1]
    ]
    selected = selector.build_node_adaptive_session(
        attempts,
        10,
        category_small=category,
        learning_intent="repair",
        rng=random.Random(306),
    )
    selected_evidence = evidence_ids(selected)
    blocked = guard.recent_short_term_evidence_ids(attempts, as_of=NOW)

    assert len(selected) == 10
    assert len(selected_evidence) == len(set(selected_evidence))
    assert not (set(selected_evidence) & blocked)
    assert any(get_category_small(question["id"]) != category for question in selected)


def test_singleton_node_without_alternate_does_not_stop_global_learning():
    attempts = [recent_attempt("Q1", user_id="singleton")]
    selected = selector.build_node_adaptive_session(
        attempts, 30, learning_intent="repair", rng=random.Random(307)
    )

    assert len(selected) == 30
    assert "Q1" not in evidence_ids(selected)


def test_physically_impossible_web_start_is_explicit_not_500_or_503(monkeypatch):
    app.web_recommendation_sessions.clear()
    monkeypatch.setattr(app, "dashboard_user_id", lambda _token: "learner")
    monkeypatch.setattr(
        app,
        "build_dashboard",
        lambda _user_id: {"recommended_study": [("神経医学", 10)]},
    )
    monkeypatch.setattr(
        app,
        "create_web_recommendation_session",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            QuestionAvailabilityError("physical shortage")
        ),
    )

    response = app.app.test_client().post(
        "/goukaku-no-michi/recommendation/start",
        json={
            "token": "signed",
            "field": "神経医学",
            "count": 10,
            "source": "dashboard",
        },
    )

    assert response.status_code == 409
    assert "直前に解いた問題を避ける" in response.get_json()["message"]


def test_adaptive_physical_shortage_raises_explicit_availability_error(monkeypatch):
    ids = [f"Q{number}" for number in range(1, 6)]
    monkeypatch.setattr(selector, "question_ids", lambda: ids)
    monkeypatch.setattr(selector, "derive_all_user_node_states", lambda *_a, **_k: [])
    monkeypatch.setattr(
        selector,
        "get_question_tag",
        lambda q_id: {
            "knowledge_node_id": f"KN{int(q_id[1:]):04d}",
            "safety": "none",
        },
    )
    monkeypatch.setattr(selector, "get_category_small", lambda _q_id: 1)
    monkeypatch.setattr(selector, "get_quiz_question", lambda q_id: {"id": q_id})

    with pytest.raises(QuestionAvailabilityError, match="non-blocked"):
        selector.build_node_adaptive_session([], 6, rng=random.Random(308))


def test_physically_impossible_line_start_returns_clear_cooldown_message(monkeypatch):
    replies = []
    monkeypatch.setattr(
        app,
        "start_quiz",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            QuestionAvailabilityError("physical shortage")
        ),
    )
    monkeypatch.setattr(app, "reply_to_line", lambda token, text: replies.append((token, text)))

    assert not app.start_and_reply_quiz("reply-token", "learner")
    assert replies == [("reply-token", QUESTION_AVAILABILITY_MESSAGE)]


def test_physically_impossible_async_start_pushes_clear_cooldown_message(monkeypatch):
    pushes = []
    monkeypatch.setattr(app, "show_loading_animation", lambda _user_id: None)
    monkeypatch.setattr(
        app,
        "start_quiz",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            QuestionAvailabilityError("physical shortage")
        ),
    )
    monkeypatch.setattr(app, "push_to_line", lambda user_id, text: pushes.append((user_id, text)))

    app.prepare_and_send_quiz("learner")

    assert pushes == [("learner", QUESTION_AVAILABILITY_MESSAGE)]
