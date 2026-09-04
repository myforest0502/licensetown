from datetime import datetime, timezone

import payment_entitlement
import stripe_entitlement_adapter as adapter


def setup_function():
    payment_entitlement.reset_local_payment_state_for_tests()


def _subscription_event(
    *,
    event_id="evt_1",
    event_type="customer.subscription.updated",
    status="active",
    cancel_at_period_end=False,
    created=1_788_487_200,
    period_start=1_788_400_000,
    period_end=1_791_079_200,
    user_id="learner-1",
):
    return {
        "id": event_id,
        "type": event_type,
        "created": created,
        "data": {
            "object": {
                "id": "sub_1",
                "customer": "cus_1",
                "status": status,
                "cancel_at_period_end": cancel_at_period_end,
                "current_period_start": period_start,
                "current_period_end": period_end,
                "metadata": {
                    "lt_user_id": user_id,
                    "lt_product_key": payment_entitlement.CORE_PRODUCT_KEY,
                },
            }
        },
    }


def test_normalize_active_subscription_event():
    normalized = adapter.normalize_verified_stripe_event(_subscription_event())

    assert normalized["verified"] is True
    assert normalized["provider"] == "stripe"
    assert normalized["user_id"] == "learner-1"
    assert normalized["provider_customer_id"] == "cus_1"
    assert normalized["provider_subscription_id"] == "sub_1"
    assert normalized["status"] == "active"
    assert normalized["current_period_end"].tzinfo == timezone.utc


def test_cancel_at_period_end_maps_to_retained_paid_access_state():
    normalized = adapter.normalize_verified_stripe_event(
        _subscription_event(cancel_at_period_end=True)
    )
    assert normalized["status"] == "cancel_at_period_end"


def test_deleted_subscription_maps_to_expired():
    normalized = adapter.normalize_verified_stripe_event(
        _subscription_event(
            event_type="customer.subscription.deleted",
            status="canceled",
            period_start=None,
            period_end=None,
        )
    )
    assert normalized["status"] == "expired"


def test_non_active_subscription_fails_closed():
    normalized = adapter.normalize_verified_stripe_event(
        _subscription_event(status="past_due")
    )
    assert normalized["status"] == "inactive"


def test_active_subscription_requires_period_end():
    event = _subscription_event(period_end=None)
    try:
        adapter.normalize_verified_stripe_event(event)
    except ValueError as exc:
        assert "current_period_end" in str(exc)
    else:
        raise AssertionError("missing paid period must fail closed")


def test_missing_internal_account_mapping_is_rejected():
    event = _subscription_event()
    event["data"]["object"]["metadata"].pop("lt_user_id")
    try:
        adapter.normalize_verified_stripe_event(event)
    except ValueError as exc:
        assert "lt_user_id" in str(exc)
    else:
        raise AssertionError("unmapped Stripe subscription must be rejected")


def test_unsupported_event_is_ignored():
    event = _subscription_event(event_type="checkout.session.completed")
    assert adapter.normalize_verified_stripe_event(event) is None


def test_period_bounds_support_subscription_item_shape():
    event = _subscription_event(period_start=None, period_end=None)
    subscription = event["data"]["object"]
    subscription["items"] = {
        "data": [
            {
                "current_period_start": 1_788_400_000,
                "current_period_end": 1_791_079_200,
            }
        ]
    }
    normalized = adapter.normalize_verified_stripe_event(event)
    assert normalized["current_period_start"].tzinfo == timezone.utc
    assert normalized["current_period_end"].tzinfo == timezone.utc


def test_process_verified_event_updates_provider_agnostic_entitlement(monkeypatch):
    monkeypatch.setattr(
        adapter,
        "verify_stripe_webhook",
        lambda payload, signature_header, webhook_secret=None: _subscription_event(),
    )

    result = adapter.process_stripe_webhook(b"{}", "sig", webhook_secret="whsec_test")

    assert result["handled"] is True
    entitlement = payment_entitlement.get_entitlement("learner-1")
    assert entitlement["status"] == "active"
    assert payment_entitlement.entitlement_allows(
        entitlement,
        payment_entitlement.CORE_PAID_FEATURE,
        now=datetime.fromtimestamp(1_788_487_200, tz=timezone.utc),
    )


def test_duplicate_webhook_is_idempotent(monkeypatch):
    event = _subscription_event()
    monkeypatch.setattr(
        adapter,
        "verify_stripe_webhook",
        lambda payload, signature_header, webhook_secret=None: event,
    )

    first = adapter.process_stripe_webhook(b"{}", "sig", webhook_secret="whsec_test")
    second = adapter.process_stripe_webhook(b"{}", "sig", webhook_secret="whsec_test")

    assert first["duplicate"] is False
    assert second["duplicate"] is True


def test_webhook_secret_is_required(monkeypatch):
    monkeypatch.delenv("STRIPE_WEBHOOK_SECRET", raising=False)
    try:
        adapter.verify_stripe_webhook(b"{}", "sig")
    except RuntimeError as exc:
        assert "STRIPE_WEBHOOK_SECRET" in str(exc)
    else:
        raise AssertionError("missing webhook secret must fail closed")


def test_official_stripe_signature_helper_is_used(monkeypatch):
    captured = {}

    def fake_construct(payload, signature, secret):
        captured.update(payload=payload, signature=signature, secret=secret)
        return {"id": "evt_x", "type": "noop"}

    monkeypatch.setattr(adapter.stripe.Webhook, "construct_event", fake_construct)
    result = adapter.verify_stripe_webhook(
        b"payload",
        "t=1,v1=sig",
        webhook_secret="whsec_test",
    )

    assert result["id"] == "evt_x"
    assert captured == {
        "payload": b"payload",
        "signature": "t=1,v1=sig",
        "secret": "whsec_test",
    }
