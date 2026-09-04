from types import SimpleNamespace

import payment_entitlement
import stripe_checkout_service as service


def setup_function():
    payment_entitlement.reset_local_payment_state_for_tests()


def test_sandbox_checkout_feature_flag_defaults_off(monkeypatch):
    monkeypatch.delenv("ENABLE_STRIPE_SANDBOX_CHECKOUT", raising=False)
    assert service.stripe_sandbox_checkout_enabled() is False


def test_live_secret_key_is_rejected(monkeypatch):
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_live_not_allowed")
    try:
        service._stripe_secret_key()
    except RuntimeError as exc:
        assert "test key" in str(exc)
    else:
        raise AssertionError("live Stripe keys must be rejected by sandbox plumbing")


def test_checkout_uses_signed_account_mapping_metadata(monkeypatch):
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_license_town")
    monkeypatch.setenv("STRIPE_SANDBOX_PRICE_ID", "price_test_monthly")
    captured = {}

    def fake_create(**params):
        captured.update(params)
        return SimpleNamespace(id="cs_test_1", url="https://checkout.stripe.test/session")

    monkeypatch.setattr(service.stripe.checkout.Session, "create", fake_create)

    session = service.create_subscription_checkout_session(
        "learner-1",
        success_url="https://example.test/success",
        cancel_url="https://example.test/cancel",
    )

    assert session.id == "cs_test_1"
    assert captured["mode"] == "subscription"
    assert captured["line_items"] == [{"price": "price_test_monthly", "quantity": 1}]
    assert captured["client_reference_id"] == "learner-1"
    assert captured["subscription_data"]["metadata"] == {
        "lt_user_id": "learner-1",
        "lt_product_key": payment_entitlement.CORE_PRODUCT_KEY,
    }
    assert captured["metadata"]["lt_user_id"] == "learner-1"
    assert captured["success_url"] == "https://example.test/success"
    assert captured["cancel_url"] == "https://example.test/cancel"
    assert "customer" not in captured


def test_checkout_reuses_existing_stripe_sandbox_customer(monkeypatch):
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_license_town")
    monkeypatch.setenv("STRIPE_SANDBOX_PRICE_ID", "price_test_monthly")
    payment_entitlement.apply_verified_provider_event(
        {
            "verified": True,
            "provider": service.STRIPE_SANDBOX_PROVIDER,
            "provider_event_id": "evt_existing",
            "event_type": "customer.subscription.deleted",
            "user_id": "learner-1",
            "product_key": payment_entitlement.CORE_PRODUCT_KEY,
            "provider_customer_id": "cus_existing",
            "provider_subscription_id": "sub_old",
            "status": "expired",
        }
    )
    captured = {}
    monkeypatch.setattr(
        service.stripe.checkout.Session,
        "create",
        lambda **params: captured.update(params) or SimpleNamespace(id="cs_test_2", url="x"),
    )

    service.create_subscription_checkout_session(
        "learner-1",
        success_url="https://example.test/success",
        cancel_url="https://example.test/cancel",
    )

    assert captured["customer"] == "cus_existing"


def test_checkout_does_not_reuse_live_stripe_customer_in_sandbox(monkeypatch):
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_license_town")
    monkeypatch.setenv("STRIPE_SANDBOX_PRICE_ID", "price_test_monthly")
    payment_entitlement.apply_verified_provider_event(
        {
            "verified": True,
            "provider": "stripe",
            "provider_event_id": "evt_live_existing",
            "event_type": "customer.subscription.deleted",
            "user_id": "learner-1",
            "product_key": payment_entitlement.CORE_PRODUCT_KEY,
            "provider_customer_id": "cus_live",
            "provider_subscription_id": "sub_live",
            "status": "expired",
        }
    )
    captured = {}
    monkeypatch.setattr(
        service.stripe.checkout.Session,
        "create",
        lambda **params: captured.update(params) or SimpleNamespace(id="cs_test_3", url="x"),
    )

    service.create_subscription_checkout_session(
        "learner-1",
        success_url="https://example.test/success",
        cancel_url="https://example.test/cancel",
    )

    assert "customer" not in captured


def test_checkout_requires_configured_price(monkeypatch):
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_license_town")
    monkeypatch.delenv("STRIPE_SANDBOX_PRICE_ID", raising=False)
    monkeypatch.delenv("STRIPE_SANDBOX_MONTHLY_AMOUNT_JPY", raising=False)
    try:
        service.create_subscription_checkout_session(
            "learner-1",
            success_url="https://example.test/success",
            cancel_url="https://example.test/cancel",
        )
    except RuntimeError as exc:
        assert "STRIPE_SANDBOX_PRICE_ID" in str(exc)
    else:
        raise AssertionError("missing price configuration must fail closed")


def test_portal_requires_existing_stripe_customer(monkeypatch):
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_license_town")
    try:
        service.create_customer_portal_session(
            "learner-1",
            return_url="https://example.test/return",
        )
    except ValueError as exc:
        assert "customer mapping" in str(exc)
    else:
        raise AssertionError("portal must not guess a Stripe customer")


def test_portal_uses_durable_sandbox_customer_mapping(monkeypatch):
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_license_town")
    payment_entitlement.apply_verified_provider_event(
        {
            "verified": True,
            "provider": service.STRIPE_SANDBOX_PROVIDER,
            "provider_event_id": "evt_active",
            "event_type": "customer.subscription.updated",
            "user_id": "learner-1",
            "product_key": payment_entitlement.CORE_PRODUCT_KEY,
            "provider_customer_id": "cus_1",
            "provider_subscription_id": "sub_1",
            "status": "active",
        }
    )
    captured = {}
    monkeypatch.setattr(
        service.stripe.billing_portal.Session,
        "create",
        lambda **params: captured.update(params) or SimpleNamespace(url="https://billing.stripe.test/portal"),
    )

    portal = service.create_customer_portal_session(
        "learner-1",
        return_url="https://example.test/return",
    )

    assert portal.url == "https://billing.stripe.test/portal"
    assert captured["customer"] == "cus_1"
    assert captured["return_url"] == "https://example.test/return"
