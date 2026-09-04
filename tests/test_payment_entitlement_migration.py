from pathlib import Path


def test_payment_entitlement_migration_is_create_only_and_has_safety_constraints():
    sql = Path("migrations/20260904_payment_entitlements.sql").read_text(encoding="utf-8")
    lowered = sql.lower()

    assert "create table if not exists account_entitlements" in lowered
    assert "create table if not exists payment_provider_events" in lowered
    assert "unique (user_id, product_key)" in lowered
    assert "unique (provider, provider_event_id)" in lowered
    assert "last_provider_event_created_at" in lowered
    assert "provider_event_created_at" in lowered
    assert "drop table" not in lowered
    assert "delete from" not in lowered
    assert "truncate" not in lowered
    assert "update learning_" not in lowered
    assert "insert into learning_" not in lowered
