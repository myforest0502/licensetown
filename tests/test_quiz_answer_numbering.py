"""小テストの表示番号・入力番号・保存番号の対応を検証する。"""

from __future__ import annotations

import ast
import json
import logging
import re
import unicodedata
import unittest
from pathlib import Path
from types import SimpleNamespace


APP_PATH = Path(__file__).resolve().parents[1] / "app.py"


def load_current_app_functions() -> SimpleNamespace:
    """外部SDKをimportせず、app.pyの対象関数本体をそのまま読み込む。"""
    module = ast.parse(
        APP_PATH.read_text(encoding="utf-8"),
        filename=str(APP_PATH),
    )
    target_names = {
        "format_quiz_messages",
        "load_question_master",
        "parse_quiz_answers",
        "calculate_quiz_result",
        "create_quiz_completion_summary",
        "format_quiz_question_numbers",
        "create_quiz_result_messages",
        "advance_quiz_explanations",
        "start_quiz",
        "start_next_quiz",
        "reply_new_user_welcome",
        "reply_gen_first_greeting",
        "is_complete_reset_command",
        "handle_text_message",
    }
    function_nodes = []

    for node in module.body:
        if isinstance(node, ast.FunctionDef) and node.name in target_names:
            node.decorator_list = []
            function_nodes.append(node)

    known_user_ids = set()
    line_replies = []
    namespace = {
        "re": re,
        "json": json,
        "Path": Path,
        "unicodedata": unicodedata,
        "logging": logging,
        "TextSendMessage": lambda text: SimpleNamespace(text=text),
        "line_bot_api": SimpleNamespace(
            reply_message=lambda token, messages: line_replies.append((token, messages))
        ),
        "threading": SimpleNamespace(Thread=None),
        "study_sessions": {},
        "explain_contexts": {},
        "user_states": {},
        "user_names": {},
        "user_modes": {},
        "reply_to_line": lambda *args, **kwargs: None,
        "reply_mode_select": lambda *args, **kwargs: None,
        "reply_study_continue_choice": lambda *args, **kwargs: None,
        "reply_study_ready_choice": lambda *args, **kwargs: None,
        "reply_quiz_score": lambda *args, **kwargs: None,
        "reply_explanation_choice": lambda *args, **kwargs: None,
        "reply_next_explanation_choice": lambda *args, **kwargs: None,
        "reply_new_user_welcome": lambda *args, **kwargs: None,
        "reply_gen_first_greeting": lambda *args, **kwargs: None,
        "reply_explain_method_choice": lambda *args, **kwargs: None,
        "reply_explain_answer_with_review": lambda *args, **kwargs: None,
        "create_contextual_explain_response": lambda *args, **kwargs: "解説回答",
        "push_to_line": lambda *args, **kwargs: None,
        "create_text_response": lambda *args, **kwargs: "unused",
        "prepare_and_send_quiz": lambda *args, **kwargs: None,
        "prepare_and_send_next_quiz": lambda *args, **kwargs: None,
        "select_random_questions": lambda count: make_questions()[:count],
        "QUIZ_QUESTION_COUNT": 30,
        "QUESTIONS_PER_SET": 5,
        "CONFIDENCE_LEVELS": {
            "1": "自信あり",
            "2": "少し迷った",
            "3": "あてずっぽう",
        },
        "known_user_ids": known_user_ids,
        "line_replies": line_replies,
        "user_profile_exists": lambda user_id: user_id in known_user_ids,
    }
    namespace["reset_user_profile"] = lambda user_id: (
        namespace["user_names"].pop(user_id, None),
        namespace["user_modes"].pop(user_id, None),
        known_user_ids.discard(user_id),
    )
    extracted_module = ast.Module(body=function_nodes, type_ignores=[])
    ast.fix_missing_locations(extracted_module)
    exec(compile(extracted_module, str(APP_PATH), "exec"), namespace)
    return SimpleNamespace(**namespace)


app = load_current_app_functions()


def make_quiz_result(total: int, correct_numbers: set[int], confidences=None) -> dict:
    confidences = confidences or {}
    details = [
        {
            "question_number": number,
            "question_id": 1000 + number,
            "selected_answer": "A" if number in correct_numbers else "B",
            "correct_answer": "A",
            "confidence": str(confidences.get(number, "1")),
            "is_correct": number in correct_numbers,
        }
        for number in range(1, total + 1)
    ]
    return {
        "score": len(correct_numbers),
        "total": total,
        "details": details,
    }


def make_questions() -> list[dict]:
    return [
        {
            "id": number,
            "question": f"テスト問題{number}",
            "choices": {key: f"選択肢{key}" for key in "ABCDE"},
            "answer": "A",
            "explanation": "テスト解説",
        }
        for number in range(1, 6)
    ]


def make_all_questions() -> list[dict]:
    return [
        {
            "id": 1000 + number,
            "question": f"テスト問題{number}",
            "choices": {key: f"選択肢{key}" for key in "ABCDE"},
            "answer": "ABCDE"[(number - 1) % 5],
            "explanation": f"テスト解説{number}",
        }
        for number in range(1, 31)
    ]


def make_text_event(user_id: str, text: str) -> SimpleNamespace:
    return SimpleNamespace(
        message=SimpleNamespace(text=text),
        source=SimpleNamespace(user_id=user_id),
        reply_token="test-reply-token",
    )


