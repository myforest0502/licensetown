"""Authenticated, feature-flagged Stripe sandbox routes.

No public CTA points here. These routes are only a sandbox lifecycle harness and
are deliberately disabled unless ENABLE_STRIPE_SANDBOX_CHECKOUT is true.
"""

from __future__ import annotations

import logging

from flask import Blueprint, abort, redirect, render_template_string, request, url_for

from goukaku_ui import authorized_dashboard_learner
from stripe_checkout_service import (
    create_customer_portal_session,
    create_subscription_checkout_session,
    stripe_sandbox_checkout_enabled,
)


logger = logging.getLogger(__name__)
stripe_billing_ui = Blueprint("stripe_billing_ui", __name__)


_SANDBOX_TEST_PAGE = """
<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>LicenseTown Stripe sandbox test</title>
  <style>
    body { font-family: sans-serif; max-width: 640px; margin: 48px auto; padding: 0 20px; line-height: 1.6; }
    .box { border: 2px solid #6b5cff; border-radius: 16px; padding: 24px; }
    button { width: 100%; padding: 14px; margin: 8px 0; border: 0; border-radius: 10px; font-weight: 700; cursor: pointer; }
    .checkout { background: #635bff; color: white; }
    .portal { background: #eee; color: #222; }
    small { display: block; margin-top: 16px; color: #555; }
  </style>
</head>
<body>
  <div class="box">
    <h1>Stripe サンドボックス確認</h1>
    <p>これは LicenseTown の決済テスト専用画面です。実際の請求は発生しません。</p>
    <form method="post" action="{{ checkout_url }}">
      <input type="hidden" name="token" value="{{ token }}">
      <button class="checkout" type="submit">サンドボックス決済を開始</button>
    </form>
    <form method="post" action="{{ portal_url }}">
      <input type="hidden" name="token" value="{{ token }}">
      <button class="portal" type="submit">Customer Portal を開く</button>
    </form>
    <small>Customer Portal は、Checkout 完了後に Stripe customer の紐付けができてから使用します。</small>
  </div>
</body>
</html>
"""


def _enabled_or_404() -> None:
    if not stripe_sandbox_checkout_enabled():
        abort(404)


def _object_url(value) -> str | None:
    if isinstance(value, dict):
        result = value.get("url")
    else:
        result = getattr(value, "url", None)
    result = str(result or "").strip()
    return result or None


@stripe_billing_ui.get("/stripe/sandbox/test")
def sandbox_test_page():
    """Authenticated human test page for the sandbox lifecycle only."""
    _enabled_or_404()
    token = request.args.get("token")
    authorized_dashboard_learner(token)
    return render_template_string(
        _SANDBOX_TEST_PAGE,
        token=token,
        checkout_url=url_for(".sandbox_checkout"),
        portal_url=url_for(".sandbox_portal"),
    )


@stripe_billing_ui.post("/stripe/sandbox/checkout")
def sandbox_checkout():
    _enabled_or_404()
    token = request.form.get("token")
    user_id = authorized_dashboard_learner(token)
    # Never send the signed dashboard token to Stripe in success/cancel URLs.
    success_url = url_for("site_ui.home", checkout="success", _external=True)
    cancel_url = url_for("site_ui.home", checkout="cancel", _external=True)
    try:
        session = create_subscription_checkout_session(
            user_id,
            success_url=success_url,
            cancel_url=cancel_url,
        )
    except (RuntimeError, ValueError):
        logger.exception("Stripe sandbox Checkout is not ready")
        abort(503)
    except Exception:
        logger.exception("Stripe sandbox Checkout creation failed")
        abort(502)
    destination = _object_url(session)
    if not destination:
        abort(502)
    return redirect(destination, code=303)


@stripe_billing_ui.post("/stripe/sandbox/portal")
def sandbox_portal():
    _enabled_or_404()
    token = request.form.get("token")
    user_id = authorized_dashboard_learner(token)
    return_url = url_for("site_ui.home", _external=True)
    try:
        session = create_customer_portal_session(user_id, return_url=return_url)
    except (RuntimeError, ValueError):
        logger.exception("Stripe sandbox portal is not ready")
        abort(503)
    except Exception:
        logger.exception("Stripe sandbox portal creation failed")
        abort(502)
    destination = _object_url(session)
    if not destination:
        abort(502)
    return redirect(destination, code=303)
