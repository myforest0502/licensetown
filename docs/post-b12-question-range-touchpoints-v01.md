# Post-B12 Question Range Touchpoints v0.1

Date: 2026-09-03

## Purpose

Record the currently verified places that encode the formal Question Bank upper bound/count so the planned Q1661-Q1737 expansion can be finished without leaving stale range assumptions behind.

This is a documentation-only inventory. It does not change runtime behavior, Production data, the selector, or the Question Bank.

## Verified hard-coded touchpoints on current main

### 1. Runtime loader — `question_bank.py`

Current main defines:

- `EXPECTED_QUESTION_COUNT = 1660`
- `EXPECTED_QUESTION_IDS = {Q1..Q1660}`
- startup fails closed unless the questions set exactly equals that range
- answers/explanations/tags must have exact ID parity with questions

Post-B12 requirement: the final implementation must still fail closed for the declared bank version/range. Do not replace the exact check with a permissive `Q\d+`-only check.

### 2. Formal validator — `scripts/validate_question_bank.py`

Current main independently defines:

- `EXPECTED_QUESTION_COUNT = 1660`
- `EXPECTED_IDS = {Q1..Q1660}`

The same set is used for:

- four-file record counts
- missing IDs
- unexpected IDs
- Knowledge Node registry missing/unexpected question mappings

Post-B12 requirement: Q1-Q1737 must be exact after B12 if the audit plan is unchanged. Later, one authoritative bank-version/count contract should replace duplicated range literals, as specified in `docs/question-bank-data-architecture-v01.md`.

### 3. JSON Schema — `data/question_bank/schema/question_bank_schema_v1.json`

Current main encodes the upper bound in two ways:

- `$defs.qid.pattern` explicitly ends at Q1660
- each of `questions`, `answers`, `explanations`, and `question_tags` has `minItems=1660` and `maxItems=1660`

Post-B12 requirement:

- QID pattern must accept through the declared max and still reject out-of-range IDs
- all four arrays must require the exact declared count
- schema exactness must remain synchronized with runtime and validator exactness

### 4. Legacy history audit — `scripts/backfill_node_learning_history.py`

`_question_number()` currently accepts only numeric IDs in the range 1..1660.

This matters even though the command is currently a read-only/dry-run history audit: after new B12 questions receive real learner history, leaving this upper bound stale would classify valid later Q IDs as `out_of_range_question_id`.

Post-B12 requirement: align this safety range with the same authoritative bank contract before the script is relied on for history that can include Q1661+.

### 5. Question Bank tests

`tests/test_question_bank.py` currently asserts:

- `question_count() == 1660`

`tests/test_question_bank_schema.py` currently asserts, among other live-data facts:

- all four canonical stores have 1660 records
- `knowledge_node_id_present == 1660`
- all registry question mappings total 1660
- registry topology counts reflecting current pre-B12 Node sharing

B12 necessarily changes some registry topology because 77 new questions are being assigned to existing Nodes, and one planned Q is shared by two consolidated Node concepts according to the approved audit. Therefore post-B12 QA must update only values that are mechanically changed by the reviewed design; it must not blindly replace every historical count.

## Known Batch-regression test surface

Batch11 touched a wider set of test files because historical bank cardinality and registry topology are used as regression fixtures. When B12 is completed, review the diff for all tests changed solely to follow legitimate count/topology growth and distinguish them from behavior changes.

Expected principles:

- old question content remains immutable except explicitly reviewed Node-label normalization
- old accepted-answer contracts remain unchanged
- classifier behavior remains unchanged
- no reviewed STRONG override is added merely to make new questions pass
- exact source/new-question STRONG checks are explicit
- Q1661-Q1737 are contiguous if the final 77-question audit remains unchanged

## Post-B12 freeze checklist

Before declaring the 1737-question bank frozen:

1. `question_bank.py` exact declared range is aligned.
2. validator exact declared range is aligned.
3. schema QID pattern and all four exact array sizes are aligned.
4. history-audit range accepts the final declared bank only.
5. four canonical JSON stores contain identical ID sets.
6. no missing or duplicate Q IDs.
7. every accepted answer belongs to a real choice.
8. choice explanation keys exactly match choice keys.
9. every question maps to exactly one registry Node entry under the formal registry contract.
10. all Node/canonical references resolve.
11. B12 source/new-question STRONG relationships satisfy the existing classifier without hacks.
12. full pytest and validator pass.
13. `question_tags_audit.txt` is regenerated through the final Q ID and reviewed.
14. a Git tag/Release is made before later JSON→DB mirror work.

## Architecture follow-up

Do not solve these repeated literals by making validation weaker during B12. Finish the expansion first. After the bank is frozen, Issue #86 owns the follow-up to establish a single explicit bank-version/count contract and then build a read-only JSON→DB mirror proof.

## Non-goals

This inventory does not authorize:

- Production DB writes
- learner-history rewrites
- Phase10 selector changes
- Phase11 weight/promotion changes
- Recent Cooldown changes
- Node-state transition changes
- runtime switch from JSON to Neon
