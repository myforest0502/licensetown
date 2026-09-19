from __future__ import annotations

import time

from linebot.models import MessageAction, QuickReplyButton
from question_bank import select_random_questions


ONE_QUESTION_COMMAND = "源さんと1問だけ"


def install_one_question_starter(legacy) -> None:
    """Add a safe one-question learning entry without changing the normal 5/30 flow."""
    original_process_study_flow_command = legacy.process_study_flow_command

    def start_one_question(reply_token, user_id):
        questions = select_random_questions(1)
        question = questions[0]
        now = time.time()
        legacy.user_modes[user_id] = "study"
        legacy.quiz_category_selections.pop(user_id, None)
        legacy.study_sessions[user_id] = {
            "session_id": str(time.time_ns()),
            "status": "waiting_for_answers",
            "current_set": 1,
            "question_count": 1,
            "questions_per_set": 1,
            "total_sets": 1,
            "questions": [question],
            "all_questions": [question],
            "all_answers": {},
            "expected_numbers": [1],
            "mode": "study",
            "started_at": now,
            "active_started_at": now,
            "nekketsu_correct": 0,
            "category_small": None,
            "session_kind": "one_question_starter",
        }
        legacy.reply_current_quiz(
            reply_token,
            legacy.study_sessions[user_id],
            intro_text=(
                "30問やれとは言わんｗ\n"
                "まず1問だけ付き合え＾＾\n"
                "これで今日の一歩は始まるぞ。"
            ),
        )

    def process_study_flow_command(reply_token, user_id, user_message):
        if str(user_message).strip() == ONE_QUESTION_COMMAND:
            try:
                start_one_question(reply_token, user_id)
            except Exception:
                legacy.logging.exception("One-question starter failed: user_id=%s", user_id)
                legacy.reply_to_line(
                    reply_token,
                    "おう、悪い。1問の準備でズッコケたｗ\n少し待って、もう一度押してくれ＾＾",
                )
            return True
        return original_process_study_flow_command(reply_token, user_id, user_message)

    legacy.process_study_flow_command = process_study_flow_command


def one_question_quick_reply_item():
    return QuickReplyButton(
        action=MessageAction(label="☝️ 源さんと1問だけ", text=ONE_QUESTION_COMMAND)
    )
