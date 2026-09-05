"""Production composition for LicenseTown.

This module keeps the legacy Flask/LINE application intact while wiring the
learner-facing "教えて源さん" path to the formal-bank term explainer.
The old consultation command remains backward compatible, but it is no longer
advertised from HOME.
"""

from __future__ import annotations

import logging
import os

import app as legacy
from linebot.models import (
    MessageAction,
    QuickReply,
    QuickReplyButton,
    TextSendMessage,
    URIAction,
)

from prerequisite_attempt_cache import install_prerequisite_attempt_cache
from site_marketing_hotfix import install_site_marketing_hotfix
from site_marketing_refresh import install_site_marketing_refresh
from site_marketing_viewport_fix import install_site_marketing_viewport_fix
from term_explainer import explain_term


logger = logging.getLogger(__name__)
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


def _apply_rich_menu_v2_if_requested() -> None:
    """One-shot deployment hook used only when explicitly enabled in Render."""
    if os.getenv("LT_APPLY_RICH_MENU_V2_ON_BOOT", "").strip().lower() not in {"1", "true", "yes", "on"}:
        return
    try:
        from scripts.setup_rich_menu import create_and_set_default

        rich_menu_id = create_and_set_default(set_default=True)
        logger.warning("lt_rich_menu_v2_apply status=ok rich_menu_id=%s", rich_menu_id)
    except Exception:
        logger.exception("lt_rich_menu_v2_apply status=error")
        raise


# Registered LINE callbacks resolve these names from the legacy app module at
# call time, so production behavior can be composed without rewriting app.py.
install_prerequisite_attempt_cache(legacy)
legacy.create_text_response = create_text_response
legacy.create_home_message = create_home_message
# Flask executes after_request handlers in reverse registration order.
# Register the viewport pass first so it runs last, after refresh + hotfix.
install_site_marketing_viewport_fix(legacy.app)
install_site_marketing_hotfix(legacy.app)
install_site_marketing_refresh(legacy.app)

_apply_rich_menu_v2_if_requested()

# Gunicorn entrypoint.
app = legacy.app
