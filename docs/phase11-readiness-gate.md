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
- Supporter diagnostics can export the current Promotion evidence as `PHASE11_PROMOTION_EVIDENCE_V1` without manual transcription

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

## Production evidence review v0.1 — 2026-09-02

The first full Production `PHASE11_PROMOTION_EVIDENCE_V1` review is complete. Current decision: **HOLD / remain Shadow-only**.

Observed positive evidence:

- current Shadow target `動作分析学` is J2 `confident_wrong_cluster` with 2 active cross-question confident-wrong Nodes and 5 active confident-wrong repairing Nodes; the current disagreement is not a one-wrong takeover
- corrected Repeat Structure Audit shows 0 true unexplained recent repeats and 0 metadata inconsistencies among classifiable history
- 2/2 retrospective anchors are eligible with complete history coverage and profile consistency
- 0 Phase11 Critical Safety miss candidates across the 2 eligible snapshots
- 0 J2/J3 formal-trigger mismatches across the 2 eligible snapshots
- both retrospective disagreements favor Shadow on formal evidence
- formal `repairing -> repaired` transitions are now present in Production (4 observed)
- latest 30-question adaptive simulation remains 30 unique Q / 30 unique Nodes / 15 repair / 10 checking / 5 exploration

Remaining evidence gaps:

- `recheck_due=0` and `stable=0`, so J4 retention behavior is not naturally observable yet
- retrospective evidence is one-sided: 2 Shadow wins, 0 Current/Baseline wins, 0 same-target agreements
- broader prospective relevance still needs additional natural-use examples
- repair supply remains constrained: 3 STRONG-available repairing Nodes out of 131 (2.3%)

Historical `metadata_unavailable=251` is retained as unknown/unclassifiable legacy repeat metadata and is not treated as evidence of a current cooldown regression.

The latest saved adaptive session at capture time was one 5-question set (`event_count_incomplete`), which is an in-progress session rather than a malformed completed 30-question session.

See `docs/phase11-production-evidence-review-20260902-v01.md` for the full review.

## Production evidence capture

Direct Neon SQL read remains useful for deeper forensic inspection, but it is no longer the only path for capturing the Promotion evidence used by this gate. The Production Supporter page `/supporter/pilot-diagnostics` can export a deterministic `PHASE11_PROMOTION_EVIDENCE_V1` bundle from the same diagnostic values displayed on the page.

The bundle is a transport/review aid only. It does not change J1→J7 policy, promotion thresholds, Phase 10 selector behavior, Node-state semantics, or learner-facing recommendation.

When reviewing a copied bundle:

- preserve the scope split between selected-period metrics, all-history current formal state, all-history retrospective replay, and the latest saved adaptive session
- review every eligible replay snapshot and every fail-closed/excluded snapshot rather than selecting only Shadow wins
- treat the copied text as evidence only insofar as it was generated from the Production Supporter diagnostic page

The current Neon connector still cannot complete ad-hoc Production SQL reads because its exposed argument schema and execution schema disagree before SQL execution. This remains a tooling blocker for DB-level forensic queries only; no Production SQL/write occurred from the failed connector attempts.

Learner-facing replacement remains blocked until the remaining evidence is sufficient for an explicit promotion decision. The first allowed promotion step is a limited feature-flagged pilot, not full replacement.

See `docs/phase11-evidence-bundle-ops-v01.md` for the evidence-capture workflow.
