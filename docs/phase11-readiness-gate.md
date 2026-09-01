# Phase 11 Diagnostics-Only Readiness Gate

Date: 2026-09-02
Status: diagnostics-only readiness satisfied; promotion remains gated by Phase 11 natural-use evidence.

Phase 11 shadow code is allowed because all architecture safeguards are satisfied:

- Recent Cooldown v0.2 is on main
- adaptive selection audit is on main
- Phase 10 natural-use closure is complete
- Phase 11 remains read-only/deterministic
- learner-facing recommendation remains unchanged
- no Production DB write is introduced
- no Node-state mutation is introduced
- exact Q selection remains owned by Phase 10
- consultation content is not consumed
- current and Shadow target comparison is symmetric and diagnostics-only

The formal Question Bank is currently Q1-Q1605 and passes validation with duplicate, missing-ID, schema, and reference inconsistencies all at zero.

Current canonical summary:

- canonical Nodes: 1509
- singleton canonical Nodes: 1422
- multi-question canonical Nodes: 87

The Safety strong-repair pilot Q1595-Q1605 added strong different-Q supply to 11 existing canonical Nodes without changing the canonical Node total.

## Promotion gate

Promotion beyond diagnostics is not automatic merely because Shadow evidence is stronger in a single snapshot.

Natural-use review must confirm:

- no critical Safety misses
- no repeated overreaction to a single ordinary wrong
- appropriate sparse-learner coverage
- no starvation of recheck_due work once such Nodes exist
- consistency between Phase 11 intent and Phase 10 exact-Q audit
- disagreement quality versus the current recommendation, using the same formal J1→J7 evidence hierarchy for both targets
- fewer obviously irrelevant recommendations than the baseline across natural examples, not just selected wins

Agreements and disagreements should both be sampled to avoid confirmation bias.

The comparison label is diagnostic evidence, not proof that one target will produce a better future learning outcome. Learner-facing replacement remains blocked until the natural-use evidence is sufficient for an explicit promotion decision.
