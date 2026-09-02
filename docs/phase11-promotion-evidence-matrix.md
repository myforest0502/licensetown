# Phase 11 Promotion Evidence Matrix

Date: 2026-09-02
Status: diagnostics/formal-policy implementation complete; learner-facing promotion not yet approved.

This document separates established evidence from the remaining Production/natural-use evidence required before promotion. It is a developer decision aid, not a learner-facing score.

## A. Architecture and safety — COMPLETE

- Phase 11 judgment is deterministic and read-only.
- No Production DB write is performed by the judgment layer.
- No formal Knowledge Node state mutation is performed by Phase 11.
- Exact Q selection remains owned by Phase 10 adaptive selection.
- Recent Question Cooldown remains owned by Phase 10.
- Consultation text is not an input.
- Learner-facing recommendation is unchanged.
- Phase 12 consumes Phase 11 output for presentation only and does not redefine mastery.
- Current-vs-Shadow target comparison is symmetric and uses the same formal J1→J7 hierarchy for both targets.

## B. Phase 10 dependency — COMPLETE

Natural adaptive_daily observation already confirmed:

- 6 persisted sets / 30 saved results / 30 unique Q
- all six adaptive audit fields persisted
- observed recent repeats were explained by the Safety/bank-supply exception at that time
- ordinary repair/checking/exploration selections did not bypass cooldown

The saved-session diagnostic is now hardened. Completion requires:

- exactly six events
- event keys parse as `{session_id}:{set_no}`
- one session ID
- set numbers exactly 1..6
- 30 result rows
- 30 unique question IDs

Supporter diagnostics now shows the session status and parsed set numbers directly. This hardening does not reopen the already manually verified Phase 10 natural-use session.

## C. Formal repair evidence semantics — COMPLETE

The current formal implementation now distinguishes:

- unresolved/unknown evidence from confirmed weakness
- current repair-cycle weakness from old repaired/stable weakness
- evaluable answers from zero-answer attempts for Phase 11 weakness/coverage tie-breaks
- actual wrong-question field attribution for multi-field Nodes
- retention-reference field attribution for recheck_due

Important formal protections on main include:

- `recheck_due` failure starts a new repair cycle rather than inheriting old repair references
- J1/J2/J3 use current-cycle active weakness rather than permanently reusing historical wrongs
- unknown does not create confirmed field weakness
- cross-Node question pairs cannot be classified as formal STRONG by the repair classifier
- Safety unknown remains high-priority unresolved evidence without being mislabeled as a confirmed wrong

## D. Question Bank repair supply — IMPROVED; EDUCATIONAL CAUTION REMAINS

Q1595-Q1605 added strong different-Q supply to 11 existing Safety Nodes.

Current bank:

- Q1-Q1605
- validator PASS
- duplicate / missing / reference / schema inconsistencies: 0

All 11 pilot source/new pairs classify structurally as `different_question_strong`.

The manual content-quality audit is COMPLETE and found no clearly incorrect keyed answer. It also found meaningful variation in discriminative quality:

- strongest current exemplar: Q1601
- highest-priority caution/review items: Q1600, Q1603, Q1599, Q1602, Q1604

Therefore structural STRONG status may be used by the formal engine, but a rise in `repairing -> repaired` produced by these pilot items must not by itself be treated as proof that the repair model is educationally calibrated. Historical learner evidence must be preserved before any future deployed-Q rewrite/retirement/replacement decision.

See `docs/strong-repair-pilot-content-audit-v01.md`.

## E. Phase 11 static/formal behavior — COMPLETE

J1→J7 remains:

1. `safety_repair`
2. `confident_wrong_cluster`
3. `repeated_wrong_cluster`
4. `recheck_due`
5. `insufficient_coverage`
6. `uncertain_correct_cluster`
7. `maintenance_only`

Confirmed by tests and integration QA:

- one ordinary wrong does not automatically commandeer a field
- unknown does not become confirmed weakness
- sparse coverage uses evaluable-answer evidence
- recheck_due remains above coverage/uncertainty/maintenance
- Shadow does not select exact Q IDs
- Baseline recommendation remains authoritative learner-facing behavior

## F. Symmetric Baseline-vs-Shadow comparison — COMPLETE AS DIAGNOSTIC

Both target fields receive the same formal evidence profile.

Different-target labels include:

- `different_target_shadow_has_stronger_evidence`
- `different_target_current_has_stronger_evidence`
- `insufficient_evidence_to_judge`

A stronger formal rank at one snapshot is diagnostic evidence, not causal proof of better learning outcome.

Supporter profile accuracy remains internally a 0–1 ratio for logic compatibility and now exposes a presentation-only percentage so QA displays `80.0%` rather than `0.8`.

## G. Repeat Structure Diagnostics — IMPLEMENTED AND CLASSIFIER FIXED

The earlier false-positive problem is fixed.

The classifier now separates:

