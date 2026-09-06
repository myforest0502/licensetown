# Phase 11 Current Open Gates — 2026-09-06

Status: **learner-facing promotion remains HOLD / Shadow-only.**

This snapshot supersedes the 2026-09-03 operational note for current natural-use evidence. It does not change J1-J7 ranking, Phase10 exact-question selection, Safety, Recent Cooldown, formal Node-state rules, or learner-facing recommendations.

## 1. Natural study-day evidence

Production recorded 200 study answers on 2026-09-06 JST:

- correct: 149 / 200 = 74.5%
- unique questions: 148
- same-day repeat attempts: 52
- unique canonical Nodes observed: 143
- confidence=1: 112
- confidence=2: 87
- confidence=3: 1
- confident wrong: 12

Cumulative same-day 50-question accuracy:

- 1-50: 78.0%
- 51-100: 78.0%
- 101-150: 74.0%
- 151-200: 68.0%

The final cumulative block was 10.0 percentage points below the first, but this must not be read as one uninterrupted 200-question session. Production timestamps contain a 322-minute gap between the morning and afternoon study periods. The block trend is a same-day cumulative-load fact, not proof of fatigue.

## 2. Generic repeats are not repair evidence

Overall same-day repeat accuracy was 45/52 = 86.5%, but prior-answer-state inspection shows:

- wrong -> correct: 6
- wrong -> wrong: 5
- correct -> correct: 39
- correct -> wrong: 2

Only 11/52 repeats immediately followed a wrong answer. Their immediate wrong-to-correct rate was 6/11 = 54.5%.

Therefore generic repeat accuracy must not be used as a repair-effectiveness metric. Phase11 diagnostics now report repeat-after-wrong and repeat-after-correct transitions separately.

## 3. STRONG repair supply is now being exercised naturally

The same study day contained 90 `adaptive_daily` attempts. The selector preserved the intended 15/10/5 composition across three 30-question sets.

Within adaptive repair work:

- repair attempts total: 45
- STRONG different-question repairing attempts: 35
- STRONG correct: 26 / 35 = 74.3%
- STRONG correct with confidence=1: 13
- STRONG wrong: 9
- distinct STRONG Nodes: 29
- distinct STRONG questions: 29
- STRONG recent-question repeats: 0
- STRONG cooldown bypasses: 0
- weak different-question repairing attempts: 5
- confident-wrong weak attempts: 3, all correct
- Safety same-question attempts: 2, one correct

The 13 confidence=1 correct STRONG attempts are **formal-confirmation candidates**, not independent state mutations. No later wrong answer was observed on those 13 Nodes during the rest of the same study day.

This is materially stronger evidence than merely showing that alternate questions exist in the bank. Repair Supply is now being selected and answered in natural Production use.

## 4. Retention gate timing is now predictable without manufacturing data

Read-only Production inspection of persisted adaptive STRONG repair confirmations identifies surviving confirmation candidates from earlier natural use.

The earliest currently observed candidates have confirmation timestamps around 2026-09-02 08:26 JST, giving seven-day review timing around **2026-09-09 08:26 JST** under the formal repaired-node policy.

Additional candidates are due later on 2026-09-09, and the 13 new candidates from 2026-09-06 would become review candidates around 2026-09-13 if no intervening evidence returns them to repairing.

These are timing forecasts from persisted natural history. Do not alter timestamps or create artificial attempts to make J4 observable sooner.

## 5. Current recommendation evidence

The persisted learner-facing recommendation plan for 2026-09-06 targeted **生理学**, goal 10, with learning intent `repair` and reason `confident_wrong_repair`.

This is notable because the current Baseline path is no longer merely a sparse-coverage recommendation in this natural state. Future Baseline-vs-Shadow review must compare both policies on the evidence actually present at each snapshot rather than assuming the older Baseline behavior remains unchanged.

No learner questionnaire is justified solely to manufacture another comparison sample.

## 6. Current open gates

### Gate 1 — Natural J4 retention

Still the most important missing evidence class. The first currently forecast natural review window begins around 2026-09-09 JST.

Observe:

- whether the formal state becomes `recheck_due` as expected;
- whether J4 receives appropriate priority when no stronger J1-J3 trigger applies;
- whether the selected retention question provides valid STRONG evidence;
- whether the outcome becomes `stable` or returns to `repairing`.

### Gate 2 — Repair durability

Natural same-day STRONG repair performance is now observable, including 13 confidence=1 correct candidates on 2026-09-06. The unresolved question is durability after spacing.

### Gate 3 — Prospective Baseline-vs-Shadow diversity

Continue natural collection only. Existing evidence should eventually include Shadow-stronger, Baseline-stronger, same-target, inconclusive, Safety-sensitive, and retention cases. Do not set a sample count that overrides evidence quality.

### Gate 4 — Safety/repeat/selector surveillance

Continue to block promotion for any meaningful recurrence of:

- Phase11 Critical Safety miss;
- unexplained recent adaptive repeat;
- metadata inconsistency that harms auditability;
- J2/J3 formal-trigger mismatch;
- one-ordinary-wrong takeover;
- conflict between Phase11 intent and Phase10 exact-question behavior.

The 35 STRONG repair attempts observed on 2026-09-06 contained zero recent-question-repeat flags and zero cooldown bypasses.

## 7. J4/J5 readiness work completed on 2026-09-06

Everything that can be prepared without manufacturing future learner behavior is now on main and read-only:

- due-before-attempt retention outcome replay catches a one-attempt `repaired -> recheck_due -> stable` transition that prefix-only timelines can hide;
- retention STRONG-supply preflight identifies repaired/due Nodes without a formal STRONG alternate;
- cooldown-aware preflight distinguishes static STRONG supply from a STRONG alternate that is actually usable outside the current 30-attempt Recent Question Cooldown window;
- the J4 gate does **not** pass merely because any retention attempt occurred: it requires a natural STRONG different-question review with a decisive formal outcome (`stable` or `repairing`);
- J5 independently joins persisted adaptive selection metadata to formal attempt history and revalidates each saved `selection_reason=recheck_due` exact Q against the retention reference immediately before answer time;
- J5 is `BLOCKED` on an evaluable weak/same-Q mismatch, `PASS` only on evaluable STRONG alignment, otherwise `OPEN`;
- J5 aggregate evidence is included in the internal Promotion Evidence Bundle.

A direct Production cross-check on 2026-09-06 found **zero persisted adaptive selections with `selection_reason=recheck_due`** in the natural learner history so far. Therefore there is no valid J4/J5 outcome to judge yet, and no further implementation should be invented solely to manufacture one.

## 8. Decision

**HOLD / Shadow-only remains correct.**

The reason is now an evidence boundary rather than an implementation gap. Repair Supply is being exercised naturally, J4/J5 capture and fail-closed gate logic are ready, and the remaining question is whether spaced repairs survive and are handled correctly when they become naturally due.

No ranking-weight change, synthetic learner event, timestamp manipulation, or learner-facing Phase11 promotion is justified before that evidence arrives.
