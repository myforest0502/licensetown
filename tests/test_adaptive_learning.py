import os
import json
import re
from collections import Counter
from pathlib import Path
from types import SimpleNamespace

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "test-token")
os.environ.setdefault("CHANNEL_SECRET", "test-secret")

import app as bot_app
import database
import learning_engine
from learning_engine import (
    build_daily_session,
    build_initial_assessment,
    initial_assessment_needs_extension,
    summarize_initial_assessment,
    summarize_daily_session,
)
from question_bank import get_question_tag, get_quiz_question, question_count


def test_all_formal_question_tags_load_and_match_ids():
    assert question_count() == 1574
    assert get_question_tag("Q1")["tag_status"] == "reviewed_sample"
    assert get_question_tag("Q1")["tag_version"] == "0.3"
    assert get_question_tag("Q200")["tag_status"] == "reviewed_sample"
    assert get_question_tag("Q201")["tag_status"] == "reviewed"
    assert get_question_tag("Q201")["tag_version"] == "1.0"
    assert any(
        get_question_tag(f"Q{number}")["secondary_ability"] is None
        for number in range(201, 231)
    )
    assert get_question_tag("Q830")["tag_version"] == "1.0"
    assert get_question_tag("Q830")["tag_status"] == "reviewed"
    assert get_question_tag("Q831")["tag_version"] == "1.0"
    assert get_question_tag("Q831")["tag_status"] == "reviewed"
    assert get_question_tag("Q1574")["tag_version"] == "1.0"
    assert get_question_tag("Q1574")["tag_status"] == "reviewed"

    tags = [get_question_tag(f"Q{number}") for number in range(1, 1575)]
    assert Counter(tag["tag_version"] for tag in tags) == {"0.3": 200, "1.0": 1374}
    assert Counter(tag["tag_status"] for tag in tags) == {
        "reviewed_sample": 200,
        "reviewed": 1374,
    }
    assert all(
        re.fullmatch(r"KN[0-9]{4}", tag["knowledge_node_id"])
        for tag in tags
    )


def test_formal_tag_schema_keeps_v03_and_accepts_v10_reviewed():
    schema = json.loads(
        (Path(__file__).parents[1] / "data" / "question_bank" /
         "question_tags.schema.json").read_text(encoding="utf-8")
    )
    properties = schema["items"]["properties"]
    assert properties["tag_version"]["enum"] == ["0.3", "1.0"]
    assert properties["tag_status"]["enum"] == [
        "reviewed_sample", "provisional_bulk", "reviewed",
    ]
    assert None in properties["secondary_ability"]["enum"]
    assert "knowledge_node_id" in schema["items"]["required"]
    assert properties["knowledge_node_id"]["pattern"] == "^KN[0-9]{4}$"


def test_initial_assessment_is_ten_balanced_questions_and_never_exceeds_fifteen():
    questions = build_initial_assessment(10)
    assert len(questions) == 10
    assert len({question["id"] for question in questions}) == 10
    abilities = Counter(get_question_tag(question["id"])["primary_ability"] for question in questions)
    levels = {get_question_tag(question["id"])["level"] for question in questions}
    assert len(abilities) >= 5
    assert len(levels) >= 2
    assert len(build_initial_assessment(15)) == 15


def test_initial_assessment_only_extends_when_evidence_is_insufficient():
    balanced = [
        {"question_id": question["id"], "is_correct": True, "confidence": 1}
        for question in build_initial_assessment(10)
    ]
    assert not initial_assessment_needs_extension(balanced)
    repeated = [{"question_id": "Q1", "is_correct": True, "confidence": 1}] * 10
    assert initial_assessment_needs_extension(repeated)


def test_daily_session_prioritizes_confident_errors_without_exposing_tags():
    selected = build_daily_session([
        {"question_id": "Q1", "is_correct": False, "confidence": 1},
        {"question_id": "Q2", "is_correct": True, "confidence": 1},
    ], question_count=30)
    assert len(selected) == 30
    assert "Q1" in {question["id"] for question in selected}
    assert all("primary_ability" not in question for question in selected)
    assert all("knowledge_node" not in question for question in selected)
    assert all("knowledge_node_id" not in question for question in selected)


