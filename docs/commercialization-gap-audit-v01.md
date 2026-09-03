# LicenseTown commercialization gap audit v0.1

Date: 2026-09-03

## Purpose

This document defines the smallest credible path from the now-working learning core to a product that can be sold responsibly. It is not a revenue forecast and does not claim pass probability or educational superiority without evidence.

Funnel to optimize as one system:

`SNS / referral / search -> official HP -> LINE start -> first successful 5-question session -> continued use -> paid conversion -> retention`

## 1. Current sellable strengths

LicenseTown already has several pieces that are meaningfully different from a static question bank or generic chat AI:

- Formal Question Bank frozen at Q1-Q1737 with manifest/version/count validation.
- Normal study is stored-data driven; no per-question OpenAI dependency.
- Confidence-aware learning history and confident-wrong detection.
- Knowledge Node based repair with different-question STRONG confirmation.
- Recent Question Cooldown and cross-route dashboard recommendation unification.
- Adaptive daily selection with repair/checking/exploration metadata.
- Real-data dashboard evidence, deterministic readiness status, and learner-facing `合格への道` navigation.
- Restart-safe learner-selected field routing for both study and nekketsu entry.
- Supporter/developer diagnostics boundary established.
- Natural learner feedback is already being used as product evidence instead of assumed preference.

These strengths support a simple value proposition: **LicenseTown decides what to do next from actual learning evidence, then lets the learner study immediately.**

## 2. Must-fix blockers before charging broadly

### Must-have before sale

