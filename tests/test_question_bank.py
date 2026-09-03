import os
from types import SimpleNamespace

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "test-token")
os.environ.setdefault("CHANNEL_SECRET", "test-secret")

import app as bot_app
from question_bank import (
    CATEGORY_GROUPS,
    CATEGORY_NAMES,
    get_category_group_names,
    get_category_names_for_group,
    get_category_name,
    get_category_small,
    get_answer,
    get_explanation,
    get_question,
    get_quiz_question,
    is_answer_correct,
    question_count,
    resolve_category_small,
    select_random_questions,
    select_questions_by_category,
)


def test_formal_category_lookup_uses_all_official_names():
    expected = [
        "解剖学", "生理学", "心理学", "人間発達学", "教育学", "医学概論",
        "病理学", "内科学", "神経医学", "精神医学", "小児学", "臨床心理学",
        "基礎運動学", "臨床運動学", "動作分析学", "運動器", "理学療法評価各論", "理学療法治療各論",
    ]
    assert list(CATEGORY_NAMES) == list(range(1, 19))
    assert [get_category_name(number) for number in range(1, 19)] == expected
    assert get_category_small("Q1") == get_question("Q1")["category_small"]


def test_formal_category_hierarchy_has_three_groups_and_six_fields_each():
    assert get_category_group_names() == ("基礎", "専門基礎", "専門")
    assert all(len(numbers) == 6 for numbers in CATEGORY_GROUPS.values())
    assert get_category_names_for_group("基礎") == (
        "解剖学", "生理学", "心理学", "人間発達学", "教育学", "医学概論",
    )
    assert get_category_names_for_group("専門基礎") == (
        "病理学", "内科学", "神経医学", "精神医学", "小児学", "臨床心理学",
    )
    assert get_category_names_for_group("専門") == (
        "基礎運動学", "臨床運動学", "動作分析学", "運動器", "理学療法評価各論", "理学療法治療各論",
    )
    assert resolve_category_small("解剖学", "基礎") == 1
    assert resolve_category_small("理学療法治療各論", "専門") == 18


def test_category_quick_replies_use_the_shared_formal_hierarchy(monkeypatch):
    replies = []
    monkeypatch.setattr(
        bot_app,
        "line_bot_api",
        type("LineApi", (), {"reply_message": lambda self, token, message: replies.append(message)})(),
    )

    bot_app.reply_quiz_category_group_choice("token")
    assert [item.action.label for item in replies.pop().quick_reply.items] == [
        "基礎", "専門基礎", "専門",
    ]

    for group_name in get_category_group_names():
        bot_app.reply_quiz_category_choice("token", group_name)
        assert [item.action.label for item in replies.pop().quick_reply.items] == list(
            get_category_names_for_group(group_name)
        )


def test_category_selection_returns_only_the_selected_formal_field():
    selected = select_questions_by_category(10, 30)
    assert len(selected) == 30
    assert all(int(question["category_small"]) == 10 for question in selected)


def test_small_category_still_keeps_thirty_question_study_flow():
    selected = select_questions_by_category(14, 30)
    assert len(selected) == 30
    assert all(int(question["category_small"]) == 14 for question in selected)


def test_formal_bank_has_all_questions_and_boundary_ids():
    assert question_count() == 1720
    assert get_question("Q1")["id"] == "Q1"
    assert get_answer("Q500")["id"] == "Q500"
    assert get_question("Q501")["id"] == "Q501"
    assert get_explanation("Q1594")["id"] == "Q1594"


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


def test_unknown_zero_parser_preserves_all_five_positions():
    cases = {
        "A1 B2 0 D1 E2": [3],
        "0 B2 C3 D1 E2": [1],
        "A1 B2 C3 D1 0": [5],
        "0 0 C3 D1 E2": [1, 2],
        "0 0 0 0 0": [1, 2, 3, 4, 5],
        "1:A1 2:B2 3:0 4:D1 5:E2": [3],
    }
    for text, unknown_numbers in cases.items():
        parsed = bot_app.parse_quiz_answers(text, expected_numbers=set(range(1, 6)))
        assert list(parsed) == [1, 2, 3, 4, 5]
        for number in unknown_numbers:
            assert parsed[number] == {
                "answer": "",
                "confidence": None,
                "answer_status": "unknown",
            }
        for number in set(range(1, 6)) - set(unknown_numbers):
            assert parsed[number].get("answer_status", "answered") == "answered"


