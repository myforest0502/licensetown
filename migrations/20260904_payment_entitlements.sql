-- Provider-agnostic paid entitlement state for LicenseTown.
-- Create-only / forward-safe: no learner data is modified by this migration.

CREATE TABLE IF NOT EXISTS account_entitlements (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    product_key TEXT NOT NULL,
    provider TEXT NOT NULL,
    provider_customer_id TEXT,
    provider_subscription_id TEXT,
    status TEXT NOT NULL CHECK (status IN ('inactive', 'active', 'cancel_at_period_end', 'expired')),
    current_period_start TIMESTAMPTZ,
    current_period_end TIMESTAMPTZ,
    cancel_at_period_end BOOLEAN NOT NULL DEFAULT FALSE,
    last_provider_event_id TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, product_key)
);

CREATE UNIQUE INDEX IF NOT EXISTS account_entitlements_provider_subscription_uidx
    ON account_entitlements (provider, provider_subscription_id)
    WHERE provider_subscription_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS account_entitlements_user_status_idx
    ON account_entitlements (user_id, status);

CREATE TABLE IF NOT EXISTS payment_provider_events (
    id BIGSERIAL PRIMARY KEY,
    provider TEXT NOT NULL,
    provider_event_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    processing_result TEXT NOT NULL DEFAULT 'processed',
    received_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    processed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (provider, provider_event_id)
);
