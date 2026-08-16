import os

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "test-token")
os.environ.setdefault("CHANNEL_SECRET", "test-secret")

import app as bot_app
from question_bank import (
    get_answer,
    get_explanation,
    get_question,
    get_quiz_question,
    is_answer_correct,
    question_count,
    select_random_questions,
)


def test_formal_bank_has_all_questions_and_boundary_ids():
    assert question_count() == 1564
    assert get_question("Q1")["id"] == "Q1"
    assert get_answer("Q500")["id"] == "Q500"
    assert get_question("Q501")["id"] == "Q501"
    assert get_explanation("Q1564")["id"] == "Q1564"


def test_accepted_answer_sets_cover_single_multi_and_either_answers():
    single = get_quiz_question("Q1")
    required_multi = get_quiz_question("Q521")
    either = get_quiz_question("Q551")

    assert is_answer_correct(single, "B")
    assert not is_answer_correct(single, "A")
    assert is_answer_correct(required_multi, "BD")
    assert is_answer_correct(required_multi, "DB")
    assert not is_answer_correct(required_multi, "B")
    assert is_answer_correct(either, "B")
    assert is_answer_correct(either, "D")
    assert not is_answer_correct(either, "BD")


def test_quiz_adapter_supplies_problem_answer_and_full_explanations():
    question = get_quiz_question("Q521")
    assert question["question"]
    assert set(question["choices"]) == set("ABCDE")
    assert question["display_answer"] == "B・D"
    assert question["explanation"]
    assert set(question["choice_explanations"]) == set("ABCDE")


def test_formal_selection_and_multiple_answer_parser_work_for_five_questions():
    selected = select_random_questions(5)
    assert len(selected) == 5
    assert len({question["id"] for question in selected}) == 5
    parsed = bot_app.parse_quiz_answers(
        "1:BD1 2:A2 3:C3 4:D1 5:E2",
        expected_numbers=set(range(1, 6)),
    )
    assert parsed[1] == {"answer": "BD", "confidence": "1"}


def test_formal_questions_flow_through_existing_thirty_question_session(monkeypatch):
    questions = [get_quiz_question(f"Q{number}") for number in range(1, 31)]
    monkeypatch.setattr(bot_app, "select_formal_questions", lambda count: questions[:count])
    monkeypatch.setattr(bot_app.user_modes, "get", lambda user_id, default=None: "study")
    session_messages = bot_app.start_quiz("formal-thirty-user")
    session = bot_app.study_sessions["formal-thirty-user"]

    assert len(session_messages) == 1
    assert session["question_count"] == 30
    assert len(session["all_questions"]) == 30
    assert len(session["questions"]) == 5
    assert session["all_questions"][0]["id"] == "Q1"

    bot_app.pause_quiz_session("formal-thirty-user")
    resumed = bot_app.resume_quiz_session("formal-thirty-user")
    assert resumed["status"] == "waiting_for_answers"
    assert resumed["all_questions"][29]["id"] == "Q30"


def test_formal_thirty_questions_grade_and_complete_all_explanations():
    questions = [get_quiz_question(f"Q{number}") for number in range(501, 531)]
    answers = {
        number: {
            "answer": "".join(question["accepted_answer_sets"][0]),
            "confidence": "1",
        }
        for number, question in enumerate(questions, 1)
    }
    result = bot_app.calculate_quiz_result(questions, answers)
    assert result["score"] == 30

    session = {
        "status": "waiting_for_explanations",
        "explanation_set": 0,
        "questions_per_set": 5,
        "question_count": 30,
        "all_questions": questions,
        "all_answers": answers,
    }
    messages = []
    for _ in range(6):
        messages.extend(bot_app.advance_quiz_explanations(session))
    assert session["status"] == "quiz_completed"
    assert any("解説：" in message for message in messages)
    assert any("A：" in message for message in messages)
