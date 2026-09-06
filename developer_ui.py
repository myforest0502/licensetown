"""Internal developer-only diagnostics and operator routes.

The public app already registers ``site_ui``. To avoid touching the large Flask
entrypoint, these routes are attached to that existing blueprint before it is
registered. Legacy supporter diagnostics/preview URLs never accept supporter
authorization; an already-authorized developer URL is redirected into /internal.
"""

from __future__ import annotations

import hmac
import os

from flask import abort, redirect, render_template, request, url_for

from developer_status import build_developer_system_status
from email_delivery import EmailDeliveryError, send_feedback_reply
from feedback_store import (
    FeedbackStoreUnavailable,
    FeedbackValidationError,
    VALID_CATEGORIES,
    get_feedback_for_operator,
    list_feedback_for_operator,
    mark_email_delivery,
    set_operator_reply,
)
from goukaku_ui import build_dashboard
from pilot_diagnostics import build_pilot_diagnostics
from supporter_performance import begin_request, finish_request


LEGACY_DIAGNOSTICS_PATH = "/supporter/pilot-diagnostics"
LEGACY_PREVIEW_PATH = "/supporter/goukaku-no-michi/learner-preview"
LEGACY_DEVELOPER_PATHS = {LEGACY_DIAGNOSTICS_PATH, LEGACY_PREVIEW_PATH}


def _configured_token() -> str:
    return os.getenv("LT_INTERNAL_ADMIN_TOKEN", "").strip()


def developer_authorized(token: str | None) -> bool:
    expected = _configured_token()
    supplied = str(token or "").strip()
    return bool(expected and supplied and hmac.compare_digest(expected, supplied))


def require_developer_authorization() -> str:
    token = request.headers.get("X-LT-Developer-Token") or request.args.get("token")
    if not _configured_token():
        abort(404)
    if not developer_authorized(token):
        abort(403)
    return str(token)


def _decorate_feedback(item):
    if not item:
        return item
    item["category_label"] = VALID_CATEGORIES.get(str(item.get("category") or ""), "その他")
    return item


def register_developer_routes(blueprint) -> None:
    """Attach developer-only routes and legacy-route guard to ``blueprint``."""

    @blueprint.before_app_request
    def _begin_supporter_perf_probe():
        if request.path == "/supporter":
            begin_request()
        return None

    @blueprint.after_app_request
    def _finish_supporter_perf_probe(response):
        if request.path == "/supporter":
            finish_request(response.status_code)
        return response

    @blueprint.before_app_request
    def _guard_legacy_developer_routes():
        if request.path not in LEGACY_DEVELOPER_PATHS:
            return None
        token = request.headers.get("X-LT-Developer-Token") or request.args.get("token")
        if not developer_authorized(token):
            abort(404)
        learner_id = request.args.get("learner_user_id", "").strip()
        if request.path == LEGACY_DIAGNOSTICS_PATH:
            return redirect(
                url_for(
                    "site_ui.internal_pilot_diagnostics",
                    token=token,
                    learner_user_id=learner_id,
                    period=request.args.get("period", "7"),
                )
            )
        return redirect(
            url_for(
                "site_ui.internal_learner_preview",
                token=token,
                learner_user_id=learner_id,
            )
        )

    @blueprint.route("/internal", endpoint="internal_index")
    @blueprint.route("/internal/", endpoint="internal_index_slash")
    def _internal_index():
        token = require_developer_authorization()
        learner_id = request.args.get("learner_user_id", "").strip()
        return render_template(
            "internal/index.html",
            internal_token=token,
            learner_id=learner_id,
            system_status=build_developer_system_status(),
            feedback_url=url_for("site_ui.internal_feedback", token=token),
            pilot_url=(
                url_for(
                    "site_ui.internal_pilot_diagnostics",
                    token=token,
                    learner_user_id=learner_id,
                )
                if learner_id
                else None
            ),
            preview_url=(
                url_for(
                    "site_ui.internal_learner_preview",
                    token=token,
                    learner_user_id=learner_id,
                )
                if learner_id
                else None
            ),
        )

    @blueprint.route("/internal/feedback", methods=["GET", "POST"], endpoint="internal_feedback")
    def _internal_feedback():
        token = require_developer_authorization()
        public_id = str(request.values.get("public_id") or "").strip()
        notice = ""
        error = ""

        if request.method == "POST":
            action = str(request.form.get("action") or "").strip()
            selected = get_feedback_for_operator(public_id)
            if not selected:
                abort(404)

            try:
                if action == "reply":
                    stored = set_operator_reply(
                        public_id=public_id,
                        reply=str(request.form.get("reply") or ""),
                        status="responded",
                    )
                    if not stored:
                        abort(404)
                    selected = get_feedback_for_operator(public_id)
                elif action == "retry":
                    if not str(selected.get("operator_reply") or "").strip():
                        raise FeedbackValidationError("再送できる保存済み返信がありません。")
                else:
                    abort(400)

                if selected and selected.get("email"):
                    try:
                        delivery = send_feedback_reply(
                            public_id=public_id,
                            to_email=str(selected["email"]),
                            reply=str(selected.get("operator_reply") or ""),
                        )
                    except EmailDeliveryError as exc:
                        mark_email_delivery(public_id=public_id, delivery_status="failed")
                        error = f"返信はNeonに保存しましたが、メール送信に失敗しました: {exc}"
                    else:
                        mark_email_delivery(
                            public_id=public_id,
                            delivery_status=delivery.delivery_state,
                        )
                        notice = (
                            "返信を保存し、メール配送を確認しました。"
                            if delivery.delivery_state == "sent"
                            else "返信を保存し、メール送信を受け付けました。配送確認待ちです。"
                        )
                else:
                    notice = "返信をNeonに保存しました。メールアドレス未入力のためメール送信はありません。"
            except FeedbackValidationError as exc:
                error = str(exc)

        try:
            items = [_decorate_feedback(item) for item in list_feedback_for_operator(limit=100)]
            selected = _decorate_feedback(get_feedback_for_operator(public_id)) if public_id else None
        except FeedbackStoreUnavailable:
            items = []
            selected = None
            error = "お問い合わせの保存先に接続できません。"

        return render_template(
            "internal/feedback.html",
            internal_token=token,
            items=items,
            selected=selected,
            notice=notice,
            error=error,
        )

    @blueprint.route(
        "/internal/pilot-diagnostics", endpoint="internal_pilot_diagnostics"
    )
    def _internal_pilot_diagnostics():
        token = require_developer_authorization()
        learner_id = request.args.get("learner_user_id", "").strip()
        if not learner_id:
            abort(400)
        period = request.args.get("period", "7")
        if period not in {"7", "30", "all"}:
            period = "7"
        return render_template(
            "goukaku/supporter_pilot_diagnostics.html",
            diagnostics=build_pilot_diagnostics(learner_id, period),
            learner_id=learner_id,
            supporter_token=token,
            internal_token=token,
            internal_mode=True,
        )

    @blueprint.route("/internal/learner-preview", endpoint="internal_learner_preview")
    def _internal_learner_preview():
        token = require_developer_authorization()
        learner_id = request.args.get("learner_user_id", "").strip()
        if not learner_id:
            abort(400)
        return render_template(
            "goukaku/home.html",
            dashboard=build_dashboard(learner_id),
            dashboard_token=None,
            dashboard_title="合格への道",
            read_only=False,
            learner_preview=True,
            subjects_url=None,
            supporter_return_url=url_for(
                "site_ui.internal_index",
                token=token,
                learner_user_id=learner_id,
            ),
            line_official_account_id="",
            liff_id="",
        )
