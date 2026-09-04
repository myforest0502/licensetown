from datetime import datetime, timedelta, timezone

import payment_access
import payment_entitlement


def setup_function():
    payment_entitlement.reset_local_payment_state_for_tests()


def _entitle(status="active", *, user_id="learner-1"):
    now = datetime.now(timezone.utc)
    payment_entitlement.apply_verified_provider_event(
        {
            "verified": True,
            "provider": "stripe_sandbox",
            "provider_event_id": f"evt_{status}",
            "event_type": "customer.subscription.updated",
            "user_id": user_id,
            "product_key": payment_entitlement.CORE_PRODUCT_KEY,
            "provider_customer_id": "cus_1",
            "provider_subscription_id": "sub_1",
            "status": status,
            "current_period_start": now - timedelta(days=1),
            "current_period_end": now + timedelta(days=29),
            "provider_event_created_at": now,
        }
    )


def test_free_floor_remains_available_without_entitlement():
    assert payment_access.can_access("learner-1", payment_access.FREE_FIRST_FIVE, enforce=True)
    assert payment_access.can_access("learner-1", payment_access.FREE_NEXT_ACTION, enforce=True)


def test_inactive_user_is_denied_paid_feature_when_enforced():
    decision = payment_access.access_decision(
        "learner-1", payment_access.PAID_ADAPTIVE_FULL, enforce=True
    )
    assert decision == {
        "allowed": False,
        "feature": payment_access.PAID_ADAPTIVE_FULL,
        "reason": "paid_required",
    }


def test_active_entitlement_allows_paid_features_when_enforced():
    _entitle("active")
    assert payment_access.can_access(
        "learner-1", payment_access.PAID_ADAPTIVE_FULL, enforce=True
    )
    assert payment_access.can_access(
        "learner-1", payment_access.PAID_DASHBOARD_FULL, enforce=True
    )
    assert payment_access.can_access(
        "learner-1", payment_access.PAID_SUPPORTER_FULL, enforce=True
    )


def test_cancel_at_period_end_keeps_paid_access_until_period_end():
    _entitle("cancel_at_period_end")
    assert payment_access.can_access(
        "learner-1", payment_access.PAID_DASHBOARD_FULL, enforce=True
    )


def test_expired_entitlement_is_denied_paid_feature():
    _entitle("expired")
    assert not payment_access.can_access(
        "learner-1", payment_access.PAID_SUPPORTER_FULL, enforce=True
    )


def test_unknown_feature_fails_closed_when_enforced():
    decision = payment_access.access_decision("learner-1", "future_unknown", enforce=True)
    assert decision["allowed"] is False
    assert decision["reason"] == "unknown_feature"


def test_rollout_defaults_off_to_preserve_existing_access(monkeypatch):
    monkeypatch.delenv("ENABLE_PAID_ACCESS_ENFORCEMENT", raising=False)
    decision = payment_access.access_decision("learner-1", payment_access.PAID_ADAPTIVE_FULL)
    assert decision["allowed"] is True
    assert decision["reason"] == "rollout_disabled"


def test_missing_user_fails_closed_even_before_rollout():
    assert not payment_access.can_access("", payment_access.FREE_FIRST_FIVE, enforce=False)
