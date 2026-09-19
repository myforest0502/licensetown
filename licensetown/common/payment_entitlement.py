"""Provider-agnostic paid entitlement state for LicenseTown.

This module intentionally knows nothing about Stripe/Square payload shapes.
A provider adapter must verify signatures and normalize a trusted event before
calling ``apply_verified_provider_event``.

Production schema is applied explicitly from
``migrations/20260904_payment_entitlements.sql``. Importing this module never
creates or alters Production tables.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

import database


CORE_PRODUCT_KEY = "licensetown_core_monthly"
CORE_PAID_FEATURE = "core_paid"
_VALID_STATUSES = {"inactive", "active", "cancel_at_period_end", "expired"}
_ENTITLED_STATUSES = {"active", "cancel_at_period_end"}

_local_entitlements: dict[tuple[str, str], dict[str, Any]] = {}
_local_provider_events: set[tuple[str, str]] = set()
_local_subscription_owners: dict[tuple[str, str], str] = {}


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _require_text(value: Any, field: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{field} is required")
    return text


def _optional_text(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None


def _optional_datetime(value: Any, field: str) -> datetime | None:
    if value is None:
        return None
    if not isinstance(value, datetime):
        raise ValueError(f"{field} must be datetime or None")
    if value.tzinfo is None:
        raise ValueError(f"{field} must be timezone-aware")
    return value.astimezone(timezone.utc)


def _inactive_entitlement(user_id: str, product_key: str) -> dict[str, Any]:
    return {
        "user_id": user_id,
        "product_key": product_key,
        "provider": None,
        "provider_customer_id": None,
        "provider_subscription_id": None,
        "status": "inactive",
        "current_period_start": None,
        "current_period_end": None,
        "cancel_at_period_end": False,
        "last_provider_event_id": None,
        "last_provider_event_created_at": None,
    }


def _row_to_entitlement(row) -> dict[str, Any]:
    return {
        "user_id": row[0],
        "product_key": row[1],
        "provider": row[2],
        "provider_customer_id": row[3],
        "provider_subscription_id": row[4],
        "status": row[5],
        "current_period_start": row[6],
        "current_period_end": row[7],
        "cancel_at_period_end": bool(row[8]),
        "last_provider_event_id": row[9],
        "last_provider_event_created_at": row[10],
    }


def _get_entitlement_db(user_id: str, product_key: str, conn) -> dict[str, Any]:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT user_id, product_key, provider, provider_customer_id,
                   provider_subscription_id, status, current_period_start,
                   current_period_end, cancel_at_period_end,
                   last_provider_event_id, last_provider_event_created_at
            FROM account_entitlements
            WHERE user_id = %s AND product_key = %s
            """,
            (user_id, product_key),
        )
        row = cur.fetchone()
    return _row_to_entitlement(row) if row else _inactive_entitlement(user_id, product_key)


def get_entitlement(user_id: str, product_key: str = CORE_PRODUCT_KEY) -> dict[str, Any]:
    """Return durable entitlement state; absence safely means inactive."""
    user_id = _require_text(user_id, "user_id")
    product_key = _require_text(product_key, "product_key")
    if not database.database_is_available():
        return dict(
            _local_entitlements.get(
                (user_id, product_key),
                _inactive_entitlement(user_id, product_key),
            )
        )
    with database.get_db_connection() as conn:
        return _get_entitlement_db(user_id, product_key, conn)


def entitlement_allows(
    entitlement: Mapping[str, Any] | None,
    feature: str,
    *,
    now: datetime | None = None,
) -> bool:
    """Centralized fail-closed paid access decision."""
    if feature != CORE_PAID_FEATURE or not entitlement:
        return False
    if entitlement.get("status") not in _ENTITLED_STATUSES:
        return False
    period_end = entitlement.get("current_period_end")
    if not isinstance(period_end, datetime) or period_end.tzinfo is None:
        return False
    current = now or _utcnow()
    if current.tzinfo is None:
        raise ValueError("now must be timezone-aware")
    return period_end.astimezone(timezone.utc) > current.astimezone(timezone.utc)