class QuizAnswerNumberingTest(unittest.TestCase):
    def setUp(self) -> None:
        app.study_sessions.clear()
        app.user_states.clear()
        app.user_names.clear()
        app.user_modes.clear()
        app.explain_contexts.clear()

    def prepare_session(
        self,
        user_id: str,
        current_set: int,
        all_answers: dict | None = None,
    ) -> None:
        app.user_names[user_id] = "テストユーザー"
        app.user_modes[user_id] = "study"
        app.study_sessions[user_id] = {
            "status": "waiting_for_answers",
            "current_set": current_set,
            "total_sets": 6,
            "question_count": 30,
            "questions_per_set": 5,
            "questions": make_questions(),
            "all_questions": make_questions(),
            "all_answers": all_answers or {},
        }

    def test_displayed_numbers_and_examples_match_each_set(self) -> None:
        questions = make_questions()

        for current_set in range(1, 7):
            with self.subTest(current_set=current_set):
                start_number = ((current_set - 1) * 5) + 1
                message = app.format_quiz_messages(
                    questions,
                    start_number=start_number,
                )[0]

                for number in range(start_number, start_number + 5):
                    self.assertIn(f"【第{number}問】", message)
                self.assertIn(f"{start_number}:A1", message)
                self.assertIn(f"{start_number + 1}:B2", message)
                self.assertIn(f"{start_number + 2}:C3", message)
                self.assertIn(f"{start_number + 3}:D1", message)
                self.assertIn(f"{start_number + 4}:E2", message)
                self.assertLess(
                    message.index("【回答方法】"),
                    message.index(f"【第{start_number}問】"),
                )
                self.assertEqual(1, message.count("【回答方法】"))

    def test_parser_accepts_common_input_variations_in_all_sets(self) -> None:
        answer_pairs = ["A1", "B2", "C3", "D1", "E2"]
        fullwidth_map = str.maketrans(
            "0123456789:ABCDE",
            "０１２３４５６７８９：ＡＢＣＤＥ",
        )

        for current_set in range(1, 7):
            start_number = ((current_set - 1) * 5) + 1
            expected_numbers = list(range(start_number, start_number + 5))
            explicit = [
                f"{number}:{answer}"
                for number, answer in zip(expected_numbers, answer_pairs)
            ]
            fullwidth = [value.translate(fullwidth_map) for value in explicit]
            valid_inputs = [
                "\n".join(explicit),
                " ".join(value.lower() for value in explicit),
                ",".join(explicit),
                "\t".join(explicit),
                "  ".join(value.replace(":", " : ") for value in explicit),
                "\n".join(value.replace("Ａ", " Ａ ").replace("１", " １ ")
                          for value in fullwidth),
                "\n".join(
                    f"{number} ： {answer[0]} {answer[1]}".translate(fullwidth_map)
                    for number, answer in zip(expected_numbers, answer_pairs)
                ),
                " ".join(value.replace(":", "") for value in explicit),
                "A1B2C3D1E2",
                "a1 b2 c3 d1 e2",
                "A 1   B 2  C 3  D 1  E 2",
            ]

            for user_message in valid_inputs:
                with self.subTest(
                    current_set=current_set,
                    user_message=user_message,
                ):
                    parsed = app.parse_quiz_answers(
                        user_message,
                        expected_numbers=expected_numbers,
                    )
                    self.assertEqual(expected_numbers, list(parsed))
                    self.assertEqual(
                        answer_pairs,
                        [
                            data["answer"] + data["confidence"]
                            for data in parsed.values()
                        ],
                    )

    def test_parser_rejects_invalid_or_incomplete_inputs(self) -> None:
        expected_numbers = list(range(6, 11))
        invalid_inputs = [
            "6:A4 7:B2 8:C3 9:D1 10:E2",
            "6:F1 7:B2 8:C3 9:D1 10:E2",
            "A1 B2 C3 D1",
            "A1 B2 C3 D1 E2 A1",
            "6:A1 6:B2 8:C3 9:D1 10:E2",
            "1:A1 2:B2 3:C3 4:D1 5:E2",
            "6:A1 7:B2 8:C3 9:D1",
            "6:A1 7:B2 8:C3 9:D1 10:E2 不明",
        ]

        for user_message in invalid_inputs:
            with self.subTest(user_message=user_message):
                self.assertEqual(
                    {},
                    app.parse_quiz_answers(
                        user_message,
                        expected_numbers=expected_numbers,
                    ),
                )

    def test_invalid_variations_do_not_modify_existing_answers(self) -> None:
        user_id = "invalid-input-test-user"
        original_answers = {
            number: {"answer": "A", "confidence": "1"}
            for number in range(1, 6)
        }
        invalid_inputs = [
            "6:A4 7:B2 8:C3 9:D1 10:E2",
            "6:F1 7:B2 8:C3 9:D1 10:E2",
            "A1 B2 C3 D1",
            "A1 B2 C3 D1 E2 A1",
            "6:A1 6:B2 8:C3 9:D1 10:E2",
            "1:A1 2:B2 3:C3 4:D1 5:E2",
        ]

        for user_message in invalid_inputs:
            with self.subTest(user_message=user_message):
                self.prepare_session(user_id, 2, {
                    number: dict(data)
                    for number, data in original_answers.items()
                })

                app.handle_text_message(make_text_event(user_id, user_message))

                session = app.study_sessions[user_id]
                self.assertEqual(original_answers, session["all_answers"])
                self.assertEqual("waiting_for_answers", session["status"])

    def test_global_numbers_are_saved_with_answer_and_confidence(self) -> None:
        user_id = "numbering-test-user"

        for current_set in range(1, 6):
            with self.subTest(current_set=current_set):
                start_number = ((current_set - 1) * 5) + 1
                expected_numbers = list(range(start_number, start_number + 5))
                answer_text = "\n".join(
                    f"{number}:A1" for number in expected_numbers
                )
                self.prepare_session(user_id, current_set)

                app.handle_text_message(make_text_event(user_id, answer_text))

                session = app.study_sessions[user_id]
                self.assertEqual(expected_numbers, sorted(session["all_answers"]))
                self.assertTrue(
                    all(
                        answer == {"answer": "A", "confidence": "1"}
                        for answer in session["all_answers"].values()
                    )
                )
                self.assertEqual("waiting_for_continue", session["status"])

    def test_final_set_completes_and_scores_all_thirty_questions(self) -> None:
        user_id = "completion-test-user"
        questions = make_all_questions()
        all_answers = {
            number: {
                "answer": questions[number - 1]["answer"],
                "confidence": str(((number - 1) % 3) + 1),
            }
            for number in range(1, 26)
        }
        final_answers = {
            26: {"answer": questions[25]["answer"], "confidence": "2"},
            27: {"answer": "E", "confidence": "3"},
            28: {"answer": questions[27]["answer"], "confidence": "1"},
            29: {"answer": "A", "confidence": "2"},
            30: {"answer": questions[29]["answer"], "confidence": "3"},
        }
        # 第27問の正答はB、第29問の正答はDなので、この2問だけ不正解。
        self.prepare_session(user_id, 6, all_answers)
        session = app.study_sessions[user_id]
        session["questions"] = questions[25:]
        session["all_questions"] = questions
        reply_messages = []
        continue_choice_calls = []
        function_globals = app.handle_text_message.__globals__
        original_reply = function_globals["reply_to_line"]
        original_score_reply = function_globals["reply_quiz_score"]
        original_continue = function_globals["reply_study_continue_choice"]
        function_globals["reply_to_line"] = (
            lambda _token, message: reply_messages.append(message)
        )
        function_globals["reply_quiz_score"] = (
            lambda _token, result: reply_messages.append(
                f"【結果】{result['score']} / {result['total']}問正解"
            )
        )
        function_globals["reply_study_continue_choice"] = (
            lambda token: continue_choice_calls.append(token)
        )
        answer_text = "\n".join(
            f"{number}:{data['answer']}{data['confidence']}"
            for number, data in final_answers.items()
        )

        try:
            app.handle_text_message(make_text_event(user_id, answer_text))
        finally:
            function_globals["reply_to_line"] = original_reply
            function_globals["reply_quiz_score"] = original_score_reply
            function_globals["reply_study_continue_choice"] = original_continue

        result = session["quiz_result"]
        self.assertEqual("waiting_for_explanations", session["status"])
        self.assertEqual([], continue_choice_calls)
        self.assertEqual(30, result["total"])
        self.assertEqual(28, result["score"])
        self.assertEqual(30, len(result["details"]))
        self.assertEqual(list(range(1, 31)), [
            detail["question_number"] for detail in result["details"]
        ])
        self.assertEqual(
            [question["id"] for question in questions],
            [detail["question_id"] for detail in result["details"]],
        )
        self.assertEqual(
            [session["all_answers"][number]["confidence"] for number in range(1, 31)],
            [detail["confidence"] for detail in result["details"]],
        )
        self.assertIn("【結果】28 / 30問正解", reply_messages[0])

        for explanation_set in range(1, 7):
            messages = app.advance_quiz_explanations(session)
            joined = "\n".join(messages)
            start = ((explanation_set - 1) * 5) + 1
            self.assertIn(f"【第{start}問】", joined)
            self.assertIn(f"【第{start + 4}問】", joined)

        self.assertEqual("quiz_completed", session["status"])

        with self.assertRaisesRegex(ValueError, "30問すべて出題済み"):
            app.start_next_quiz(user_id)

    def test_each_set_rejects_numbers_outside_its_range(self) -> None:
        user_id = "range-validation-test-user"

        for current_set in range(1, 7):
            with self.subTest(current_set=current_set):
                invalid_start = 6 if current_set == 1 else 1
                invalid_text = "\n".join(
                    f"{number}:A1"
                    for number in range(invalid_start, invalid_start + 5)
                )
                self.prepare_session(user_id, current_set)

                app.handle_text_message(make_text_event(user_id, invalid_text))

                session = app.study_sessions[user_id]
                self.assertEqual({}, session["all_answers"])
                self.assertEqual("waiting_for_answers", session["status"])

    def test_second_set_does_not_overwrite_first_set_answers(self) -> None:
        user_id = "overwrite-test-user"
        original_answers = {
            number: {"answer": "B", "confidence": "2"}
            for number in range(1, 6)
        }
        self.prepare_session(user_id, 2, original_answers.copy())
        reply_messages = []
        function_globals = app.handle_text_message.__globals__
        original_reply = function_globals["reply_to_line"]
        function_globals["reply_to_line"] = (
            lambda _token, message: reply_messages.append(message)
        )

        try:
            app.handle_text_message(
                make_text_event(
                    user_id,
                    "1:A1\n2:B2\n3:C3\n4:D2\n5:E1",
                )
            )
        finally:
            function_globals["reply_to_line"] = original_reply

        session = app.study_sessions[user_id]
        self.assertEqual(original_answers, session["all_answers"])
        self.assertEqual("waiting_for_answers", session["status"])
        self.assertIn("第6問から第10問まで", reply_messages[0])
        self.assertIn("6:A1", reply_messages[0])
        self.assertIn("10:E1", reply_messages[0])

    def test_restart_command_completely_resets_every_session_state(self) -> None:
        user_id = "reset-test-user"
        reset_cases = [
            ("waiting_for_answers", "study"),
            ("waiting_for_continue", "study"),
            ("preparing_next", "study"),
            ("quiz_completed", "study"),
            (None, "study"),
            (None, "chat"),
            (None, "explain"),
            (None, "normal"),
        ]
        function_globals = app.handle_text_message.__globals__
        original_reply = function_globals["reply_to_line"]
        original_create_text_response = function_globals["create_text_response"]
        original_continue = function_globals["reply_study_continue_choice"]

        try:
            for status, mode in reset_cases:
                with self.subTest(status=status, mode=mode):
                    app.user_states[user_id] = "waiting_name"
                    app.user_names[user_id] = "テストユーザー"
                    app.user_modes[user_id] = mode
                    app.known_user_ids.add(user_id)

                    if status is None:
                        app.study_sessions.pop(user_id, None)
                    else:
                        app.study_sessions[user_id] = {
                            "status": status,
                            "current_set": 6,
                            "total_sets": 6,
                            "questions": make_questions(),
                            "all_questions": make_all_questions(),
                            "all_answers": {
                                1: {"answer": "A", "confidence": "1"}
                            },
                            "quiz_result": {"score": 1, "total": 30},
                        }

                    reply_messages = []
                    function_globals["reply_to_line"] = (
                        lambda _token, message: reply_messages.append(message)
                    )
                    function_globals["create_text_response"] = (
                        lambda *args, **kwargs: self.fail(
                            "リセット命令が通常のAI会話へ流れました。"
                        )
                    )
                    function_globals["reply_study_continue_choice"] = (
                        lambda *args, **kwargs: self.fail(
                            "リセット後に以前の学習状態が処理されました。"
                        )
                    )

                    app.handle_text_message(
                        make_text_event(user_id, "ふりだしにもどる")
                    )

                    self.assertEqual("waiting_gen_intro", app.user_states[user_id])
                    self.assertNotIn(user_id, app.study_sessions)
                    self.assertNotIn(user_id, app.user_modes)
                    self.assertNotIn(user_id, app.user_names)
                    self.assertNotIn(user_id, app.known_user_ids)
                    self.assertEqual(1, len(reply_messages))
                    self.assertIn("ようこそ、ライセンスタウンへ！", reply_messages[0])
        finally:
            function_globals["reply_to_line"] = original_reply
            function_globals["create_text_response"] = original_create_text_response
            function_globals["reply_study_continue_choice"] = original_continue

    def test_restart_command_requires_exact_match_after_trimming(self) -> None:
        rejected = [
            "ふ",
            "ふり",
            "ふりだし",
            "ふりだしに",
            "ふりだしにもど",
            "ふりだしにもどるよ",
            "ふりだしにもどりたい",
        ]
        for message in rejected:
            with self.subTest(message=message):
                self.assertFalse(app.is_complete_reset_command(message))

        self.assertTrue(app.is_complete_reset_command("ふりだしにもどる"))
        self.assertTrue(app.is_complete_reset_command(" ふりだしにもどる "))

        function_globals = app.handle_text_message.__globals__
        original_reset = function_globals["reset_user_profile"]
        original_reply = function_globals["reply_to_line"]
        original_create_text_response = function_globals["create_text_response"]
        reset_calls = []
        function_globals["reset_user_profile"] = lambda user_id: reset_calls.append(user_id)
        function_globals["reply_to_line"] = lambda *args: None
        function_globals["create_text_response"] = lambda *args, **kwargs: "通常応答"

        try:
            for index, message in enumerate(rejected):
                user_id = f"non-reset-{index}"
                app.user_names[user_id] = "既存ユーザー"
                app.handle_text_message(make_text_event(user_id, message))
                self.assertEqual("既存ユーザー", app.user_names[user_id])

            for index, message in enumerate((
                "ふりだしにもどる",
                " ふりだしにもどる ",
            )):
                user_id = f"exact-reset-{index}"
                app.user_names[user_id] = "初期化対象"
                app.handle_text_message(make_text_event(user_id, message))
        finally:
            function_globals["reset_user_profile"] = original_reset
            function_globals["reply_to_line"] = original_reply
            function_globals["create_text_response"] = original_create_text_response

        self.assertEqual(["exact-reset-0", "exact-reset-1"], reset_calls)

    def test_restart_command_reports_database_failure_without_ai_fallback(self) -> None:
        user_id = "reset-failure-test-user"
        app.user_states[user_id] = "waiting_name"
        app.user_names[user_id] = "テストユーザー"
        app.user_modes[user_id] = "study"
        app.study_sessions[user_id] = {
            "status": "waiting_for_continue",
            "current_set": 2,
        }
        reply_messages = []
        function_globals = app.handle_text_message.__globals__
        original_reply = function_globals["reply_to_line"]
        original_reset = function_globals["reset_user_profile"]
        original_create_text_response = function_globals["create_text_response"]
        function_globals["reply_to_line"] = (
            lambda _token, message: reply_messages.append(message)
        )
        function_globals["reset_user_profile"] = (
            lambda _user_id: (_ for _ in ()).throw(RuntimeError("DB unavailable"))
        )
        function_globals["create_text_response"] = (
            lambda *args, **kwargs: self.fail(
                "DB障害時に通常のAI会話へ流れました。"
            )
        )

        try:
            app.handle_text_message(
                make_text_event(user_id, "ふりだしにもどる")
            )
        finally:
            function_globals["reply_to_line"] = original_reply
            function_globals["reset_user_profile"] = original_reset
            function_globals["create_text_response"] = original_create_text_response

        self.assertNotIn(user_id, app.user_states)
        self.assertNotIn(user_id, app.study_sessions)
        self.assertEqual("テストユーザー", app.user_names[user_id])
        self.assertEqual("study", app.user_modes[user_id])
        self.assertEqual(1, len(reply_messages))
        self.assertNotIn("全部ふりだしに戻した", reply_messages[0])
        self.assertIn("最後まで確認できなかった", reply_messages[0])


