# Phase 11 Ship Checklist

Date: 2026-09-02
Status: diagnostics-only ship COMPLETE / learner-facing promotion NOT YET APPROVED

## A. Diagnostics-only implementation gate — COMPLETE

All conditions are satisfied:

- judgment module is pure/read-only and deterministic
- J1→J7 decision order is covered by tests
- current-vs-Shadow comparison is explicit
- comparison is symmetric and can identify either current or Shadow as stronger
- diagnostics UI is development-only
- learner dashboard recommendation remains unchanged
- no write helper is used by the judgment module
- no formal Node-state mutation occurs
- no adaptive selector policy change occurs
- consultation content is absent from inputs
- related tests pass
- full pytest passes apart from the known unmanaged external fixture exclusion
- Question Bank validator passes through Q1605
- DB migration: none
- Production DB write: none

Phase 11 diagnostics-only implementation is therefore shipped on main.

## B. Phase 10 dependency — COMPLETE

Phase 10 no longer blocks Phase 11 evaluation.

Natural adaptive use confirmed:

- audit metadata persistence
- 30 unique questions in the audited 30-question session
- repeat/bypass metadata explainability
- eight observed bypasses were Safety same-question cases
- all eight affected Safety Nodes were verified to lack non-recent strong alternate supply at that time

The Question Bank is currently validated through Q1605.

## C. Learner-facing promotion gate — OPEN

Phase 11 must NOT yet replace the baseline learner-facing recommendation.

Promotion still needs natural-use evidence covering:

- critical Safety miss rate: no unresolved critical miss pattern
- ordinary single wrong: no repeated overreaction
- sparse coverage: conservative and useful behavior
- recheck_due: no starvation when naturally present
- Phase 11 intent vs Phase 10 exact selection: compatible behavior
- disagreement review: both Shadow wins and current-guidance wins considered
- repeat structure: no unexplained adaptive repeat pattern
- enough natural cases to avoid promotion based on one favorable screenshot

## D. Promotion decision

Possible outcomes after evidence review:

1. remain diagnostics-only
2. adjust Phase 11 rules and continue Shadow evaluation
3. start a limited feature-flagged learner-facing pilot

Do not jump directly from diagnostics to full replacement.

See:

- `docs/phase11-shadow-evaluation.md`
- `docs/phase11-promotion-evidence-matrix.md`
