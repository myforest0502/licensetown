from datetime import datetime, timedelta, timezone

import database
import payment_entitlement as ent


def _event(
    event_id,
    status,
    *,
    user_id="learner-1",
    subscription_id="sub-1",
    created_at=None,
    period_end=None,
    verified=True,
):
    created_at = created_at or datetime(2026, 9, 4, 1, 0, tzinfo=timezone.utc)
    period_end = period_end or datetime(2026, 10, 4, 1, 0, tzinfo=timezone.utc)
    return {
        "verified": verified,
        "provider": "stripe",
        "provider_event_id": event_id,
        "event_type": f"subscription.{status}",
        "provider_event_created_at": created_at,
        "user_id": user_id,
        "product_key": ent.CORE_PRODUCT_KEY,
        "provider_customer_id": f"cus-{user_id}",
        "provider_subscription_id": subscription_id,
        "status": status,
        "current_period_start": datetime(2026, 9, 4, 1, 0, tzinfo=timezone.utc),
        "current_period_end": period_end,
    }


def setup_function():
    ent.reset_local_payment_state_for_tests()


def test_missing_entitlement_is_inactive_and_paid_access_fails_closed(monkeypatch):
    monkeypatch.setattr(database, "database_is_available", lambda: False)
    state = ent.get_entitlement("learner-1")
    assert state["status"] == "inactive"
    assert not ent.entitlement_allows(
        state,
        ent.CORE_PAID_FEATURE,
        now=datetime(2026, 9, 4, 2, 0, tzinfo=timezone.utc),
    )
    assert not ent.entitlement_allows(state, "unknown_feature")


def test_verified_event_activates_entitlement_and_duplicate_is_idempotent(monkeypatch):
    monkeypatch.setattr(database, "database_is_available", lambda: False)
    event = _event("evt-active", "active")

    first = ent.apply_verified_provider_event(event)
    second = ent.apply_verified_provider_event(event)

    assert first["duplicate"] is False
    assert first["entitlement"]["status"] == "active"
    assert second["duplicate"] is True
    assert second["entitlement"] == first["entitlement"]
    assert ent.can_use_paid_core(
        "learner-1",
        now=datetime(2026, 9, 5, 0, 0, tzinfo=timezone.utc),
    )


def test_cancel_at_period_end_keeps_access_until_period_end(monkeypatch):
    monkeypatch.setattr(database, "database_is_available", lambda: False)
    ent.apply_verified_provider_event(_event("evt-active", "active"))
    cancelled = ent.apply_verified_provider_event(
        _event(
            "evt-cancel",
            "cancel_at_period_end",
            created_at=datetime(2026, 9, 5, 1, 0, tzinfo=timezone.utc),
        )
    )["entitlement"]

    assert cancelled["cancel_at_period_end"] is True
    assert ent.entitlement_allows(
        cancelled,
        ent.CORE_PAID_FEATURE,
        now=datetime(2026, 10, 3, 23, 0, tzinfo=timezone.utc),
    )
    assert not ent.entitlement_allows(
        cancelled,
        ent.CORE_PAID_FEATURE,
        now=datetime(2026, 10, 4, 1, 0, tzinfo=timezone.utc),
    )


def test_expired_event_returns_user_to_free_boundary(monkeypatch):
    monkeypatch.setattr(database, "database_is_available", lambda: False)
    ent.apply_verified_provider_event(_event("evt-active", "active"))
    expired = ent.apply_verified_provider_event(
        _event(
            "evt-expired",
            "expired",
            created_at=datetime(2026, 10, 4, 1, 1, tzinfo=timezone.utc),
            period_end=datetime(2026, 10, 4, 1, 0, tzinfo=timezone.utc),
        )
    )["entitlement"]

    assert expired["status"] == "expired"
    assert not ent.entitlement_allows(
        expired,
        ent.CORE_PAID_FEATURE,
        now=datetime(2026, 10, 4, 1, 1, tzinfo=timezone.utc),
    )


def test_forged_or_malformed_event_fails_closed(monkeypatch):
    monkeypatch.setattr(database, "database_is_available", lambda: False)
    forged = _event("evt-forged", "active", verified=False)

    try:
        ent.apply_verified_provider_event(forged)
        assert False, "forged event must fail"
    except ValueError:
        pass

    assert ent.get_entitlement("learner-1")["status"] == "inactive"


def test_subscription_cannot_be_reassigned_to_another_learner(monkeypatch):
    monkeypatch.setattr(database, "database_is_available", lambda: False)
    ent.apply_verified_provider_event(_event("evt-owner", "active"))

    try:
        ent.apply_verified_provider_event(
            _event(
                "evt-wrong-user",
                "active",
                user_id="learner-2",
                subscription_id="sub-1",
                created_at=datetime(2026, 9, 5, 1, 0, tzinfo=timezone.utc),
            )
        )
        assert False, "cross-account subscription mapping must fail"
    except ValueError:
        pass

    assert ent.get_entitlement("learner-2")["status"] == "inactive"


def test_stale_provider_event_cannot_roll_state_back(monkeypatch):
    monkeypatch.setattr(database, "database_is_available", lambda: False)
    newer = _event(
        "evt-newer",
        "cancel_at_period_end",
        created_at=datetime(2026, 9, 6, 1, 0, tzinfo=timezone.utc),
    )
    older = _event(
        "evt-older",
        "active",
        created_at=datetime(2026, 9, 5, 1, 0, tzinfo=timezone.utc),
    )

    ent.apply_verified_provider_event(newer)
    result = ent.apply_verified_provider_event(older)

    assert result["stale"] is True
    assert result["entitlement"]["status"] == "cancel_at_period_end"
    assert ent.get_entitlement("learner-1")["status"] == "cancel_at_period_end"


def test_entitlement_transitions_do_not_touch_learning_history(monkeypatch):
    monkeypatch.setattr(database, "database_is_available", lambda: False)
    database._local_learning_events.clear()
    database._local_learning_events["learning-sentinel"] = {
        "event_key": "learning-sentinel",
        "user_id": "learner-1",
        "answered_count": 5,
    }
    before = dict(database._local_learning_events["learning-sentinel"])

    ent.apply_verified_provider_event(_event("evt-active", "active"))
    ent.apply_verified_provider_event(
        _event(
            "evt-cancel",
            "cancel_at_period_end",
            created_at=datetime(2026, 9, 5, 1, 0, tzinfo=timezone.utc),
        )
    )
    ent.apply_verified_provider_event(
        _event(
            "evt-expired",
            "expired",
            created_at=datetime(2026, 10, 4, 1, 1, tzinfo=timezone.utc),
            period_end=datetime(2026, 10, 4, 1, 0, tzinfo=timezone.utc),
        )
    )

    assert database._local_learning_events["learning-sentinel"] == before


def test_missing_period_end_never_fabricates_paid_access(monkeypatch):
    monkeypatch.setattr(database, "database_is_available", lambda: False)
    event = _event("evt-no-end", "active")
    event["current_period_end"] = None
    state = ent.apply_verified_provider_event(event)["entitlement"]

    assert state["status"] == "active"
    assert not ent.entitlement_allows(
        state,
        ent.CORE_PAID_FEATURE,
        now=datetime(2026, 9, 5, 0, 0, tzinfo=timezone.utc),
    )
