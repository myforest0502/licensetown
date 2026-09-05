"""Production composition for LicenseTown.

This module keeps the legacy Flask/LINE application intact while wiring the
learner-facing "教えて源さん" path to the formal-bank term explainer.
The old consultation command remains backward compatible, but it is no longer
advertised from HOME.
"""

from __future__ import annotations

import app as legacy
from linebot.models import (
    MessageAction,
    QuickReply,
    QuickReplyButton,
    TextSendMessage,
    URIAction,
)

from term_explainer import explain_term


_original_create_text_response = legacy.create_text_response


def create_text_response(user_message, mode="normal"):
    """Use saved formal data for term explanations; preserve other legacy modes."""
    if mode == "gensan_explain":
        return explain_term(user_message)
    return _original_create_text_response(user_message, mode)


def create_home_message(user_id=None):
    """Expose the exam-term tool instead of free-form consultation on HOME."""
    dashboard_url = legacy.build_dashboard_url(user_id)
    return TextSendMessage(
        text=(
            "お！きたなｗ\n初めて来た奴も、戻ってきた奴も、お疲れさん＾＾\n"
            "ここはお前たちの〝家”だよ＾＾\nここから全てが始まる…\n"
            "さあ！行き先はお前が決めるんだ！"
        ),
        quick_reply=QuickReply(items=[
            QuickReplyButton(action=URIAction(
                label="📊 合格への道",
                uri=dashboard_url,
            )),
            QuickReplyButton(action=MessageAction(
                label="📘 勉強する！",
                text="勉強する",
            )),
            QuickReplyButton(action=MessageAction(
                label="❓ 教えて源さん",
                text="教えて源さん",
            )),
            QuickReplyButton(action=MessageAction(
                label="🔥 熱血モード",
                text="熱血モード",
            )),
        ]),
    )


# Registered LINE callbacks resolve these names from the legacy app module at
# call time, so production behavior can be composed without rewriting app.py.
legacy.create_text_response = create_text_response
legacy.create_home_message = create_home_message

# Gunicorn entrypoint.
app = legacy.app
