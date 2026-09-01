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

## Formal policy newly fixed

### Issue #11 — evaluable-only Phase11 J2 accuracy tie-break

Decision:

- unknown counts as learning/exposure activity
- unknown does not count as confirmed wrong evidence
- unknown must not lower the accuracy used as the final J2 weakness-priority tie-break

Future implementation should add separate evidence fields:

- `evaluable_answer_count`
- `evaluable_correct_count`
- `evaluable_accuracy`

Existing general `question_accuracy` semantics remain unchanged for compatibility.

J2 reliability threshold must use **10 evaluable answers**, not 10 raw attempts.

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
- replay applies the **current Phase11 v0.1 policy** to historical evidence; it is not historical-code time travel and not causal A/B evidence

## Current promotion order

1. Execute tests for draft PR #9 and #10; merge only if green.
2. Implement Issue #4 corrected repeat classification and re-read Production repeat history.
3. Implement Issue #11 evaluable-only J2 tie-break semantics together with the shared evidence fix.
4. Implement Issue #3 retrospective replay.
5. Harden Issue #2 and fix Issue #5 presentation when touching the same diagnostics area.
6. Continue prospective natural-use comparison of Baseline vs Shadow, including Current wins and Shadow losses.
7. Observe natural recheck_due behavior when it exists.
8. Only then consider a limited learner-facing Phase11 pilot.

## Promotion rule unchanged

Do not promote Phase11 because of one favorable screenshot, one disagreement, or one newly repaired Node.

Promotion still requires no Critical Safety miss, no systematic single-wrong takeover, trustworthy repeat diagnostics, acceptable sparse coverage, recheck behavior, symmetric disagreement review, and prospective evidence that is clearly no worse than Baseline.
