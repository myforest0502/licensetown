# LicenseTown pre-sale paid-facing audit v0.1

Date: 2026-09-03
Related: #109, #137

## Purpose

This audit identifies the current paid-facing trust/prototype risks before LicenseTown accepts money. It is based on the current `main` route/template structure and does not change runtime behavior.

Severity:
- `BLOCKER`: must not remain in a broadly paid launch path.
- `MUST FIX`: can coexist during internal/pilot use but should be corrected before sale.
- `ACCEPTABLE LIMITATION`: may launch if clearly stated and technically contained.

## Current learner/parent web surfaces reviewed

- `/goukaku-no-michi`
- `/goukaku-no-michi/subjects`
- `/goukaku-no-michi/footprints`
- `/goukaku-no-michi/learning`
- `/supporter`
- supporter `合格への道` read-only views
- legacy supporter diagnostic/preview route definitions as a boundary check

The LINE study engine, dashboard recommendation POST path, and restart-safe field route are separate from this document and remain covered by #107/#108.

## Findings

### F1 — legacy field-study confirmation page is still an explicit prototype stub

**Severity: BLOCKER if exposed to paying users**

`templates/goukaku/learning.html` still states:

> `Ver.1では選択内容の確認まで利用できます。問題出題はLINEの既存学習モードへ接続します。`

The page accepts a field/count from query parameters and hands off using a generated LINE text message rather than the current formal learner-navigation recommendation contract.

This is not merely cosmetic: the main `合格への道` legacy weak-field card still links to `goukaku_ui.learning`.

Required pre-sale disposition:
- either remove this route from learner-facing navigation and route all study starts through the formal structured selector path,
- or replace it with a fully authenticated/token-preserving route that delegates exact-Q selection to the centralized selector.

Do not maintain this as a second independent selection contract.

### F2 — legacy weak-field `取り組む` link can drop learner dashboard context

**Severity: BLOCKER**

The legacy weak-field card links to `url_for('goukaku_ui.learning', field=item.name, count=10)` without carrying the dashboard token. The destination page's back link also targets `goukaku_ui.home` without the original token.

An authenticated learner can therefore move from a real-data dashboard into a contextless prototype page.

Required disposition:
- remove the legacy action once learner-navigation is authoritative, or
- preserve/revalidate auth context and call the existing structured recommendation endpoint.

### F3 — learner dashboard/subjects currently render a learner-shaped empty page when no valid token is present

**Severity: MUST FIX before broad sale**

`/goukaku-no-michi` calls `build_dashboard(None)` when the dashboard token is absent/invalid. The result is a fully rendered dashboard shell populated with zero/empty defaults rather than an authentication error or a clearly separate public landing page.

`/goukaku-no-michi/subjects` similarly calls field/activity builders with an empty user id when not authenticated.

The values are not fabricated learner history, but the page shape can be mistaken for actual learner state. In a paid product the failure mode should be unambiguous.

Required disposition:
- fail closed for learner-data routes, or
- redirect to a clearly distinct public/reconnect screen that cannot be confused with a learner dashboard.

### F4 — two different meanings of “overall progress” coexist

**Severity: MUST FIX**

The evidence-based learner navigation/readiness path now exists, but the default legacy `総合到達度` card can still use `calculate_overall_progress(study_minutes, total_answers, unique_answered_questions)` when `ENABLE_OVERALL_PROGRESS_UI` is off.

The legacy card does state that it is a learning-volume indicator and not a pass guarantee, which reduces risk. However, displaying it next to the newer evidence-based current-position guidance can create two competing definitions of progress in a paid experience.

Required disposition before sale:
- prefer the formal evidence-based progress presentation when validated for production, or
- rename the legacy measure more explicitly as activity/learning-volume progress and visually subordinate it.

Never present either measure as a pass probability.

### F5 — field labels based on raw accuracy are descriptive, not formal readiness

**Severity: ACCEPTABLE LIMITATION with wording discipline**

The legacy field list uses thresholds such as `得意（70%以上）`, `要注意`, `弱点` from raw accuracy. The formal evidence/readiness layer is more conservative and distinguishes insufficient coverage, active repair, and retention.

This can remain as a descriptive score view if the product does not imply that the threshold is the formal readiness judgment. New paid-facing guidance should prefer the evidence-based layer.

### F6 — legacy supporter diagnostic route functions remain in `goukaku_ui.py`

**Severity: ACCEPTABLE ONLY while the #99 global internal boundary remains enforced**

Legacy supporter diagnostic/learner-preview route definitions are still present in the module. #99 introduced global blocking/internal-only replacements, and the supporter page was separated from developer diagnostics.

Pre-sale requirement:
- keep regression coverage that the legacy URLs remain inaccessible from normal supporter use,
- do not reintroduce links from supporter pages,
- eventually remove obsolete route definitions once compatibility needs are gone.

### F7 — no payment/entitlement implementation is currently present

**Severity: BLOCKER before first real paid transaction**

Repository search found no current payment/subscription implementation contract. This is appropriate for the present audit stage, but no payment button should be launched before the entitlement lifecycle is defined.

Minimum provider-neutral entitlement model:

- `user_id`
- `plan_code`
- `status` (`active`, `grace`, `cancel_at_period_end`, `expired`, `payment_failed`)
- `provider_customer_id`
- `provider_subscription_id`
- `current_period_start`
- `current_period_end`
- `cancel_at_period_end`
- `last_provider_event_id`
- `updated_at`

Rules:
- provider webhooks/events must be idempotent,
- learner authorization should read entitlement state, not trust client-side UI,
- cancellation should not silently erase earned learning history,
- expired users retain access to their data and essential account/privacy controls,
- answer correctness and already-served essential explanations are not withdrawn mid-question.

### F8 — trust/legal artifacts are not yet a verified launch gate

**Severity: BLOCKER before broad paid launch**

Before accepting money, confirm the actual production surfaces for:
- Terms of Service
- Privacy Policy
- cancellation/refund handling
- support/contact route
- required operator/commercial disclosure for the chosen jurisdiction/payment method
- truthful AI-use explanation
- limitation language (no pass guarantee, no fabricated outcomes, no unapproved endorsement)

This checklist is product readiness, not legal advice; final language should be reviewed for the actual business/jurisdiction.

## Minimal launch gate

The first real paid transaction is allowed only after all of the following are true:

1. #107 real-device learner-route smoke gate passes.
2. #100/#106 measured latency baseline exists and no core first-value path has an unknown severe delay.
3. F1/F2 are removed from the paid learner path.
4. learner data routes fail closed or clearly separate unauthenticated state (F3).
5. progress terminology is unambiguous (F4/F5).
6. supporter/developer boundary regression remains green (F6).
7. provider-neutral entitlement contract and idempotent payment lifecycle are implemented/tested (F7).
8. trust/legal/support artifacts are present and linked before purchase (F8).
9. no pass guarantee, fabricated success statistic, or unverified endorsement is used.
10. payment cancellation/expiry cannot destroy learner history.

## Recommended next implementation order

1. fix the paid-facing learner-route/prototype leaks F1–F4;
2. finish real-device route validation #107;
3. collect latency evidence #100/#106;
4. define entitlement storage/API contract before choosing payment UI details;
5. add trust/legal/support pages and purchase disclosures;
6. only then connect a payment provider and test lifecycle states end-to-end.

This keeps monetization subordinate to the already-formal learning evidence and selector architecture rather than creating a second product path around it.
