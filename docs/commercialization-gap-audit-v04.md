# LicenseTown commercialization gap audit v0.4

Date: 2026-09-05
Status: current product/commercial position after owner clarification

## Purpose

This document supersedes the commercial-position section of v0.3.

LicenseTown has enough technical payment infrastructure to charge later, but **that does not mean it is ready to ask users for money now**.

The product remains in a validation phase. Real users may expose defects, confusing behavior, educational weaknesses, performance issues, or missing safeguards that the current builders cannot see yet. That unknown-risk surface is itself a reason to keep normal use free.

## 1. Current operating model

Current user-facing LicenseTown is **free during validation**.

Operational requirements:

- live Stripe charging: OFF;
- paid access enforcement: OFF;
- public subscription offer: not active;
- future price candidate: **¥980/month**;
- sandbox Stripe lifecycle: retained as tested future infrastructure;
- normal learning access must not depend on payment while validation mode is active.

No automatic date or usage threshold should switch LicenseTown to paid mode.

## 2. Why this is the correct commercial stance now

The main unresolved commercial problem is no longer payment plumbing. It is evidence.

We do not yet know enough about:

- how broader learners use the product outside the builder's family;
- which learner routes still contain hidden state/UX failures;
- whether `教えて源さん` definitions are consistently useful across many terms;
- whether recommendation and repair behavior remains understandable over weeks/months;
- how much parent monitoring is actually valued;
- what support burden appears with multiple users;
- what users would reasonably pay for after sustained use.

Charging before those unknowns are reduced would create pressure to defend a product contract before the product has earned that confidence.

Therefore the current success criterion is **better evidence and fewer unknowns**, not conversion revenue.

## 3. Optional development support / 応援

The current public philosophy may include an optional development-support message:

> LicenseTown is still being built and tested. Normal use is not being sold yet. If someone nevertheless wants to support continued development, that support is voluntary.

This must remain separate from access to learning functions.

Any support mechanism must never imply:

- pay to keep using LicenseTown;
- pay to receive better answers or learning priority;
- pay because the learner owes the project something;
- guaranteed completion, results, or pass outcomes;
- automatic conversion into a future subscription.

Support collection itself remains OFF unless separately approved by the owner. A future voluntary-support flow would need its own truthful payment/legal wording.

## 4. Future paid candidate

If later evidence supports charging, the current one-plan candidate is **¥980/month**.

The likely recurring value is:

- adaptive study continuity;
- repair/recheck continuity;
- longitudinal learning history;
- full `合格への道` evidence/navigation;
- supported field-study continuity;
- parent `学習見守り`;
- Trial100 longitudinal evidence.

The future paid boundary is intentionally **not frozen**. Real use may show that some of these should remain free, that other recurring value matters more, or that the whole contract should change.

`教えて源さん` should not be paywalled merely because it is useful. Its current role is fast exam-term clarification and trust/activation.

## 5. What product work should continue now

The highest-value work while payment remains OFF is:

1. continue natural learner use and record concrete failures/confusions;
2. improve the definition quality and coverage of `教えて源さん`;
3. keep learner routes/regression safety stable while making only evidence-backed changes;
4. use the internal developer console to shorten diagnosis when real-use issues occur;
5. keep performance measurement targeted to actual slow learner/supporter paths;
6. invite a very small external validation cohort only when current known issues are acceptable;
7. measure activation, return use, route failures, confusion, and support burden before discussing real paid conversion.

## 6. What not to do now

Do not:

- enable live Stripe;
- enable paid enforcement;
- publish ¥980 as a current subscription price;
- remove useful learning access to manufacture a free/paid boundary;
- turn the optional support message into a disguised subscription;
- re-enable OpenAI billing merely to make the product look more AI-heavy;
- add broad new features without evidence that they solve a real learner problem;
- use current family success as proof of market-wide effectiveness.

## 7. Promotion gate to real charging

A paid launch requires a new explicit owner decision after a fresh readiness review.

At minimum, that review should include:

- broader real-user evidence;
- current known defect list and severity;
- route reliability evidence;
- term-explainer quality/coverage evidence;
- retention/repeat-use evidence;
- parent value evidence where applicable;
- actual operating/support cost;
- willingness-to-pay evidence;
- current payment fees;
- final HP/terms/checkout/cancellation/refund consistency;
- explicit owner approval to accept real money.

Technical readiness alone is not sufficient.

## 8. Current product decision

The correct sequence is now:

**build -> use -> discover -> fix -> validate -> repeat**.

Monetization stays prepared but dormant.

The working commercial position is:

**Use is free while LicenseTown is still proving itself. ¥980/month is the current future-price candidate. Optional development support is separate and voluntary, and no money collection is activated without another explicit owner decision.**