def test_unknown_zero_parser_rejects_attached_or_wrong_token_counts():
    invalid = [
        "A0 B2 C3 D1 E2",
        "B0 B2 C3 D1 E2",
        "0A B2 C3 D1 E2",
        "01 B2 C3 D1 E2",
        "A1 B2 D1 E2",
        "A1 B2 C3 D1 E2 A1",
    ]
    for text in invalid:
        assert bot_app.parse_quiz_answers(text, expected_numbers=set(range(1, 6))) == {}


def test_answer_instructions_explain_zero_without_replacing_existing_rules():
    message = bot_app.format_quiz_messages(
        [get_quiz_question(f"Q{number}") for number in range(1, 6)]
    )[0]
    assert "A1 B2 0 D1 E2" in message
    assert "0は自信度じゃなくて「分からない」の意味" in message
    assert "C0のようには入力しない" in message
    assert "5問分の位置は必ず残して" in message
    assert "1＝自信あり" in message
    assert "2＝少し迷った" in message
    assert "3＝あてずっぽう" in message
    assert "BD1" in message


def test_unknown_zero_is_graded_wrong_and_displayed_as_unknown():
    questions = [get_quiz_question(f"Q{number}") for number in range(1, 6)]
    parsed = bot_app.parse_quiz_answers(
        "A1 B2 0 D1 E2", expected_numbers=set(range(1, 6))
    )
    result = bot_app.calculate_quiz_result(questions, parsed)
    detail = result["details"][2]
    assert detail["is_correct"] is False
    assert detail["confidence"] == ""
    assert detail["answer_status"] == "unknown"
    rendered = "\n".join(bot_app.create_quiz_result_messages(questions, parsed))
    assert "あなたの回答：0（分からない）" in rendered
    assert "自信度：—（分からない）" in rendered


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


def test_selected_category_flows_into_existing_session(monkeypatch):
    user_id = "formal-category-user"
    questions = [get_quiz_question("Q14")] * 30
    monkeypatch.setattr(
        bot_app,
        "select_formal_questions_by_category",
        lambda category_small, count: questions[:count],
    )
    bot_app.quiz_category_selections[user_id] = {
        "mode": "study", "group_name": "基礎", "category_small": 1,
    }
    bot_app.user_modes[user_id] = "study"

    bot_app.start_quiz(user_id)
    session = bot_app.study_sessions[user_id]

    assert session["category_small"] == 1
    assert len(session["all_questions"]) == 30
    assert user_id not in bot_app.quiz_category_selections


def test_return_home_clears_pending_category_selection(monkeypatch):
    user_id = "pending-category-user"
    bot_app.quiz_category_selections[user_id] = {
        "mode": "nekketsu", "group_name": "専門",
    }
    bot_app.user_states[user_id] = "waiting_quiz_category_small"
    monkeypatch.setattr(bot_app, "reply_mode_select", lambda *args, **kwargs: None)

    bot_app.return_home("reply-token", user_id)

    assert user_id not in bot_app.quiz_category_selections
    assert user_id not in bot_app.user_states