class NewUserWelcomeTest(unittest.TestCase):
    def setUp(self) -> None:
        app.study_sessions.clear()
        app.user_states.clear()
        app.user_names.clear()
        app.user_modes.clear()
        app.explain_contexts.clear()
        app.known_user_ids.clear()
        app.line_replies.clear()

    def test_welcome_reply_contains_only_the_updated_welcome_message(self) -> None:
        function_globals = app.reply_new_user_welcome.__globals__
        original_reply = function_globals["reply_to_line"]
        replies = []
        function_globals["reply_to_line"] = (
            lambda token, message: replies.append((token, message))
        )

        try:
            app.reply_new_user_welcome("reply-token")
        finally:
            function_globals["reply_to_line"] = original_reply

        self.assertEqual(1, len(replies))
        token, message = replies[0]
        self.assertEqual("reply-token", token)
        self.assertTrue(message.startswith("ようこそ、ライセンスタウンへ！"))
        self.assertNotIn("おぉｗよくきたな！", message)
        self.assertLess(
            message.index("源さんにバトンタッチ"),
            message.index("何か源さんに話しかけて"),
        )
        self.assertIn(
            "何か源さんに話しかけてみてくださいねｗ\n\nそれではいってらっしゃい＾＾",
            message,
        )

    def test_new_user_sees_welcome_then_existing_greeting_and_can_register_name(self) -> None:
        user_id = "brand-new-user"
        function_globals = app.handle_text_message.__globals__
        original_welcome = function_globals["reply_new_user_welcome"]
        original_gen = function_globals["reply_gen_first_greeting"]
        original_mode_select = function_globals["reply_mode_select"]
        events = []
        function_globals["reply_new_user_welcome"] = (
            lambda _token: events.append("welcome")
        )
        function_globals["reply_gen_first_greeting"] = lambda _token: events.append("gen")
        function_globals["reply_mode_select"] = (
            lambda _token, intro_text=None: events.append(("registered", intro_text))
        )

        try:
            app.handle_text_message(make_text_event(user_id, "はじめまして"))
            self.assertEqual("waiting_gen_intro", app.user_states[user_id])
            app.handle_text_message(make_text_event(user_id, "勉強する"))
            self.assertEqual("waiting_name", app.user_states[user_id])
            self.assertNotIn(user_id, app.user_names)
            self.assertNotIn(user_id, app.user_modes)
            app.handle_text_message(make_text_event(user_id, "太郎"))
        finally:
            function_globals["reply_new_user_welcome"] = original_welcome
            function_globals["reply_gen_first_greeting"] = original_gen
            function_globals["reply_mode_select"] = original_mode_select

        self.assertEqual("太郎", app.user_names[user_id])
        self.assertNotIn(user_id, app.user_states)
        self.assertEqual(["welcome", "gen"], events[:2])
        self.assertEqual("registered", events[2][0])
        self.assertIn("太郎", events[2][1])

    def test_registered_user_does_not_see_welcome(self) -> None:
        user_id = "registered-user"
        app.user_names[user_id] = "花子"
        app.known_user_ids.add(user_id)
        function_globals = app.handle_text_message.__globals__
        original_welcome = function_globals["reply_new_user_welcome"]
        welcome_calls = []
        function_globals["reply_new_user_welcome"] = lambda *args: welcome_calls.append(args)

        try:
            app.handle_text_message(make_text_event(user_id, "今日は休む"))
        finally:
            function_globals["reply_new_user_welcome"] = original_welcome

        self.assertEqual([], welcome_calls)

    def test_reset_user_returns_to_complete_first_use_flow(self) -> None:
        user_id = "reset-existing-user"
        app.user_names[user_id] = "次郎"
        app.user_modes[user_id] = "study"
        app.known_user_ids.add(user_id)
        function_globals = app.handle_text_message.__globals__
        original_welcome = function_globals["reply_new_user_welcome"]
        original_gen = function_globals["reply_gen_first_greeting"]
        original_reply = function_globals["reply_to_line"]
        original_mode_select = function_globals["reply_mode_select"]
        welcome_calls = []
        gen_calls = []
        replies = []
        registered = []
        function_globals["reply_new_user_welcome"] = lambda *args: welcome_calls.append(args)
        function_globals["reply_gen_first_greeting"] = lambda *args: gen_calls.append(args)
        function_globals["reply_to_line"] = lambda _token, message: replies.append(message)
        function_globals["reply_mode_select"] = (
            lambda _token, intro_text=None: registered.append(intro_text)
        )

        try:
            app.handle_text_message(make_text_event(user_id, "ふりだしにもどる"))
            app.handle_text_message(make_text_event(user_id, "もう一度はじめる"))
            app.handle_text_message(make_text_event(user_id, "再登録ユーザー"))
        finally:
            function_globals["reply_new_user_welcome"] = original_welcome
            function_globals["reply_gen_first_greeting"] = original_gen
            function_globals["reply_to_line"] = original_reply
            function_globals["reply_mode_select"] = original_mode_select

        self.assertEqual(1, len(welcome_calls))
        self.assertEqual(1, len(gen_calls))
        self.assertNotIn(user_id, app.known_user_ids)
        self.assertEqual(0, len(replies))
        self.assertEqual("再登録ユーザー", app.user_names[user_id])
        self.assertNotIn(user_id, app.user_states)
        self.assertIn("再登録ユーザー", registered[0])


