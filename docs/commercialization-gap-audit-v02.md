# LicenseTown commercialization gap audit v0.2

Date: 2026-09-04

## Purpose

This document refreshes the commercialization gap audit after the 2026-09-04 payment/HP work. It is a launch-readiness document, not a revenue forecast, pass-probability model, or claim of educational superiority.

Funnel:

`SNS / referral / search -> official HP -> LINE start -> first successful 5-question session -> continued use -> paid conversion -> retention`

## 1. Current sellable strengths

LicenseTown now has a credible product core rather than only a prototype:

- Formal Question Bank: Q1-Q1737 / 1737 questions.
- Normal study is stored-data driven; no per-question OpenAI dependency.
- Confidence-aware learning history, confident-wrong detection, Knowledge Node repair, STRONG different-question confirmation, and Recent Question Cooldown.
- Adaptive repair/checking/exploration selection plus read-only source-mix diagnostics.
- Real-data `合格への道`, deterministic readiness semantics, priority TOP3, and one primary next action.
- Learner-selected field study and dashboard recommendation both operate through the supported question-selection path.
- Parent/supporter view exists with deliberately limited scope.
- Natural learner feedback on 2026-09-04 reported broad output across both recommendation and field-based study, no similar-question repetition, and no bug/problem during that session.
- Stripe sandbox Checkout, verified webhook handling, provider-agnostic entitlement persistence, period-end cancellation, and centralized paid-access policy are implemented.
- Stripe sandbox and live entitlement namespaces are separated; live charging remains disabled.
- Official HP now has sale-safe presentation boundaries, legal/operator routes, source-of-truth question count, and fail-closed CTA wiring.

The strongest concise value proposition remains:

**LicenseTown uses actual learning evidence to decide what should happen next, then lets the learner act on that decision immediately.**

## 2. Remaining blockers before accepting real money

### Must-have before public sale

