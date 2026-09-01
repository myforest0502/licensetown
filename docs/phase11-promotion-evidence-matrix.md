# Phase 11 Promotion Evidence Matrix

Date: 2026-09-02
Status: diagnostics-only implementation complete; learner-facing promotion not yet approved.

This document separates established evidence from evidence still required before promotion. It is a developer decision aid, not a learner-facing score.

## A. Architecture and safety — COMPLETE

- Phase 11 judgment is deterministic and read-only.
- No Production DB write is performed by the judgment layer.
- No formal Knowledge Node state mutation is performed by Phase 11.
- Exact Q selection remains owned by Phase 10 adaptive selection.
- Recent Question Cooldown remains owned by Phase 10.
- Consultation text is not an input.
- Learner-facing recommendation is unchanged.
- Phase 12 consumes Phase 11 output for presentation only and does not redefine mastery.
- Current-vs-Shadow target comparison is symmetric and uses the same formal J1→J7 evidence hierarchy for both targets.

## B. Phase 10 dependency — COMPLETE

Natural adaptive_daily observation confirmed:

- 6 events / 30 questions / 30 unique Q
- all six saved adaptive audit fields present
- observed recent repeats fully explained by Safety/bank-supply exception
- ordinary repair/checking/exploration selections did not bypass cooldown

Phase 10 is operationally closed.

## C. Question Bank repair supply — IMPROVED, CONTENT-QUALITY REVIEW STILL REQUIRED

Initial Production repairability snapshot:

- repairing Nodes: 135
- strong different-Q available: 1
- weak-only: 5
- same-Q/formally blocked: 129

Q1595-Q1605 added strong different-Q supply to 11 existing Safety Nodes.

Current bank:

- Q1-Q1605
- canonical Nodes: 1509
- singleton: 1422
- multi-question: 87
- validator PASS

All 11 pilot source/new pairs classify structurally as `different_question_strong`.

A manual medical review found no obvious incorrect keyed answer in Q1595-Q1605. However structural STRONG classification does not guarantee sufficient **discriminative quality** for formal repair confirmation. Several items, especially Q1600/Q1602/Q1603, contain very weak or obviously implausible distractors.

Therefore:

- the 11 questions may be used as available strong alternate supply under the current formal engine
- but a future rise in `repaired` caused by these pilot questions must not automatically be treated as proof that the repair model is educationally validated
- before using pilot-driven `repairing -> repaired` transitions as strong product evidence, complete the item-quality audit tracked in GitHub Issue #7
- if any deployed Q has already produced learner evidence, do not silently rewrite it without preserving historical interpretation

This improves Safety repair supply but does not make the whole bank repairable. Global supply expansion remains a separate content task.

## D. Shadow judgment static behavior — COMPLETE

J1→J7:

1. safety_repair
2. confident_wrong_cluster
3. repeated_wrong_cluster
4. recheck_due
5. insufficient_coverage
6. uncertain_correct_cluster
7. maintenance_only

Confirmed:

- one ordinary wrong does not automatically commandeer a field
- unknown answers do not create confirmed weakness inside Phase 11 judgment
- sparse fields are treated conservatively
- high same-day volume is an observation, not a blocker
- Shadow does not select exact Q IDs

A separate shared-evidence inconsistency is tracked in Issue #6: `field_evidence` currently allows unknown attempts to enter repeated-weakness aggregation even though Phase 11 itself filters them. Do not consume that field-level repeated-weakness value as confirmed evidence until the inconsistency is fixed.

## E. Current-vs-Shadow comparison — COMPLETE AS DIAGNOSTIC

Both target fields receive the same formal evidence profile.

Different-target labels:

- `different_target_shadow_has_stronger_evidence`
- `different_target_current_has_stronger_evidence`
- `insufficient_evidence_to_judge`

A stronger formal rank at one snapshot is not proof of better future learning outcome.

Supporter profile accuracy is internally a 0–1 ratio; Issue #5 tracks percentage formatting so QA readers do not misread `0.8` as 0.8%. This is presentation-only and does not alter ranking.

## F. Known natural disagreement — OBSERVED

Previously observed:

- Baseline: 小児学 10問
- Shadow: 内科学 10問
- Shadow reason: confident_wrong_cluster
- confidence: high

Internal-medicine diagnostics showed five confident-wrong repairing Nodes including one cross-question confident-wrong Node. This is real repair evidence, but one example is insufficient for promotion.

## G. Repeat structure audit — IMPLEMENTED, PROMOTION INTERPRETATION TEMPORARILY PAUSED

Repeat Structure Diagnostics is on main, but a diagnostics-only false-positive risk has been confirmed and tracked in GitHub Issue #4.

Current classifier can incorrectly label a legitimate **non-recent** adaptive same-Q checking/recheck as `adaptive_unexplained_repeat` because:

- actual `recheck_due` selections use `selection_group='checking'`
- uncertain-correct/checking selections also use group `checking`
- a same-Q that is outside the newest-30 recent window can legitimately be selected without cooldown bypass

Therefore:

