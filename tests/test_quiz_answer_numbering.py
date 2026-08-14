"""小テストの表示番号・入力番号・保存番号の対応を検証する。"""

from __future__ import annotations

import ast
import json
import logging
import re
import threading
import time
import unicodedata
import unittest
from pathlib import Path
from types import SimpleNamespace


APP_PATH = Path(__file__).resolve().parents[1] / "app.py"


def load_teaching_tracking_functions():
    module = ast.parse(APP_PATH.read_text(encoding="utf-8"), filename=str(APP_PATH))
    names = {
        "register_teaching_image_analysis",
        "invalidate_teaching_image_analysis",
        "is_current_teaching_image_analysis",
        "process_teaching_image",
    }
    nodes = [
        node for node in module.body
        if isinstance(node, ast.FunctionDef) and node.name in names
    ]
    states = {}
    contexts = {}
    active_ids = {}
    recent_ids = {}
    pushes = []
    reviews = []
    namespace = {
        "time": time,
        "threading": threading,
        "logging": logging,
        "time": time,
        "user_states": states,
        "explain_contexts": contexts,
        "teaching_image_active_ids": active_ids,
        "teaching_image_recent_ids": recent_ids,
        "teaching_image_tracking_lock": threading.Lock(),
        "TEACHING_IMAGE_MESSAGE_ID_TTL_SECONDS": 600,
        "TEACHING_IMAGE_MESSAGE_ID_MAX_COUNT": 3,
        "push_to_line": lambda user_id, text: pushes.append((user_id, text)),
        "push_explain_answer_with_review": (
            lambda user_id, text: reviews.append((user_id, text))
        ),
        "analyze_teaching_image_stage1": lambda *_args, **_kwargs: {
            "read_confidence": "high",
            "uncertain_fields": [],
            "patient_info_raw": "",
            "findings_raw": ["所見"],
            "question_prompt_raw": "問い",
            "choices_raw": {"A": "選択肢"},
            "tables_or_figures_raw": None,
            "unreadable_notes": None,
        },
        "solve_teaching_image_stage2": lambda data, **_kwargs: data["question_prompt_raw"],
    }
    extracted = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(extracted)
    exec(compile(extracted, str(APP_PATH), "exec"), namespace)
    return SimpleNamespace(
        namespace=namespace,
        states=states,
        contexts=contexts,
        active_ids=active_ids,
        recent_ids=recent_ids,
        pushes=pushes,
        reviews=reviews,
    )


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
        "is_home_command",
        "pause_quiz_session",
        "resume_quiz_session",
        "process_study_answer_input",
        "process_study_flow_command",
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
        "time": time,
        "Path": Path,
        "unicodedata": unicodedata,
        "logging": logging,
        "TextSendMessage": lambda text: SimpleNamespace(text=text),
        "line_bot_api": SimpleNamespace(
            reply_message=lambda token, messages: line_replies.append((token, messages))
        ),
        "threading": SimpleNamespace(Thread=None),
        "study_sessions": {},
        "consultation_contexts": {},
        "learning_answer_counts": {},
        "explain_contexts": {},
        "user_states": {},
        "user_names": {},
        "user_modes": {},
        "reply_to_line": lambda *args, **kwargs: None,
        "reply_mode_select": lambda *args, **kwargs: None,
        "reply_study_continue_choice": lambda *args, **kwargs: None,
        "reply_study_set_result": lambda token, session: namespace["reply_study_continue_choice"](token),
        "reply_quiz_ready_for_explanations": lambda token, session: namespace["reply_quiz_score"](token, session["quiz_result"]),
        "reply_question_type_choice": lambda *args, **kwargs: None,
        "reply_saved_session_choice": lambda *args, **kwargs: None,
        "reply_current_quiz": lambda *args, **kwargs: None,
        "reply_quiz_input_error": (
            lambda token, start, count: namespace["reply_to_line"](
                token,
                f"第{start}問から第{start + count - 1}問まで\n"
                + "\n".join(
                    f"{number}:{answer}"
                    for number, answer in zip(
                        range(start, start + count),
                        ["A1", "B2", "C3", "D2", "E1"],
                    )
                ),
            )
        ),
        "reply_recommended_intro": lambda *args, **kwargs: None,
        "return_home": lambda token, user_id, interrupt=True: (
            namespace["user_states"].pop(user_id, None),
            namespace["study_sessions"].pop(user_id, None),
            namespace["user_modes"].__setitem__(user_id, "normal"),
            namespace["reply_mode_select"](token),
        ),
        "reply_study_ready_choice": lambda *args, **kwargs: None,
        "reply_quiz_score": lambda *args, **kwargs: None,
        "reply_explanation_choice": lambda *args, **kwargs: None,
        "reply_next_explanation_choice": lambda *args, **kwargs: None,
        "reply_new_user_welcome": lambda *args, **kwargs: None,
        "reply_gen_first_greeting": lambda *args, **kwargs: None,
        "reply_explain_method_choice": lambda *args, **kwargs: None,
        "reply_explain_answer_with_review": lambda *args, **kwargs: None,
        "reply_consultation_start": lambda token: line_replies.append((token, "consultation")),
        "reply_consultation_response": lambda token, text: line_replies.append((token, text)),
        "reply_nekketsu_start": lambda token: line_replies.append((token, "nekketsu")),
        "reply_nekketsu_continue_choice": lambda *args, **kwargs: None,
        "invalidate_teaching_image_analysis": lambda *args, **kwargs: None,
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

    def test_session_expected_numbers_follow_every_displayed_batch(self) -> None:
        user_id = "expected-number-user"
        globals_ = app.start_quiz.__globals__
        original_select = globals_["select_random_questions"]
        globals_["select_random_questions"] = lambda count: make_all_questions()[:count]
        app.user_modes[user_id] = "study"
        try:
            app.start_quiz(user_id)
            self.assertEqual(list(range(1, 6)), app.study_sessions[user_id]["expected_numbers"])
            for current_set in range(2, 7):
                app.start_next_quiz(user_id)
                start = ((current_set - 1) * 5) + 1
                self.assertEqual(
                    list(range(start, start + 5)),
                    app.study_sessions[user_id]["expected_numbers"],
                )
        finally:
            globals_["select_random_questions"] = original_select

    def test_quiz_ui_sources_keep_required_actions_and_heat_total(self) -> None:
        source = APP_PATH.read_text(encoding="utf-8")
        module = ast.parse(source)

        def function_source(name):
            node = next(
                item for item in module.body
                if isinstance(item, ast.FunctionDef) and item.name == name
            )
            return ast.get_source_segment(source, node)

        study = function_source("reply_study_set_result")
        heat = function_source("reply_nekketsu_continue_choice")
        invalid = function_source("reply_quiz_input_error")
        resumed = function_source("reply_current_quiz")
        pushed = function_source("push_quiz_to_line")
        for label in ("続ける", "源さんに預ける", "ホームに戻る"):
            self.assertIn(label, study)
        for label in ("続ける", "源さんに預ける", "終了する"):
            self.assertIn(label, heat)
        self.assertIn('f"🔥 {answered_count}問終了！', heat)
        for body in (invalid, resumed):
            self.assertIn("源さんに預ける", body)
            self.assertIn("ホームに戻る", body)
        for body in (resumed, pushed):
            self.assertIn('session.get("mode") == "nekketsu"', body)
            self.assertIn('label="続ける"', body)

    def test_heat_result_uses_cumulative_10_and_15_question_counts(self) -> None:
        source = APP_PATH.read_text(encoding="utf-8")
        module = ast.parse(source)
        node = next(
            item for item in module.body
            if isinstance(item, ast.FunctionDef)
            and item.name == "reply_nekketsu_continue_choice"
        )
        replies = []
        namespace = {
            "line_bot_api": SimpleNamespace(
                reply_message=lambda token, message: replies.append(message)
            ),
            "TextSendMessage": lambda text, quick_reply=None: SimpleNamespace(
                text=text, quick_reply=quick_reply
            ),
            "QuickReply": lambda items: SimpleNamespace(items=items),
            "QuickReplyButton": lambda action: SimpleNamespace(action=action),
            "MessageAction": lambda label, text: SimpleNamespace(label=label, text=text),
        }
        extracted = ast.Module(body=[node], type_ignores=[])
        ast.fix_missing_locations(extracted)
        exec(compile(extracted, str(APP_PATH), "exec"), namespace)

        for current_set, answered in ((2, 10), (3, 15)):
            session = {
                "current_set": current_set,
                "questions_per_set": 5,
                "questions": make_questions(),
                "all_answers": {
                    number: {"answer": "A", "confidence": "1"}
                    for number in range(1, answered + 1)
                },
                "nekketsu_correct": 0,
            }
            namespace["reply_nekketsu_continue_choice"]("token", session)

        self.assertIn("🔥 10問終了！", replies[0].text)
        self.assertIn("🔥 15問終了！", replies[1].text)
        self.assertEqual(
            ["🔥 続ける", "📥 源さんに預ける", "🏁 終了する"],
            [item.action.label for item in replies[1].quick_reply.items],
        )

    def test_heat_end_discards_session_and_returns_home(self) -> None:
        user_id = "heat-end-user"
        app.user_modes[user_id] = "nekketsu"
        app.study_sessions[user_id] = {
            "status": "waiting_for_continue", "mode": "nekketsu"
        }
        globals_ = app.handle_text_message.__globals__
        original_home = globals_["return_home"]
        home_calls = []
        globals_["return_home"] = (
            lambda token, target_user, interrupt=True:
            home_calls.append((target_user, interrupt))
        )
        try:
            app.handle_text_message(make_text_event(user_id, "終了する"))
        finally:
            globals_["return_home"] = original_home

        self.assertNotIn(user_id, app.study_sessions)
        self.assertEqual([(user_id, True)], home_calls)

    def test_heat_continue_while_unanswered_keeps_current_set(self) -> None:
        user_id = "heat-unanswered-user"
        app.user_modes[user_id] = "nekketsu"
        app.study_sessions[user_id] = {
            "status": "waiting_for_answers", "mode": "nekketsu",
            "current_set": 3, "questions_per_set": 5,
            "questions": make_questions(), "all_answers": {},
        }
        globals_ = app.handle_text_message.__globals__
        original_current = globals_["reply_current_quiz"]
        redisplayed = []
        globals_["reply_current_quiz"] = (
            lambda token, session: redisplayed.append(session["current_set"])
        )
        try:
            app.handle_text_message(make_text_event(user_id, "続ける"))
        finally:
            globals_["reply_current_quiz"] = original_current

        self.assertEqual([3], redisplayed)
        self.assertEqual(3, app.study_sessions[user_id]["current_set"])
        self.assertEqual("waiting_for_answers", app.study_sessions[user_id]["status"])

    def test_heat_continue_after_results_starts_next_five_without_ai(self) -> None:
        user_id = "heat-continue-user"
        app.user_modes[user_id] = "nekketsu"
        app.study_sessions[user_id] = {
            "session_id": "heat-session", "status": "waiting_for_continue",
            "mode": "nekketsu", "current_set": 1, "total_sets": 6,
            "question_count": 30, "questions_per_set": 5,
            "questions": make_all_questions()[:5],
            "all_questions": make_all_questions(), "all_answers": {},
        }
        globals_ = app.handle_text_message.__globals__
        original_threading = globals_["threading"]
        original_prepare = globals_["prepare_and_send_next_quiz"]
        original_ai = globals_["create_text_response"]

        class ImmediateThread:
            def __init__(self, target, args=(), daemon=None):
                self.target, self.args = target, args

            def start(self):
                self.target(*self.args)

        globals_["threading"] = SimpleNamespace(Thread=ImmediateThread)
        globals_["prepare_and_send_next_quiz"] = (
            lambda target_user, session_id=None: app.start_next_quiz(target_user)
        )
        globals_["create_text_response"] = lambda *args, **kwargs: self.fail(
            "熱血の続けるが自由会話AIへ流れました。"
        )
        try:
            app.handle_text_message(make_text_event(user_id, "続ける"))
            self.assertEqual(2, app.study_sessions[user_id]["current_set"])
            self.assertEqual(list(range(6, 11)), app.study_sessions[user_id]["expected_numbers"])
            app.study_sessions[user_id]["status"] = "waiting_for_continue"
            app.pause_quiz_session(user_id)
            app.resume_quiz_session(user_id)
            app.handle_text_message(make_text_event(user_id, "続ける"))
        finally:
            globals_["threading"] = original_threading
            globals_["prepare_and_send_next_quiz"] = original_prepare
            globals_["create_text_response"] = original_ai

        self.assertEqual(3, app.study_sessions[user_id]["current_set"])
        self.assertEqual(list(range(11, 16)), app.study_sessions[user_id]["expected_numbers"])
        self.assertEqual("waiting_for_answers", app.study_sessions[user_id]["status"])

    def test_study_fixed_flow_completes_30_questions_and_all_explanations(self) -> None:
        user_id = "fixed-thirty-user"
        globals_ = app.handle_text_message.__globals__
        originals = {
            name: globals_[name]
            for name in (
                "prepare_and_send_next_quiz", "create_text_response",
                "push_to_line", "reply_next_explanation_choice",
                "reply_explanation_choice",
            )
        }
        original_threading = globals_["threading"]
        pushed, next_choices, completion_calls = [], [], []

        class ImmediateThread:
            def __init__(self, target, args=(), daemon=None):
                self.target, self.args = target, args

            def start(self):
                self.target(*self.args)

        globals_["threading"] = SimpleNamespace(Thread=ImmediateThread)
        globals_["prepare_and_send_next_quiz"] = (
            lambda target_user, _session_id=None: app.start_next_quiz(target_user)
        )
        globals_["create_text_response"] = lambda *args, **kwargs: self.fail(
            "通常学習の固定フローが自由会話AIへ流れました。"
        )
        globals_["push_to_line"] = lambda _user, message: pushed.append(message)
        globals_["reply_next_explanation_choice"] = lambda token: next_choices.append(token)
        def capture_completion(token, completed=False, quiz_result=None):
            completion_calls.append(completed)

        globals_["reply_explanation_choice"] = capture_completion
        app.user_names[user_id] = "学習者"
        app.user_modes[user_id] = "study"
        questions = make_all_questions()
        app.study_sessions[user_id] = {
            "session_id": "fixed-session", "status": "waiting_for_answers",
            "current_set": 1, "question_count": 30, "questions_per_set": 5,
            "total_sets": 6, "questions": questions[:5],
            "all_questions": questions, "all_answers": {},
            "expected_numbers": list(range(1, 6)), "mode": "study",
        }

        try:
            for current_set in range(1, 7):
                start = ((current_set - 1) * 5) + 1
                answers = " ".join(
                    f"{number}:A1" for number in range(start, start + 5)
                )
                app.handle_text_message(make_text_event(user_id, answers))
                if current_set < 6:
                    self.assertEqual("waiting_for_continue", app.study_sessions[user_id]["status"])
                    app.handle_text_message(make_text_event(user_id, "続ける"))
                    self.assertEqual(current_set + 1, app.study_sessions[user_id]["current_set"])
                    self.assertEqual(
                        list(range(start + 5, start + 10)),
                        app.study_sessions[user_id]["expected_numbers"],
                    )

            self.assertEqual("waiting_for_explanations", app.study_sessions[user_id]["status"])
            app.handle_text_message(make_text_event(user_id, "解答解説を見る"))
            for _ in range(5):
                app.handle_text_message(make_text_event(user_id, "次の5問"))
        finally:
            for name, original in originals.items():
                globals_[name] = original
            globals_["threading"] = original_threading

        self.assertEqual("quiz_completed", app.study_sessions[user_id]["status"])
        self.assertEqual(6, len(pushed))
        self.assertEqual(5, len(next_choices))
        self.assertEqual([True], completion_calls)

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
        original_welcome = function_globals["reply_new_user_welcome"]

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
                    welcome_calls = []
                    function_globals["reply_new_user_welcome"] = (
                        lambda token: welcome_calls.append(token)
                    )

                    app.handle_text_message(
                        make_text_event(user_id, "ふりだしにもどる")
                    )

                    self.assertEqual("waiting_gen_intro", app.user_states[user_id])
                    self.assertNotIn(user_id, app.study_sessions)
                    self.assertNotIn(user_id, app.user_modes)
                    self.assertNotIn(user_id, app.user_names)
                    self.assertNotIn(user_id, app.known_user_ids)
                    self.assertEqual(0, len(reply_messages))
                    self.assertEqual(1, len(welcome_calls))
        finally:
            function_globals["reply_to_line"] = original_reply
            function_globals["create_text_response"] = original_create_text_response
            function_globals["reply_study_continue_choice"] = original_continue
            function_globals["reply_new_user_welcome"] = original_welcome

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

    def test_home_keeps_registered_name(self) -> None:
        user_id = "home-keeps-name"
        app.user_names[user_id] = "登録済みユーザー"
        app.user_modes[user_id] = "chat"

        app.handle_text_message(make_text_event(user_id, "ホームに戻る"))

        self.assertEqual("登録済みユーザー", app.user_names[user_id])
        self.assertEqual("normal", app.user_modes[user_id])

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
            self.assertEqual("waiting_gen_intro", app.user_states[user_id])
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
        self.assertIn("再登録ユーザー", registered[-1])

    def test_active_modes_do_not_fall_back_to_onboarding_when_name_is_missing(self) -> None:
        globals_ = app.handle_text_message.__globals__
        original_welcome = globals_["reply_new_user_welcome"]
        original_gen = globals_["reply_gen_first_greeting"]
        original_study_result = globals_["reply_study_set_result"]
        original_heat_result = globals_["reply_nekketsu_continue_choice"]
        original_create = globals_["create_text_response"]
        welcome_calls, study_results, heat_results, consultations = [], [], [], []
        globals_["reply_new_user_welcome"] = lambda *args: welcome_calls.append(args)
        globals_["reply_gen_first_greeting"] = lambda *args: welcome_calls.append(args)
        globals_["reply_study_set_result"] = lambda token, session: study_results.append(session["status"])
        globals_["reply_nekketsu_continue_choice"] = lambda token, session: heat_results.append(session["status"])
        globals_["create_text_response"] = lambda message, mode: consultations.append((message, mode)) or "相談返答"

        def session(mode):
            return {
                "status": "waiting_for_answers", "current_set": 1,
                "total_sets": 6, "question_count": 30, "questions_per_set": 5,
                "questions": make_questions(), "all_questions": make_all_questions(),
                "all_answers": {}, "mode": mode,
            }

        try:
            app.user_modes["study-active"] = "study"
            app.study_sessions["study-active"] = session("study")
            app.handle_text_message(make_text_event("study-active", "1:A1 2:B2 3:C3 4:D1 5:E2"))

            app.user_modes["heat-active"] = "nekketsu"
            app.study_sessions["heat-active"] = session("nekketsu")
            app.handle_text_message(make_text_event("heat-active", "1:A1 2:B2 3:C3 4:D1 5:E2"))

            app.user_modes["chat-active"] = "chat"
            app.user_states["chat-active"] = "consultation_input"
            app.handle_text_message(make_text_event("chat-active", "相談内容です"))
        finally:
            globals_["reply_new_user_welcome"] = original_welcome
            globals_["reply_gen_first_greeting"] = original_gen
            globals_["reply_study_set_result"] = original_study_result
            globals_["reply_nekketsu_continue_choice"] = original_heat_result
            globals_["create_text_response"] = original_create

        self.assertEqual([], welcome_calls)
        self.assertEqual(["waiting_for_continue"], study_results)
        self.assertEqual(["waiting_for_continue"], heat_results)
        self.assertEqual([("相談内容です", "chat")], consultations)


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
            "📊 合格への道",
            "📘 勉強する",
            "💬 相談する",
            "🔥 熱血モード",
        ]
        source = APP_PATH.read_text(encoding="utf-8")
        module = ast.parse(source)
        mode_select_node = next(
            node
            for node in module.body
            if isinstance(node, ast.FunctionDef) and node.name == "create_home_message"
        )
        mode_select_source = ast.get_source_segment(source, mode_select_node)

        for user_id in ("study-user", "chat-user", "explain-user", "heat-user"):
            app.user_names[user_id] = "登録済みユーザー"

        try:
            app.handle_text_message(make_text_event("study-user", "勉強する"))
            app.handle_text_message(make_text_event("chat-user", "相談する"))
            app.handle_text_message(make_text_event("explain-user", "教えて源さん"))
            app.handle_text_message(make_text_event("heat-user", "熱血モード"))
        finally:
            function_globals["reply_to_line"] = original_reply
            function_globals["reply_study_ready_choice"] = original_study_ready
            function_globals["reply_explain_method_choice"] = original_explain_choice

        self.assertEqual(4, mode_select_source.count("QuickReplyButton("))
        self.assertNotIn("教えて源さん", mode_select_source)
        self.assertIn("/goukaku-no-michi", mode_select_source)
        self.assertIn("ここはお前たちの〝家”だよ＾＾", mode_select_source)
        self.assertEqual(
            sorted(mode_select_source.index(label) for label in labels),
            [mode_select_source.index(label) for label in labels],
        )
        self.assertEqual("study", app.user_modes["study-user"])
        self.assertEqual("chat", app.user_modes["chat-user"])
        self.assertEqual("explain", app.user_modes["explain-user"])
        self.assertEqual("nekketsu", app.user_modes["heat-user"])
        self.assertEqual(1, len(study_replies))
        self.assertEqual(1, len(explain_choices))
        self.assertEqual(2, len(app.line_replies))
        self.assertEqual("consultation", app.line_replies[0][1])
        self.assertEqual("nekketsu", app.line_replies[1][1])

    def test_home_command_variants_use_fixed_home_before_current_state(self) -> None:
        function_globals = app.handle_text_message.__globals__
        original_return_home = function_globals["return_home"]
        home_calls = []
        function_globals["return_home"] = (
            lambda token, user_id, interrupt=True:
            home_calls.append((token, user_id, interrupt))
        )
        variants = [
            " ホームに戻る ", "ホームにもどる", "ホームへ戻る",
            "ホームへもどる", "ほーむに戻る", "HOMEに戻る",
            "Homeに戻る", "homeに戻る", "ＨＯＭＥに戻る",
            "ホーム戻る", "ホーム",
        ]
        user_id = "home-command-user"
        app.user_states[user_id] = "waiting_quiz_answer"

        try:
            for message in variants:
                app.handle_text_message(make_text_event(user_id, message))
        finally:
            function_globals["return_home"] = original_return_home

        self.assertEqual(len(variants), len(home_calls))
        self.assertFalse(app.is_home_command("老人ホームについて教えて"))
        self.assertFalse(app.is_home_command("ホームポジションって何？"))

    def test_study_save_resume_and_new_start_flow(self) -> None:
        globals_ = app.handle_text_message.__globals__
        originals = {
            name: globals_[name]
            for name in ("return_home", "reply_saved_session_choice",
                         "reply_current_quiz", "reply_question_type_choice")
        }
        home_calls, saved_choices, resumed, new_choices = [], [], [], []
        globals_["return_home"] = lambda token, user_id, interrupt=True: home_calls.append(user_id)
        globals_["reply_saved_session_choice"] = lambda token: saved_choices.append(token)
        globals_["reply_current_quiz"] = lambda token, session: resumed.append(session["current_set"])
        globals_["reply_question_type_choice"] = lambda token, mode: new_choices.append(mode)
        user_id = "saved-study-user"
        app.user_names[user_id] = "学習者"
        app.user_modes[user_id] = "study"
        app.study_sessions[user_id] = {
            "status": "waiting_for_answers", "current_set": 2,
            "questions_per_set": 5, "questions": make_questions(),
            "all_answers": {number: {"answer": "A", "confidence": "1"} for number in range(1, 6)},
            "mode": "study",
        }
        try:
            app.handle_text_message(make_text_event(user_id, "中断する"))
            self.assertEqual("paused", app.study_sessions[user_id]["status"])
            app.handle_text_message(make_text_event(user_id, "勉強する"))
            app.handle_text_message(make_text_event(user_id, "続きから始める"))
            app.pause_quiz_session(user_id)
            app.handle_text_message(make_text_event(user_id, "新しく始める"))
        finally:
            for name, original in originals.items():
                globals_[name] = original

        self.assertEqual([user_id], home_calls)
        self.assertEqual(1, len(saved_choices))
        self.assertEqual([2], resumed)
        self.assertEqual(["学習"], new_choices)
        self.assertNotIn(user_id, app.study_sessions)

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
            app.handle_text_message(make_text_event(attachment_user, "Word・PDFを見せる"))
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
        self.assertIn("WordやPDFを送ってくれれば", attachment_prompt)
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
            choice_source.index("Word・PDFを見せる"),
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

    def test_teach_gen_attachments_keep_word_pdf_and_suspend_image_entry(self) -> None:
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
        replies = []

        def analyze_image_stub(
            image_base64,
            use_teaching_intro=False,
            response_meta=None,
        ):
            analysis_calls.append(("image", image_base64, use_teaching_intro))
            answer = "画像の教師型解説" if use_teaching_intro else "長" * 4501
            if response_meta is not None:
                response_meta.update(
                    {
                        "status": "completed",
                        "incomplete_reason": "none",
                        "input_tokens": 500,
                        "output_tokens": 700,
                        "total_tokens": 1200,
                        "answer_chars": len(answer),
                    }
                )
            return answer

        class ImmediateThread:
            def __init__(self, target, args, daemon):
                self.target = target
                self.args = args

            def start(self):
                self.target(*self.args)

        def process_teaching_image_stub(user_id, _analysis_id, image_base64, _started_at):
            analysis_calls.append(("teaching_image", image_base64, True))
            states[user_id] = "explain_review"
            contexts[user_id] = {
                "kind": "teaching_image",
                "structured_data": {"question_prompt_raw": "問題"},
                "turns": [("assistant", "画像の教師型解説")],
            }
            pushed_reviews.append((user_id, "画像の教師型解説"))

        namespace = {
            "logging": logging,
            "time": __import__("time"),
            "threading": SimpleNamespace(Thread=ImmediateThread),
            "user_states": states,
            "explain_contexts": contexts,
            "reply_to_line": lambda _token, text: replies.append(text),
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
            "analyze_image": analyze_image_stub,
            "register_teaching_image_analysis": lambda *_args, **_kwargs: True,
            "process_teaching_image": process_teaching_image_stub,
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

        general_event = SimpleNamespace(
            message=SimpleNamespace(id="general-image-message"),
            source=SimpleNamespace(user_id="general-image-user"),
            reply_token="reply-token",
        )
        namespace["handle_image_message"](general_event)

        self.assertEqual("explain_attachment", states[image_user])
        self.assertNotIn(image_user, contexts)
        self.assertEqual(2, len(pushed_reviews))
        self.assertEqual(2, len(analysis_calls))
        self.assertTrue(all(call[2] is True for call in analysis_calls))
        self.assertTrue(all("対応を見合わせてる" in text for text in replies[-2:]))

    def test_gunicorn_timeout_is_90_seconds(self) -> None:
        procfile_path = APP_PATH.parent / "Procfile"
        self.assertEqual(
            "web: gunicorn --timeout 90 app:app",
            procfile_path.read_text(encoding="utf-8").strip(),
        )

    def test_q1_image_accuracy_contract_keeps_source_terms_without_hardcoding(self) -> None:
        source = APP_PATH.read_text(encoding="utf-8")
        q1_question = (
            "左立脚後期の踵離地が乏しく、右歩幅が短い。"
            "足関節背屈ROMは膝屈曲位15°、膝伸展位0°。"
            "膝過伸展は認めない。"
        )
        q1_choices = {
            "A": "股関節内転筋の痙縮による歩隔の減少",
            "B": "下腿三頭筋筋力低下と腓腹筋の伸張性低下",
            "C": "大腿四頭筋筋持久力低下による膝折れ",
            "D": "動的バランス低下による立脚時間の延長",
            "E": "股関節外転筋筋力低下による骨盤下制",
        }
        self.assertEqual(
            "下腿三頭筋筋力低下と腓腹筋の伸張性低下",
            q1_choices["B"],
        )
        for exact_term in (
            "踵離地",
            "右歩幅",
            "膝屈曲位15°",
            "膝伸展位0°",
            "膝過伸展は認めない",
        ):
            self.assertIn(exact_term, q1_question)
        self.assertIn("痙縮", q1_choices["A"])
        self.assertNotIn("麻痺", q1_choices["A"])
        self.assertIn("歩隔", q1_choices["A"])
        self.assertNotIn("歩幅", q1_choices["A"])
        self.assertNotIn("B．" + q1_choices["B"], source)
        self.assertIn("歩幅／歩隔", source)
        self.assertIn("痙縮／麻痺", source)
        self.assertIn("選択肢は読み取った実際の文言のまま", source)

    def test_teaching_image_uses_exactly_two_stages_and_stage2_gets_json_only(self) -> None:
        source = APP_PATH.read_text(encoding="utf-8")
        module = ast.parse(source)
        wanted = {
            "_record_responses_api_meta",
            "_parse_teaching_image_stage1_json",
            "analyze_teaching_image_stage1",
            "solve_teaching_image_stage2",
        }
        nodes = [
            node for node in module.body
            if isinstance(node, ast.FunctionDef) and node.name in wanted
        ]
        constants = {}
        for node in module.body:
            if not isinstance(node, ast.Assign) or len(node.targets) != 1:
                continue
            target = node.targets[0]
            if isinstance(target, ast.Name) and target.id in {
                "TEACHING_IMAGE_CHARACTER_PROMPT",
                "TEACHING_IMAGE_STAGE1_PROMPT",
                "TEACHING_IMAGE_STAGE2_PROMPT",
            }:
                constants[target.id] = ast.literal_eval(node.value)

        structured = {
            "read_confidence": "high",
            "uncertain_fields": [],
            "patient_info_raw": "左麻痺なし",
            "findings_raw": ["右歩幅が短い", "MMT4", "ROM 15°"],
            "question_prompt_raw": "正しいのはどれか。",
            "choices_raw": {"A": "歩隔の増加", "B": "痙縮なし"},
            "tables_or_figures_raw": None,
            "unreadable_notes": None,
        }
        calls = []
        responses = [
            SimpleNamespace(
                output_text=json.dumps(structured, ensure_ascii=False),
                status="completed",
                incomplete_details=None,
                usage=SimpleNamespace(input_tokens=100, output_tokens=200, total_tokens=300),
            ),
            SimpleNamespace(
                output_text="おう、【正答】Bだ。",
                status="completed",
                incomplete_details=None,
                usage=SimpleNamespace(input_tokens=200, output_tokens=300, total_tokens=500),
            ),
        ]

        def create_response(**kwargs):
            calls.append(kwargs)
            return responses[len(calls) - 1]

        namespace = {
            **constants,
            "json": json,
            "client": SimpleNamespace(
                responses=SimpleNamespace(create=create_response)
            ),
        }
        extracted = ast.Module(body=nodes, type_ignores=[])
        ast.fix_missing_locations(extracted)
        exec(compile(extracted, str(APP_PATH), "exec"), namespace)

        stage1_meta = {}
        parsed = namespace["analyze_teaching_image_stage1"](
            "secret-base64",
            response_meta=stage1_meta,
        )
        answer = namespace["solve_teaching_image_stage2"](parsed, response_meta={})

        self.assertEqual(2, len(calls))
        self.assertIn("input_image", str(calls[0]["input"]))
        self.assertIn("secret-base64", str(calls[0]["input"]))
        self.assertNotIn("input_image", str(calls[1]["input"]))
        self.assertNotIn("secret-base64", str(calls[1]["input"]))
        self.assertIn("左麻痺なし", str(calls[1]["input"]))
        self.assertEqual("おう、【正答】Bだ。", answer)
        self.assertTrue(stage1_meta["json_parse_success"])
        self.assertEqual(3, stage1_meta["finding_count"])

    def test_teaching_image_prompts_preserve_raw_text_and_reject_guessing(self) -> None:
        source = APP_PATH.read_text(encoding="utf-8")
        for phrase in (
            "医学的に推論する",
            "推測補完",
            "左右、数値、単位",
            "歩幅／歩隔",
            "痙縮／麻痺",
            "read_confidence",
            "uncertain_fields",
            "1所見を1項目",
        ):
            self.assertIn(phrase, source)
        for phrase in (
            "question_prompt_rawから何を問う問題か",
            "すべての選択肢",
            "必ず要素分解",
            "根拠不足",
            "read_confidenceがlow",
            "最後の文章だけを源さん",
        ):
            self.assertIn(phrase, source)
        self.assertNotIn("正答B", source)

    def test_stage1_invalid_json_or_schema_is_rejected(self) -> None:
        source = APP_PATH.read_text(encoding="utf-8")
        module = ast.parse(source)
        node = next(
            node for node in module.body
            if isinstance(node, ast.FunctionDef)
            and node.name == "_parse_teaching_image_stage1_json"
        )
        namespace = {"json": json}
        exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])), str(APP_PATH), "exec"), namespace)
        parse_stage1 = namespace["_parse_teaching_image_stage1_json"]

        with self.assertRaises((json.JSONDecodeError, ValueError)):
            parse_stage1("読み取り結果です")
        with self.assertRaises(ValueError):
            parse_stage1(json.dumps({"read_confidence": "maybe"}))

    def test_teaching_image_stage_failures_stop_safely(self) -> None:
        source = APP_PATH.read_text(encoding="utf-8")
        module = ast.parse(source)
        node = next(
            node for node in module.body
            if isinstance(node, ast.FunctionDef)
            and node.name == "process_teaching_image"
        )
        states = {"stage1-user": "explain_attachment", "stage2-user": "explain_attachment"}
        pushed = []
        stage2_calls = []
        namespace = {
            "time": __import__("time"),
            "logging": logging,
            "user_states": states,
            "explain_contexts": {},
            "push_to_line": lambda user_id, text: pushed.append((user_id, text)),
            "push_explain_answer_with_review": lambda *args: None,
            "analyze_teaching_image_stage1": (
                lambda *_args, **_kwargs: (_ for _ in ()).throw(ValueError("bad json"))
            ),
            "solve_teaching_image_stage2": (
                lambda *_args, **_kwargs: stage2_calls.append(True) or "unused"
            ),
            "is_current_teaching_image_analysis": lambda *_args: True,
            "invalidate_teaching_image_analysis": lambda *_args: None,
        }
        exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])), str(APP_PATH), "exec"), namespace)
        namespace["process_teaching_image"]("stage1-user", "stage1-id", "image", 0.0)
        self.assertEqual([], stage2_calls)
        self.assertIn("対応を見合わせてる", pushed[-1][1])
        self.assertEqual("explain_attachment", states["stage1-user"])

        namespace["analyze_teaching_image_stage1"] = lambda *_args, **_kwargs: {
            "read_confidence": "high",
            "uncertain_fields": [],
            "patient_info_raw": "",
            "findings_raw": [],
            "question_prompt_raw": "",
            "choices_raw": {},
            "tables_or_figures_raw": None,
            "unreadable_notes": None,
        }
        namespace["solve_teaching_image_stage2"] = (
            lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("solve failed"))
        )
        namespace["process_teaching_image"]("stage2-user", "stage2-id", "image", 0.0)
        self.assertIn("対応を見合わせてる", pushed[-1][1])
        self.assertEqual("explain_attachment", states["stage2-user"])
        self.assertNotIn("stage2-user", namespace["explain_contexts"])

    def test_latest_teaching_image_wins_regardless_of_completion_order(self) -> None:
        for completion_order in (("image-1", "image-2"), ("image-2", "image-1")):
            with self.subTest(completion_order=completion_order):
                app = load_teaching_tracking_functions()
                user_id = "same-user"
                app.states[user_id] = "explain_attachment"
                register = app.namespace["register_teaching_image_analysis"]
                process = app.namespace["process_teaching_image"]
                self.assertTrue(register(user_id, "image-1", now=1.0))
                self.assertTrue(register(user_id, "image-2", now=2.0))

                for analysis_id in completion_order:
                    process(user_id, analysis_id, "base64", time.perf_counter())

                self.assertEqual([(user_id, "問い")], app.reviews)
                self.assertEqual("explain_review", app.states[user_id])
                self.assertEqual("teaching_image", app.contexts[user_id]["kind"])

    def test_teaching_image_duplicate_ids_use_ttl_and_count_limit(self) -> None:
        app = load_teaching_tracking_functions()
        register = app.namespace["register_teaching_image_analysis"]
        self.assertTrue(register("user", "message-1", now=1.0))
        self.assertFalse(register("user", "message-1", now=2.0))
        self.assertTrue(register("user", "message-2", now=3.0))
        self.assertTrue(register("user", "message-3", now=4.0))
        self.assertTrue(register("user", "message-4", now=5.0))
        self.assertEqual(3, len(app.recent_ids))
        self.assertNotIn("message-1", app.recent_ids)

        expired = load_teaching_tracking_functions()
        register_expiring = expired.namespace["register_teaching_image_analysis"]
        self.assertTrue(register_expiring("user", "same-id", now=1.0))
        self.assertTrue(register_expiring("user", "same-id", now=602.0))

    def test_image_webhook_does_not_start_pipeline_while_entry_is_suspended(self) -> None:
        source = APP_PATH.read_text(encoding="utf-8")
        module = ast.parse(source)
        handler_node = next(
            node for node in module.body
            if isinstance(node, ast.FunctionDef) and node.name == "handle_image_message"
        )
        handler_node.decorator_list = []
        seen_ids = set()
        pipeline_calls = []
        replies = []

        class ImmediateThread:
            def __init__(self, target, args, daemon):
                self.target = target
                self.args = args

            def start(self):
                self.target(*self.args)

        def register(_user_id, analysis_id):
            if analysis_id in seen_ids:
                return False
            seen_ids.add(analysis_id)
            return True

        namespace = {
            "time": time,
            "logging": logging,
            "threading": SimpleNamespace(Thread=ImmediateThread),
            "user_states": {"user": "explain_attachment"},
            "register_teaching_image_analysis": register,
            "reply_to_line": lambda _token, text: replies.append(text),
            "show_loading_animation": lambda *_args: None,
            "download_line_file": lambda *_args: SimpleNamespace(),
            "image_buffer_to_base64": lambda *_args: "base64",
            "process_teaching_image": (
                lambda *_args: pipeline_calls.append("openai-pipeline")
            ),
            "analyze_image": lambda *_args, **_kwargs: "general",
            "push_to_line": lambda *_args: None,
        }
        exec(compile(ast.fix_missing_locations(ast.Module(body=[handler_node], type_ignores=[])), str(APP_PATH), "exec"), namespace)
        event = SimpleNamespace(
            message=SimpleNamespace(id="duplicate-message"),
            source=SimpleNamespace(user_id="user"),
            reply_token="reply-token",
        )
        namespace["handle_image_message"](event)
        namespace["handle_image_message"](event)
        self.assertEqual([], pipeline_calls)
        self.assertEqual(set(), seen_ids)
        self.assertEqual(2, len(replies))
        self.assertTrue(all("対応を見合わせてる" in text for text in replies))

    def test_stale_failures_and_mode_changes_never_push_or_restore_state(self) -> None:
        for failure_stage in ("stage1", "stage2"):
            with self.subTest(failure_stage=failure_stage):
                app = load_teaching_tracking_functions()
                user_id = "failure-user"
                app.states[user_id] = "explain_attachment"
                register = app.namespace["register_teaching_image_analysis"]
                process = app.namespace["process_teaching_image"]
                register(user_id, "old-image", now=1.0)
                register(user_id, "new-image", now=2.0)
                if failure_stage == "stage1":
                    app.namespace["analyze_teaching_image_stage1"] = (
                        lambda *_args, **_kwargs: (_ for _ in ()).throw(ValueError("fail"))
                    )
                else:
                    app.namespace["solve_teaching_image_stage2"] = (
                        lambda *_args, **_kwargs: (_ for _ in ()).throw(ValueError("fail"))
                    )
                process(user_id, "old-image", "base64", time.perf_counter())
                self.assertEqual([], app.pushes)
                self.assertEqual([], app.reviews)
                self.assertEqual("explain_attachment", app.states[user_id])

        for destination in ("reset", "chat", "study"):
            with self.subTest(destination=destination):
                app = load_teaching_tracking_functions()
                user_id = "moving-user"
                app.states[user_id] = "explain_attachment"
                app.namespace["register_teaching_image_analysis"](
                    user_id, "running-image", now=1.0
                )
                app.namespace["invalidate_teaching_image_analysis"](user_id)
                if destination == "reset":
                    app.states[user_id] = "waiting_gen_intro"
                else:
                    app.states.pop(user_id, None)
                app.namespace["process_teaching_image"](
                    user_id, "running-image", "base64", time.perf_counter()
                )
                self.assertEqual([], app.pushes)
                self.assertEqual([], app.reviews)
                self.assertNotEqual("explain_review", app.states.get(user_id))

    def test_attachment_generation_prompt_teaches_the_full_reasoning_to_the_answer(self) -> None:
        source = APP_PATH.read_text(encoding="utf-8")
        module = ast.parse(source)
        required_constants = {
            "GEN_OJI_PROMPT",
            "EDUCATION_RULE_PROMPT",
            "IMAGE_ANALYSIS_PROMPT",
            "TEACHING_IMAGE_CHARACTER_PROMPT",
            "TEACHING_IMAGE_READING_PROMPT",
            "TEACHING_IMAGE_RESPONSE_PROMPT",
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
        namespace["logging"] = logging

        image_calls = []
        word_calls = []
        namespace["client"] = SimpleNamespace(
            responses=SimpleNamespace(
                create=lambda **kwargs: image_calls.append(kwargs)
                or SimpleNamespace(
                    output_text="画像解説",
                    status="completed",
                    incomplete_details=None,
                    usage=SimpleNamespace(
                        input_tokens=500,
                        output_tokens=700,
                        total_tokens=1200,
                    ),
                )
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

        teaching_response_meta = {}
        namespace["analyze_image"](
            "image-data",
            use_teaching_intro=True,
            response_meta=teaching_response_meta,
        )
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
            self.assertIn("その選択肢が正しい理由", prompt)
            self.assertIn("問題作成者向けの評価をしてはいけません", prompt)
            self.assertIn("問題ではない資料にも「正答」", prompt)
            self.assertIn("考えてみよう", prompt)
            self.assertIn("正答を明示せずに回答を終了することを原則禁止", prompt)
            self.assertIn("問題文の情報をすべて同じ重さで読み上げない", prompt)
            self.assertIn("今回の問いへの優先度が低い背景情報", prompt)
            self.assertIn("本来の説明をユーザーへ丸投げしていないか", prompt)

        self.assertEqual(
            namespace["GEN_OJI_PROMPT"]
            + "\n\n"
            + namespace["EDUCATION_RULE_PROMPT"]
            + "\n\n"
            + namespace["IMAGE_ANALYSIS_PROMPT"],
            image_general_prompt,
        )
        self.assertNotIn(
            "返信は原則として次の順番にしてください。",
            image_teaching_prompt,
        )
        for forbidden in (
            "良かった点",
            "良い点",
            "気になる点",
            "一番良かった点",
            "次に行うこと",
            "次の行動を一つに絞る",
            "問題そのものへの講評",
        ):
            self.assertNotIn(forbidden, image_teaching_prompt)
        self.assertIn("小さい文字、ぼやけた文字、見切れた部分を推測で補完しない", image_teaching_prompt)
        self.assertIn("読み取れない、または不明", image_teaching_prompt)
        self.assertIn("正答の推論を始める前", image_teaching_prompt)
        self.assertIn("選択肢A～Eの実際の文言", image_teaching_prompt)
        self.assertIn("歩幅／歩隔", image_teaching_prompt)
        self.assertIn("痙縮／麻痺", image_teaching_prompt)
        self.assertIn("「踵離地」を別表現へ変え", image_teaching_prompt)
        self.assertIn("「歩隔」を「歩幅」へ変え", image_teaching_prompt)
        self.assertIn("「膝過伸展は認めない」", image_teaching_prompt)
        self.assertIn("左右、数値、単位、屈曲・伸展", image_teaching_prompt)
        self.assertIn("推測で正答を出さない", image_teaching_prompt)
        self.assertIn("問いと選んだ正答が対応", image_teaching_prompt)
        self.assertIn("選択肢の文言を改変していない", image_teaching_prompt)
        self.assertIn("複数の要素", image_teaching_prompt)
        self.assertIn("全要素の根拠", image_teaching_prompt)
        self.assertIn("複合選択肢の各要素", image_teaching_prompt)
        self.assertIn("根拠が不足する要素", image_teaching_prompt)
        self.assertNotIn("膝屈曲位と膝伸展位", image_teaching_prompt)
        self.assertNotIn("腓腹筋の伸張性", image_teaching_prompt)
        self.assertIn("回答の最初の方で【正答】と主要根拠", image_teaching_prompt)
        self.assertIn("原則600～1,000文字程度", image_teaching_prompt)
        self.assertIn("問題文の全文を再掲せず", image_teaching_prompt)
        self.assertIn("迷いやすい1～2個だけ", image_teaching_prompt)
        self.assertEqual(1600, image_calls[0]["max_output_tokens"])
        self.assertEqual(1200, image_calls[1]["max_output_tokens"])
        self.assertNotIn(
            "B．下腿三頭筋筋力低下と腓腹筋の伸張性低下",
            image_teaching_prompt,
        )
        self.assertEqual(
            {
                "status": "completed",
                "incomplete_reason": "none",
                "input_tokens": 500,
                "output_tokens": 700,
                "total_tokens": 1200,
                "answer_chars": 4,
            },
            teaching_response_meta,
        )
        self.assertIn("良かった点や重要な点", image_general_prompt)
        self.assertIn("気になる点", image_general_prompt)
        self.assertIn("次に行うこと", image_general_prompt)

        self.assertNotIn("これは「教えて源さん」における最優先", image_general_prompt)
        self.assertNotIn("これは「教えて源さん」における最優先", word_general_prompt)
        self.assertIn(
            'text="だいたい理解できたか？＾＾\\n次はどうする？"',
            source,
        )
        self.assertIn('label="わかった！"', source)
        self.assertIn('label="まだ質問がある！"', source)


if __name__ == "__main__":
    unittest.main()
