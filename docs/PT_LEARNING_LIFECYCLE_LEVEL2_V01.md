# PT Learning Lifecycle / Level 2 v0.1 — pure model

2026-09-20. Baseline main: 289f09edd1392252b60c7b68211431f83396b91a.
Status: provisional diagnostic model, not runtime authority or exam readiness certification.

## Motivation and evidence boundary

Boss supplied anonymous Production natural-use aggregates for 2026-09-20:
250 attempts, 156 correct (62.4%), 250 unique questions, 247 unique Nodes;
72-hour same-question repeats: zero. Q2001-Q2233 supplied 233 distinct questions
and Nodes, 144 correct; 232 Nodes were previously touched and 76 had prior wrong
answers. Selection included 76 repair and 174 checking questions. Strong
different-question candidate evidence occurred 78 times, with 41 correct;
confidence is not provided, so these are not 41 proven repair confirmations.
Stage E recorded 180 soft-pilot answers and 60 eligible-supply fallback answers.
These supplied observations motivate depth/repair rather than infinite Bank growth.
No Production DB was accessed to remeasure them in this task. No production
acceptance or learning benefit of this new helper is claimed.

## API and existing components

`licensetown.pt.learning_lifecycle.build_learning_lifecycle(
evidence_bundle, target_bundle, node_states,
critical_safety_unresolved_count=None)` takes:

- `build_field_evidence` output, containing all 18 PT fields;
- `build_field_targets` output (Stage D), from the same evidence/progress snapshot;
- complete `derive_all_user_node_states` output for the same learner and as_of;
- an explicitly observed, unresolved Critical Safety count; None means unavailable.

Callers own single-learner, prefix-only history, common observation time and
canonical/equivalence consistency. This helper does not replay history, read the
clock, load the Bank, import DB adapters, call a selector or mutate inputs.
It rejects missing/duplicate fields, invalid counts, supply mismatch, duplicate
formal Node IDs and overlapping catalog/formal state mismatches. It does not
reconstruct the entire upstream snapshot validator. Node counts use the unique
formal records, not sums of multi-field memberships. Formal evidence Nodes may
also exist outside the field catalog; they are not silently discarded.

## Coverage checkpoint (Level 1)

For every supplied field, require all three:

```
evaluable_answer_count >= minimum_initial_questions
answered_unique_question_count >= minimum_initial_questions
attempted_canonical_node_count >= minimum_node_spread
```

Thresholds come from Stage D, including min(60, field supply) and its existing
Node spread. All 18 rows must be supplied; a zero-supply field does not block the
checkpoint, but an entirely empty Bank never reaches it. Stage B's
`evidence_sufficient` is not required: small fields can finish their first pass
while remaining assessing. Raw distinct-Q counts are exposure, not independent
mastery evidence. Unknown attempts do not inflate evaluable-answer counts.

This means a broad initial checkpoint, not all Nodes mastered, all questions
consumed, graduation from all coverage work or a passing score. Unseen work can
continue. No global Q count, Q range, bank version or accuracy threshold is used.

## Phase precedence (provisional policy)

1. Current repairing Node(s) or observed unresolved Critical Safety ->
   `depth_repair`, `repair_priority=True`, independently of coverage completion.
2. With no such repair demand, formal `recheck_due` -> `retention_readiness`,
   even before the initial coverage checkpoint.
3. Otherwise, after the checkpoint, with no checking Nodes and at least one
   repaired/stable day3/day7/day30 checkpoint or stable/durable record ->
   `retention_readiness`.
4. Otherwise, reached checkpoint -> `depth_repair` for further depth confirmation
   (this does not imply `repair_priority=True`).
5. Otherwise -> `coverage`.

Scheduled future retention or durable evidence alone does not displace incomplete
coverage. Retention details remain visible when repair takes precedence.
The strict no-checking rule in step 3 is a conservative v0.1 definition of
retention predominance, not an already validated educational threshold.
Missing Safety is returned as None plus `missing_evidence` and a reason code;
absence of observed repair is not proof of safety. All outputs are provisional,
with `selection_authority=False`, including when the input is complete.

## Formal state reuse (Levels 2 and 3)

Current state, not cumulative wrong history, determines unresolved repair.
Old wrong evidence cannot reopen a repaired/stable Node here. A new formal
repairing state does reopen repair priority. Same-Q/weak different-Q corrections,
STRONG different-Q + correct + confidence=1, and wrong/unknown regressions remain
entirely owned by the existing state transition engine.

Retention uses existing `recheck_due`, `retention_checkpoint` day3/day7/day30,
and `retention_stage=durable`; no new state machine or dates are calculated.
`stable` is not synonymous with durable. Existing day30 scheduling remains as
implemented (30 days after the successful day7-horizon check).

## Supply, reassessment and runtime boundary

`eligible_supply_insufficient` is not a phase input. Temporary cooldown, formal
eligibility, equivalence and field supply can cause it; it proves neither Bank
saturation nor coverage completion. It is ignored if present as extra metadata.
The optional 60-question reassessment is not implemented and is not an entry
gate. Stage B's per-field 60-answer floor is a different contract. Natural
history can establish repair demand without a special examination.

Runtime integration is NOT done. No app/LINE/UI/Stage E/Phase11 call site imports
this helper. Existing selector ranking, Safety, 72-hour/recent cooldown,
equivalence and fallback behavior are unchanged. Level 2 grants no new repeat
permission. No Bank/DB/schema/env/Render changes, promotion or activation.

## Validation and Phase 2

Ten dedicated tests cover lifecycle boundaries using existing formal state
snapshots; existing state machine semantics are not reimplemented. Focused
regressions and the Q2233 validator are recorded in CURRENT_STATE and the PR.

Phase 2 should first compare aligned natural snapshots and review reason codes,
missing Safety context, multi-field/equivalence identity and the conservative
retention predominance rule. Only a separate decision may connect this signal
to presentation or strategy; the exact-Q selector keeps its existing guards.
Rollback: revert this PR (no migration or persisted state to undo).
