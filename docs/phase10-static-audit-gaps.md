# Phase 10 Static Audit Status

Date: 2026-09-01
Status: Q1-Q1594 static audit refreshed and committed.

## Current snapshot

`data/question_bank/question_tags_audit.txt` now describes Q1-Q1594.

Verified totals:

- records: 1594
- duplicates: 0
- missing: 0
- schema errors: 0
- Knowledge Node reference errors: 0
- answers/explanations/tags inconsistencies: 0

Committed in:

`07fb8a028ea8de29b32cfcdfb63c249ae6951bed`

Question Bank validator: PASS.
Static related tests: 38 passed.

## Current distributions

Tag version:

- 0.3 = 200
- 1.0 = 1394

Status:

- reviewed_sample = 200
- reviewed = 1394

Task:

- assessment 170
- device 44
- fact recall 880
- finding 186
- goal 17
- intervention 211
- prognosis 5
- safety 81

Primary ability:

- DECIDE 98
- INTERPRET 186
- KNOW 880
- MEASURE 170
- PREDICT 5
- PRESCRIBE 255

Secondary ability:

- DECIDE 68
- INTERPRET 275
- KNOW 27
- MEASURE 14
- PREDICT 1
- PRESCRIBE 20
- null 1189

Level:

- 1 = 859
- 2 = 185
- 3 = 455
- 4 = 95

Safety:

- critical 65 (4.1%)
- moderate 216
- none 1313

Source:

- original 500
- past_exam 1094

Compared with the previous Q1-Q1564 report:

- records 1564 -> 1594
- fact recall 850 -> 880
- critical 65 -> 65
- the added 30 questions are all past_exam

## Canonical Node update

Current audit:

- canonical 1509
- singleton 1433
- multi-question 76

Previous snapshot:

- singleton 1462
- multi-question 47

The 29-node shift is expected because new questions turned 29 formerly-singleton canonical Nodes into multi-question Nodes.

Earlier strong/weak different-Q repairability totals were produced before the Q1565-Q1594 imports. Recompute those totals before using them as current supply counts.

## Follow-on static checks

Useful later QA includes:

- Safety concentration by field
- fact_recall concentration by field/source
- level concentration by field/source
- singleton vs multi-question canonical Node distribution
- refreshed strong/weak different-Q availability
- Q1565-Q1594 contribution by field and repairability

Any imbalance becomes a review candidate, not an automatic rewrite.

## Phase 11 relevance

Question-bank distribution describes available evidence supply; it is not learner weakness. Phase 11 must never infer that a learner is weak in a field simply because the bank contains many questions there.