def _assert_node_history_prioritizes_second_question(monkeypatch, tags):
    monkeypatch.setattr(learning_engine, "_candidate_ids", lambda _category=None: ["Q2", "Q3"])
    monkeypatch.setattr(learning_engine, "get_question_tag", lambda q_id: tags[q_id])
    monkeypatch.setattr(learning_engine, "get_quiz_question", lambda q_id: {"id": q_id})
    rng = SimpleNamespace(random=lambda: 0.0)
    history = [
        {"question_id": "Q1", "is_correct": False},
        {"question_id": "Q1", "is_correct": False},
    ]

    assert learning_engine.build_daily_session(
        history, question_count=1, rng=rng
    ) == [{"id": "Q2"}]


def test_daily_session_groups_node_history_by_stable_id(monkeypatch):
    _assert_node_history_prioritizes_second_question(monkeypatch, {
        "Q1": {"knowledge_node_id": "KN0001", "knowledge_node": "old label"},
        "Q2": {"knowledge_node_id": "KN0001", "knowledge_node": "new label"},
        "Q3": {"knowledge_node_id": "KN0003", "knowledge_node": "other label"},
    })


def test_daily_session_groups_reviewed_alias_with_canonical_node(monkeypatch):
    _assert_node_history_prioritizes_second_question(monkeypatch, {
        "Q1": {"knowledge_node_id": "KN0597"},
        "Q2": {"knowledge_node_id": "KN0807"},
        "Q3": {"knowledge_node_id": "KN0003"},
    })


def test_daily_session_groups_v02_pusher_alias_with_canonical_node(monkeypatch):
    _assert_node_history_prioritizes_second_question(monkeypatch, {
        "Q1": {"knowledge_node_id": "KN0071"},
        "Q2": {"knowledge_node_id": "KN0211"},
        "Q3": {"knowledge_node_id": "KN0003"},
    })


def test_daily_session_falls_back_to_knowledge_node_label(monkeypatch):
    _assert_node_history_prioritizes_second_question(monkeypatch, {
        "Q1": {"knowledge_node": "shared legacy label"},
        "Q2": {"knowledge_node": "shared legacy label"},
        "Q3": {"knowledge_node": "other legacy label"},
    })


def test_assessment_state_is_saved_existing_history_counts_and_reset_clears_it():
    user_id = "adaptive-state-user"
    database.reset_user_profile(user_id)
    assert not database.is_initial_assessment_completed(user_id)
    database.mark_initial_assessment_completed(user_id)
    assert database.is_initial_assessment_completed(user_id)
    database.reset_user_profile(user_id)
    assert not database.is_initial_assessment_completed(user_id)

    database.record_learning_batch(user_id, "legacy:1", "study", 5, 3)
    assert database.is_initial_assessment_completed(user_id)
    database.reset_user_profile(user_id)


def test_new_user_ready_starts_location_check_and_existing_user_starts_daily(monkeypatch):
    replies = []
    starts = []
    ready_replies = []

    class LineApi:
        def reply_message(self, token, messages):
            replies.append((token, messages))

    monkeypatch.setattr(bot_app, "line_bot_api", LineApi())
    monkeypatch.setattr(
        bot_app,
        "start_and_reply_quiz",
        lambda token, user_id, **kwargs: starts.append((user_id, kwargs)) or True,
    )
    monkeypatch.setattr(
        bot_app,
        "reply_study_ready_choice",
        lambda token: ready_replies.append(token),
    )

    def send(user_id, text):
        bot_app.handle_text_message(SimpleNamespace(
            message=SimpleNamespace(text=text),
            source=SimpleNamespace(user_id=user_id),
            reply_token="token",
        ))

    monkeypatch.setattr(bot_app, "is_initial_assessment_completed", lambda user_id: False)
    send("new-adaptive-user", "勉強する")
    assert not starts
    assert not ready_replies
    assert "new-adaptive-user" not in bot_app.study_sessions
    assert bot_app.user_states["new-adaptive-user"] == "awaiting_initial_assessment_start"
    intro_message = replies[-1][1]
    assert intro_message.text == (
        "「敵を知り、己を知れば百戦危うからず」ってな。\n\n"
        "国家試験を突破する。\n"
        "まず“敵”のことはこっちで見てある。\n\n"
        "じゃあ次は、お前のことを少し知りたい。\n"
        "どこまでできてて、どこから手を入れると一番伸びるのか。\n\n"
        "まずは小手調べに10問いくぞ。\n"
        "点数をつけたいわけじゃない。\n"
        "これから無駄なく進めるための現在地確認だ＾＾\n\n"
        "気楽にやってみてくれ。\n\n"
        "では、いくぞ！"
    )
    assert [item.action.text for item in intro_message.quick_reply.items] == [
        "現在地チェックを始める"
    ]

    send("new-adaptive-user", "現在地チェックを始める")
    assert starts[-1][1]["session_kind"] == "initial_assessment"
    assert starts[-1][1]["question_count"] == 10
    assert "intro_text" not in starts[-1][1]

    monkeypatch.setattr(bot_app, "is_initial_assessment_completed", lambda user_id: True)
    send("existing-adaptive-user", "勉強する")
    assert ready_replies == ["token"]
    send("existing-adaptive-user", "準備OK！")
    assert starts[-1][1]["session_kind"] == "adaptive_daily"
    assert starts[-1][1]["intro_text"] == "今のお前に必要な30問を組んだぞ。さあ始めよう＾＾"


