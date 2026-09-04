# LicenseTown Payment Entitlement v0.1

Status: implementation contract / no Production payment enabled
Parent issue: #109
Implementation issue: #154
Date: 2026-09-04

## 1. Goal

Add the smallest safe monthly paid-access foundation needed to sell LicenseTown without coupling the learning engine to a payment provider.

This phase does **not** choose a complicated tier matrix and does **not** change the deterministic Question Bank / selector / grading flow.

## 2. Product boundary

The payment system answers only one question for paid-facing authorization:

> What entitlement does this LicenseTown account have now?

Learning code must not inspect Stripe objects, webhook payloads, card data, invoice details, or provider-specific subscription statuses directly.

Expected direction:

`provider event -> verified adapter -> entitlement service -> durable entitlement state -> centralized access policy`

The learner's study history survives cancellation, payment failure, and later reactivation.

## 3. Provider direction

Stripe is the v0.1 implementation default candidate unless account/application constraints block it during onboarding.

Public Japan pricing checked on 2026-09-04:

- Stripe Payments standard domestic online card pricing: 3.6% per successful card payment.
- Stripe Billing pay-as-you-go: 0.7% of Billing transaction volume in addition to payment processing where applicable.
- Square online/subscription payment processing: 3.6%; viable alternative, but moving LicenseTown into Square's site stack is not required.
- PAY.JP advertises card pricing from 2.59% depending on plan, but current help documentation says API v2 recurring billing is not yet supported, creating avoidable uncertainty for an immediate monthly-subscription implementation.

Provider fees are time-sensitive and must be rechecked before public pricing is finalized.

## 4. Domain model

Recommended durable record (exact SQL naming may change after schema review):

```text
account_entitlements
- id
- user_id                     # LicenseTown learner/account identifier
- product_key                 # e.g. licensetown_core_monthly
- provider                    # stripe
- provider_customer_id        # nullable until provider customer exists
- provider_subscription_id    # nullable while inactive
- status                      # inactive | active | cancel_at_period_end | expired
- current_period_start        # nullable
- current_period_end          # nullable
- cancel_at_period_end        # boolean
- last_provider_event_id      # audit/idempotency aid
- updated_at
- created_at
```

Do not store card numbers, CVC, raw payment credentials, or webhook secrets in this table.

A separate processed-provider-event ledger is preferred for idempotency if provider event volume/semantics make one `last_provider_event_id` insufficient:

```text
payment_provider_events
- provider
- provider_event_id           # unique(provider, provider_event_id)
- event_type
- received_at
- processed_at
- processing_result
```

Do not store unnecessary full raw event payloads long-term merely for convenience.

## 5. Entitlement states

### inactive
No current paid entitlement. User remains within the defined free floor.

### active
Paid access is available through `current_period_end` subject to provider state.

### cancel_at_period_end
User has cancelled renewal but retains access through the already-paid current period. This is a product state, not an error.

### expired
The paid period has ended. Paid-only features return to the free boundary. Study history remains intact.

Payment-failure grace is **not** part of v0.1 unless deliberately added later. Avoid inventing a grace policy implicitly.

## 6. Centralized access policy

Application code should ask a small provider-agnostic API, for example:

```python
entitlement = get_entitlement(user_id)
can_use_paid = entitlement_allows(entitlement, "core_paid")
```

Do not spread checks such as `stripe_status == ...` across LINE handlers, learner dashboard routes, supporter routes, or selector code.

The selector must never change question-selection semantics because of payment-provider metadata. Free/paid boundaries determine feature access, not medical/learning evidence priority.

## 7. Free floor

The final commercial offer remains to be validated, but the free floor must be genuinely useful and capable of reaching LicenseTown's first-value event:

1. LINE onboarding completes.
2. Learner can start a small daily study allowance.
3. First 5 questions can be completed.
4. Learner receives grading/explanation and a meaningful next-action signal.

Do not make the free floor a broken demo whose only purpose is forcing checkout.

## 8. Paid core candidate

Candidate paid value for launch testing:

