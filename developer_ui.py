"""Internal developer-only diagnostics routes.

These routes are intentionally separate from learner/supporter orchestration. They
fail closed unless an explicit deployment secret is configured.
"""

from __future__ import annotations

import hmac
import os

from flask import Blueprint, abort, render_template, request, url_for

from goukaku_ui import build_dashboard
from pilot_diagnostics import build_pilot_diagnostics


developer_ui = Blueprint("developer_ui", __name__, url_prefix="/internal")


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


@developer_ui.route("")
@developer_ui.route("/")
def index():
    token = require_developer_authorization()
    learner_id = request.args.get("learner_user_id", "").strip()
    return render_template(
        "internal/index.html",
        internal_token=token,
        learner_id=learner_id,
        pilot_url=(
            url_for("developer_ui.pilot_diagnostics", token=token, learner_user_id=learner_id)
            if learner_id else None
        ),
        preview_url=(
            url_for("developer_ui.learner_preview", token=token, learner_user_id=learner_id)
            if learner_id else None
        ),
    )


@developer_ui.route("/pilot-diagnostics")
def pilot_diagnostics():
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
        supporter_token=None,
        internal_token=token,
        internal_mode=True,
    )


@developer_ui.route("/learner-preview")
def learner_preview():
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
            "developer_ui.index", token=token, learner_user_id=learner_id
        ),
        line_official_account_id="",
        liff_id="",
    )
