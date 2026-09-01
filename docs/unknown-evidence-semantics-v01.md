# Unknown Evidence Semantics v0.1

Date: 2026-09-02
Status: formal policy for future implementation; current behavior is partially compliant.

## Purpose

LicenseTown stores a 0-answer / unanswered item as:

- `selected_answers=[]`
- `confidence=null`
- `answer_status='unknown'`
- `is_correct=false`

The storage representation must not cause every downstream layer to treat unknown as a confirmed wrong answer.

This document separates four meanings that were previously easy to conflate:

1. exposure/activity
2. unresolved repair trigger
3. confirmed weakness evidence
4. evaluable statistical evidence

## Core rule

**Unknown means: encountered but not evaluably answered.**

It is important learning information, but it is not confirmed wrong-answer evidence.

## 1. Exposure / activity

Unknown **does count** as exposure/activity.

It may count toward:

- raw total attempts
- raw field answer/exposure count
- same-day learning volume
- whether a question/Node has been encountered
- coarse global foundation/analysis phase milestones that intentionally use raw persisted answered_count

Do not erase the learner's effort merely because the answer was unknown.

## 2. Formal Node-state repair trigger

Unknown **does count** as unresolved evidence for formal Node state.

Preserve current behavior:

- unseen/checking + unknown -> repairing
- repaired/stable + unknown -> repairing
- unknown may establish a repair cycle
- a later strong different-Q correct with confidence=1 may confirm repair

Reason: a learner who cannot answer a concept has not demonstrated stability and should not remain repaired/stable merely because the response was not a conventional wrong choice.

Use wording such as **unresolved repair trigger**, not confirmed wrong evidence.

## 3. Confirmed weakness evidence

Unknown **does not count** as confirmed weakness.

It must not independently create:

- SINGLE_WRONG weakness
- repeated-same-question wrong weakness
- cross-question wrong weakness
- confident-wrong weakness
- Critical Safety wrong evidence in Phase11 J1
- confident-wrong cluster in J2
- repeated-wrong cluster in J3

Confirmed weakness derives from evaluable non-unknown attempts only.

## 4. Evaluable statistical evidence

For policy decisions that require a sample of actual answers, unknown is excluded from the denominator.

Formal shared fields should be added in the evidence layer:

- `evaluable_answer_count`
- `evaluable_correct_count`
- `evaluable_accuracy`

Definition:

- evaluable attempt = `answer_status != 'unknown'`
- evaluable correct = evaluable attempt with `is_correct is True`
- evaluable accuracy = evaluable_correct / evaluable_answer_count, or null when denominator is zero

Existing raw/general fields remain for compatibility:

- `question_answer_count`
- `question_correct_count`
- `question_accuracy`
- `unknown_answer_count`

Do not silently redefine general dashboard accuracy in the same change.

## Phase11 rule map

### J1 Safety repair

Unknown alone does **not** satisfy confirmed Critical Safety wrong evidence.

A Critical Safety Node may be formally unresolved/repairing from unknown, but J1 requires evaluable wrong evidence under current policy.

### J2 confident-wrong cluster

Unknown does not contribute to the cluster.

The final accuracy tie-break uses:

- minimum `evaluable_answer_count >= 10`
- `evaluable_accuracy`

not raw attempt count or raw accuracy.

### J3 repeated-wrong cluster

Unknown does not contribute to repeated weakness counts.

### J4 recheck_due

Driven by formal retention state/timing. No denominator change is introduced here.

### J5 insufficient coverage

Keep the global `<100` coarse foundation milestone on raw total attempts for compatibility.

After global >=100, per-field sufficiency uses:

- `evaluable_answer_count < 10` => insufficient coverage

Unknown counts as exposure but cannot by itself prove that a field has enough evaluable evidence.

### J6 uncertain-correct stabilization

Numerator already uses non-unknown confidence2/3 correct answers.

Use:

- `evaluable_answer_count >= 5`
- uncertain-correct proportion = uncertain_correct / evaluable_answer_count

Unknown must not satisfy the five-answer threshold or dilute the proportion.

### J7 maintenance

J7 is reached only after the corrected J1-J6 rules fail to match. A field consisting largely of unknown exposure should therefore not fall into maintenance merely because raw attempt thresholds were met.

## Phase10 selector rule map

Unknown remains repair work.

### Non-Safety unknown

Current intent remains:

- group: repair
- reason: repairing/unresolved

### Safety unknown

Preserve high Safety priority and existing singleton cooldown exception, but distinguish semantics:

- evaluable Safety wrong => `safety_wrong`
- unknown-only Safety unresolved => `safety_unresolved`

A Node with both confirmed wrong and unknown evidence uses `safety_wrong`.

The Safety recent same-Q exception may apply to either Safety reason only when no non-recent same-canonical-Node alternative exists.

Do not broaden the exception to ordinary unknowns.

## Repeat diagnostics

Repeat diagnostics audit saved selection metadata, not learner correctness semantics.

Correct classification remains based on:

- `recent_question_repeat`
- `recent_cooldown_bypassed`

The selector reason (`safety_wrong` vs future `safety_unresolved`) is explanatory metadata and must remain visible, but it does not override a true recent-without-bypass red flag.

## Node-state evidence fields

Current state transition output has legacy fields such as `evidence_level` / `wrong_question_count` that may be based on unknown-inclusive history.

Do not automatically treat those fields as confirmed weakness.

Preferred future split after consumer audit:

- repair-trigger/state fields remain compatible
- explicit confirmed weakness fields use evaluable history, e.g.
  - `confirmed_weakness_evidence_level`
  - `evaluable_wrong_question_count`
  - `unknown_attempt_count`

Phase11 should continue its explicit non-unknown weakness derivation until equivalence is proven.

## Historical compatibility

Do not rewrite old Production learning events or old audit metadata.

Historical events may contain `selection_reason='safety_wrong'` for cases that newer code would call `safety_unresolved`. Interpret saved metadata under the code/version that produced it.

Retrospective Phase11 replay applies the **current policy** to historical raw evidence at time T; it must derive evaluable values from the historical attempts rather than trusting old semantic labels.

## Implementation bundle

Related work:

- Issue #6 — field repeated weakness excludes unknown; draft PR #9
- Issue #11 — J2 evaluable-only accuracy
- Issue #12 — J5 evaluable coverage
- Issue #13 — J6 evaluable denominator
- Issue #14 — Safety unknown selector reason
- Issue #15 — Node repair-trigger vs confirmed weakness field split

Implement #11/#12/#13 from the shared evaluable fields introduced in the evidence layer. Do not create three separate definitions of evaluable attempt.

## Required invariant tests across the bundle

1. unknown is preserved in raw exposure counts.
2. unknown sends formal Node state to repairing.
3. unknown alone creates no confirmed weakness.
4. unknown alone does not trigger Phase11 J1/J2/J3.
5. unknown cannot satisfy per-field J5 evaluable sufficiency.
6. unknown cannot satisfy J6 minimum evaluable sample.
7. unknown cannot change J2 final accuracy tie-break between otherwise identical evaluable histories.
8. Safety unknown remains high-priority repair work but is not labeled confirmed wrong in new audit metadata.
9. old Production events are not mutated.
10. selector, Node-state and Phase11 responsibilities remain separate.