**Do not use the current `adaptive_unexplained_repeat` count as a Phase 11 promotion pass/fail gate until Issue #4 is fixed and Production data is re-read.**

The invariant that still matters is narrower:

- saved `recent_question_repeat=True`
- saved `recent_cooldown_bypassed=False`

is a red-flag recent repeat and must remain visible after the diagnostic fix.

Other repeat categories and elapsed-time observations remain useful, but the promotion interpretation of the unexplained count is paused.

## H. Retrospective historical replay — DESIGNED, IMPLEMENTATION PENDING

The learner-facing dashboard stores at most one daily `recommendation_plan` anchor containing the first persisted Baseline field/goal for that JST day.

Historical Baseline phase can be reconstructed from the same source production uses:

`SUM(learning_events.answered_count)` before the plan timestamp.

Shadow replay is eligible only when cumulative question-level history coverage is complete. Legacy learning events must not be assumed to have complete `question_attempts` coverage.

For an eligible snapshot:

1. reconstruct Baseline total answers/phase from events before T
2. verify formal result-to-attempt history coverage
3. truncate attempts to `< T`
4. build field evidence with `as_of=T`
5. apply the **current Phase 11 v0.1 policy** at T
6. compare persisted Baseline target vs replayed Shadow target symmetrically

This is current-policy historical replay, not historical code time-travel and not causal evidence.

See `docs/phase11-retrospective-shadow-audit-v01.md` and GitHub Issue #3.

## I. Natural-use promotion checks — PENDING

### I1. Critical Safety misses

Target: zero cases where stronger unresolved Critical Safety evidence exists while Phase 11 selects a weaker field.

Historical replay may expand the sample if coverage is complete.

### I2. Single-wrong overreaction

Target: no repeated pattern of one ordinary wrong causing unnecessary field takeover.

### I3. Sparse learner coverage

Target: continue coverage when weakness evidence is insufficient.

### I4. Recheck due handling

Target: naturally occurring `recheck_due` work is not starved by J5-J7.

### I5. Phase 11 intent vs Phase 10 exact-Q behavior

Target: repair/recheck/coverage intent is directionally compatible with Phase 10 exact selection without violating cooldown or Safety.

### I6. Baseline disagreement quality

Review both wins and losses:

- Baseline target
- Shadow target
- both formal evidence profiles
- symmetric comparison label
- later target sampling when observable

Do not review only Shadow-favorable cases.

### I7. Recommendation relevance

Prospective natural examples should show Shadow is no less relevant/safe than Baseline and preferably better.

Retrospective replay can support consistency review but cannot substitute for prospective relevance evidence.

### I8. Repeat behavior

This gate is **temporarily not evaluable from the current `adaptive_unexplained_repeat` aggregate** until Issue #4 is fixed.

After the diagnostic fix:

- re-read Production history
- confirm true recent repeat without bypass is absent or individually explained
- do not treat legitimate spaced checking/recheck as regression

### I9. Repair-transition evidence quality

If Q1595-Q1605 begin producing `repairing -> repaired` transitions:

- confirm the formal transition mechanics are correct
- separately confirm the pilot question itself is a meaningful independent knowledge check
- do not count a trivially easy strong-tagged item as full educational validation merely because the formal state changed

Issue #7 owns the content-quality review.

## J. Promotion decision rule

Do not promote from one screenshot, one favorable disagreement, or one burst of pilot repair transitions.

Promotion requires:

- architecture/safety gates remain green
- repeat diagnostic false-positive issue resolved before using repeat count as evidence
- no true unexplained recent adaptive repeat regression
- no Critical Safety miss
- no systematic single-wrong overreaction
- acceptable sparse-coverage behavior
- recheck_due behavior observed when naturally available
- symmetric disagreement review includes Current wins/losses
- eligible retrospective replay reveals no policy-consistency regression
- pilot repair evidence is interpreted with item-quality review rather than structural STRONG status alone
- prospective natural evidence is at least clearly no worse than Baseline

If evidence is mixed, remain Shadow-only rather than changing ranking weights prematurely.

## K. Next implementation/review order

1. Fix Repeat Structure false-positive classification (Issue #4).
2. Re-read Production Repeat Structure Audit with corrected semantics.
3. Fix shared unknown/repeated-weakness field evidence inconsistency (Issue #6) before future consumers rely on it.
4. Implement Phase11 retrospective historical replay (Issue #3).
5. Review Q1595-Q1605 discriminative quality before treating pilot repair transitions as strong educational evidence (Issue #7).
6. Format symmetric profile accuracy clearly in Supporter diagnostics (Issue #5).
7. Read current symmetric Baseline-vs-Shadow profiles.
8. Review historical/current disagreement winners including Current wins.
9. Check Safety / sparse coverage / recheck candidates.
10. Continue prospective natural sampling.
11. Only then decide on a limited learner-facing pilot.

Diagnostics robustness Issue #2 (30-question session set-sequence validation) should also be fixed, but it is not a Phase 11 ranking change and does not reopen the already verified Phase 10 natural-use session.
