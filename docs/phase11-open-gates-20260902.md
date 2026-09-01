# Phase 11 Current Open Gates — 2026-09-02

Status: learner-facing promotion remains blocked; diagnostics and evidence work continue.

This is the current operational supplement to `phase11-promotion-evidence-matrix.md`.

## Completed since the matrix snapshot

### Q1595-Q1605 content-quality audit — COMPLETE

Issue #7 is closed.

Audit document:

`docs/strong-repair-pilot-content-audit-v01.md`

Findings:

- no clearly incorrect keyed answer found in Q1595-Q1605
- structural `different_question_strong` status remains unchanged
- discriminative quality varies materially
- Q1601 is the strongest current repair-confirmation exemplar
- Q1600 / Q1603 / Q1599 / Q1602 / Q1604 require the most caution when interpreting future `repairing -> repaired` transitions

A rise in repaired Nodes from these items is formal state evidence, not by itself proof of calibrated educational difficulty.

## Implementation-ready, pending executable tests

### Issue #6 — unknown in field repeated-weakness evidence

Draft PR #9:

`fix/field-evidence-unknown-weakness-v01`

Production-code diff is intentionally minimal:

- repeated-weakness derivation receives non-unknown attempts only
- total answers, unknown counts, general accuracy inputs and Node-state derivation remain unchanged

Do not merge until focused/full pytest can run.

### Issue #8 — cross-Node STRONG defense

Draft PR #10:

`fix/repair-confirmation-same-node-guard-v01`

The core repair-confirmation classifier now fails closed unless both questions resolve to the same canonical Node before any STRONG decision.

Current formal state-transition code already enforces one canonical Node, so this is defense-in-depth rather than a known Production state corruption.

Do not merge until focused/full pytest can run.

## Unknown evidence policy — FORMALLY DEFINED

Canonical policy documents:

- `docs/unknown-evidence-semantics-v01.md`
- `docs/unknown-storage-contract-v01.md`

Core rule:

> unknown means encountered but not evaluably answered.

Therefore unknown has different meanings by layer.

### Exposure/activity

Unknown counts toward raw activity/exposure and coarse global answer-volume milestones.

### Formal Node state

Unknown remains an unresolved repair trigger:

- it can move a Node to `repairing`
- it can reopen a repaired/stable Node
- a later strong different-Q confidence=1 correct may still confirm repair

Do not remove this behavior without a separate state-machine decision.

### Confirmed weakness

Unknown does not independently create confirmed wrong evidence, repeated weakness, confident wrong, or Critical Safety wrong evidence.

### Evaluable policy statistics

Issues #11/#12/#13 specify one shared evidence definition:

- `evaluable_answer_count`
- `evaluable_correct_count`
- `evaluable_accuracy`

Existing general/raw accuracy fields remain unchanged for compatibility.

## Phase11 unknown-related gates

### Issue #11 — J2 evaluable-only accuracy tie-break

Formal decision:

- J2 final accuracy tie-break uses `evaluable_accuracy`
- reliability threshold is `evaluable_answer_count >= 10`
- unknown cannot make an otherwise equal field appear weaker through the final accuracy tie-break

J2 evidence hierarchy itself remains unchanged.

### Issue #12 — J5 evaluable field sufficiency

A field with many unknown attempts must not escape insufficient-coverage merely because raw `question_answer_count >= 10`.

After the global 100-answer stage boundary, J5 field sufficiency uses:

- `evaluable_answer_count < 10` => insufficient coverage

The global 100-answer foundation/analysis exposure milestone remains raw for compatibility.

### Issue #13 — J6 evaluable denominator

J6 uncertain-correct stabilization uses:

- minimum `evaluable_answer_count >= 5`
- uncertain-correct proportion = uncertain-correct / evaluable answers

Unknown cannot satisfy the five-answer threshold or dilute the proportion.

## Phase10 unknown semantics

### Issue #14 — Safety unknown selector reason

Current selector correctly treats unknown as repair work, but Safety unknown-only evidence can currently be labeled `safety_wrong` because unknown Qs are placed in the internal wrong-question set.

Approved future semantics preserve Safety priority and the existing Safety singleton cooldown exception while separating the audit reason:

- confirmed Safety wrong => `safety_wrong`
- Safety unknown-only unresolved => `safety_unresolved`

