"""Shared infrastructure canonicalization stays import-compatible."""

import importlib

MODULES = (
    "payment_entitlement",
    "stripe_billing_ui",
    "stripe_checkout_service",
    "stripe_entitlement_adapter",
    "stripe_webhook_ui",
    "email_delivery",
    "feedback_store",
    "durable_paused_session",
    "durable_web_learning_session",
    "qualification_dashboard_scope",
    "qualification_history_scope",
    "qualification_learning_time_scope",
    "qualification_learning_writer_scope",
    "learner_navigation_performance",
    "learner_path_performance",
    "recommendation_daily_summary",
)

def test_common_legacy_imports_are_canonical_modules():
    for name in MODULES:
        legacy = importlib.import_module(name)
        canonical = importlib.import_module(f"licensetown.common.{name}")
        assert legacy is canonical