class QuizCompletionSummaryTest(unittest.TestCase):
    def test_all_correct_shows_100_percent_and_only_uncertain_review_items(self) -> None:
        result = make_quiz_result(
            30,
            set(range(1, 31)),
            {5: "2", 11: "3"},
        )

        summary = app.create_quiz_completion_summary(result)

        self.assertIn("正解：30 / 30問", summary)
        self.assertIn("正答率：100％", summary)
        self.assertIn("今回は間違えた問題はなかったぞ！", summary)
        self.assertIn("少し迷って正解：第5問", summary)
        self.assertIn("あてずっぽうで正解：第11問", summary)
        self.assertNotIn("自信ありで間違えた", summary)

    def test_partial_result_groups_priority_review_by_confidence(self) -> None:
        incorrect = {4, 8, 12, 17, 22, 29}
        result = make_quiz_result(
            30,
            set(range(1, 31)) - incorrect,
            {8: "1", 17: "1", 4: "2", 12: "3", 15: "3"},
        )

        summary = app.create_quiz_completion_summary(result)

        self.assertIn("正解：24 / 30問", summary)
        self.assertIn("正答率：80.0％", summary)
        self.assertIn(
            "第4問、第8問、第12問、第17問、第22問、第29問",
            summary,
        )
        self.assertIn("自信ありで間違えた：第8問、第17問、第22問、第29問", summary)
        self.assertIn("少し迷って間違えた：第4問", summary)
        self.assertIn("あてずっぽうで間違えた：第12問", summary)
        self.assertIn("あてずっぽうで正解：第15問", summary)
        self.assertIn("覚え違いの可能性", summary)

    def test_under_70_percent_prioritizes_understanding_explanations(self) -> None:
        result = make_quiz_result(30, set(range(1, 21)))

        summary = app.create_quiz_completion_summary(result)

        self.assertIn("正答率：66.7％", summary)
        self.assertIn("解説を理解することを優先", summary)
        self.assertIn("復習してから、次のテストへ進む", summary)

    def test_summary_uses_configured_total_for_30_40_and_50_questions(self) -> None:
        for total in (30, 40, 50):
            with self.subTest(total=total):
                result = make_quiz_result(total, set(range(1, total + 1)))
                summary = app.create_quiz_completion_summary(result)
                self.assertIn(f"{total}問、本当におつかれさん！", summary)
                self.assertIn(f"正解：{total} / {total}問", summary)
                self.assertIn(f"今日の{total}問はこれで終了！", summary)

    def test_final_explanation_completes_quiz_and_requests_summary_once(self) -> None:
        user_id = "summary-once-user"
        questions = make_all_questions()
        answers = {
            number: {"answer": question["answer"], "confidence": "1"}
            for number, question in enumerate(questions, start=1)
        }
        result = app.calculate_quiz_result(questions, answers)
        app.study_sessions[user_id] = {
            "status": "waiting_for_next_explanation",
            "question_count": 30,
            "questions_per_set": 5,
            "all_questions": questions,
            "all_answers": answers,
            "quiz_result": result,
            "explanation_set": 5,
        }

        function_globals = app.handle_text_message.__globals__
        original_push = function_globals["push_to_line"]
        original_completed = function_globals["reply_explanation_choice"]
        original_reply = function_globals["reply_to_line"]
        pushed = []
        completion_calls = []
        function_globals["push_to_line"] = lambda *args: pushed.append(args)
        function_globals["reply_explanation_choice"] = (
            lambda *args, **kwargs: completion_calls.append((args, kwargs))
        )
        function_globals["reply_to_line"] = lambda *args: None

        try:
            app.handle_text_message(make_text_event(user_id, "次の5問"))
            app.handle_text_message(make_text_event(user_id, "次の5問"))
        finally:
            function_globals["push_to_line"] = original_push
            function_globals["reply_explanation_choice"] = original_completed
            function_globals["reply_to_line"] = original_reply

        self.assertEqual("quiz_completed", app.study_sessions[user_id]["status"])
        self.assertTrue(pushed)
        self.assertEqual(1, len(completion_calls))
        self.assertTrue(completion_calls[0][1]["completed"])
        self.assertIs(result, completion_calls[0][1]["quiz_result"])


