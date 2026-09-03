"""Internal developer-only diagnostics routes.

The public app already registers ``site_ui``.  To avoid touching the large Flask
entrypoint, these routes are attached to that existing blueprint before it is
registered.  Legacy supporter diagnostics/preview URLs are blocked globally so
a supporter token cannot reach developer-only screens.
"""

from __future__ import annotations

import hmac
import os

from flask import abort, render_template, request, url_for

from goukaku_ui import build_dashboard
from pilot_diagnostics import build_pilot_diagnostics


LEGACY_DEVELOPER_PATHS = {
    "/supporter/pilot-diagnostics",
    "/supporter/goukaku-no-michi/learner-preview",
}


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


def register_developer_routes(blueprint) -> None:
    """Attach developer-only routes and legacy-route guard to ``blueprint``."""

    @blueprint.before_app_request
    def _block_legacy_developer_routes():
        if request.path in LEGACY_DEVELOPER_PATHS:
            abort(404)

    @blueprint.route("/internal", endpoint="internal_index")
    @blueprint.route("/internal/", endpoint="internal_index_slash")
    def _internal_index():
        token = require_developer_authorization()
        learner_id = request.args.get("learner_user_id", "").strip()
        return render_template(
            "internal/index.html",
            internal_token=token,
            learner_id=learner_id,
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
            "internal/pilot_diagnostics.html",
            diagnostics=build_pilot_diagnostics(learner_id, period),
            learner_id=learner_id,
            internal_token=token,
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
