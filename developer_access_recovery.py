"""Internal-only recovery hub for LicenseTown developer and learner QA views."""

from __future__ import annotations

from urllib.parse import parse_qs, urlsplit

from flask import abort, render_template, request, url_for

from developer_ui import require_developer_authorization
from goukaku_ui import authorized_supporter_learner


ROUTE = "/internal/recovery"
ENDPOINT = "internal_recovery"


def _supporter_token_from_input(value: str) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""
    if "://" not in raw:
        return raw
    try:
        query = parse_qs(urlsplit(raw).query, keep_blank_values=False)
    except ValueError:
        return ""
    values = query.get("token") or []
    return str(values[0]).strip() if values else ""


def install_developer_access_recovery(app) -> None:
    if ENDPOINT in app.view_functions:
        return

    def internal_recovery():
        token = require_developer_authorization()
        learner_id = str(request.args.get("learner_user_id") or "").strip()
        supporter_input = str(request.args.get("supporter") or "").strip()
        error = ""

        if supporter_input and not learner_id:
            supporter_token = _supporter_token_from_input(supporter_input)
            if not supporter_token:
                error = "見守りURLまたはsupporter tokenを確認してください。"
            else:
                try:
                    _, learner_id = authorized_supporter_learner(supporter_token)
                except Exception as exc:
                    code = getattr(exc, "code", None)
                    if code in {403, 404}:
                        error = "見守りURLから学習者を確認できませんでした。"
                    else:
                        raise

        urls = None
        if learner_id:
            urls = {
                "developer": url_for(
                    "site_ui.internal_index",
                    token=token,
                    learner_user_id=learner_id,
                ),
                "preview": url_for(
                    "site_ui.internal_learner_preview",
                    token=token,
                    learner_user_id=learner_id,
                ),
                "diagnostics": url_for(
                    "site_ui.internal_pilot_diagnostics",
                    token=token,
                    learner_user_id=learner_id,
                ),
                "phase11": url_for(
                    "internal_phase11_gates",
                    token=token,
                    learner_user_id=learner_id,
                ),
            }

        return render_template(
            "internal/recovery.html",
            internal_token=token,
            learner_id=learner_id,
            supporter_input=supporter_input,
            error=error,
            urls=urls,
        )

    app.add_url_rule(ROUTE, ENDPOINT, internal_recovery, methods=["GET"])
