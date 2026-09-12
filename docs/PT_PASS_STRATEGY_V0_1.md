# PT Pass Strategy v0.1

Updated: 2026-09-12 JST

## 1. Purpose

LicenseTown's highest-order objective is not to maximize solved-question count or to eliminate every weakness. It is to maximize the learner's chance of passing the Physical Therapist National Examination within the finite time remaining before the exam.

All decisions below therefore optimize exam-wide pass readiness rather than a single field in isolation.

## 2. Existing formal truth path

Preserve the current formal path:

`question_attempts -> derived Knowledge Node state -> field / strategy / readiness -> selector -> presentation`

Phase11 remains HOLD / Shadow-only unless separately approved. Existing Safety priority, recent same-Q protection, Knowledge Node logic, and PR #342 low-coverage exploration floor must not be weakened by this specification.

## 3. One learner-facing action authority

### Rule

`今日やること` is the only learner-facing instruction about what to study next.

`学習の現在地` is descriptive only. It may explain the learner's current stage, coverage, repair status, retention status, or other evidence, but it must not issue another competing instruction such as `今日は生理学を10問` when `今日やること` says `病理学を10問`.

### Required invariant

At any point in the learner dashboard there must be at most one authoritative next-action field/count pair.

## 4. Assessment sufficiency before strong/normal/weak classification

A field must not be classified as `得意 / 普通 / 苦手` before sufficient evidence exists.

### Agreed first gate

- Minimum attempt evidence: **60 answered questions per field**.
- 60 questions equals two LicenseTown 30-question cycles.
- Attempt count alone is not sufficient. The attempts must also cover a sufficient breadth of Canonical Knowledge Nodes.
- Exact Node breadth threshold is **TBD by evidence review** and must not be guessed into production.

### State model

Before sufficient evidence:

- `未評価`
- `評価中`

After sufficient evidence:

- provisional `得意`
- provisional `普通`
- provisional `苦手`

The classification thresholds for accuracy / Node states / retention are intentionally TBD until the available Question Bank and historical-exam evidence are analyzed.

## 5. Initial assessment phase

Until every field has enough evidence for an initial assessment, `今日やること` should preferentially fill fields below the 60-question assessment floor.

When several fields are below 60:

1. Safety remains an allowed highest-priority override.
2. Among otherwise eligible under-assessed fields, future Exam Weight should help determine which field reaches 60 sooner.
3. Do not infer `得意` merely because a small sample happened to have high accuracy.
4. Do not infer `苦手` merely because a small sample happened to have low accuracy.

This is not a requirement to make total attempts equal across all 18 fields forever. It is a requirement to obtain enough initial evidence before aggressive personalization.

## 6. Weak-field re-evaluation cadence

Once a field is provisionally classified as weak:

- 60 attempts -> initial weak classification
- +30 -> re-evaluate at 90
- +30 -> re-evaluate at 120
- +30 -> re-evaluate at 150
- continue only when additional investment remains strategically justified

Every additional 30-question block is a decision checkpoint, not an automatic entitlement to another 30 questions.

## 7. Weakness state and study priority are separate

A field may remain objectively weak while not being the current highest-priority study target.

Therefore:

`field weakness state != current allocation priority`

Example: a low-exam-weight field can remain weak while a higher-exam-weight under-assessed or moderately weak field receives the next 30-question investment because that allocation is more likely to improve exam-wide passing performance.

## 8. Overcome / graduation model

`克服` must not be defined by cumulative accuracy alone.

A future production rule should use evidence such as:

- repair of previously weak Canonical Nodes,
- confirmation with a different question from the same Node rather than immediate same-Q recall,
- spaced recheck evidence,
- field-specific required target attainment,
- exam importance.

Useful states may include:

- `苦手`
- `改善中`
- `一旦克服` (priority may be reduced)
- `定着済み`

Exact numeric thresholds are TBD and must be derived rather than guessed.

## 9. Anti-overconcentration rule

LicenseTown must not spend unlimited questions on one persistently weak field while other fields remain unassessed or materially below their exam-relevant targets.

If repeated 30-question blocks produce insufficient improvement, the response is not automatically `another identical +30`.

Instead the strategy should consider:

- whether the same Nodes are being over-sampled,
- whether foundational Nodes are missing,
- whether question difficulty is mismatched,
- whether the repair method is ineffective,
- whether spaced confirmation is missing,
- whether another field now has higher expected pass-value per question.

The exact escalation / investment cap is TBD and may vary by Exam Weight.

## 10. Historical-exam analysis and Exam Weight

Before finalizing field-specific thresholds, analyze the available historical PT national-exam corpus by the same 18 LicenseTown fields.

Required measures where source metadata permits:

- question count by field and exam year,
- share of exam questions by field,
- point contribution by field,
- distinction between question types when scoring differs,
- year-to-year stability,
- latest 5-year trend,
- latest 10-year trend,
- available ~20-year trend.

### Data integrity rule

Do not manufacture year, round, score, or question-type metadata. If the current Question Bank provenance does not contain enough information for a requested historical measure, report the gap and locate the original exam source before assigning a production Exam Weight.

### Exam Weight

A field-level `Exam Weight` will represent examination importance. The exact formula is TBD after the source audit.

It must not be based only on intuition.

## 11. Raw attainment and required target attainment are different values

Keep the existing raw Knowledge-Node-derived attainment truthful and comparable.

Do not inflate raw attainment because a field is less important.

Instead introduce a separate field-specific required target.

Example:

- raw attainment: 70%
- field target attainment: 65%
- status: target met

For a high-weight field:

- raw attainment: 82%
- field target attainment: 90%
- status: target not yet met

Thus the learner can see both what has actually been learned and how much is considered sufficient for exam strategy.

## 12. Field-specific standards

The following may legitimately differ by field after Exam Weight is established:

- minimum evidence required before a confident classification,
- target attainment,
- required Node breadth,
- recheck strictness,
- maximum / preferred additional weak-field investment,
- maintenance frequency.

The common 60-question initial floor remains the agreed first assessment gate unless later evidence demonstrates a reason to revise it.

## 13. Priority model

Safety remains a highest-order override.

Below Safety, the future strategy should combine at least:

- Exam Weight,
- weakness severity,
- attainment deficit relative to that field's target,
- under-assessment / uncertainty,
- remaining time to the exam.

Conceptually:

`priority ~ Exam Weight x weakness x attainment deficit x under-assessment x time adjustment`

This is a conceptual model, not yet a production formula. Exact weights and nonlinear rules are TBD after evidence analysis.

## 14. Global optimization rule

The system must prefer exam-wide pass readiness over perfection in one subject.

A learner should not fail because LicenseTown spent excessive time perfecting one stubborn weakness while leaving other high-value exam areas unassessed or under-covered.

The key 30-question decision is:

> Where should the next 30 questions be invested to move this learner closest to passing?

not merely:

> Which field is currently weakest?

## 15. Compatibility with PR #342

The existing low-coverage exploration floor remains in place while this strategy is validated.

Do not prematurely alter the current 15 repair / 10 checking / 5 exploration composition solely because this document exists. Historical-exam and Production evidence must be reviewed first.

The new assessment-sufficiency and Exam Weight concepts should eventually explain and refine allocation without discarding working safety and repeat protections.

## 16. Acceptance / validation sequence

Before Production promotion:

1. Trace both learner-facing cards to their formal source and remove competing action language from current-state presentation.
2. Confirm that the one-action-authority invariant is covered by tests.
3. Audit available historical-exam provenance.
4. Produce field-level historical distributions only from verifiable source metadata.
5. Define Exam Weight with a reproducible calculation.
6. Define the 60-question + Node-breadth initial assessment rule.
7. Define +30 re-evaluation and anti-overconcentration rules.
8. Define field-specific target attainment and overcome states.
9. Add focused tests and run the relevant full regression / validator set.
10. Update CURRENT_STATE.
11. Promote only after existing production safeguards remain green.

## 17. Explicit non-goals for v0.1

- Do not make all 18 fields have equal attempt counts after initial assessment.
- Do not classify a field from a small sample just to make the UI look complete.
- Do not turn raw attainment into a pass probability.
- Do not let `学習の現在地` become a second recommendation engine.
- Do not activate another qualification such as Takken.
- Do not promote Phase11 from shadow/HOLD.