def test_manual_selection_route_remains_available(monkeypatch):
    replies = []
    monkeypatch.setattr(
        bot_app,
        "reply_question_type_choice",
        lambda token, mode: replies.append((token, mode)),
    )
    bot_app.handle_text_message(SimpleNamespace(
        message=SimpleNamespace(text="自分で選ぶ"),
        source=SimpleNamespace(user_id="manual-user"),
        reply_token="token",
    ))
    assert replies == [("token", "学習")]


def test_location_check_completes_after_ten_and_marks_profile(monkeypatch):
    user_id = "assessment-completion-user"
    replies = []
    completed = []

    class LineApi:
        def reply_message(self, token, message):
            replies.append(message)

    questions = [get_quiz_question(f"Q{number}") for number in range(1, 11)]
    monkeypatch.setattr(bot_app, "line_bot_api", LineApi())
    monkeypatch.setattr(bot_app, "build_initial_assessment", lambda count, **_kwargs: questions[:count])
    monkeypatch.setattr(bot_app, "initial_assessment_needs_extension", lambda _results: False)
    monkeypatch.setattr(bot_app, "record_confirmed_learning_batch", lambda *_args: True)
    monkeypatch.setattr(bot_app, "finish_active_learning_time", lambda *_args: None)
    monkeypatch.setattr(bot_app, "mark_initial_assessment_completed", completed.append)
    bot_app.user_modes[user_id] = "study"
    bot_app.start_quiz(user_id, session_kind="initial_assessment", question_count=10)
    session = bot_app.study_sessions[user_id]

    def answer_current_batch():
        start = (session["current_set"] - 1) * 5 + 1
        text = "\n".join(
            f"{number}:{''.join(question['accepted_answer_sets'][0])}1"
            for number, question in zip(range(start, start + 5), session["questions"])
        )
        assert bot_app.process_study_answer_input("token", user_id, text)

    answer_current_batch()
    assert session["status"] == "waiting_for_continue"
    bot_app.start_next_quiz(user_id)
    answer_current_batch()
    assert session["status"] == "assessment_completed"
    assert completed == [user_id]
    assert "お前の現在地はだいたい分かった" in replies[-1].text


def _assessment_results(question_ids, correct=True, confidence=1):
    return [
        {"question_id": q_id, "is_correct": correct, "confidence": confidence}
        for q_id in question_ids
    ]


def test_initial_feedback_handles_good_partial_guess_and_confident_error_results():
    question_ids = [question["id"] for question in build_initial_assessment(10)]
    good = summarize_initial_assessment(_assessment_results(question_ids))
    partial_results = _assessment_results(question_ids)
    partial_results[0]["is_correct"] = False
    partial_results[1]["is_correct"] = False
    partial = summarize_initial_assessment(partial_results)
    guessed = summarize_initial_assessment(_assessment_results(question_ids, confidence=3))
    confident_errors = summarize_initial_assessment(
        _assessment_results(question_ids, correct=False, confidence=1)
    )

    for message in (good, partial, guessed, confident_errors):
        assert message.startswith("おう！お前の現在地はだいたい分かったぞ。")
        assert message.endswith("ここからが勝負だぜ＾＾")
        assert "弱点" not in message
        assert "苦手" not in message
        for internal_name in (
            "Knowledge Node", "Primary Ability", "KNOW", "MEASURE", "INTERPRET",
            "PREDICT", "PRESCRIBE", "DECIDE", "Level", "Safety", "tag_status",
        ):
            assert internal_name not in message
    assert "迷いながら" in guessed
    assert "確認" in partial
    assert "確認" in confident_errors or "確かめ" in confident_errors


