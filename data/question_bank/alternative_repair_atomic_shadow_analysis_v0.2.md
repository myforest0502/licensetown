# ⑩-E Atomic Rubric AI Shadow Analysis v0.2

## Result

- API calls: 140
- API errors: 0
- AI PASS evaluations: 27
- Final PASS evaluations: 24
- AI PASS -> gate block: 7
- Final false-PASS cases: 7 (13 evaluations)
- False-FAIL candidate cases: 5
- Memorized-answer PASS: 0
- Critical-error-answer PASS: 0
- Unrelated-answer PASS: 0
- Adversarial incomplete-answer PASS: 3 cases (6 evaluations)
- KN0899 recurrence: 2 cases
- Verdict instability: 2 cases
- Clear-correct PASS reproducibility: 55%
- Missing-element blocks: 116
- Critical-error blocks: 40
- Target-mismatch blocks: 0
- Parse/error blocks: 20 (empty answers handled locally)
- Formal state changes: 0

## False-PASS cases

1. `KN0017` / `missing_required_element` / PASS, PASS
2. `KN0017` / `adversarial_label_only` / PASS, PASS
3. `KN0611` / `missing_required_element` / PASS, PASS
4. `KN0611` / `adversarial_label_only` / PASS, PASS
5. `KN0652` / `missing_required_element` / FAIL, PASS
6. `KN0899` / `missing_required_element` / PASS, PASS
7. `KN0899` / `adversarial_label_only` / PASS, PASS

For every final PASS above, the model reported all required element IDs as
matched, no required ID as missing, and no critical error.  The outer gate
therefore had no independent basis on which to block PASS.

The v0.2 result schema stored aggregate matched/missing block counts but did not
retain per-evaluation short reasons.  The exact AI short reason from this run is
therefore unavailable.  The runner has now been changed to retain future
structured evaluation details; no additional API calls were made.

## Root cause

The atomic elements were derived from the full Knowledge Node label.  Several
labels are themselves complete explanatory statements.  The label-only fixture
then supplied that same full statement, so it was not truly a term-only or
incomplete response.  In addition, the deterministic gate recomputed set
completeness from model-reported matched IDs, but did not independently verify
whether each semantic criterion was present in the answer.

Thus an AI that over-matches every ID can still pass the gate.  The gate is
structurally strict but not semantically independent.

## KN0899

Required elements were:

- R1: Drop arm test checks whether the arm can be lowered slowly from shoulder abduction.
- R2: The tested structure is the rotator cuff.
- R3: It is positive particularly with a supraspinatus tear.

The incomplete fixture used the full Node label containing all three facts,
rather than only the term `drop arm test`.  Both incomplete and adversarial
cases therefore passed twice.  This reproduces the safety failure rather than
fixing it.

## Decision

Do not connect written confirmation to formal repair evidence.  Before another
shadow run, fixture answers must be authored independently of the full Node
label, and matched atomic elements need deterministic or separately reviewed
evidence instead of relying only on the evaluator's ID claims.