A Node containing both real wrong and unknown remains `safety_wrong`.

Historical saved events are not rewritten.

### Issue #15 — Node repair trigger vs confirmed weakness

Current state transition behavior remains intact, but returned state evidence must not be casually interpreted as confirmed weakness when unknown is the only repair trigger.

Before changing legacy `evidence_level` fields, audit consumers and add explicit confirmed-weakness fields if needed.

## Supporter diagnostic unknown semantics

### Issue #16 — weekly wrong/unknown overlap

Current weekly Q history can place an unknown Q in both `wrong_question_ids` and `unknown_question_ids` because unknown is physically stored with `is_correct=false`.

Approved diagnostic meaning:

- unknown list = unknown attempts
- wrong list = evaluable non-unknown wrong attempts
- a Q may still appear in both only if separate attempts of both kinds genuinely occurred within the period

This is Supporter diagnostic cleanup only.

## Diagnostics gates still open

### Issue #4 — Repeat Structure false positive

Formal matrix is fixed:

- recent=True / bypass=True -> `justified_cooldown_bypass`
- recent=True / bypass=False -> `adaptive_unexplained_repeat` red flag
- recent=False / bypass=False -> `adaptive_spaced_repeat`
- recent=False / bypass=True -> `adaptive_metadata_inconsistent`

Do not use the current pre-fix `adaptive_unexplained_repeat` aggregate as a promotion pass/fail gate.

### Issue #2 — adaptive 30-question completion hardening

Confirmed event format:

`{session_id}:{set_no}`

A complete 30-question audit requires exact set numbers `{1,2,3,4,5,6}`, one session ID, six events, 30 results and 30 unique Qs.

This hardening does not invalidate the already manually verified Production 30-question session.

### Issue #5 — symmetric profile accuracy display

Internal profile accuracy is a 0-1 ratio while the Supporter template currently renders the raw value.

Presentation-only fix remains pending. Do not alter ranking semantics to solve a display problem.

## Phase11 retrospective replay

### Issue #3 — read-only historical replay

Specification is ready.

Confirmed persistence behavior:

- `recommendation_plan` is written only when the learner opens `/goukaku-no-michi`
- Supporter views and learner-preview do not write it
- persisted payload contains Baseline `field` and `goal`
- historical Baseline phase must be reconstructed from `SUM(learning_events.answered_count)` before snapshot T
- Shadow replay is eligible only when formal result/attempt history coverage is complete
- replay applies the **current Phase11 policy** to historical evidence; it is not historical-code time travel and not causal A/B evidence

Static audit also confirmed Baseline field statistics count unknown in raw answered count while unknown does not increment correct count. Retrospective output should therefore show raw vs evaluable evidence context for both target fields without claiming that unknown caused the persisted Baseline choice.

Production `question_attempts` has no dedicated answer_status column; `get_question_attempts()` reconstructs unknown from empty `selected_answers`. Retrospective coverage validation must use that actual storage contract and fail closed on event/attempt inconsistency.

## Current promotion/implementation order

1. Execute tests for draft PR #9 and #10; merge only if green.
2. Land the shared evaluable evidence fields once #6 is green.
3. Implement Issues #11/#12/#13 together from that shared evidence definition; do not duplicate unknown filters in each rule.
4. Implement Issue #14 Safety unresolved labeling without weakening Safety priority/cooldown protection.
5. Implement Issue #4 corrected repeat classification and re-read Production repeat history.
6. Implement Issue #3 retrospective replay using the corrected current-policy evidence semantics.
7. Harden Issue #2 and fix Issues #5/#16 when touching the same Supporter diagnostics area.
8. Audit/clarify legacy state evidence fields under Issue #15 before any new consumer treats them as confirmed weakness.
9. Continue prospective natural-use Baseline-vs-Shadow comparison, including Current wins and Shadow losses.
10. Observe natural recheck_due behavior when it exists.
11. Only then consider a limited learner-facing Phase11 pilot.

## Promotion rule unchanged

Do not promote Phase11 because of one favorable screenshot, one disagreement, one newly repaired Node, or one apparently better formal rank.

Promotion still requires no Critical Safety miss, no systematic single-wrong takeover, trustworthy repeat diagnostics, evaluable sparse-coverage handling, correct recheck behavior, symmetric disagreement review, and prospective evidence that is clearly no worse than Baseline.
