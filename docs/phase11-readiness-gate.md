# Phase 11 Diagnostics-Only Readiness Gate

Date: 2026-09-02
Status: implementation/formal-policy readiness satisfied; learner-facing promotion remains evidence-gated.

Phase 11 shadow is allowed on main because the architecture safeguards are satisfied:

- Recent Cooldown v0.2 is on main
- adaptive selection audit is on main
- Phase 10 natural-use closure is complete
- Phase 11 remains deterministic and read-only
- learner-facing recommendation remains unchanged
- no Production DB write is introduced by judgment/replay diagnostics
- exact Q selection remains owned by Phase 10
- consultation content is not consumed
- current and Shadow target comparison is symmetric
- formal weakness uses current repair-cycle/evaluable evidence
- unknown remains unresolved evidence without becoming confirmed weakness
- recheck_due repair-cycle reset and retention-reference semantics are explicit
- retrospective Shadow replay is implemented fail-closed for incomplete history
- repeat diagnostics distinguish legitimate spaced repeats from true recent repeats without bypass

The formal Question Bank is Q1-Q1605 and passes validation with duplicate, missing-ID, schema, reference, Safety, and task-primary inconsistencies at zero.

## Promotion gate

Promotion beyond diagnostics is not automatic merely because Shadow evidence is stronger in one snapshot or because formal repaired counts rise.

Remaining work is evidence gathering, not a known missing Phase 11 ranking implementation.

Production/natural-use review must still confirm:

- no critical Safety miss pattern
- no repeated overreaction to one ordinary wrong
- appropriate sparse-learner coverage
- no starvation of naturally occurring recheck_due work
- consistency between Phase 11 intent and Phase 10 exact-Q behavior
- disagreement quality including both Shadow wins and Current/Baseline wins
- corrected repeat audit has no true unexplained recent-repeat regression
- eligible retrospective replay has no policy-consistency regression
- prospective recommendations are clearly no worse than Baseline

The Q1595-Q1605 repair-content audit is complete. Their formal STRONG status remains valid, but weaker distractor discrimination in several pilot items means pilot-driven `repairing -> repaired` growth is not by itself educational validation.

The current Neon connector cannot complete the pending Production re-read because its exposed argument schema and execution schema disagree before SQL execution. This is a tooling blocker only; no Production SQL/write occurred from the failed connector attempts.

Learner-facing replacement remains blocked until the remaining evidence is sufficient for an explicit promotion decision. The first allowed promotion step is a limited feature-flagged pilot, not full replacement.
