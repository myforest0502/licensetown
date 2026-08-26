import os
from collections import Counter
from types import SimpleNamespace

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("CHANNEL_ACCESS_TOKEN", "test-token")
os.environ.setdefault("CHANNEL_SECRET", "test-secret")

import app as bot_app
import database
from learning_engine import (
    build_daily_session,
    build_initial_assessment,
    initial_assessment_needs_extension,
    summarize_initial_assessment,
)
from question_bank import get_question_tag, get_quiz_question, question_count


def test_all_formal_question_tags_load_and_match_ids():
    assert question_count() == 1564
    assert get_question_tag("Q1")["tag_status"] == "reviewed_sample"
    assert get_question_tag("Q200")["tag_status"] == "reviewed_sample"
    assert get_question_tag("Q201")["tag_status"] == "provisional_bulk"
    assert get_question_tag("Q1564")["tag_status"] == "provisional_bulk"


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

    class LineApi:
        def reply_message(self, token, messages):
            replies.append((token, messages))

    monkeypatch.setattr(bot_app, "line_bot_api", LineApi())
    monkeypatch.setattr(
        bot_app,
        "start_and_reply_quiz",
        lambda token, user_id, **kwargs: starts.append((user_id, kwargs)) or True,
    )

    def send(user_id, text):
        bot_app.handle_text_message(SimpleNamespace(
            message=SimpleNamespace(text=text),
            source=SimpleNamespace(user_id=user_id),
            reply_token="token",
        ))

    monkeypatch.setattr(bot_app, "is_initial_assessment_completed", lambda user_id: False)
    send("new-adaptive-user", "準備OK！")
    assert starts[-1][1]["session_kind"] == "initial_assessment"
    assert starts[-1][1]["question_count"] == 10

    monkeypatch.setattr(bot_app, "is_initial_assessment_completed", lambda user_id: True)
    send("existing-adaptive-user", "準備OK！")
    assert starts[-1][1]["session_kind"] == "adaptive_daily"


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
