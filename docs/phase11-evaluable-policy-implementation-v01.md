# Phase11 Evaluable Policy Implementation v0.1

Date: 2026-09-02
Status: implementation specification; depends on draft PR #9 and stacked draft PR #17.

## Dependency chain

1. PR #9 — field repeated weakness excludes unknown
2. PR #17 — field evidence exposes shared evaluable metrics
3. Then implement Issues #11/#12/#13 in `judgment_shadow.py`

Do not duplicate the unknown definition inside J2/J5/J6.

## Shared field evidence contract

After PR #17, each field provides both raw/exposure and evaluable values:

Raw / compatibility:

- `question_answer_count`
- `question_correct_count`
- `question_accuracy`
- `unknown_answer_count`

Evaluable / policy:

- `evaluable_answer_count`
- `evaluable_correct_count`
- `evaluable_accuracy`

Phase11 uses evaluable values only where the policy asks whether actual answers provide enough evidence.

## File to change

`judgment_shadow.py`

Do not change:

- J1-J7 priority order
- Critical Safety confirmed-wrong definition
- repeated weakness derivation source
- global `<100` foundation/exposure boundary
- selector or exact Q selection
- Node-state transition
- learner-facing Baseline algorithm
- database persistence

## 1. Symmetric evidence profiles

Function:

`build_field_judgment_evidence_profiles()`

Current profile computes:

- `answered = question_answer_count`
- J5 from `answered < 10`
- J6 from `uncertain_correct >= 3 and answered >= 5`
- exposes `answered_count` and raw `accuracy`

Required change:

Read:

```python
answered = int(field.get("question_answer_count") or 0)
evaluable_answered = int(field.get("evaluable_answer_count") or 0)
evaluable_accuracy = field.get("evaluable_accuracy")
```

Reason assignment must match the real current-policy engine:

```python
elif total_answers < 100 or evaluable_answered < 10:
    reason = "insufficient_coverage"
elif uncertain_correct >= 3 and evaluable_answered >= 5:
    reason = "uncertain_correct_cluster"
```

Because J5 is ranked before J6, after global >=100 any field with evaluable<10 is J5 and cannot simultaneously surface as J6. Keep this ordering.

Expose both:

- `answered_count` = raw exposure
- `accuracy` = existing raw compatibility ratio
- `evaluable_answer_count`
- `evaluable_accuracy`

Do not replace/rename raw fields in the same change.

## 2. J2 confident-wrong tie-break

Inside `build_shadow_judgment()`, `facts[field_id]` currently stores raw:

- answered
- accuracy

Add:

```python
"evaluable_answered": int(field.get("evaluable_answer_count") or 0),
"evaluable_accuracy": field.get("evaluable_accuracy"),
```

Approved final tie-break:

```python
reliable_accuracy = (
    fact["evaluable_accuracy"]
    if fact["evaluable_answered"] >= 10
    and fact["evaluable_accuracy"] is not None
    else 1.0
)
```

Keep the preceding J2 tuple dimensions unchanged:

1. cross-question confident-wrong Node count
2. distinct confident-wrong repairing Node count
3. repairing Node count
4. evaluable accuracy
5. field ID

Evidence output should add enough diagnostic context to prove which denominator was used, for example:

- `evaluable_answers=...`
- `evaluable_accuracy=...` when available

Do not make accuracy itself a stronger reason than formal wrong evidence.

## 3. J5 insufficient coverage

### Global foundation stage

Keep:

```python
total_answers = len(attempts)
if total_answers < 100:
    ... existing foundation target behavior ...
```

This remains a coarse exposure/product-stage boundary.

### After global >=100

Replace raw sparse trigger:

```python
question_answer_count < 10
```

with:

```python
evaluable_answer_count < 10
```

Approved deterministic sparse ordering:

```python
key=lambda field: (
    int(field.get("evaluable_answer_count") or 0),
    float((field.get("node_coverage") or {}).get("percent") or 0),
    int(field.get("question_answer_count") or 0),
    int(field["field_id"]),
)
```

Rationale:

1. least actual answer evidence first
2. then least Node coverage
3. then least raw exposure
4. deterministic field ID

Evidence output should distinguish:

- `field_evaluable_answer_count`
- `field_raw_answer_count`
- `field_node_coverage_percent`
- `minimum_reliable_field_evaluable_answers=10`

Do not continue emitting only `field_answered_count` because that would hide the policy change.

## 4. J6 uncertain-correct stabilization

Keep numerator source unchanged:

- correct is True
- answer_status != unknown
- confidence 2 or 3

Replace raw denominator:

```python
answered = question_answer_count
```

with:

```python
evaluable_answered = evaluable_answer_count
```

Eligibility:

```python
if evaluable_answered < 5 or count < 3:
    continue
```

Rank proportion:

```python
count / evaluable_answered
```

Evidence output:

- `uncertain_correct_count`
- `evaluable_answer_count`
- `uncertain_correct_proportion`
- `checking_nodes`

Unknown must neither satisfy the minimum sample nor dilute the proportion.

## 5. Symmetric comparison invariant

After the change:

`build_field_judgment_evidence_profiles()` and `build_shadow_judgment()` must agree on the strongest J1→J7 reason for the Shadow target under the same snapshot.

Existing output:

`shadow_reason_profile_consistent`

must remain true in tests for J2/J5/J6 examples using unknowns.

This is critical for retrospective replay: a current-policy historical result cannot use one denominator in the decision engine and another in the symmetric comparison profile.

## Required tests

Add focused tests covering at least:

### J2

- two equal J2 fields with identical evaluable histories but extra unknowns in one field: unknown does not change target
- evaluable accuracy breaks a true tie only when each field has >=10 evaluable answers
- raw attempts >=10 but evaluable<10 uses neutral J2 accuracy fallback

### J5

- global >=100 + field 10 unknown/0 evaluable => J5 coverage
- global >=100 + field 9 evaluable + extra unknown => J5 coverage
- field 10 evaluable can leave J5 if no stronger rule applies
- under global <100 current foundation target behavior remains unchanged

### J6

- 3 uncertain correct + 2 unknown => not J6-eligible on sample size alone
- 3 uncertain correct + 2 other evaluable answers => eligible if no J1-J5 rule matches
- adding unknown does not change uncertain-correct proportion

### Symmetric profiles

- profile exposes raw and evaluable counts
- profile uses evaluable J5/J6 thresholds
- `shadow_reason_profile_consistent` remains true

### Regression

- unknown alone still does not create J1/J2/J3 confirmed weakness
- J4 retention behavior unchanged
- J7 unchanged when no higher rule matches
- current learner-facing Baseline is untouched
- no selector call / no DB write

## Retrospective replay dependency

Issue #3 must consume this corrected current-policy implementation. Do not freeze the old raw-denominator J2/J5/J6 behavior into retrospective replay.

Historical Baseline context may still show raw statistics because that is how the existing Baseline aggregates operate. Shadow current-policy context must also show evaluable statistics so disagreement interpretation is transparent.
