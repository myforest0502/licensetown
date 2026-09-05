# LicenseTown commercialization gap audit v0.3

Date: 2026-09-05

## Purpose

This document refreshes launch readiness after the learning-route audit, supporter rebuild, developer-console expansion, official-HP finishing, Stripe sandbox lifecycle proof, and the change from free-form consultation to the formal-bank `教えて源さん` term explainer.

This is not a revenue forecast, pass-probability claim, or evidence of educational superiority.

Funnel:

`SNS / referral / search -> official HP -> LINE start -> first successful study block -> continued use -> paid conversion -> retention`

## 1. Product core now ready for small-scale product validation

Current strengths:

- Formal Question Bank Q1-Q1737 / 1737 questions (643 original / 1094 past_exam), with saved audit errors 0.
- Normal study is stored-data driven and does not depend on OpenAI per question.
- Confidence-aware history, confident-wrong handling, Knowledge Node evidence, different-question repair confirmation, Recent Question Cooldown, and adaptive repair/checking/exploration foundations are implemented.
- Real-data `合格への道`, deterministic readiness semantics, priority TOP3, learner-selected field study, recommendation study, 熱血, pause/resume, HOME return, scoring and explanation flows are in place.
- The full learner-route real-device audit (#107) completed without observed route failure in the accepted flow.
- `教えて源さん` is now a national-exam term explainer using the formal LicenseTown Question Bank / saved explanations rather than a required OpenAI free-chat call. It answers definition-first, then exam points and related questions.
- Parent `学習見守り` is intentionally small and no longer runs per-question Phase11/readiness diagnostic work on first open.
- Post-rebuild parent first-open real samples on 2026-09-05 were about 4.31-4.73 s server-side (warm n=4), matching the owner's ~5 s device estimate; the page was judged easy to understand.
- Developer diagnostics are separated behind `/internal` admin authorization. The internal top now shows a read-only Question Bank / Knowledge Node / safety / feature-flag overview plus user-specific diagnostics, without adding DB work to parent or learner paths.
- Stripe sandbox subscription lifecycle is proven end-to-end through active -> cancel_at_period_end -> expired entitlement, with verified webhook processing and centralized access policy. Live charging remains OFF.
- Official HP PC/mobile visual paths have been real-device reviewed, factual question-count/illustrative-data boundaries are in place, verified LINE onboarding is configured, and legal/operator routes are configured fail-closed.

The strongest concise product value remains:

**LicenseTown uses actual learning evidence to decide what should happen next, then lets the learner act on that decision immediately.**

A supporting utility value is now clearer too:

**When a national-exam term is unclear, `教えて源さん` explains it from LicenseTown's own formal study data instead of requiring a separate AI chat.**

## 2. What is no longer a launch blocker

The following items were blockers in v0.2 but are now sufficiently resolved for a small pre-sale/product-validation phase:

1. **Stripe sandbox lifecycle proof** — completed. The terminal expired state was observed end-to-end and Issue #154 is closed.
2. **Real onboarding destination** — configured to the verified LicenseTown LINE friend-add URL through `SITE_ONBOARDING_URL`.
3. **Operator/contact runtime configuration** — supplied through Render environment variables without committing personal data; operating brand `myforest` is separated from legal identity.
4. **PC/mobile HP structural and visual defects** — accepted after real-device review through the latest public-site fixes.
5. **Parent/developer responsibility split** — normal parent monitoring no longer serves as an engineering dashboard; internal diagnostics have a separate authenticated route and loading boundary.
6. **OpenAI consultation as a required core feature** — removed from the main product path. The term explainer works from saved formal data without OpenAI API billing.

## 3. Remaining blockers before accepting real money

### A. Decide one real offer and one real price

This is now the largest unresolved commercial decision.

The previous `¥1,480/month` value was a sandbox test amount, not a public price decision.

Before charging, decide and publish consistently:

- one monthly price;
- exactly what remains free;
- exactly what the monthly product adds;
- billing timing / recurring-payment wording;
- cancellation timing;
- refund handling;
- what happens to learning history after cancellation/expiry.

Do not create a three-tier matrix merely to look commercial. Start with one useful free floor and one paid monthly offer if paid launch is chosen.

### B. Re-evaluate the paid boundary after removing free-form consultation

The old paid-candidate list included a bounded AI consultation allowance. That should no longer be treated as a core reason to pay.

The paid value, if used, should instead come from recurring learning-management value such as:

- higher/full adaptive study allowance;
- continuity of repair/recheck/history;
- full `合格への道` navigation and evidence;
- unrestricted learner-selected field study within supported rules;
- parent `学習見守り`;
- Trial100 evidence tracking / richer longitudinal analysis;
- future optional AI features only where they demonstrate enough educational value to justify their variable cost.

Safety, correctness, and explanation for already-served questions should never be degraded merely to force conversion.

### C. Final paid-offer legal / confirmation-screen review

Issue #155 remains open for the actual paid offer, not for HP layout.

Before public charging:

- final price and recurring-payment terms must appear consistently on HP / checkout / terms / legally required display;
- cancellation/refund wording needs final human review;
- checkout confirmation presentation must make the actual charge clear before purchase;
- perform a final pre-launch legal/content smoke check after the real offer is configured.

### D. Explicit live-payment go/no-go

Live Stripe, paid enforcement, and public charging remain OFF.

Enabling real charges must be a separate owner decision after current payment fees and any other paid-service costs are shown. Sandbox configuration must not be mistaken for permission to enable live mode.

## 4. Free / paid boundary recommendation for validation

### Free floor

The free experience should reach real learning value:

- LINE onboarding;
- first meaningful study block;
- scoring and saved explanation for served questions;
- `教えて源さん` term lookup;
- a concrete next action;
- enough status to understand how LicenseTown is guiding study.

First-value event:

**Learner completes the first study block and receives a useful next action based on the result.**

### Paid monthly candidate

Paid value should be **continuity and direction**, not merely access to answers or a larger static question pile.

A candidate paid contract is:

- ongoing adaptive study beyond the free validation allowance;
- persistent repair/recheck continuity;
- full longitudinal `合格への道` evidence/navigation;
- parent monitoring;
- Trial100 longitudinal evidence;
- future premium assistance only after real-use value and cost are measured.

This boundary still requires real-user validation before it should be treated as final.

## 5. Price hypotheses remain hypotheses

Historical hypotheses remain:

- ¥980/month — low-friction, but may underfund support and infrastructure;
- ¥1,480/month — previously used as the sandbox test amount and a working hypothesis, not a decision;
- ¥1,980/month — requires clearer recurring parent/longitudinal value.

The next decision should not be made from competitor aesthetics or development effort alone. Judge price against:

1. value to learner/parent;
2. expected use frequency and retention;
3. actual variable costs;
4. support burden;
5. willingness to pay observed in a tiny cohort.

## 6. Current operating-cost implications

Core study, scoring, saved explanations, dashboard logic, term lookup, parent monitoring, and internal diagnostics do not need a per-question OpenAI call.

OpenAI-dependent legacy/optional paths still exist in the codebase (for example some document/image analysis and written-understanding evaluation), and API billing is currently not a safe assumption. These paths should be classified explicitly as one of:

- remove/deprecate;
- keep as graceful optional fallback;
- re-enable later with measured value and cost.

Do not restore API billing merely because old code can call it. First decide whether each AI-dependent feature improves the actual learning product enough to justify operating cost.

## 7. Parent/supporter status

The parent surface now answers the intended simple questions without loading developer diagnostics:

- how much was studied;
- how long;
- which area;
- recent correctness / understandable current status;
- whether pace/direction appears okay.

Post-rebuild warm real samples were roughly 4.3-4.7 seconds server-side. This is a meaningful improvement from earlier observed ~8-10 second examples, but it is not yet evidence for a universal latency target.

Further performance work belongs in the later evidence-based optimization phase, not before product responsibilities and commercial boundaries are stable.

## 8. Developer-console status

The internal console is now a genuine separate engineering surface rather than only a redirect shell:

- explicit developer-token boundary;
- formal Question Bank count/version/audit status;
- Knowledge Node summary;
- safety/source summary;
- temporary feature/performance flags shown only as booleans;
- per-user Phase11/repeat/cooldown diagnostics;
- learner-view QA preview;
- Render/Neon monitoring acknowledged as external operational sources instead of doing heavy work on console landing.

It can continue to grow, but parent/developer separation itself is no longer the reason to delay commercialization work.

## 9. Acquisition experiment order

Do not start broad paid acquisition yet.

1. continue real use with the existing learner;
2. introduce a very small invited external cohort when the offer/free boundary is clear;
3. observe HP -> LINE -> first study completion;
4. observe Day-2 / Day-7 return and parent usage where applicable;
5. ask whether the product would be worth paying for before enabling real charging;
6. only after activation/retention are interpretable, test small paid acquisition.

Do not use follower count, raw messages, or total served questions as substitutes for learning/product value.

## 10. Smallest credible next sequence

The post-core productization sequence is now materially advanced:

1. learning-route reliability — completed for the current supported routes;
2. supporter/developer separation — completed at the current product boundary;
3. supporter lightweight rebuild — completed first pass and real-device checked;
4. developer console expansion — completed useful v0.2 first pass;
5. commercialization gap audit — this document;
6. pricing / offer / conversion implementation — **next human product decision**;
7. tiny-cohort validation;
8. only then evidence-based broader performance optimization and acquisition scaling.

## Current product decision

Do not add broad new learning features now.

The next hard problem is no longer engineering completeness. It is deciding **what recurring value LicenseTown is asking someone to pay for, and at what price**, now that free-form AI consultation is no longer central.

Until that is decided:

- live payment stays OFF;
- paid enforcement stays OFF;
- development support collection stays OFF;
- OpenAI billing should not be re-enabled just to preserve legacy AI paths;
- natural learner evidence continues to outrank speculative feature expansion.