1. **Finish real-device route verification (#107).** Automated route repair exists, but every supported learner entry path still needs one real smartphone LINE smoke test before the product is called reliable.
2. **Measure user-perceived latency (#100 / #106).** Especially supporter first-open, study start, answer->result, consultation, and `合格への道`. Do not sell a product whose slowest core path is still unknown.
3. **Define Trial100 recording (#102).** Readiness can already treat missing Trial100 as missing evidence, but paid-facing readiness becomes more credible once real full-format results can be recorded audibly.
4. **Remove/identify remaining prototype-only paid-facing values.** No demo statistic, placeholder, internal diagnostic wording, or developer concept should appear in learner/parent paid paths.
5. **Minimum trust pages before payment.** Terms, privacy, cancellation/refund handling, support contact, operator information as legally required, and truthful description of what AI does/does not do.
6. **Payment lifecycle.** Purchase, entitlement check, failed payment, cancellation, expiry, and restore flow must be explicit before money is accepted.

### Can launch with a stated limitation

- Phase11 remains Shadow/HOLD while natural prospective evidence accumulates.
- Past-exam source preference (#105) can remain diagnostic-only; current evidence does not justify changing selector priority.
- Trial100 can initially be entered manually by parent/developer rather than digitizing all 100 answers.
- Supporter view can stay deliberately small if the parent contract is clear and fast.

### Post-launch improvement

- More sophisticated source-mix personalization.
- Additional Trial100 analytics.
- Broader cohort calibration once more learners exist.
- More acquisition channels and automated lifecycle messaging.

## 3. Proposed free / paid boundary

Keep the first offer simple. Do not create many tiers until real users reveal a need.

### Free floor

Purpose: let a learner experience the core value, not merely view marketing.

Suggested free experience:
- LINE onboarding and name registration.
- A limited daily study allowance sufficient to complete a first meaningful 5-question session.
- Basic scoring/explanation.
- Limited `合格への道` current-position summary.
- A small consultation allowance or no-cost introductory consultation quota.

The first-value event should be: **the learner completes the first 5 questions and receives a concrete next action based on the result.**

### Paid monthly

Paid should unlock recurring decision/support value rather than simply “more questions”:
- Full daily adaptive study volume.
- Confidence-aware repair/recheck continuity.
- Full `合格への道` evidence and next-action navigation.
- Learner-selected field study and normal supported routes without free quota restriction.
- Parent/supporter monitoring.
- AI consultation allowance sized to operating cost.
- Trial100 result tracking when implemented.

Do not put Safety, answer correctness, or essential explanations behind an abusive paywall after a question is already served.

## 4. Pricing hypotheses to test

These are hypotheses, not a final price. Actual gross margin must be checked against OpenAI, Render, Neon, LINE, payment, support, and acquisition cost before launch.

### Hypothesis A: ¥980/month

Use if the goal is low-friction parent/student trial and AI usage remains tightly bounded. Advantage: easy first purchase. Risk: support/payment/acquisition overhead may make the price too low for sustainable reinvestment.

### Hypothesis B: ¥1,480/month

Current leading hypothesis for a single simple paid plan. It leaves more room for AI consultation and infrastructure while remaining far below private tutoring/cram-school economics. Validate willingness to pay rather than assuming affordability equals value.

### Hypothesis C: ¥1,980/month

Use only if the paid experience clearly includes durable parent value, meaningful AI consultation, Trial100/readiness evidence, and strong reliability. This price requires clearer proof of recurring value.

Initial test should compare clarity and conversion around **one recommended paid price**, not show a confusing three-tier matrix. The other values are experiment anchors.

## 5. Official HP conversion gaps

The official HP should answer these in this order:

1. What is LicenseTown?
2. Who is it for?
3. What problem does it remove today?
4. What happens after LINE start?
5. Why is its recommendation more than random question delivery?
6. What does the parent see?
7. What is free and what is paid?
8. What does it cost and how does cancellation work?
9. What evidence supports the claims?
10. One primary CTA to LINE/onboarding.

Preserve the established brand direction and main copy, but every section should be judged by whether it reduces uncertainty before the next funnel step.

Do not use teacher endorsement, pass-rate claims, or learner success claims without explicit truthful evidence and permission.

## 6. Acquisition experiment order

Do not start with paid advertising. First prove that the destination and activation path work.

1. **Existing personal/referral circle:** tiny controlled cohort; observe onboarding and first-study completion.
2. **Organic SNS educational posts:** useful PT national-exam learning content, common mistakes, confidence-aware study ideas, and product demonstrations.
3. **Track HP -> LINE -> first 5 questions**, not impressions alone.
4. **Only after activation/retention is interpretable**, test small paid acquisition.
5. Scale only channels whose acquired learners actually study and return.

Content should help even when the reader does not buy. Product mentions should connect naturally to the problem shown in the post.

## 7. Activation and retention metrics

Minimum funnel metrics:

- HP primary CTA click rate.
- LINE start/onboarding completion rate.
- First 5-question completion rate.
- Time from LINE start to first completed 5 questions.
- Day-2 return rate.
- Day-7 return rate.
- Weekly active learners who complete at least one meaningful study block.
- `合格への道` open -> recommended study start rate.
- Free -> paid conversion rate.
- Paid month-1 -> month-2 retention.
- Cancellation reason categories.
- AI consultation use per paid learner and estimated variable cost.

Do not optimize raw message count or total questions answered as a substitute for learning value.

## 8. Smallest credible launch plan

### Gate 1: reliability
- Close #107 only after real-device smoke testing.
- Capture #100/#106 latency baselines and fix only measured bottlenecks that materially hurt first value.

### Gate 2: trust + payment readiness
- Complete terms/privacy/support/cancellation/operator disclosures.
- Implement one paid entitlement lifecycle.
- Confirm no paid-facing demo/internal values remain.

### Gate 3: offer
- One useful free floor.
- One recommended monthly paid plan; start testing around the ¥1,480 hypothesis unless real cost/value evidence argues otherwise.
- State limitations plainly; no pass guarantee.

### Gate 4: tiny launch
- Invite a very small cohort first.
- Measure the full funnel through first 5 questions, Day-2/Day-7 return, and paid conversion.
- Interview or collect brief natural feedback only after actual use.

### Gate 5: revise before scale
- Fix the largest observed activation/retention failure.
- Recalculate operating cost per active/paid learner.
- Only then increase SNS volume or test paid acquisition.

## Current product decision

The next commercialization work should **not** be “add more features.” The shortest path to revenue is:

1. prove all learner routes on a real device;
2. measure and fix noticeable latency;
3. establish trust/payment basics;
4. make the free-to-paid promise simple;
5. launch to a tiny cohort and measure real continuation.

Learning-engine changes continue only when natural learner evidence or safety/reliability data justify them.