class ConfigurableQuizTest(unittest.TestCase):
    def setUp(self) -> None:
        app.study_sessions.clear()
        app.explain_contexts.clear()

    def test_30_40_50_question_settings_select_once_without_duplicates(self) -> None:
        function_globals = app.start_quiz.__globals__
        original_count = function_globals["QUIZ_QUESTION_COUNT"]
        original_selector = function_globals["select_random_questions"]
        pool = [
            {
                "id": number,
                "question": f"問題{number}",
                "choices": {key: f"選択肢{key}" for key in "ABCDE"},
                "answer": "A",
                "explanation": f"解説{number}",
            }
            for number in range(1, 311)
        ]
        calls = []

        try:
            function_globals["select_random_questions"] = (
                lambda count: calls.append(count) or pool[:count]
            )

            for question_count in (30, 40, 50):
                with self.subTest(question_count=question_count):
                    calls.clear()
                    function_globals["QUIZ_QUESTION_COUNT"] = question_count
                    app.start_quiz(f"user-{question_count}")
                    session = app.study_sessions[f"user-{question_count}"]

                    self.assertEqual([question_count], calls)
                    self.assertEqual(question_count, len(session["all_questions"]))
                    self.assertEqual(
                        question_count,
                        len({question["id"] for question in session["all_questions"]}),
                    )
                    self.assertEqual(question_count // 5, session["total_sets"])

                    while session["current_set"] < session["total_sets"]:
                        app.start_next_quiz(f"user-{question_count}")
                        start = (session["current_set"] - 1) * 5
                        self.assertEqual(
                            session["all_questions"][start:start + 5],
                            session["questions"],
                        )
        finally:
            function_globals["QUIZ_QUESTION_COUNT"] = original_count
            function_globals["select_random_questions"] = original_selector

    def test_runtime_loader_supports_current_utf16_and_candidate_utf8(self) -> None:
        app_dir = APP_PATH.parent
        project_root = app_dir.parents[1]
        current_questions = app.load_question_master(app_dir / "questions_master.json")
        candidate_path = project_root / "data" / "questions_master_candidate_v2.json"
        if not candidate_path.exists():
            candidate_path = (
                project_root / "data" / "questions_master_candidate_v2_q1_q100.json"
            )
        candidate_questions = app.load_question_master(candidate_path)

        self.assertEqual(310, len(current_questions))
        self.assertIn(len(candidate_questions), {100, 310})

    def test_explanations_keep_question_answer_and_confidence_alignment(self) -> None:
        questions = make_all_questions()
        answers = {
            number: {
                "answer": questions[number - 1]["answer"],
                "confidence": str(((number - 1) % 3) + 1),
            }
            for number in range(1, 31)
        }
        session = {
            "status": "waiting_for_explanations",
            "question_count": 30,
            "questions_per_set": 5,
            "all_questions": questions,
            "all_answers": answers,
            "explanation_set": 0,
        }

        for explanation_set in range(1, 7):
            messages = app.advance_quiz_explanations(session)
            text = "\n".join(messages)
            start = ((explanation_set - 1) * 5) + 1

            for number in range(start, start + 5):
                question = questions[number - 1]
                self.assertIn(f"【第{number}問】○", text)
                self.assertIn(f"正解：{question['answer']}", text)
                self.assertIn(f"解説：{question['explanation']}", text)

        self.assertEqual("quiz_completed", session["status"])
        with self.assertRaisesRegex(ValueError, "表示できる状態"):
            app.advance_quiz_explanations(session)

    def test_new_quiz_cannot_start_while_explanations_are_open(self) -> None:
        user_id = "explanation-lock-user"
        app.user_names[user_id] = "テストユーザー"
        app.user_modes[user_id] = "study"
        app.study_sessions[user_id] = {
            "status": "waiting_for_next_explanation",
            "question_count": 30,
            "questions_per_set": 5,
            "all_questions": make_all_questions(),
            "all_answers": {},
            "explanation_set": 1,
        }
        function_globals = app.handle_text_message.__globals__
        original_reply = function_globals["reply_to_line"]
        original_prepare = function_globals["prepare_and_send_quiz"]
        replies = []
        starts = []
        function_globals["reply_to_line"] = (
            lambda _token, message: replies.append(message)
        )
        function_globals["prepare_and_send_quiz"] = (
            lambda _user_id: starts.append(_user_id)
        )

        try:
            app.handle_text_message(make_text_event(user_id, "問題出して"))
        finally:
            function_globals["reply_to_line"] = original_reply
            function_globals["prepare_and_send_quiz"] = original_prepare

        self.assertEqual([], starts)
        self.assertEqual("waiting_for_next_explanation", app.study_sessions[user_id]["status"])
        self.assertIn("次の5問", replies[0])

    def test_question_and_chat_mode_selection_still_work(self) -> None:
        function_globals = app.handle_text_message.__globals__
        original_reply = function_globals["reply_to_line"]
        original_study_ready = function_globals["reply_study_ready_choice"]
        original_explain_choice = function_globals["reply_explain_method_choice"]
        replies = []
        study_replies = []
        explain_choices = []
        function_globals["reply_to_line"] = (
            lambda _token, message: replies.append(message)
        )
        function_globals["reply_study_ready_choice"] = (
            lambda token: study_replies.append(token)
        )
        function_globals["reply_explain_method_choice"] = (
            lambda token: explain_choices.append(token)
        )

        labels = [
            "📖 勉強する！",
            "💡 教えて源さん",
            "😎 相談したい",
            "🔥 熱血モード",
        ]
        source = APP_PATH.read_text(encoding="utf-8")
        module = ast.parse(source)
        mode_select_node = next(
            node
            for node in module.body
            if isinstance(node, ast.FunctionDef) and node.name == "reply_mode_select"
        )
        mode_select_source = ast.get_source_segment(source, mode_select_node)

        for user_id in ("study-user", "chat-user", "explain-user", "heat-user"):
            app.user_names[user_id] = "登録済みユーザー"

        try:
            app.handle_text_message(make_text_event("study-user", "勉強する"))
            app.handle_text_message(make_text_event("chat-user", "相談したい"))
            app.handle_text_message(make_text_event("explain-user", "教えて源さん"))
            app.handle_text_message(make_text_event("heat-user", "熱血モード"))
        finally:
            function_globals["reply_to_line"] = original_reply
            function_globals["reply_study_ready_choice"] = original_study_ready
            function_globals["reply_explain_method_choice"] = original_explain_choice

        self.assertEqual(4, mode_select_source.count("QuickReplyButton("))
        self.assertIn(
            'text="今日は何する？＾＾\\n下のボタンを押して教えてくれな＾＾"',
            mode_select_source,
        )
        self.assertEqual(
            sorted(mode_select_source.index(label) for label in labels),
            [mode_select_source.index(label) for label in labels],
        )
        self.assertEqual("study", app.user_modes["study-user"])
        self.assertEqual("chat", app.user_modes["chat-user"])
        self.assertEqual("explain", app.user_modes["explain-user"])
        self.assertNotIn("heat-user", app.user_modes)
        self.assertEqual(1, len(study_replies))
        self.assertEqual(1, len(explain_choices))
        self.assertEqual(2, len(replies))
        self.assertIn("熱血モードはこれから準備するぞ🔥", replies[-1])

    def test_teach_gen_entry_supports_direct_question_and_attachment_choices(self) -> None:
        function_globals = app.handle_text_message.__globals__
        original_choice = function_globals["reply_explain_method_choice"]
        original_reply = function_globals["reply_to_line"]
        original_contextual = function_globals["create_contextual_explain_response"]
        original_answer_review = function_globals["reply_explain_answer_with_review"]
        original_mode_select = function_globals["reply_mode_select"]
        choice_calls = []
        replies = []
        questions = []
        reviewed_answers = []
        mode_selects = []
        function_globals["reply_explain_method_choice"] = (
            lambda token: choice_calls.append(token)
        )
        function_globals["reply_to_line"] = (
            lambda _token, message: replies.append(message)
        )
        function_globals["create_contextual_explain_response"] = (
            lambda user_id, message: questions.append((user_id, message))
            or f"質問への回答{len(questions)}"
        )
        function_globals["reply_explain_answer_with_review"] = (
            lambda _token, answer: reviewed_answers.append(answer)
        )
        function_globals["reply_mode_select"] = (
            lambda _token, intro_text=None: mode_selects.append(intro_text)
        )

        direct_user = "direct-explain-user"
        attachment_user = "attachment-explain-user"
        app.user_names[direct_user] = "直接質問者"
        app.user_names[attachment_user] = "資料質問者"

        try:
            app.handle_text_message(make_text_event(direct_user, "教えて源さん"))
            app.handle_text_message(make_text_event(direct_user, "源さんに直接質問する"))
            app.handle_text_message(make_text_event(direct_user, "反射って何？"))
            first_review_state = app.user_states[direct_user]
            app.handle_text_message(make_text_event(direct_user, "まだ質問がある！"))
            followup_state = app.user_states[direct_user]
            app.handle_text_message(make_text_event(direct_user, "具体例も教えて"))
            second_review_state = app.user_states[direct_user]
            app.handle_text_message(make_text_event(direct_user, "わかった！"))

            app.handle_text_message(make_text_event(attachment_user, "教えて源さん"))
            app.handle_text_message(make_text_event(attachment_user, "文書・写真等を見せる"))
            attachment_mode_before_switch = app.user_modes[attachment_user]
            attachment_state_before_switch = app.user_states[attachment_user]
            attachment_prompt = replies[-1]
            app.handle_text_message(make_text_event(attachment_user, "相談したい"))
        finally:
            function_globals["reply_explain_method_choice"] = original_choice
            function_globals["reply_to_line"] = original_reply
            function_globals["create_contextual_explain_response"] = original_contextual
            function_globals["reply_explain_answer_with_review"] = original_answer_review
            function_globals["reply_mode_select"] = original_mode_select

        self.assertEqual(2, len(choice_calls))
        self.assertEqual("normal", app.user_modes[direct_user])
        self.assertNotIn(direct_user, app.user_states)
        self.assertIn("そのまま書いて送ってくれればいいぞ！", replies[0])
        self.assertEqual("explain_review", first_review_state)
        self.assertEqual("explain_followup", followup_state)
        self.assertEqual("explain_review", second_review_state)
        self.assertEqual(
            [
                (direct_user, "反射って何？"),
                (direct_user, "具体例も教えて"),
            ],
            questions,
        )
        self.assertEqual(["質問への回答1", "質問への回答2"], reviewed_answers)
        self.assertIn("どこがまだ分からないか、書いて送ってくれ！", replies[1])
        self.assertIn("おう、それならよかった＾＾", mode_selects[0])
        self.assertEqual("explain", attachment_mode_before_switch)
        self.assertEqual("explain_attachment", attachment_state_before_switch)
        self.assertIn("Word、PDF、写真なんかを送ってくれれば", attachment_prompt)
        self.assertEqual("chat", app.user_modes[attachment_user])
        self.assertNotIn(attachment_user, app.user_states)

        source = APP_PATH.read_text(encoding="utf-8")
        module = ast.parse(source)
        choice_node = next(
            node
            for node in module.body
            if isinstance(node, ast.FunctionDef)
            and node.name == "reply_explain_method_choice"
        )
        choice_source = ast.get_source_segment(source, choice_node)
        self.assertEqual(2, choice_source.count("QuickReplyButton("))
        self.assertLess(
            choice_source.index("源さんに直接質問する"),
            choice_source.index("文書・写真等を見せる"),
        )
        self.assertIn("どうやって聞く？", choice_source)

        review_node = next(
            node
            for node in module.body
            if isinstance(node, ast.FunctionDef)
            and node.name == "create_explain_review_message"
        )
        review_source = ast.get_source_segment(source, review_node)
        self.assertIn("だいたい理解できたか？＾＾\\n次はどうする？", review_source)
        self.assertIn("わかった！", review_source)
        self.assertIn("まだ質問がある！", review_source)
        self.assertIn("源さん自身が着眼点から正答まで順番に説明し切って", source)
        self.assertIn("EXPLAIN_TEACHING_PROMPT", source)
        self.assertIn("use_teaching_intro=use_teaching_intro", source)

    def test_contextual_explain_reuses_direct_document_and_image_context(self) -> None:
        source = APP_PATH.read_text(encoding="utf-8")
        module = ast.parse(source)
        function_node = next(
            node
            for node in module.body
            if isinstance(node, ast.FunctionDef)
            and node.name == "create_contextual_explain_response"
        )
        chat_calls = []
        image_calls = []

        def create_chat_response(**kwargs):
            chat_calls.append(kwargs)
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content="文脈付き回答"))]
            )

        def create_image_response(**kwargs):
            image_calls.append(kwargs)
            return SimpleNamespace(output_text="画像を見直した回答")

        namespace = {
            "explain_contexts": {},
            "GEN_OJI_PROMPT": "源さん",
            "EDUCATION_RULE_PROMPT": "教育ルール",
            "EXPLAIN_TEACHING_PROMPT": "解答思考を教える",
            "client": SimpleNamespace(
                chat=SimpleNamespace(
                    completions=SimpleNamespace(create=create_chat_response)
                ),
                responses=SimpleNamespace(create=create_image_response),
            ),
        }
        extracted = ast.Module(body=[function_node], type_ignores=[])
        ast.fix_missing_locations(extracted)
        exec(compile(extracted, str(APP_PATH), "exec"), namespace)
        create_response = namespace["create_contextual_explain_response"]

        create_response("direct", "最初の質問")
        create_response("direct", "追加質問")
        second_messages = chat_calls[1]["messages"]
        self.assertTrue(any(message["content"] == "最初の質問" for message in second_messages))
        self.assertTrue(any(message["content"] == "文脈付き回答" for message in second_messages))

        namespace["explain_contexts"]["document"] = {
            "kind": "document",
            "source_text": "PDFの3ページ目の図表内容",
            "turns": [("assistant", "最初の資料解説")],
        }
        create_response("document", "3ページ目はどういう意味？")
        self.assertIn("PDFの3ページ目の図表内容", chat_calls[-1]["messages"][0]["content"])

        namespace["explain_contexts"]["image"] = {
            "kind": "image",
            "image_base64": "base64-image-data",
            "turns": [("assistant", "最初の画像解説")],
        }
        create_response("image", "なぜこの選択肢なの？")
        image_content = image_calls[-1]["input"][0]["content"]
        self.assertTrue(any("最初の画像解説" in item.get("text", "") for item in image_content))
        self.assertTrue(any("base64-image-data" in item.get("image_url", "") for item in image_content))

    def test_teach_gen_attachments_keep_existing_image_word_and_pdf_analysis(self) -> None:
        source = APP_PATH.read_text(encoding="utf-8")
        module = ast.parse(source)
        handler_nodes = [
            node
            for node in module.body
            if isinstance(node, ast.FunctionDef)
            and node.name in {"handle_file_message", "handle_image_message"}
        ]
        for node in handler_nodes:
            node.decorator_list = []

        states = {}
        contexts = {}
        analysis_calls = []
        pushed_reviews = []
        namespace = {
            "logging": logging,
            "user_states": states,
            "explain_contexts": contexts,
            "reply_to_line": lambda *args: None,
            "show_loading_animation": lambda *args: None,
            "download_line_file": lambda _message_id: SimpleNamespace(),
            "extract_text_from_docx": lambda _buffer: "Wordから抽出した問題文",
            "extract_text_from_pdf": lambda _buffer: "PDFから抽出した問題文",
            "image_buffer_to_base64": lambda _buffer: "image-base64",
            "analyze_word_document": (
                lambda file_name, document_text, use_teaching_intro=False:
                analysis_calls.append((file_name, document_text, use_teaching_intro))
                or "文書の教師型解説"
            ),
            "analyze_image": (
                lambda image_base64, use_teaching_intro=False:
                analysis_calls.append(("image", image_base64, use_teaching_intro))
                or "画像の教師型解説"
            ),
            "push_explain_answer_with_review": (
                lambda user_id, answer: pushed_reviews.append((user_id, answer))
            ),
            "push_to_line": lambda *args: None,
        }
        extracted = ast.Module(body=handler_nodes, type_ignores=[])
        ast.fix_missing_locations(extracted)
        exec(compile(extracted, str(APP_PATH), "exec"), namespace)

        for user_id, file_name in (("word-user", "sample.docx"), ("pdf-user", "sample.pdf")):
            states[user_id] = "explain_attachment"
            event = SimpleNamespace(
                message=SimpleNamespace(
                    file_name=file_name,
                    file_size=100,
                    id=f"{user_id}-message",
                ),
                source=SimpleNamespace(user_id=user_id),
                reply_token="reply-token",
            )
            namespace["handle_file_message"](event)
            self.assertEqual("explain_review", states[user_id])
            self.assertEqual("document", contexts[user_id]["kind"])

        image_user = "image-user"
        states[image_user] = "explain_attachment"
        image_event = SimpleNamespace(
            message=SimpleNamespace(id="image-message"),
            source=SimpleNamespace(user_id=image_user),
            reply_token="reply-token",
        )
        namespace["handle_image_message"](image_event)

        self.assertEqual("explain_review", states[image_user])
        self.assertEqual("image", contexts[image_user]["kind"])
        self.assertEqual("image-base64", contexts[image_user]["image_base64"])
        self.assertEqual(3, len(pushed_reviews))
        self.assertTrue(all(call[2] is True for call in analysis_calls))

    def test_attachment_generation_prompt_teaches_the_full_reasoning_to_the_answer(self) -> None:
        source = APP_PATH.read_text(encoding="utf-8")
        module = ast.parse(source)
        required_constants = {
            "GEN_OJI_PROMPT",
            "EDUCATION_RULE_PROMPT",
            "IMAGE_ANALYSIS_PROMPT",
            "WORD_ANALYSIS_PROMPT",
            "EXPLAIN_TEACHING_PROMPT",
        }
        namespace = {}
        for node in module.body:
            if not isinstance(node, ast.Assign) or len(node.targets) != 1:
                continue
            target = node.targets[0]
            if isinstance(target, ast.Name) and target.id in required_constants:
                namespace[target.id] = ast.literal_eval(node.value)

        image_calls = []
        word_calls = []
        namespace["client"] = SimpleNamespace(
            responses=SimpleNamespace(
                create=lambda **kwargs: image_calls.append(kwargs)
                or SimpleNamespace(output_text="画像解説")
            ),
            chat=SimpleNamespace(
                completions=SimpleNamespace(
                    create=lambda **kwargs: word_calls.append(kwargs)
                    or SimpleNamespace(
                        choices=[
                            SimpleNamespace(
                                message=SimpleNamespace(content="文書解説")
                            )
                        ]
                    )
                )
            ),
        )
        function_nodes = [
            node
            for node in module.body
            if isinstance(node, ast.FunctionDef)
            and node.name in {"analyze_image", "analyze_word_document"}
        ]
        extracted = ast.Module(body=function_nodes, type_ignores=[])
        ast.fix_missing_locations(extracted)
        exec(compile(extracted, str(APP_PATH), "exec"), namespace)

        namespace["analyze_image"]("image-data", use_teaching_intro=True)
        namespace["analyze_image"]("image-data", use_teaching_intro=False)
        namespace["analyze_word_document"](
            "question.docx",
            "国家試験問題の本文",
            use_teaching_intro=True,
        )
        namespace["analyze_word_document"](
            "general.docx",
            "一般資料",
            use_teaching_intro=False,
        )

        image_teaching_prompt = image_calls[0]["instructions"]
        image_general_prompt = image_calls[1]["instructions"]
        word_teaching_prompt = word_calls[0]["messages"][1]["content"]
        word_general_prompt = word_calls[1]["messages"][1]["content"]

        for prompt in (image_teaching_prompt, word_teaching_prompt):
            self.assertIn("源さん自身が着眼点から正答まで順番に説明し切って", prompt)
            self.assertIn("下腿三頭筋MMT2", prompt)
            self.assertIn("その選択肢が正しい理由", prompt)
            self.assertIn("問題作成者の立場で講評してはいけません", prompt)
            self.assertIn("問題ではない資料にも「正答」", prompt)
            self.assertIn("考えてみよう", prompt)

        self.assertNotIn("これは「教えて源さん」における最優先", image_general_prompt)
        self.assertNotIn("これは「教えて源さん」における最優先", word_general_prompt)


if __name__ == "__main__":
    unittest.main()