- justified recent cooldown bypass
- legitimate spaced adaptive repeat
- true recent repeat without bypass
- inconsistent saved metadata
- non-adaptive repeat
- unavailable audit metadata

The red-flag invariant remains:

- saved `recent_question_repeat=True`
- saved `recent_cooldown_bypassed=False`

A legitimate non-recent checking/recheck repeat is not treated as a regression merely because the same Q appeared again.

### Remaining evidence requirement

Production history must still be re-read with the corrected classifier before repeat behavior can be marked promotion-green. The current Neon connector is blocked before SQL execution by a connector argument-schema mismatch, so this read remains pending without any Production DB write.

## H. Retrospective historical replay — IMPLEMENTED

Historical replay is now implemented as read-only diagnostics.

For each persisted learner-facing daily `recommendation_plan` anchor, the replay:

1. reconstructs Baseline phase from historical `learning_events.answered_count`
2. verifies question-level history coverage before accepting the snapshot
3. truncates attempts to the anchor time
4. rebuilds field evidence with the historical `as_of`
5. applies the current Phase 11 policy to that historical evidence
6. compares persisted Baseline target and replayed Shadow target symmetrically

Fail-closed behavior is used for incomplete/ambiguous history coverage.

This is current-policy retrospective replay, not historical-code time travel and not causal evidence.

### Remaining evidence requirement

Production replay results still need to be read and reviewed. Implementation alone does not satisfy the promotion gate.

## I. Known natural disagreement — OBSERVED, INSUFFICIENT ALONE

A previously observed natural snapshot showed:

- Baseline: 小児学 10問
- Shadow: 内科学 10問
- Shadow reason: `confident_wrong_cluster`
- confidence: high

The internal-medicine side had real confident-wrong repair evidence. This remains useful natural evidence, but one favorable disagreement is not sufficient for promotion.

## J. Remaining learner-facing promotion checks — OPEN

These are now the real remaining gates.

### J1. Critical Safety misses

Target: no pattern where stronger unresolved Critical Safety evidence exists while Phase 11 selects a weaker field.

### J2. Single-wrong overreaction

Target: no repeated pattern of one ordinary wrong causing unnecessary field takeover.

### J3. Sparse learner coverage

Target: when confirmed weakness evidence is insufficient, coverage behavior remains conservative and useful.

### J4. Recheck due handling

Target: naturally occurring `recheck_due` work is not starved by J5-J7.

### J5. Phase 11 intent vs Phase 10 exact-Q behavior

Target: repair/recheck/coverage intent is directionally compatible with Phase 10 exact selection while preserving cooldown and Safety rules.

### J6. Baseline disagreement quality

Review both directions:

- Shadow stronger
- Current/Baseline stronger
- same-target agreement
- insufficient-evidence cases

Do not select only Shadow wins.

### J7. Recommendation relevance

Prospective natural examples should show Shadow is at least no less relevant/safe than Baseline before a learner-facing pilot begins.

### J8. Repeat behavior after corrected classifier

Re-read Production history and confirm there is no true recent repeat-without-bypass pattern or that every such instance is individually explained.

### J9. Retrospective replay consistency

Review all eligible Production replay snapshots, including Current wins/losses and excluded snapshots with their fail-closed reasons.

### J10. Repair-transition evidence quality

If Q1595-Q1605 produce formal `repairing -> repaired` transitions, verify mechanics separately from item discrimination. A structurally STRONG but trivial item is not full educational validation.

## K. Promotion decision rule

Do not promote from one screenshot, one favorable disagreement, or one burst of pilot repair transitions.

A limited feature-flagged learner-facing pilot may be considered only when:

- architecture/formal safety gates remain green
- corrected repeat audit is green on Production history
- no Critical Safety miss pattern is found
- no systematic single-wrong overreaction is found
- sparse coverage remains appropriate
- recheck_due behavior has been observed when naturally available
- Phase 11 intent and Phase 10 exact-Q behavior are compatible
- symmetric disagreement review includes both Shadow and Current wins
- eligible retrospective replay reveals no policy-consistency regression
- pilot repair transitions are interpreted with the content-quality caution above
- prospective natural evidence is clearly no worse than Baseline

If evidence is mixed or insufficient, remain Shadow-only. Do not compensate by changing ranking weights prematurely.

## L. Current next order

1. Re-read Production Repeat Structure Audit with the corrected classifier when DB read access is available.
2. Read Production retrospective replay output and symmetric current profiles.
3. Review eligible historical disagreement winners/losses.
4. Observe prospective natural Safety / sparse-coverage / recheck_due / intent-vs-selection cases.
5. Decide whether evidence supports a **limited feature-flagged learner-facing pilot**, not full replacement.

Open GitHub implementation Issues for the previously identified diagnostics/formal-policy defects are currently cleared. Remaining blockers are evidence-gathering gates, not known unimplemented Phase 11 ranking defects.
