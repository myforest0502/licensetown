"""Read-only daily review for questions answered incorrectly today.

The feature intentionally does not create attempts, mutate Knowledge Node state,
or call OpenAI. It only re-renders saved formal answers/explanations for questions
that had at least one incorrect attempt on the current JST calendar day.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Iterable

from linebot.models import MessageAction, QuickReply, QuickReplyButton, TextSendMessage


JST = timezone(timedelta(hours=9))
REVIEW_COMMAND = "本日の振り返り"
NEXT_REVIEW_COMMAND = "振り返り：次の5問"
END_REVIEW_COMMAND = "振り返りを終わる"
PAGE_SIZE = 5


def _as_datetime(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        parsed = value
    elif value:
        try:
            parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except (TypeError, ValueError):
            return None
    else:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def wrong_question_ids_for_jst_day(
    attempts: Iterable[dict[str, Any]],
    *,
    target_date=None,
) -> list[str]:
    """Return unique Q IDs that were wrong at least once on one JST date.

    A later correct answer does not remove the Q from the review list because the
    purpose is to retain every question the learner stumbled on that day.
    """
    day = target_date or datetime.now(JST).date()
    seen: set[str] = set()
    rows: list[tuple[datetime, str]] = []

    for item in attempts or ():
        if item.get("is_correct") is not False:
            continue
        question_id = str(item.get("question_id") or "").strip()
        if not question_id:
            continue
        answered_at = _as_datetime(item.get("answered_at") or item.get("attempted_at"))
        if answered_at is None or answered_at.astimezone(JST).date() != day:
            continue
        rows.append((answered_at, question_id))

    rows.sort(key=lambda row: row[0])
    result: list[str] = []
    for _, question_id in rows:
        if question_id in seen:
            continue
        seen.add(question_id)
        result.append(question_id)
    return result


def build_review_block(question: dict[str, Any], display_answer) -> str:
    """Render answer/explanation only, intentionally omitting the question stem."""
    question_id = str(question.get("id") or "")
    correct_answer = display_answer(question)
    explanation = str(question.get("explanation") or "解説はありません。").strip()
    choice_explanations = question.get("choice_explanations") or {}
    choice_text = ""
    if choice_explanations:
        choice_text = "\n" + "\n".join(
            f"{label}：{text}" for label, text in choice_explanations.items()
        )
    text = (
        f"【{question_id}】\n"
        f"正解：{correct_answer}\n"
        f"解説：{explanation}{choice_text}"
    )
    if len(text) > 4400:
        return text[:4399] + "…"
    return text


def install_daily_wrong_review(legacy) -> None:
    """Compose the review command into the legacy LINE flow at runtime."""
    original_process = legacy.process_study_flow_command
    review_sessions: dict[str, dict[str, Any]] = {}

    def _send_page(reply_token: str, user_id: str) -> None:
        state = review_sessions.get(user_id)
        if not state:
            legacy.reply_to_line(reply_token, "本日の振り返りを開き直してくれ＾＾")
            return

        ids = state["question_ids"]
        start = int(state.get("index", 0))
        end = min(start + PAGE_SIZE, len(ids))
        page_ids = ids[start:end]
        messages: list[TextSendMessage] = []
        for offset, question_id in enumerate(page_ids):
            question = legacy.get_quiz_question(question_id)
            block = build_review_block(question, legacy.get_display_answer)
            if offset == 0:
                block = (
                    f"📝 本日の振り返り\n"
                    f"今日つまずいた問題：{len(ids)}問\n"
                    f"表示：{start + 1}〜{end}問目\n\n" + block
                )
            messages.append(TextSendMessage(text=block))

        state["index"] = end
        has_next = end < len(ids)
        quick_items = []
        if has_next:
            quick_items.append(QuickReplyButton(action=MessageAction(
                label="次の5問",
                text=NEXT_REVIEW_COMMAND,
            )))
        quick_items.extend([
            QuickReplyButton(action=MessageAction(
                label="振り返りを終わる",
                text=END_REVIEW_COMMAND,
            )),
            QuickReplyButton(action=MessageAction(
                label="ホームに戻る",
                text="ホームに戻る",
            )),
        ])
        if messages:
            messages[-1].quick_reply = QuickReply(items=quick_items)
            legacy.line_bot_api.reply_message(reply_token, messages)
        if not has_next:
            review_sessions.pop(user_id, None)

    def _start(reply_token: str, user_id: str) -> None:
        question_ids = wrong_question_ids_for_jst_day(legacy.get_question_attempts(user_id))
        if not question_ids:
            review_sessions.pop(user_id, None)
            legacy.line_bot_api.reply_message(
                reply_token,
                TextSendMessage(
                    text=(
                        "📝 本日の振り返り\n\n"
                        "今日は振り返る不正解問題はないぞ＾＾\n"
                        "そのまま次へ進んで大丈夫だ！"
                    ),
                    quick_reply=QuickReply(items=[
                        QuickReplyButton(action=MessageAction(
                            label="ホームに戻る", text="ホームに戻る"
                        )),
                    ]),
                ),
            )
            return
        review_sessions[user_id] = {"question_ids": question_ids, "index": 0}
        _send_page(reply_token, user_id)

    def process_study_flow_command(reply_token, user_id, user_message):
        if user_message == REVIEW_COMMAND:
            _start(reply_token, user_id)
            return True
        if user_message == NEXT_REVIEW_COMMAND and user_id in review_sessions:
            _send_page(reply_token, user_id)
            return True
        if user_message == END_REVIEW_COMMAND and user_id in review_sessions:
            review_sessions.pop(user_id, None)
            legacy.return_home(reply_token, user_id, interrupt=False)
            return True
        return original_process(reply_token, user_id, user_message)

    legacy.process_study_flow_command = process_study_flow_command
    legacy.daily_wrong_review_sessions = review_sessions
