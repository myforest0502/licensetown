from question_order_quality import arrange_five_question_sets, has_predictable_answer_pattern
import app


def questions(keys):
    return [
        {
            "id": f"Q{index}",
            "question_text": f"stem-{index}",
            "answer": key,
            "accepted_answer_sets": [[key]],
            "explanation": f"explanation-{index}",
        }
        for index, key in enumerate(keys, start=1)
    ]


def keys(items):
    return "".join(item["answer"] for item in items)


def test_conspicuous_five_question_patterns_are_reordered():
    for pattern in ("ABCDE", "EDCBA", "AAAAA", "ABABA"):
        ordered = arrange_five_question_sets(questions(pattern + "BCDEA"))
        assert not has_predictable_answer_pattern(ordered[:5])
        assert keys(ordered[:5]) != pattern


def test_natural_imbalance_is_allowed_and_not_forced_to_one_of_each():
    original = questions("AABCD")
    ordered = arrange_five_question_sets(original)
    assert ordered == original
    assert keys(ordered) == "AABCD"


def test_reordering_preserves_membership_and_each_question_mapping():
    original = questions("ABCDEBCDEA")
    expected = {
        item["id"]: (item["question_text"], item["answer"], item["explanation"])
        for item in original
    }
    ordered = arrange_five_question_sets(original)
    assert {item["id"] for item in ordered} == set(expected)
    assert len(ordered) == len(original)
    assert {
        item["id"]: (item["question_text"], item["answer"], item["explanation"])
        for item in ordered
    } == expected
    assert all(
        not has_predictable_answer_pattern(ordered[start:start + 5])
        for start in range(0, len(ordered), 5)
    )


def test_start_quiz_applies_one_guard_to_adaptive_fallback_random_and_category(monkeypatch):
    selected = questions("ABCDEABCDE")
    monkeypatch.setattr(app, "format_quiz_messages", lambda _questions: ["quiz"])
    monkeypatch.setattr(app, "get_question_history", lambda _user: [])
    monkeypatch.setattr(app, "get_question_attempts", lambda _user: [])
    monkeypatch.setattr(app, "build_daily_session", lambda *_args, **_kwargs: list(selected))
    monkeypatch.setattr(app, "build_node_adaptive_session", lambda *_args, **_kwargs: list(selected))
    monkeypatch.setattr(app, "select_random_questions", lambda *_args, **_kwargs: list(selected))
    monkeypatch.setattr(app, "select_category_questions", lambda *_args, **_kwargs: list(selected))

    cases = [
        ("adaptive", "adaptive_daily", True, None),
        ("fallback", "adaptive_daily", False, None),
        ("random", None, False, None),
        ("category", None, False, {"category_small": 1}),
    ]
    for user_id, session_kind, adaptive_enabled, category in cases:
        monkeypatch.setattr(app, "ENABLE_NODE_ADAPTIVE_RECOMMENDATION", adaptive_enabled)
        monkeypatch.setattr(
            app, "NODE_ADAPTIVE_RECOMMENDATION_PILOT_USER_IDS",
            {user_id} if adaptive_enabled else set(),
        )
        if category:
            app.quiz_category_selections[user_id] = category
        app.start_quiz(user_id, session_kind=session_kind, question_count=10)
        stored = app.study_sessions.pop(user_id)["all_questions"]
        assert {item["id"] for item in stored} == {item["id"] for item in selected}
        assert all(
            not has_predictable_answer_pattern(stored[start:start + 5])
            for start in (0, 5)
        )
