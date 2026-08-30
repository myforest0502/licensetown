# ⑩-D AI Reliability Shadow Analysis v0.1

## Execution

- Model: `gpt-4.1-mini`
- Temperature: `0`
- Nodes: 10
- Cases: 70
- Repeats: 2
- Actual API calls: 120
- Production user data: none

## Result

- False-PASS cases: 1 (2 PASS evaluations)
- False-FAIL candidate cases: 0
- Memorized-answer PASS: 0
- Critical-error-answer PASS: 0
- Unrelated-answer PASS: 0
- PARTIAL-equivalent-answer PASS: 1 case (2 evaluations)
- Verdict instability: 0
- Clear-correct PASS reproducibility: 100%
- Non-empty UNKNOWN: 0
- Observable fail-closed activations: 20 (empty answers, local UNKNOWN)
- Formal state changes: 0

## Blocking false PASS

- Canonical Node: `KN0899`
- Reference type: existing strong-alt Node
- Case: `missing_required_element`
- Expected: `PARTIAL`
- Results: `PASS`, `PASS`
- Answer form: the Knowledge Node label only; the causal/explanatory element required by the rubric was absent.

The failure was stable rather than random: both evaluations returned PASS.  The
current rubric supplies a long reference explanation as one required element,
but it does not decompose that explanation into atomic mandatory concepts.  The
evaluator therefore accepted topic recognition as if it demonstrated the full
understanding requirement.

## Strong-alt references

- `KN0268`: clear answer PASS; incomplete answer FAIL; all unsafe answers FAIL.
- `KN0652`: clear answer PASS; incomplete answer PARTIAL; all unsafe answers FAIL.
- `KN0899`: clear answer PASS; incomplete answer incorrectly PASS; all other unsafe answers FAIL.

Written confirmation is therefore not equivalent to formal strong-alt evidence.

## Decision

Formal repair-evidence integration is blocked.  Before retesting, `KN0899` and
the other rubrics must express small, atomic required elements and require every
mandatory element for PASS.  Relation review also remains human-pending.