def test_all_eighteen_categories_reply_with_first_five_without_extra_input(monkeypatch):
    replies = []
    monkeypatch.setattr(
        bot_app,
        "line_bot_api",
        type("LineApi", (), {"reply_message": lambda self, token, messages: replies.append((token, messages))})(),
    )

    for mode in ("study", "nekketsu"):
        for category_small in range(1, 19):
            user_id = f"first-batch-{mode}-{category_small}"
            bot_app.user_modes[user_id] = mode
            bot_app.quiz_category_selections[user_id] = {
                "mode": mode,
                "category_small": category_small,
            }

            assert bot_app.start_and_reply_quiz("reply-token", user_id)
            session = bot_app.study_sessions[user_id]
            assert session["status"] == "waiting_for_answers"
            assert len(session["questions"]) == 5
            assert all(
                int(question["category_small"]) == category_small
                for question in session["all_questions"]
            )
            assert len(replies[-1][1]) == 3
            assert "第1問" in replies[-1][1][1].text
            assert replies[-1][1][2].text == "じゃあ、解答を入力してくれ＾＾"


def test_next_batch_is_replied_immediately_for_study_and_nekketsu(monkeypatch):
    replies = []
    monkeypatch.setattr(
        bot_app,
        "line_bot_api",
        type("LineApi", (), {"reply_message": lambda self, token, messages: replies.append(messages)})(),
    )

    for mode in ("study", "nekketsu"):
        user_id = f"next-batch-{mode}"
        bot_app.user_modes[user_id] = mode
        bot_app.quiz_category_selections[user_id] = {"mode": mode, "category_small": 16}
        bot_app.start_quiz(user_id)
        session = bot_app.study_sessions[user_id]
        session["status"] = "waiting_for_continue"

        assert bot_app.advance_and_reply_quiz(
            "reply-token", user_id, expected_session_id=session["session_id"]
        )
        assert session["current_set"] == 2
        assert session["status"] == "waiting_for_answers"
        assert session["expected_numbers"] == list(range(6, 11))
        assert "第6問" in replies[-1][1].text


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


def test_adaptive_study_replies_with_first_five_and_advances_in_same_requests(monkeypatch):
    """実機のHOME→準備OK→自動選択→回答→続けるを再現する。"""
    replies = []

    class LineApi:
        def reply_message(self, token, messages):
            replies.append((token, messages))

        def push_message(self, *_args, **_kwargs):
            raise AssertionError("おすすめ学習はPush APIに依存しない")

    monkeypatch.setattr(bot_app, "line_bot_api", LineApi())
    monkeypatch.setattr(bot_app, "return_home", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(bot_app, "record_confirmed_learning_batch", lambda *_args: True)
    monkeypatch.setattr(bot_app, "is_initial_assessment_completed", lambda _user_id: True)

    user_id = "recommended-first-batch-user"
    bot_app.study_sessions.pop(user_id, None)
    bot_app.user_states.pop(user_id, None)
    bot_app.user_modes.pop(user_id, None)
    bot_app.quiz_category_selections.pop(user_id, None)
    bot_app.learning_answer_counts.pop(user_id, None)

    def send(text):
        bot_app.handle_text_message(SimpleNamespace(
            message=SimpleNamespace(text=text),
            source=SimpleNamespace(user_id=user_id),
            reply_token=f"token-{len(replies)}",
        ))

    send("ホームに戻る")
    send("勉強する")
    send("準備OK！")

    session = bot_app.study_sessions[user_id]
    assert session["status"] == "waiting_for_answers"
    assert session["current_set"] == 1
    assert session["expected_numbers"] == list(range(1, 6))
    assert len(session["questions"]) == 5
    first_reply = replies[-1][1]
    assert len(first_reply) == 3
    assert "今のお前に必要な30問" in first_reply[0].text
    assert "【第1問】" in first_reply[1].text
    assert "【第5問】" in first_reply[1].text

    answers = []
    for number, question in enumerate(session["questions"], 1):
        answers.append(f"{number}:{''.join(question['accepted_answer_sets'][0])}1")
    send("\n".join(answers))
    assert session["status"] == "waiting_for_continue"

    send("続ける")
    assert session["status"] == "waiting_for_answers"
    assert session["current_set"] == 2
    assert session["expected_numbers"] == list(range(6, 11))
    second_reply = replies[-1][1]
    assert len(second_reply) == 3
    assert "【第6問】" in second_reply[1].text
    assert "【第10問】" in second_reply[1].text