def test_initial_feedback_supports_fifteen_question_completion():
    question_ids = [question["id"] for question in build_initial_assessment(15)]
    message = summarize_initial_assessment(_assessment_results(question_ids))
    assert "現在地" in message
    assert "ここからが勝負" in message


def test_assessment_questions_are_excluded_from_following_daily_session():
    for assessment_count in (10, 15):
        assessment = build_initial_assessment(assessment_count)
        assessment_ids = {question["id"] for question in assessment}
        daily = build_daily_session(
            [], question_count=30, exclude_ids=assessment_ids
        )
        assert assessment_ids.isdisjoint({question["id"] for question in daily})


def test_assessment_handoff_passes_one_time_question_exclusions(monkeypatch):
    user_id = "assessment-handoff-user"
    questions = [get_quiz_question(f"Q{number}") for number in range(1, 11)]
    captured = []
    bot_app.study_sessions[user_id] = {
        "status": "assessment_completed",
        "mode": "study",
        "all_questions": questions,
    }
    monkeypatch.setattr(
        bot_app,
        "start_and_reply_quiz",
        lambda *args, **kwargs: captured.append(kwargs) or True,
    )
    assert bot_app.process_study_flow_command("token", user_id, "勉強を始める")
    assert captured[0]["session_kind"] == "adaptive_daily"
    assert captured[0]["exclude_ids"] == [question["id"] for question in questions]


def test_daily_summary_uses_natural_labels_without_declaring_weakness():
    questions = [get_quiz_question(f"Q{number}") for number in range(1, 31)]
    results = [
        {
            "question_id": question["id"],
            "is_correct": index % 3 != 0,
            "confidence": 1 if index % 4 else 3,
        }
        for index, question in enumerate(questions, 1)
    ]
    message = summarize_daily_session(results)
    assert "今日の結果" in message
    assert "/ 30" in message
    assert "弱点" not in message
    for internal_name in (
        "Knowledge Node", "Primary Ability", "KNOW", "MEASURE", "INTERPRET",
        "PREDICT", "PRESCRIBE", "DECIDE", "Level", "Safety", "tag_status",
    ):
        assert internal_name not in message


def test_explanations_are_replied_synchronously_from_first_to_last_batch(monkeypatch):
    user_id = "adaptive-explanations-user"
    replies = []

    class LineApi:
        def reply_message(self, token, messages):
            replies.append(messages)

    questions = [get_quiz_question(f"Q{number}") for number in range(501, 531)]
    answers = {
        number: {"answer": "".join(question["accepted_answer_sets"][0]), "confidence": "1"}
        for number, question in enumerate(questions, 1)
    }
    bot_app.study_sessions[user_id] = {
        "status": "waiting_for_explanations",
        "mode": "study",
        "explanation_set": 0,
        "questions_per_set": 5,
        "question_count": 30,
        "all_questions": questions,
        "all_answers": answers,
        "quiz_result": bot_app.calculate_quiz_result(questions, answers),
    }
    monkeypatch.setattr(bot_app, "line_bot_api", LineApi())
    monkeypatch.setattr(
        bot_app, "push_to_line", lambda *_args: (_ for _ in ()).throw(
            AssertionError("解説本文をPush APIへ分離しない")
        )
    )

    assert bot_app.process_study_flow_command("token", user_id, "解答解説を見る")
    first_text = "\n".join(message.text for message in replies[-1])
    assert "【第1問】" in first_text and "解説：" in first_text
    assert bot_app.study_sessions[user_id]["status"] == "waiting_for_next_explanation"

    for expected_start in (6, 11, 16, 21, 26):
        assert bot_app.process_study_flow_command("token", user_id, "次の5問")
        text = "\n".join(message.text for message in replies[-1])
        assert f"【第{expected_start}問】" in text
    assert bot_app.study_sessions[user_id]["status"] == "quiz_completed"
    final_quick_replies = replies[-1][-1].quick_reply.items
    assert [item.action.text for item in final_quick_replies] == [
        "源さんに預ける", "ホームに戻る",
    ]
