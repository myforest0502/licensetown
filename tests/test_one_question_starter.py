from types import SimpleNamespace

import one_question_starter as starter


def test_one_question_command_builds_single_question_session(monkeypatch):
    captured = {}
    question = {
        "id": "Q1",
        "question": "test",
        "choices": {"A": "a", "B": "b"},
        "answer": "A",
    }
    monkeypatch.setattr(starter, "select_random_questions", lambda count: [question])

    legacy = SimpleNamespace(
        process_study_flow_command=lambda *args: False,
        user_modes={},
        quiz_category_selections={"u1": {"category_small": "old"}},
        study_sessions={},
        reply_current_quiz=lambda reply_token, session, intro_text=None: captured.update(
            reply_token=reply_token, session=session, intro_text=intro_text
        ),
        logging=__import__("logging"),
        reply_to_line=lambda *args: None,
    )
    starter.install_one_question_starter(legacy)

    assert legacy.process_study_flow_command("r1", "u1", starter.ONE_QUESTION_COMMAND) is True
    session = legacy.study_sessions["u1"]
    assert session["question_count"] == 1
    assert session["questions_per_set"] == 1
    assert session["total_sets"] == 1
    assert session["expected_numbers"] == [1]
    assert session["session_kind"] == "one_question_starter"
    assert session["questions"] == [question]
    assert legacy.user_modes["u1"] == "study"
    assert "u1" not in legacy.quiz_category_selections
    assert captured["reply_token"] == "r1"
    assert "まず1問だけ" in captured["intro_text"]


def test_other_commands_fall_through():
    calls = []
    legacy = SimpleNamespace(
        process_study_flow_command=lambda *args: calls.append(args) or "original",
        user_modes={},
        quiz_category_selections={},
        study_sessions={},
        reply_current_quiz=lambda *args, **kwargs: None,
        logging=__import__("logging"),
        reply_to_line=lambda *args: None,
    )
    starter.install_one_question_starter(legacy)

    assert legacy.process_study_flow_command("r", "u", "勉強する") == "original"
    assert calls == [("r", "u", "勉強する")]
