"""Authenticated, feature-flagged Stripe sandbox routes.

No public CTA points here. These routes are only a sandbox lifecycle harness and
are deliberately disabled unless ENABLE_STRIPE_SANDBOX_CHECKOUT is true.
"""

from __future__ import annotations

import logging

from flask import Blueprint, abort, redirect, request, url_for

from goukaku_ui import authorized_dashboard_learner
from stripe_checkout_service import (
    create_customer_portal_session,
    create_subscription_checkout_session,
    stripe_sandbox_checkout_enabled,
)


logger = logging.getLogger(__name__)
stripe_billing_ui = Blueprint("stripe_billing_ui", __name__)


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
