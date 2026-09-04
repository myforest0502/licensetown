# Stripe sandbox v0.1

Status: sandbox-only implementation boundary
Issue: #154

## Selected path

- Account: `LicenseTownサンドボックス` only
- Stripe-hosted Checkout (redirect)
- one flat-rate monthly subscription at launch
- useful free floor; no-card freemium before paid upgrade
- Customer Portal for payment-method updates and cancellation
- cancellation at period end
- Stripe subscription webhook is durable entitlement authority
- browser success redirect never activates paid access
- LicenseTown account mapping is carried on subscription metadata as `lt_user_id`
- `lt_product_key=licensetown_core_monthly`

## Intentionally not enabled

- live charging
- Managed Payments
- Stripe Tax collection
- Stripe Invoicing
- paid gating on learner routes
- public price/checkout CTA

## Webhook events used by v0.1

- `customer.subscription.created`
- `customer.subscription.updated`
- `customer.subscription.deleted`

Unsupported events are acknowledged without changing LicenseTown entitlement state.
All accepted events must pass Stripe signature verification before normalization.
Duplicate Stripe event IDs are idempotent in the provider-event ledger.

## Status mapping

- Stripe `active` -> LT `active`
- Stripe `active` + `cancel_at_period_end=true` -> LT `cancel_at_period_end`
- subscription deleted/canceled/unpaid/incomplete_expired -> LT `expired`
- other non-active states -> LT `inactive` (fail closed; no implicit grace in v0.1)

Paid access also requires a future `current_period_end`; malformed active data cannot fabricate access.

## Rollout gate

No live charging until sandbox proves:

`checkout -> verified subscription webhook -> entitlement active -> portal cancel -> cancel_at_period_end -> period end/deleted -> expired`

and #155 makes public HP/terms/privacy/特商法/cancellation copy consistent with the actual offer.
