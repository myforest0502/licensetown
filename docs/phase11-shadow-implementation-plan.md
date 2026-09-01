# Phase 11 Shadow Implementation Plan

Date: 2026-09-02
Status: diagnostics implementation complete / symmetric comparison complete / learner-facing promotion pending natural-use evidence

## Implemented integration target

Phase 11 v0.1 is integrated into the existing read-only supporter pilot diagnostics page:

`/supporter/pilot-diagnostics`

This remains the correct primary evaluation surface because it:

- reads formal attempt history
- shows the current recommendation and Shadow judgment side by side
- exposes evidence for developer review
- does not replace learner study flow
- adds no learning write path

## Implemented module

`judgment_shadow.py`

Primary API:

```python
def build_shadow_judgment(attempts, field_evidence, current_guidance, *, as_of=None):
    ...
```

The module remains deterministic and read-only:

- no Flask dependency for judgment logic
- no DB write
- no LLM call
- no exact-Q selection
- no Node-state mutation

## Decision policy — COMPLETE

The deterministic order is implemented as J1→J7:

1. critical Safety repair
2. confident wrong cluster
3. repeated wrong cluster
4. recheck_due
5. insufficient coverage
6. uncertain-correct stabilization
7. maintenance

Unknown answers do not create confirmed weakness evidence.

## Evidence reuse — COMPLETE

Phase 11 reuses existing formal evidence rather than creating a parallel state system:

- question attempts
- field evidence
- repeated weakness evidence
- canonical Node state / retention evidence
- current production guidance as control
- question tags / canonical mapping for Safety and field membership

Consultation content is not consumed.

## Current-vs-shadow comparison — COMPLETE AND SYMMETRIC

The first comparison implementation was intentionally diagnostics-only. It has since been strengthened so the current target field and Shadow target field receive the same formal J1→J7 evidence profile.

Supported labels:

- same_target_same_reason
- same_target_stronger_reason
- different_target_shadow_has_stronger_evidence
- different_target_current_has_stronger_evidence
- insufficient_evidence_to_judge

Important interpretation:

- the current target can have stronger formal evidence
- the Shadow target can have stronger formal evidence
- equal ranks remain inconclusive
- the current target profile describes evidence present in that field; it does not claim the baseline algorithm selected the field for that formal reason
- comparison is diagnostic evidence, not proof of future learning outcome

No weighted winner score is used.

## Diagnostics UI — COMPLETE

`/supporter/pilot-diagnostics` includes the development-only Phase 11 Shadow section.

It can display:

- current recommendation target
- Shadow intent / target / count
- reason code and learner-independent rationale confidence
- evidence values
- symmetric current-vs-Shadow formal evidence profiles
- comparison label
- Shadow reason/profile consistency

The diagnostic result does not write or mutate learner state.

## Additional diagnostics now supporting Phase 11 evaluation

The supporter diagnostic surface also includes:

- confident-wrong Node detail
- saved adaptive_daily 30-question audit
- repairing-Node repairability
- strong repair-supply priority
- repeat structure audit

These diagnostics were added to answer concrete natural-use questions before promotion rather than changing behavior prematurely.

## Question Bank repair-supply pilot

Natural diagnostics found that formal repair supply was a major constraint: a snapshot of 135 repairing Nodes had only one strong different-Q candidate, five weak-only Nodes, and 129 same-Q/formally blocked Nodes.

Q1595-Q1605 therefore added eleven targeted strong different-Q alternatives for Safety repairing Nodes. All eleven source/new pairs pass formal strong classification. This changes available evidence supply only; it does not itself mark any learner Node repaired.

## Phase 10 dependency — CLOSED

Phase 10 is now operationally closed:

- Recent Cooldown v0.2 is on main
- adaptive audit metadata persistence was confirmed in natural use
- observed recent overlap/bypass was fully explained by legitimate Safety singleton supply shortage
- no unexplained ordinary adaptive overlap remained in the audited session
- Question Bank validator is current through Q1605

Phase 11 promotion therefore no longer waits on Phase 10 closure. It waits on Phase 11 natural-use promotion evidence.

## Promotion policy — STILL GATED

Passing tests and shipping diagnostics to main are not enough to replace the learner-facing recommendation.

Promotion requires natural-use review showing, at minimum:

- no critical Safety miss
- no recurring overreaction to a single ordinary wrong
- appropriate sparse-learner coverage
- no starvation of naturally occurring recheck_due work
- compatibility between Phase 11 intent and Phase 10 exact selection
- symmetric review of disagreements, including current-guidance wins
- no unexplained adaptive repeat pattern
- enough natural examples to justify a limited learner-facing pilot

See:

`docs/phase11-promotion-evidence-matrix.md`

## Current next step

Do not redesign J1→J7 simply because one Shadow/current disagreement is observed.

Continue collecting natural-use diagnostics. When enough disagreement and agreement examples exist, use the promotion evidence matrix to decide whether a limited feature-flagged learner-facing pilot is justified.
