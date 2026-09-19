"""Stripe-hosted Checkout and Customer Portal helpers for LicenseTown.

These helpers are sandbox-capable plumbing only. They never activate a
LicenseTown entitlement: verified subscription webhooks remain authoritative.
"""

from __future__ import annotations

import os
from typing import Any

import stripe

from payment_entitlement import CORE_PRODUCT_KEY, get_entitlement
from stripe_entitlement_adapter import STRIPE_SANDBOX_PROVIDER


_PORTAL_CONFIG_METADATA_KEY = "lt_purpose"
_PORTAL_CONFIG_METADATA_VALUE = "licensetown_sandbox_v01"


def _required_env(name: str) -> str:
    value = str(os.getenv(name) or "").strip()
    if not value:
        raise RuntimeError(f"{name} is not configured")
    return value


def stripe_sandbox_checkout_enabled() -> bool:
    return str(os.getenv("ENABLE_STRIPE_SANDBOX_CHECKOUT") or "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def _stripe_secret_key() -> str:
    key = _required_env("STRIPE_SECRET_KEY")
    # This integration must remain sandbox-only until the explicit live rollout
    # gate. A live secret key must never be accepted by the sandbox route.
    if not key.startswith("sk_test_"):
        raise RuntimeError("STRIPE_SECRET_KEY must be a Stripe test key")
    return key


def _existing_stripe_customer(user_id: str) -> str | None:
    entitlement = get_entitlement(user_id)
    if str(entitlement.get("provider") or "").strip() != STRIPE_SANDBOX_PROVIDER:
        return None
    customer_id = str(entitlement.get("provider_customer_id") or "").strip()
    return customer_id or None


def _checkout_line_item(price_id: str | None = None) -> dict[str, Any]:
    price = str(price_id or os.getenv("STRIPE_SANDBOX_PRICE_ID") or "").strip()
    if price:
        return {"price": price, "quantity": 1}

    raw_amount = str(os.getenv("STRIPE_SANDBOX_MONTHLY_AMOUNT_JPY") or "").strip()
    try:
        amount = int(raw_amount)
    except (TypeError, ValueError):
        amount = 0
    if amount <= 0:
        raise RuntimeError(
            "STRIPE_SANDBOX_PRICE_ID or STRIPE_SANDBOX_MONTHLY_AMOUNT_JPY is required"
        )
    return {
        "price_data": {
            "currency": "jpy",
            "unit_amount": amount,
            "recurring": {"interval": "month"},
            "product_data": {"name": "LicenseTown sandbox monthly"},
        },
        "quantity": 1,
    }


def _object_id(value: Any) -> str | None:
    if isinstance(value, dict):
        object_id = value.get("id")
    else:
        object_id = getattr(value, "id", None)
    object_id = str(object_id or "").strip()
    return object_id or None


def _object_metadata(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        metadata = value.get("metadata") or {}
    else:
        metadata = getattr(value, "metadata", None) or {}
    if isinstance(metadata, dict):
        return metadata
    try:
        return dict(metadata)
    except (TypeError, ValueError):
        return {}


def ensure_sandbox_portal_configuration() -> str:
    """Return the dedicated LT sandbox portal configuration, creating it once.

    We do not reuse arbitrary active portal configurations because cancellation
    semantics are part of LicenseTown's paid-access contract. The sandbox portal
    must cancel at period end and must not expose plan switching.
    """
    key = _stripe_secret_key()
    configurations = stripe.billing_portal.Configuration.list(
        api_key=key,
        active=True,
        limit=100,
    )
    rows = configurations.get("data", []) if isinstance(configurations, dict) else getattr(
        configurations, "data", []
    )
    for configuration in rows or []:
        metadata = _object_metadata(configuration)
        if metadata.get(_PORTAL_CONFIG_METADATA_KEY) == _PORTAL_CONFIG_METADATA_VALUE:
            configuration_id = _object_id(configuration)
            if configuration_id:
                return configuration_id

    configuration = stripe.billing_portal.Configuration.create(
        api_key=key,
        features={
            "customer_update": {"enabled": False, "allowed_updates": []},
            "invoice_history": {"enabled": True},
            "payment_method_update": {"enabled": True},
            "subscription_cancel": {
                "enabled": True,
                "mode": "at_period_end",
                "proration_behavior": "none",
            },
            "subscription_update": {
                "enabled": False,
                "default_allowed_updates": [],
                "proration_behavior": "none",
            },
        },
        metadata={_PORTAL_CONFIG_METADATA_KEY: _PORTAL_CONFIG_METADATA_VALUE},
    )
    configuration_id = _object_id(configuration)
    if not configuration_id:
        raise RuntimeError("Stripe sandbox portal configuration id is missing")
    return configuration_id


def create_subscription_checkout_session(
    user_id: str,
    *,
    success_url: str,
    cancel_url: str,
    price_id: str | None = None,
) -> Any:
    """Create a Stripe-hosted subscription Checkout session for one LT user."""
    user_id = str(user_id or "").strip()
    if not user_id:
        raise ValueError("user_id is required")

    params = {
        "api_key": _stripe_secret_key(),
        "mode": "subscription",
        "line_items": [_checkout_line_item(price_id)],
        "client_reference_id": user_id,
        "subscription_data": {
            "metadata": {
                "lt_user_id": user_id,
                "lt_product_key": CORE_PRODUCT_KEY,
            }
        },
        "metadata": {
            "lt_user_id": user_id,
            "lt_product_key": CORE_PRODUCT_KEY,
        },
        "success_url": success_url,
        "cancel_url": cancel_url,
    }
    existing_customer = _existing_stripe_customer(user_id)
    if existing_customer:
        params["customer"] = existing_customer

    return stripe.checkout.Session.create(**params)


def create_customer_portal_session(user_id: str, *, return_url: str) -> Any:
    """Create a self-service portal session for an entitled LT sandbox account."""
    user_id = str(user_id or "").strip()
    if not user_id:
        raise ValueError("user_id is required")
    customer_id = _existing_stripe_customer(user_id)
    if not customer_id:
        raise ValueError("Stripe sandbox customer mapping is not available")

    configuration_id = ensure_sandbox_portal_configuration()
    return stripe.billing_portal.Session.create(
        api_key=_stripe_secret_key(),
        customer=customer_id,
        configuration=configuration_id,
        return_url=return_url,
    )