def can_use_paid_core(user_id: str, *, now: datetime | None = None) -> bool:
    return entitlement_allows(get_entitlement(user_id), CORE_PAID_FEATURE, now=now)


def _normalize_verified_event(event: Mapping[str, Any]) -> dict[str, Any]:
    if event.get("verified") is not True:
        raise ValueError("provider event is not verified")
    status = _require_text(event.get("status"), "status")
    if status not in _VALID_STATUSES:
        raise ValueError("unsupported entitlement status")
    normalized = {
        "provider": _require_text(event.get("provider"), "provider"),
        "provider_event_id": _require_text(event.get("provider_event_id"), "provider_event_id"),
        "event_type": _require_text(event.get("event_type"), "event_type"),
        "user_id": _require_text(event.get("user_id"), "user_id"),
        "product_key": _require_text(event.get("product_key") or CORE_PRODUCT_KEY, "product_key"),
        "provider_customer_id": _optional_text(event.get("provider_customer_id")),
        "provider_subscription_id": _optional_text(event.get("provider_subscription_id")),
        "status": status,
        "current_period_start": _optional_datetime(event.get("current_period_start"), "current_period_start"),
        "current_period_end": _optional_datetime(event.get("current_period_end"), "current_period_end"),
        "provider_event_created_at": _optional_datetime(
            event.get("provider_event_created_at"), "provider_event_created_at"
        ),
    }
    normalized["cancel_at_period_end"] = status == "cancel_at_period_end"
    return normalized


def _local_apply(event: dict[str, Any]) -> dict[str, Any]:
    event_key = (event["provider"], event["provider_event_id"])
    entitlement_key = (event["user_id"], event["product_key"])
    if event_key in _local_provider_events:
        return {"duplicate": True, "stale": False, "entitlement": get_entitlement(*entitlement_key)}

    subscription_id = event["provider_subscription_id"]
    if subscription_id:
        subscription_key = (event["provider"], subscription_id)
        owner = _local_subscription_owners.get(subscription_key)
        if owner and owner != event["user_id"]:
            raise ValueError("provider subscription is mapped to another user")

    current = _local_entitlements.get(entitlement_key)
    current_created_at = current.get("last_provider_event_created_at") if current else None
    incoming_created_at = event["provider_event_created_at"]
    stale = bool(
        current_created_at
        and incoming_created_at
        and incoming_created_at < current_created_at
    )
    _local_provider_events.add(event_key)
    if stale:
        return {"duplicate": False, "stale": True, "entitlement": dict(current)}

    entitlement = {
        "user_id": event["user_id"],
        "product_key": event["product_key"],
        "provider": event["provider"],
        "provider_customer_id": event["provider_customer_id"],
        "provider_subscription_id": subscription_id,
        "status": event["status"],
        "current_period_start": event["current_period_start"],
        "current_period_end": event["current_period_end"],
        "cancel_at_period_end": event["cancel_at_period_end"],
        "last_provider_event_id": event["provider_event_id"],
        "last_provider_event_created_at": incoming_created_at,
    }
    _local_entitlements[entitlement_key] = entitlement
    if subscription_id:
        _local_subscription_owners[(event["provider"], subscription_id)] = event["user_id"]
    return {"duplicate": False, "stale": False, "entitlement": dict(entitlement)}


