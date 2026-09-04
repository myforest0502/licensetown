"""Stripe-hosted Checkout and Customer Portal helpers for LicenseTown.

These helpers are sandbox-capable plumbing only. They never activate a
LicenseTown entitlement: verified subscription webhooks remain authoritative.
"""

from __future__ import annotations

import os
from typing import Any

import stripe

from payment_entitlement import CORE_PRODUCT_KEY, get_entitlement


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
    price = str(price_id or os.getenv("STRIPE_SANDBOX_PRICE_ID") or "").strip()
    if not price:
        raise RuntimeError("STRIPE_SANDBOX_PRICE_ID is not configured")

    return stripe.checkout.Session.create(
        api_key=_stripe_secret_key(),
        mode="subscription",
        line_items=[{"price": price, "quantity": 1}],
        client_reference_id=user_id,
        subscription_data={
            "metadata": {
                "lt_user_id": user_id,
                "lt_product_key": CORE_PRODUCT_KEY,
            }
        },
        metadata={
            "lt_user_id": user_id,
            "lt_product_key": CORE_PRODUCT_KEY,
        },
        success_url=success_url,
        cancel_url=cancel_url,
    )


def create_customer_portal_session(user_id: str, *, return_url: str) -> Any:
    """Create a self-service portal session for an entitled LT account."""
    user_id = str(user_id or "").strip()
    if not user_id:
        raise ValueError("user_id is required")
    entitlement = get_entitlement(user_id)
    customer_id = str(entitlement.get("provider_customer_id") or "").strip()
    provider = str(entitlement.get("provider") or "").strip()
    if provider != "stripe" or not customer_id:
        raise ValueError("Stripe customer mapping is not available")

    return stripe.billing_portal.Session.create(
        api_key=_stripe_secret_key(),
        customer=customer_id,
        return_url=return_url,
    )
