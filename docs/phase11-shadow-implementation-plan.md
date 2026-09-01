# Phase 11 Shadow Implementation Plan

Date: 2026-09-01
Status: ready for implementation after Phase 10 deployment gate

## First integration target

Do **not** connect Phase 11 v0.1 to the learner dashboard first.

The safest first integration point is the existing read-only supporter pilot diagnostics page:

`/supporter/pilot-diagnostics`

Why:

- already explicitly marked as development diagnostics
- already reads formal attempt history
- already simulates the latest adaptive 30 questions
- already exposes Node state and weakness evidence
- does not change the learner's recommendation or study flow
- lets Phase 11 be compared with current guidance before product promotion

## Proposed new module

Create:

`judgment_shadow.py`

It should be pure/read-only and contain no Flask/UI code and no DB writes.

Suggested public function:

```python
def build_shadow_judgment(
    attempts,
    field_evidence,
    current_guidance,
    *,
    as_of=None,
):
    ...
```

Return one deterministic result dictionary.

No LLM call.

## Input construction

Inside `pilot_diagnostics.py`:

1. reuse `all_attempts = get_question_attempts(user_id)`
2. build `field_evidence = build_field_evidence(all_attempts, as_of=now)`
3. create the legacy field summary shape needed by `build_learning_guidance`
4. calculate `current_guidance` using the same existing production function
5. pass attempts/evidence/current guidance to `build_shadow_judgment`

### Legacy field adapter

The adapter can be local/pure and should map:

```python
{
    "category_small": field["field_id"],
    "name": field["field_name"],
    "answered_count": field["question_answer_count"],
    "correct_count": field["question_correct_count"],
    "accuracy": round(field["question_accuracy"] * 100) if field["question_accuracy"] is not None else None,
}
```

This prevents Phase 11 diagnostics from needing another database aggregation solely to reconstruct the current recommendation baseline.

## Shadow decision engine

Implement the deterministic order from `phase11-v01-decision-table.md`.

Initial reason codes:

- safety_repair
- confident_wrong_cluster
- repeated_wrong_cluster
- recheck_due
- insufficient_coverage
- uncertain_correct_cluster
- maintenance_only

The module must return evidence strings/numbers that explain the result without hidden reasoning.

## Safety signal construction

Critical Safety must not be inferred only from field accuracy.

For wrong attempts:

- canonicalize Node ID
- read question tag Safety
- identify unresolved formal state

J1 triggers only for `critical` Safety in v0.1 shadow.

Moderate Safety remains available to Phase 10 priority but does not automatically commandeer the Phase 11 daily field recommendation from a single ordinary wrong.

## Repeated weakness construction

Reuse `derive_repeated_weakness_evidence(attempts)`.

Map each evidence record to field membership through the question IDs / canonical Node catalog.

For v0.1:

- CROSS_QUESTION_CONFIDENT_WRONG is the strongest non-Safety repair signal
- CROSS_QUESTION_WRONG is next
- REPEATED_SAME_QUESTION_WRONG is supporting evidence, not enough alone to commandeer a field recommendation
- SINGLE_WRONG never triggers a field-level repair recommendation by itself

## Retention signal

Use field evidence `retention_nodes` and select only state=`recheck_due` for J4.

Tie-break using:

- due Node count
- max overdue days
- total overdue days
- field ID

## Coverage signal

When total answers < 100 and no higher rule applies, preserve the current production foundation recommendation exactly.

This is important: Phase 11 should demonstrate improvement by overriding only when stronger evidence exists, not by rewriting the early learner experience unnecessarily.

After 100 answers, use insufficient evidence/coverage conservatively.

## Uncertain-correct signal

Do not use aggregate confidence counts alone because they include wrong answers.

Compute per-field uncertain-correct evidence directly from attempts:

- is_correct=True
- confidence in {2, 3}
- answer_status != unknown

v0.1 minimum:

- at least 5 field answers
- at least 3 uncertain-correct answers

## Current vs shadow comparison

Return a comparison block:

```python
{
    "current": {
        "target_field": "人間発達学",
        "question_count": 10,
        "reason": "..."
    },
    "shadow": {...},
    "comparison_label": "same_target_same_reason|..."
}
```

Do not attempt automatic quality scoring yet.

## Pilot diagnostics UI

Add one development-only card to `supporter_pilot_diagnostics.html`:

Title:

`⑪ Shadow判断（開発中）`

Display:

- current recommendation
- shadow intent
- shadow target field
- question count
- reason code / Japanese label
- confidence
- evidence list
- comparison label

Prominent label:

`この判断は学習者画面には反映されていません。`

Do not add controls that mutate data.

## Required tests

### Pure judgment tests

At minimum:

1. new user -> coverage/current foundation target
2. sparse learner + no strong weakness -> coverage
3. one ordinary wrong -> does not override coverage
4. critical Safety wrong -> safety repair
5. cross-question confident wrong -> repair
6. cross-question wrong -> repair
7. lone repeated same-Q wrong -> does not commandeer field
8. recheck_due with no urgent repair -> recheck
9. uncertain-correct cluster -> stabilization
10. no higher evidence -> maintenance
11. deterministic ties -> stable field_id fallback
12. consultation content is not an input/API field

### Integration tests

13. pilot diagnostics includes shadow result
14. supporter diagnostics render includes development-only warning
15. learner dashboard recommendation remains unchanged
16. no write helper is imported/called from `judgment_shadow.py`
17. no Node state mutation
18. no Production DB write

### Regression

- existing pilot diagnostics tests
- adaptive selector tests
- field evidence/progress tests
- full pytest
- Question Bank validator

## Promotion policy

This first implementation stays diagnostics-only even if tests pass.

Real-use comparison should accumulate before any dashboard switch.

Promotion requires an explicit later change and a separate feature flag.
