"""Stripe -> LicenseTown entitlement adapter.

Only verified Stripe webhook payloads may reach the provider-agnostic
``payment_entitlement`` service. Browser redirects are never authoritative.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Mapping

import stripe

from payment_entitlement import CORE_PRODUCT_KEY, apply_verified_provider_event


STRIPE_LIVE_PROVIDER = "stripe"
STRIPE_SANDBOX_PROVIDER = "stripe_sandbox"
_SUPPORTED_SUBSCRIPTION_EVENTS = {
    "customer.subscription.created",
    "customer.subscription.updated",
    "customer.subscription.deleted",
}


def _timestamp(value: Any) -> datetime | None:
    if value is None:
        return None
    try:
        return datetime.fromtimestamp(int(value), tz=timezone.utc)
    except (TypeError, ValueError, OSError):
        return None


def _text(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None


def _as_mapping(value: Any) -> Mapping[str, Any]:
    """Convert Stripe SDK resources to plain mappings before normalization."""
    if isinstance(value, Mapping):
        return value
    for method_name in ("to_dict_recursive", "to_dict"):
        method = getattr(value, method_name, None)
        if callable(method):
            converted = method()
            if isinstance(converted, Mapping):
                return converted
    raise ValueError("Stripe event payload is not mapping-compatible")


def verify_stripe_webhook(
    payload: bytes,
    signature_header: str,
    *,
    webhook_secret: str | None = None,
) -> Any:
    """Verify one Stripe webhook with Stripe's official signing helper.

    The webhook secret must be supplied explicitly or through
    ``STRIPE_WEBHOOK_SECRET``. Missing secrets fail closed.
    """
    secret = _text(webhook_secret) or _text(os.getenv("STRIPE_WEBHOOK_SECRET"))
    if not secret:
        raise RuntimeError("STRIPE_WEBHOOK_SECRET is not configured")
    if not signature_header:
        raise ValueError("Stripe-Signature header is required")
    return stripe.Webhook.construct_event(payload, signature_header, secret)


def _period_bounds(subscription: Mapping[str, Any]) -> tuple[datetime | None, datetime | None]:
    start = _timestamp(subscription.get("current_period_start"))
    end = _timestamp(subscription.get("current_period_end"))
    if start and end:
        return start, end

    items = subscription.get("items") or {}
    rows = items.get("data") if isinstance(items, Mapping) else None
    if isinstance(rows, list) and rows:
        first = rows[0] if isinstance(rows[0], Mapping) else {}
        start = start or _timestamp(first.get("current_period_start"))
        end = end or _timestamp(first.get("current_period_end"))
    return start, end


def _license_town_metadata(subscription: Mapping[str, Any]) -> tuple[str, str]:
    metadata = subscription.get("metadata") or {}
    if not isinstance(metadata, Mapping):
        raise ValueError("Stripe subscription metadata is invalid")
    user_id = _text(metadata.get("lt_user_id"))
    product_key = _text(metadata.get("lt_product_key")) or CORE_PRODUCT_KEY
    if not user_id:
        raise ValueError("Stripe subscription is missing lt_user_id metadata")
    if product_key != CORE_PRODUCT_KEY:
        raise ValueError("Stripe subscription product mapping is not supported")
    return user_id, product_key


def _entitlement_status(event_type: str, subscription: Mapping[str, Any]) -> str:
    if event_type == "customer.subscription.deleted":
        return "expired"

    stripe_status = _text(subscription.get("status")) or ""
    if stripe_status == "active":
        if bool(subscription.get("cancel_at_period_end")):
            return "cancel_at_period_end"
        return "active"

    # v0.1 has no implicit payment-failure grace. Anything other than a fully
    # active paid subscription fails closed at the paid-access boundary.
    if stripe_status in {"canceled", "unpaid", "incomplete_expired"}:
        return "expired"
    return "inactive"


def _provider_for_event(event: Mapping[str, Any]) -> str:
    livemode = event.get("livemode")
    if livemode is True:
        return STRIPE_LIVE_PROVIDER
    if livemode is False:
        return STRIPE_SANDBOX_PROVIDER
    raise ValueError("Stripe event livemode is required")


def normalize_verified_stripe_event(event: Mapping[str, Any]) -> dict[str, Any] | None:
    """Normalize a verified Stripe subscription event for payment_entitlement.

    Unsupported event types are intentionally ignored. The returned mapping is
    safe to pass to ``apply_verified_provider_event``.
    """
    event_type = _text(event.get("type"))
    if event_type not in _SUPPORTED_SUBSCRIPTION_EVENTS:
        return None

    event_id = _text(event.get("id"))
    if not event_id:
        raise ValueError("Stripe event id is required")

    provider = _provider_for_event(event)
    data = event.get("data") or {}
    subscription = data.get("object") if isinstance(data, Mapping) else None
    if not isinstance(subscription, Mapping):
        raise ValueError("Stripe subscription payload is missing")

    user_id, product_key = _license_town_metadata(subscription)
    subscription_id = _text(subscription.get("id"))
    customer_id = _text(subscription.get("customer"))
    if not subscription_id or not customer_id:
        raise ValueError("Stripe subscription/customer mapping is incomplete")

    period_start, period_end = _period_bounds(subscription)
    status = _entitlement_status(event_type, subscription)
    if status in {"active", "cancel_at_period_end"} and period_end is None:
        raise ValueError("active Stripe subscription is missing current_period_end")

    return {
        "verified": True,
        "provider": provider,
        "provider_event_id": event_id,
        "event_type": event_type,
        "provider_event_created_at": _timestamp(event.get("created")),
        "user_id": user_id,
        "product_key": product_key,
        "provider_customer_id": customer_id,
        "provider_subscription_id": subscription_id,
        "status": status,
        "current_period_start": period_start,
        "current_period_end": period_end,
    }


def process_stripe_webhook(
    payload: bytes,
    signature_header: str,
    *,
    webhook_secret: str | None = None,
) -> dict[str, Any]:
    """Verify, normalize, and durably apply one Stripe webhook event."""
    verified_event = verify_stripe_webhook(
        payload,
        signature_header,
        webhook_secret=webhook_secret,
    )
    event_mapping = _as_mapping(verified_event)
    normalized = normalize_verified_stripe_event(event_mapping)
    if normalized is None:
        return {"handled": False, "event_type": _text(event_mapping.get("type"))}
    result = apply_verified_provider_event(normalized)
    return {
        "handled": True,
        "event_type": normalized["event_type"],
        "duplicate": bool(result.get("duplicate")),
        "stale": bool(result.get("stale")),
        "entitlement": result.get("entitlement"),
    }
