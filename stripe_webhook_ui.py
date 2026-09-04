"""Minimal Stripe webhook HTTP boundary for LicenseTown.

This blueprint performs no checkout creation and exposes no paid gating. It only
accepts signed Stripe webhook POSTs and delegates trusted subscription events to
the provider-agnostic entitlement service.
"""

from __future__ import annotations

import logging

from flask import Blueprint, jsonify, request
from stripe.error import SignatureVerificationError

from stripe_entitlement_adapter import process_stripe_webhook


logger = logging.getLogger(__name__)
stripe_webhook_ui = Blueprint("stripe_webhook_ui", __name__)


@stripe_webhook_ui.post("/stripe/webhook")
def stripe_webhook():
    payload = request.get_data(cache=False)
    signature = request.headers.get("Stripe-Signature", "")
    try:
        result = process_stripe_webhook(payload, signature)
    except (SignatureVerificationError, ValueError) as exc:
        logger.warning("Stripe webhook rejected: %s", type(exc).__name__)
        return jsonify({"ok": False}), 400
    except RuntimeError:
        logger.exception("Stripe webhook is not configured")
        return jsonify({"ok": False}), 503
    except Exception:
        logger.exception("Stripe webhook processing failed")
        return jsonify({"ok": False}), 500

    return jsonify(
        {
            "ok": True,
            "handled": bool(result.get("handled")),
            "duplicate": bool(result.get("duplicate", False)),
            "stale": bool(result.get("stale", False)),
        }
    )