def apply_verified_provider_event(event: Mapping[str, Any]) -> dict[str, Any]:
    """Apply one already-verified normalized provider event idempotently.

    Duplicate event ids are acknowledged without changing entitlement state.
    Older provider events are recorded but cannot roll state backward when both
    events carry trusted provider creation timestamps.
    """
    normalized = _normalize_verified_event(event)
    if not database.database_is_available():
        return _local_apply(normalized)

    with database.get_db_connection() as conn:
        with conn.cursor() as cur:
            subscription_id = normalized["provider_subscription_id"]
            if subscription_id:
                cur.execute(
                    """
                    SELECT user_id
                    FROM account_entitlements
                    WHERE provider = %s AND provider_subscription_id = %s
                    """,
                    (normalized["provider"], subscription_id),
                )
                owner = cur.fetchone()
                if owner and owner[0] != normalized["user_id"]:
                    raise ValueError("provider subscription is mapped to another user")

            cur.execute(
                """
                INSERT INTO payment_provider_events (
                    provider, provider_event_id, event_type,
                    provider_event_created_at, processing_result
                )
                VALUES (%s, %s, %s, %s, 'received')
                ON CONFLICT (provider, provider_event_id) DO NOTHING
                RETURNING id
                """,
                (
                    normalized["provider"],
                    normalized["provider_event_id"],
                    normalized["event_type"],
                    normalized["provider_event_created_at"],
                ),
            )
            inserted = cur.fetchone()
            if not inserted:
                return {
                    "duplicate": True,
                    "stale": False,
                    "entitlement": _get_entitlement_db(
                        normalized["user_id"], normalized["product_key"], conn
                    ),
                }

            current = _get_entitlement_db(
                normalized["user_id"], normalized["product_key"], conn
            )
            current_created_at = current.get("last_provider_event_created_at")
            incoming_created_at = normalized["provider_event_created_at"]
            stale = bool(
                current_created_at
                and incoming_created_at
                and incoming_created_at < current_created_at
            )
            if stale:
                cur.execute(
                    """
                    UPDATE payment_provider_events
                    SET processing_result = 'ignored_stale', processed_at = NOW()
                    WHERE provider = %s AND provider_event_id = %s
                    """,
                    (normalized["provider"], normalized["provider_event_id"]),
                )
                return {"duplicate": False, "stale": True, "entitlement": current}

            cur.execute(
                """
                INSERT INTO account_entitlements (
                    user_id, product_key, provider, provider_customer_id,
                    provider_subscription_id, status, current_period_start,
                    current_period_end, cancel_at_period_end,
                    last_provider_event_id, last_provider_event_created_at,
                    updated_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                ON CONFLICT (user_id, product_key) DO UPDATE SET
                    provider = EXCLUDED.provider,
                    provider_customer_id = EXCLUDED.provider_customer_id,
                    provider_subscription_id = EXCLUDED.provider_subscription_id,
                    status = EXCLUDED.status,
                    current_period_start = EXCLUDED.current_period_start,
                    current_period_end = EXCLUDED.current_period_end,
                    cancel_at_period_end = EXCLUDED.cancel_at_period_end,
                    last_provider_event_id = EXCLUDED.last_provider_event_id,
                    last_provider_event_created_at = EXCLUDED.last_provider_event_created_at,
                    updated_at = NOW()
                """,
                (
                    normalized["user_id"],
                    normalized["product_key"],
                    normalized["provider"],
                    normalized["provider_customer_id"],
                    subscription_id,
                    normalized["status"],
                    normalized["current_period_start"],
                    normalized["current_period_end"],
                    normalized["cancel_at_period_end"],
                    normalized["provider_event_id"],
                    incoming_created_at,
                ),
            )
            cur.execute(
                """
                UPDATE payment_provider_events
                SET processing_result = 'processed', processed_at = NOW()
                WHERE provider = %s AND provider_event_id = %s
                """,
                (normalized["provider"], normalized["provider_event_id"]),
            )
        return {
            "duplicate": False,
            "stale": False,
            "entitlement": _get_entitlement_db(
                normalized["user_id"], normalized["product_key"], conn
            ),
        }


def reset_local_payment_state_for_tests() -> None:
    """Test-only helper; Production state is never touched."""
    _local_entitlements.clear()
    _local_provider_events.clear()
    _local_subscription_owners.clear()
