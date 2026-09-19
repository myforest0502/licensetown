"""Read-only learner-screen preview for an already-authorized supporter.

This is a development/product-design convenience so the linked supporter can
inspect the learner's actual 合格への道 presentation without borrowing the
learner's LINE device. The preview uses the same persisted learner data and
learner-navigation builder, but all learner actions are inert.
"""

from __future__ import annotations

from functools import wraps
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from flask import render_template, request, url_for

from goukaku_ui import authorized_supporter_learner, build_dashboard


PREVIEW_QUERY_KEY = "learner_preview"
PREVIEW_QUERY_VALUE = "1"
TARGET_ENDPOINT = "goukaku_ui.supporter_goukaku_home"
TARGET_PATH = "/supporter/goukaku-no-michi"


def _with_preview_flag(url: str, enabled: bool) -> str:
    parts = urlsplit(url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    if enabled:
        query[PREVIEW_QUERY_KEY] = PREVIEW_QUERY_VALUE
    else:
        query.pop(PREVIEW_QUERY_KEY, None)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


def install_supporter_learner_preview_bridge(app) -> None:
    """Add an inert learner-view toggle to the existing supporter dashboard URL."""
    original = app.view_functions.get(TARGET_ENDPOINT)
    if original is None or getattr(original, "_lt_learner_preview_bridge", False):
        return

    @wraps(original)
    def wrapped_supporter_goukaku_home(*args, **kwargs):
        if request.args.get(PREVIEW_QUERY_KEY) != PREVIEW_QUERY_VALUE:
            return original(*args, **kwargs)

        token = request.args.get("token")
        _, learner_id = authorized_supporter_learner(
            token,
            request.args.get("learner_user_id"),
        )
        dashboard = build_dashboard(learner_id, include_learner_navigation=True)
        return render_template(
            "goukaku/home.html",
            dashboard=dashboard,
            dashboard_token=None,
            dashboard_title="合格への道（本人画面プレビュー）",
            read_only=False,
            learner_preview=True,
            subjects_url=None,
            supporter_return_url=_with_preview_flag(request.url, False),
            line_official_account_id="",
            liff_id="",
        )

    wrapped_supporter_goukaku_home._lt_learner_preview_bridge = True
    app.view_functions[TARGET_ENDPOINT] = wrapped_supporter_goukaku_home

    @app.after_request
    def _add_preview_switch(response):
        if request.path != TARGET_PATH or response.status_code != 200:
            return response
        if not response.content_type or "text/html" not in response.content_type:
            return response

        html = response.get_data(as_text=True)
        enabled = request.args.get(PREVIEW_QUERY_KEY) == PREVIEW_QUERY_VALUE
        target = _with_preview_flag(request.url, not enabled)
        label = "見守り画面へ戻る" if enabled else "本人画面をプレビュー"
        banner = (
            '<div data-lt-learner-preview-switch style="position:sticky;top:0;z-index:9999;'
            'padding:10px 14px;text-align:center;background:#fff7df;border-bottom:1px solid #ead59a">'
            f'<a href="{target}" style="display:inline-block;padding:9px 18px;border-radius:999px;'
            'background:#146c43;color:#fff;text-decoration:none;font-weight:700">'
            f'{label}</a></div>'
        )
        if "<body>" in html and "data-lt-learner-preview-switch" not in html:
            html = html.replace("<body>", "<body>" + banner, 1)
            response.set_data(html)
            response.headers["Content-Length"] = str(len(response.get_data()))
        return response
