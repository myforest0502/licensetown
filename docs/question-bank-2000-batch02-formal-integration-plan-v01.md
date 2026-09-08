# Question Bank 2000 Batch02 formal integration plan v01

## Scope

This plan prepares formal integration of the already reviewed Batch02 staging set. It does not itself modify the formal bank.

## Allocation

- Baseline: Q1-Q1749 / 1749 questions
- Batch02 allocation: Q1750-Q1761
- Target bank version: `2026-09-b14`
- All 12 new records are source `original` / formal source code `O`

## Atomic formal changes

Formal integration must change these together:

1. `questions.json`
2. `answers.json`
3. `explanations.json`
4. `question_tags.json`
5. `knowledge_nodes.json`
6. `bank_manifest.json`
7. `schema/question_bank_schema_v1.json`

No DB, Render setting, LINE runtime, selector, Phase11, canonical map, or relation data is changed.

## Node transition

Each accepted Batch02 target is currently a canonical singleton. At integration, append exactly its allocated Q ID after the existing reference Q and set registry status from `singleton_initial` to `confirmed_shared`.

Expected pairs:

- KN0117: Q117 + Q1750
- KN0575: Q583 + Q1751
- KN0639: Q647 + Q1752
- KN0241: Q242 + Q1753
- KN0287: Q289 + Q1754
- KN0408: Q415 + Q1755
- KN0364: Q369 + Q1756
- KN0423: Q431 + Q1757
- KN0378: Q383 + Q1758
- KN0369: Q374 + Q1759
- KN0327: Q329 + Q1760
- KN1533: Q1559 + Q1761

## Strong different-question behavior

No new row is required in `strong_different_question_pairs.json` for this batch. The current formal classifier treats two different questions in the same canonical Node as strong when their `(task, primary_ability)` demand differs. All 12 staging candidates were reviewed and sealed with a different metadata demand from their reference.

After formal integration, permanent tests must verify the 12 reference/new pairs classify as `different_question_strong` using the runtime classifier.

## Manifest/schema contract

Manifest becomes:

- `bank_version = 2026-09-b14`
- `question_count = 1761`
- `last_question_number = 1761`

Schema must require exactly 1761 records in each of the four stores and reject Q1762 and higher. The integrator owns this update so manifest and schema cannot advance independently.

## Guardrails

The integrator must fail closed on:

- baseline other than 1749 before first integration;
- any partial Q1750-Q1761 allocation;
- staging content seal mismatch;
- target no longer singleton;
- Node/reference mismatch;
- category mismatch;
- same `(task, primary_ability)` demand as reference;
- non-single-best answer;
- non-contiguous four-store IDs;
- manifest/schema mismatch.

It must be idempotent after a complete integration.

## Validation sequence

Before formal write:

1. Batch02 staging validator
2. temp-bank dry-run integrator test
3. full CI

After generated formal diff:

1. lifecycle-aware Batch02 validator: integrated 12/12
2. exact staging-to-formal content match for all 12
3. Node transitions exact
4. runtime strong classification 12/12
5. Question Bank validator
6. schema/manifest checker
7. Batch01 regression
8. Batch02 staging/integration tests
9. full pytest
10. `git diff --check`

Formal generation and the final generated JSON diff must be reviewed before merge.
