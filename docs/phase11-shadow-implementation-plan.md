# Phase 11 Shadow Implementation Plan

Date: 2026-09-01
Status: ready for diagnostics-only implementation; learner-facing promotion remains gated by Phase 10 natural-use observation.

## First integration target

Do not connect Phase 11 v0.1 to the learner dashboard first.

The safest initial integration point is the existing read-only supporter pilot diagnostics page:

`/supporter/pilot-diagnostics`

Reason:

- development diagnostics already exists
- it reads formal attempt history
- it can compare existing recommendation and a shadow result
- it does not change learner study flow
- it provides a place to inspect evidence before promotion

## Proposed module

Create `judgment_shadow.py` as a pure/read-only deterministic module.

Suggested function:

```python
def build_shadow_judgment(attempts, field_evidence, current_guidance, *, as_of=None):
    ...
```

No Flask/UI logic, no DB write, no LLM call.

## Decision policy

Use the deterministic order in `phase11-v01-decision-table.md`:

1. critical Safety repair
2. confident wrong cluster
3. repeated wrong cluster
4. recheck_due
5. insufficient coverage
6. uncertain-correct stabilization
7. maintenance

The output explains the recommendation using explicit reason codes and evidence values.

## Reuse existing evidence

Prefer current read-only helpers rather than new aggregation tables:

- get_question_attempts
- field evidence/progress helpers
- repeated weakness evidence
- formal Node state / retention evidence
- current production guidance as control
- question tags / canonical Node mapping for Safety and field membership

Do not consume consultation content.

## Current-vs-shadow comparison

Return a comparison block containing current and shadow targets/reasons plus one label:

- same_target_same_reason
- same_target_stronger_reason
- different_target_shadow_has_stronger_evidence
- different_target_current_has_stronger_evidence
- insufficient_evidence_to_judge

Do not auto-score which system is better yet.

## Diagnostics UI

If `/supporter/pilot-diagnostics` is used, add a clearly development-only card:

`⑪ Shadow判断（開発中）`

Display:

- current recommendation
- shadow intent
- target field
- question count
- reason code / Japanese label
- confidence in rationale
- evidence list
- comparison label

Prominent warning:

`この判断は学習者画面には反映されていません。`

No write/mutation controls.

## Minimum tests

Pure judgment:

1. sparse/new learner -> coverage
2. one ordinary wrong does not commandeer field recommendation
3. critical Safety wrong -> safety repair
4. cross-question confident wrong -> repair
5. cross-question wrong -> repair
6. lone repeated same-Q wrong does not commandeer field
7. recheck_due -> recheck when no urgent repair
8. uncertain-correct cluster -> stabilization
9. no higher evidence -> maintenance
10. ties deterministic
11. consultation content not accepted as judgment input

Integration/regression:

12. diagnostics can include shadow result
13. development-only warning renders
14. learner dashboard recommendation remains unchanged
15. judgment module imports/calls no write helper
16. no Node-state mutation
17. existing adaptive/field/pilot tests pass
18. full pytest
19. Question Bank validator

## Promotion policy

Passing tests is not enough to switch the learner dashboard.

Keep the first implementation diagnostics-only. Promotion requires a later explicit feature-flagged change after natural-use comparison shows it is safer/more relevant than the baseline.
