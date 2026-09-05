# LicenseTown launch offer / pricing recommendation v0.1

Date: 2026-09-05
Status: owner decision required before runtime/public sale changes

## Recommendation

For the first tiny paid validation cohort, use **¥980/month** as the single launch-test price.

Do not create multiple paid tiers yet.

### Free floor

- LINE onboarding
- first meaningful 5-question study block
- scoring and saved explanation for served questions
- `教えて源さん` term lookup
- one meaningful next action based on the result
- enough basic status to understand what LicenseTown is doing

### Paid monthly core

- full ongoing adaptive study
- repair/recheck continuity and learning history
- full `合格への道` evidence/navigation
- learner-selected field study within supported rules
- parent `学習見守り`
- Trial100 longitudinal evidence/tracking

`教えて源さん` term lookup should remain free in the first offer. It is a low-variable-cost learning utility and a good trust/activation feature.

## Why ¥980 instead of the sandbox ¥1,480

The current direct PT national-exam app market is inexpensive. Public App Store listings checked on 2026-09-05 include examples around:

- ¥200/month for ad removal with 1,576 questions otherwise free;
- ¥300/month for a PT past-question app membership;
- ¥370 one-time for an ad-free PT past-question app;
- ¥700 one-time for an all-in PT past-question app.

These are not direct substitutes for LicenseTown: they mostly monetize access, ads, or a static question/review experience. LicenseTown's recurring differentiation is the evidence-driven choice of what to do next, repair/recheck continuity, `合格への道`, and parent monitoring.

However, LicenseTown does not yet have external paid-cohort evidence proving that users will value those recurring functions enough to justify ¥1,480/month. Starting at ¥980 reduces the first conversion hurdle without collapsing the product into the ¥200-¥700 static-app price frame.

## Payment cost check

Stripe Japan public pricing checked on 2026-09-05 shows:

- standard successful card payment: 3.6%
- Stripe Billing pay-as-you-go: 0.7% of Billing volume

At ¥980/month, the simple combined percentage estimate is 4.3%, or about ¥42 before any tax/accounting/chargeback/support/infrastructure considerations, leaving about ¥938 before other costs.

Because core study and `教えて源さん` do not require a per-question OpenAI call, AI variable cost is not currently a reason to start at ¥1,480.

## Why not ¥480-¥700

A price too close to simple past-question apps would make it difficult to communicate the product category LicenseTown is trying to create. LicenseTown is not selling only a question pile; it is selling recurring study direction and evidence continuity.

¥980 is therefore a validation price, not a claim that the final mature value is capped there.

## Why not ¥1,980 now

¥1,980 would require stronger external proof of recurring value, especially parent/supporter value and retention. The current strongest evidence is still one real learner and family use. That is enough to build the product, not enough to demand a premium market price confidently.

## Required owner decision

Before implementation, the owner should explicitly approve or reject this contract:

> **LicenseTown first paid validation offer: ¥980/month. First 5 questions + term lookup + result/next-action free; ongoing adaptive learning, full `合格への道`, field study continuity, parent monitoring, and Trial100 longitudinal tracking paid.**

If approved, implementation should then:

1. change the sandbox/public offer configuration from test-only ¥1,480 to the approved public ¥980 contract while keeping live charging OFF;
2. write the exact free/paid/cancellation/refund wording once;
3. make HP / terms / confirmation screen use that one source of truth;
4. run sandbox regression with the final offer;
5. present current Stripe fees to the owner again before any live-mode activation;
6. only after explicit live-payment approval, enable real charging for a tiny cohort.

## Sources checked

- Apple App Store: `理学療法士国試ドリル` — public listing includes ¥200/month ad removal and ¥1,000 buyout; all 1,576 questions described as free.
- Apple App Store: `理学療法士 過去問 試験対策` — public listing includes low-price monthly in-app memberships including ¥300.
- Apple App Store: `理学療法士 過去問（完全版）` — public listing ¥370 one-time.
- Apple App Store: `理学療法士 過去問 PT国家試験｜合格ノート` — public listing includes ¥700 all-in purchase.
- Stripe Japan pricing: https://stripe.com/jp/pricing
- Stripe Billing Japan pricing: https://stripe.com/jp/billing/pricing
