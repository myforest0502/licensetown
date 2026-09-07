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
import developer_ui as developer_ui_module
import goukaku_ui as goukaku_module
import supporter_learner_preview_bridge as supporter_preview_module
from linebot.models import (
    MessageAction,
    QuickReply,
    QuickReplyButton,
    TextSendMessage,
    URIAction,
)

from daily_wrong_review import REVIEW_COMMAND, install_daily_wrong_review
from dashboard_progress_trend import install_dashboard_progress_trend
from developer_access_recovery import install_developer_access_recovery
from phase11_gate_ui import install_phase11_gate_ui
from prerequisite_attempt_cache import install_prerequisite_attempt_cache
from site_direct_line_cta import install_site_direct_line_cta
from site_marketing_hotfix import install_site_marketing_hotfix
from site_marketing_refresh import install_site_marketing_refresh
from site_marketing_viewport_fix import install_site_marketing_viewport_fix
from supporter_learner_preview_bridge import install_supporter_learner_preview_bridge
from term_explainer import explain_term


logger = logging.getLogger(__name__)
_original_create_text_response = legacy.create_text_response


def create_text_response(user_message, mode="normal"):
    """Use saved formal data for term explanations; preserve other legacy modes."""
    if mode == "gensan_explain":
        return explain_term(user_message)
    return _original_create_text_response(user_message, mode)


def create_home_message(user_id=None):
    """Expose core learner tools from HOME."""
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
                label="📝 本日の振り返り",
                text=REVIEW_COMMAND,
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
install_dashboard_progress_trend(legacy, goukaku_module)
# Preview helpers imported build_dashboard by value before composition. Rebind
# them to the same decorated builder used by the live learner route.
supporter_preview_module.build_dashboard = goukaku_module.build_dashboard
developer_ui_module.build_dashboard = goukaku_module.build_dashboard
_developer_dashboard_builder = developer_ui_module.build_dashboard


def _build_full_developer_preview_dashboard(learner_id):
    """Render the exact paid learner dashboard data path for development QA."""
    return _developer_dashboard_builder(learner_id, include_learner_navigation=True)


developer_ui_module.build_dashboard = _build_full_developer_preview_dashboard
install_daily_wrong_review(legacy)
legacy.create_text_response = create_text_response
legacy.create_home_message = create_home_message
# Flask executes after_request handlers in reverse registration order.
# Register the viewport pass first so it runs last. The direct CTA pass is
# registered before hotfix so it runs after hotfix and restores the verified
# onboarding link as the final public action.
install_site_marketing_viewport_fix(legacy.app)
install_site_direct_line_cta(legacy.app)
install_site_marketing_hotfix(legacy.app)
install_site_marketing_refresh(legacy.app)
install_phase11_gate_ui(legacy.app)
install_supporter_learner_preview_bridge(legacy.app)
install_developer_access_recovery(legacy.app)

_apply_rich_menu_v2_if_requested()

# Gunicorn entrypoint.
app = legacy.app