1. **Finish Stripe sandbox lifecycle proof (#154).**
   - already proven: Checkout -> subscription -> verified webhook -> durable entitlement -> `cancel_at_period_end`.
   - still required: final expiry/deletion transition proof using a real Stripe sandbox event or equivalent supported time-control path.
   - paid enforcement must remain OFF until this is complete.

2. **Provide the real onboarding destination (#155).**
   - code now uses `SITE_ONBOARDING_URL`.
   - invalid/missing values fail closed to LicenseTown contact.
   - the actual LINE/onboarding HTTPS URL still must be supplied and verified on PC/mobile.

3. **Finalize operator/legal sale fields (#155).**
   - routes exist for 特商法, privacy, terms, operator information, and contact.
   - sale readiness remains fail-closed until the required operator/contact fields are configured.
   - final legal wording/operator identity must receive human review before public sale.

4. **Choose one real offer and price.**
   - current ¥1,480 is sandbox-only test configuration, not a public price decision.
   - exact monthly price, included free floor, cancellation description, and any refund policy must be published consistently across HP, Stripe, and terms before charging.

5. **Switch from sandbox to live Stripe only after explicit cost/fee approval.**
   - no live key, live Checkout, or public charging is enabled at this checkpoint.
   - enabling real charging is a separate launch action and must not happen implicitly.

### Can launch with stated limitation

- Phase11 learning-strategy judgment may remain Shadow/HOLD while natural evidence accumulates.
- Past-exam source preference remains non-primary; the completed #105 evaluation supports no selector promotion now.
- Trial100 can initially be entered through the current explicit recording flow instead of a full learner-entry UI.
- Parent/supporter surface can remain intentionally small if its privacy and scope are clearly stated.

### Post-launch improvement

- cohort-level calibration and broader learning-effect analysis;
- richer Trial100 analysis;
- additional lifecycle messaging;
- more refined source-mix personalization if future evidence justifies it;
- paid acquisition only after activation/retention are interpretable.

## 3. Free / paid candidate boundary

Keep one useful free floor and one monthly paid product at launch.

### Free floor

The free experience must reach first value rather than stop at a marketing wall:

- LINE onboarding;
- first meaningful 5-question study block;
- scoring/explanation for questions already served;
- a concrete next action after that block;
- enough basic status to understand what LicenseTown is doing.

First-value event:

**Learner completes the first 5 questions and receives a meaningful next action based on the result.**

### Paid monthly candidate

Paid value should be recurring decision/support value, not merely a bigger pile of questions:

- full adaptive study volume;
- confidence-aware repair/recheck continuity;
- full `合格への道` evidence/navigation;
- learner-selected field study without the free quota boundary;
- parent/supporter monitoring;
- bounded AI consultation/伴走 allowance sized to operating cost;
- Trial100 evidence tracking.

Safety, answer correctness, and essential explanation for an already-served question must not be hidden behind an abusive paywall.

## 4. Pricing hypotheses

These remain experiments, not decisions:

- **¥980/month** — low-friction hypothesis; risk is insufficient margin for support/acquisition/AI.
- **¥1,480/month** — current working hypothesis and sandbox test amount; not yet a public price.
- **¥1,980/month** — requires clearer recurring value, especially parent value and AI/Trial100 support.

Launch should present **one recommended monthly price**, not a three-tier matrix. Gross-margin checks should include Stripe, OpenAI, Render, Neon, LINE, support, refunds/chargebacks, and acquisition cost.

## 5. Official HP status

Completed code-side sale-safety work:

- stale `1000 + 1000 = 2000` claim removed from paid-facing paths;
- formal-bank total is now the default source of truth for public question-count copy;
- fake free-period language removed;
- illustrative dashboard values receive a `画面イメージ` boundary;
- fixed `合格まであと123日` demo framing is removed from the public render boundary;
- mobile privacy typo `金融内容` corrected to `相談内容`;
- legal/footer routes exist and return stable destinations;
- `まずは使ってみる` CTAs use one verified HTTPS configuration boundary and fail closed when missing.

Remaining human/public-sale inputs:

- final LINE/onboarding URL;
- final operator/contact/legal fields;
- final paid offer/price/cancellation/refund language;
- final visual smoke check after those values are configured.

## 6. Acquisition experiment order

Do not start paid acquisition before the full destination/activation path is coherent.

1. existing personal/referral circle;
2. organic PT national-exam educational content;
3. track HP -> LINE -> first 5 questions;
4. observe Day-2 and Day-7 return;
5. only after that, test small paid acquisition.

Content should be useful even when the reader never buys. Do not use unverified teacher endorsement, success rate, or pass claims.

## 7. Activation / retention metrics

Minimum metrics for the first paid cohort:

- HP primary CTA click rate;
- LINE onboarding completion rate;
- first 5-question completion rate;
- time from LINE start to first completed 5 questions;
- `合格への道` open -> recommended-study start rate;
- Day-2 return rate;
- Day-7 return rate;
- weekly active learners completing at least one meaningful block;
- free -> paid conversion rate;
- paid month-1 -> month-2 retention;
- cancellation reason categories;
- AI consultation usage and variable cost per paid learner.

Do not use raw message count or total question count alone as a proxy for learning value.

## 8. Smallest credible launch plan

### Gate A — finish sandbox lifecycle

- prove final Stripe `expired` transition;
- keep paid enforcement OFF;
- confirm no learning history is changed by entitlement expiration.

### Gate B — configure sale truth

- set the real LINE/onboarding URL;
- fill/review operator/legal/contact fields;
- decide one real monthly price and exact free boundary;
- ensure HP, Stripe, terms, and cancellation wording agree.

### Gate C — explicit live-payment go/no-go

Before any real charge:

- disclose expected Stripe/payment fees and any other paid services;
- obtain explicit owner approval;
- only then configure live Stripe and enable the public paid path.

### Gate D — tiny launch

- invite a very small cohort;
- watch onboarding and first 5-question completion;
- collect natural feedback after actual use;
- fix reliability/activation problems before increasing acquisition.

### Gate E — revise before scale

- identify the largest activation/retention failure;
- calculate actual variable cost per active and paid learner;
- revise offer/price/product only from real evidence.

## Current product decision

Do **not** add broad new learning features merely because commercialization work is nearing completion. The shortest credible route is now:

1. finish the Stripe sandbox expiry proof;
2. configure truthful onboarding/legal/offer inputs;
3. perform an explicit live-payment cost/go-no-go decision;
4. launch to a tiny cohort;
5. measure activation and retention before scaling acquisition.

Natural learner evidence continues to outrank speculative feature expansion.