- full adaptive daily learning allowance
- full weakness / repair / checking / recheck engine
- 合格への道
- persistent learning-history use in recommendations
- Trial100 integration when real records exist
- richer, bounded 源さん consultation
- supporter dashboard bundled initially instead of creating another complex tier

Final boundary must be reflected identically in HP copy, LINE onboarding, entitlement policy, and cancellation documentation.

## 9. Webhook contract

Webhook processing must:

1. verify provider signature before reading the event as trusted;
2. reject malformed/forged events fail-closed;
3. identify the provider event id;
4. be idempotent for duplicate delivery;
5. map provider customer/subscription to the intended LicenseTown account;
6. update only entitlement/payment-domain state;
7. never modify learning history as a side effect;
8. avoid logging secrets or sensitive payment contents;
9. return provider-appropriate success/retry behavior only after durable processing outcome is known.

Duplicate webhook delivery must not extend periods twice, create duplicate entitlements, or corrupt account mapping.

## 10. Checkout/account mapping

The payment flow must establish an unambiguous mapping from the authenticated LicenseTown account to the provider customer/subscription.

Do not trust a user-supplied arbitrary `user_id` in a checkout callback/webhook as sufficient account authorization.

Preferred pattern:

- authenticated LT route creates checkout intent/session;
- LT places a non-secret stable internal reference in provider-supported metadata/client-reference fields;
- webhook verifies provider signature and resolves that reference server-side;
- entitlement becomes active only from trusted provider event/state, not merely from a browser success redirect.

A success page is presentation; the webhook/provider state is the durable authority.

## 11. Cancellation

Launch contract should be simple:

- user can request cancellation without contacting support as the only path where provider tooling permits;
- cancellation at period end preserves access until `current_period_end`;
- renewal stops afterward;
- historical learning data is not deleted by cancellation;
- re-subscription can restore paid access without creating a second learner identity;
- refund policy is a separate legal/operational rule and must be stated explicitly before sale.

## 12. Production rollout safety

Before Production enablement:

- schema migration reviewed and forward-safe;
- no fake paid Production user inserted for testing;
- provider test/sandbox mode covers end-to-end lifecycle first;
- webhook secret is stored only in environment/secrets management;
- signed/webhook validation tests are green;
- entitlement lookup failure has an explicit fail-safe behavior;
- rollback/disabling paid gating does not destroy user data;
- legal/privacy/特商法/cancellation copy matches actual behavior.

## 13. Required automated tests

At minimum:

- inactive -> active from verified provider event
- duplicate event id is idempotent
- active -> cancel_at_period_end
- cancel_at_period_end retains access until period end
- period end -> expired/free boundary
- malformed or forged webhook is rejected
- wrong account mapping cannot activate another learner
- learning history remains unchanged across entitlement transitions
- provider outage/read failure does not fabricate active entitlement
- free learner can still reach the intended first-value flow

## 14. Launch pricing hypotheses

These are experiments, not decisions:

- H1: ¥980/month — maximum low-friction entry
- H2: ¥1,480/month — preferred first serious hypothesis for full adaptive + dashboard + supporter + bounded AI
- H3: ¥1,980/month — only if recurring companion/supporter value and retention evidence justify it

Do not launch three public tiers. Initially test the clarity/willingness-to-pay around one offer, likely comparing ¥980 and ¥1,480 during validation. Recalculate margin with actual OpenAI, Render, Neon, LINE, payment fees, support burden, and refund/chargeback experience before scaling acquisition.

## 15. Explicit non-goals

- no pass guarantee or pass-probability claim
- no per-question AI billing dependency
- no payment data in Question Bank/Node state
- no complex coupons/annual plans/family tier matrix in v0.1
- no Production fake transactions
- no deletion of learning evidence when entitlement expires

## 16. Completion gate

Issue #154 can close only when a provider test/sandbox lifecycle proves:

`checkout -> verified event -> entitlement active -> paid access -> cancel -> period-end behavior`

and all access/cancellation/history-preservation tests are green.

Public charging still remains blocked until #155 makes the HP/terms/privacy/特商法/real CTA consistent with the actual implemented offer.
