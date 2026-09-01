# Phase 10 Static Audit Status

Date: 2026-09-02
Status: Q1-Q1605 static audit refreshed; Phase 10 static integrity remains PASS.

## Current snapshot

`data/question_bank/question_tags_audit.txt` describes the current formal Question Bank through Q1605.

Verified totals:

- records: 1605
- Q range: Q1-Q1605
- duplicates: 0
- missing: 0
- schema errors: 0
- Knowledge Node reference errors: 0
- cross-file ID mismatches: 0
- validator: PASS

## Current distributions

Tag version:

- 0.3 = 200
- 1.0 = 1405

Status:

- reviewed_sample = 200
- reviewed = 1405
- provisional_bulk = 0

Task:

- assessment_selection = 172
- device_selection = 44
- fact_recall = 880
- finding_interpretation = 191
- functional_goal_decision = 17
- intervention_selection = 212
- prognosis_prediction = 5
- safety_priority = 84

Primary ability:

- DECIDE = 101
- INTERPRET = 191
- KNOW = 880
- MEASURE = 172
- PREDICT = 5
- PRESCRIBE = 256

Secondary ability:

- DECIDE = 72
- INTERPRET = 277
- KNOW = 27
- MEASURE = 15
- PREDICT = 1
- PRESCRIBE = 24
- null = 1189

Level:

- 1 = 859
- 2 = 185
- 3 = 466
- 4 = 95

Safety:

- critical = 65 (4.0%)
- moderate = 227 (14.1%)
- none = 1313 (81.8%)

Source:

- original = 511 (31.8%)
- past_exam = 1094 (68.2%)

## Canonical Node snapshot

- canonical = 1509
- singleton = 1422
- multi-question = 87

The canonical count remains unchanged because Q1565-Q1605 were mapped onto existing canonical Nodes rather than creating new concepts.

## Q1565-Q1594 import effect

The 30 added past-exam questions mapped to 30 existing canonical Nodes. Twenty-nine formerly-singleton Nodes became multi-question Nodes; one Node was already multi-question.

Historical delta:

- records 1564 -> 1594 (+30)
- fact_recall 850 -> 880 (+30)
- canonical 1509 -> 1509
- singleton 1462 -> 1433 (-29)
- multi-question 47 -> 76 (+29)

## Q1595-Q1605 Safety strong-repair pilot effect

Eleven original questions were added as strong different-Q repair supply for eleven existing Safety repairing Nodes.

Static additions:

- records = 11
- source original = 11
- assessment_selection = 2
- finding_interpretation = 5
- intervention_selection = 1
- safety_priority = 3
- safety moderate = 11
- formal strong source/new pairs = 11 / 11

Current delta from Q1594:

- records 1594 -> 1605 (+11)
- reviewed 1394 -> 1405 (+11)
- moderate Safety 216 -> 227 (+11)
- original 500 -> 511 (+11)
- canonical 1509 -> 1509
- singleton 1433 -> 1422 (-11)
- multi-question 76 -> 87 (+11)

These additions were intentionally targeted repair-supply changes, not an attempt to normalize the global Question Bank distribution.

## Repairability interpretation

The old pre-Q1565 repairability counts must not be used as current supply counts.

Production learner diagnostics later showed that, before the Q1595-Q1605 pilot, 135 repairing Nodes included only one Node with a strong different-Q candidate, five weak-only Nodes, and 129 same-Q/formally blocked Nodes. This established that `repaired=0` was largely constrained by repair-evidence supply, not simply learner performance.

Q1595-Q1605 deliberately add strong different-Q supply to eleven Safety Nodes. Static validation confirms all eleven source/new pairs classify as `different_question_strong`. Actual learner state progression still requires natural correct confidence-1 responses to those alternate questions; Question Bank availability alone must not be reported as learner repair.

## Follow-on static checks

Useful continuing QA:

- Safety concentration by field
- fact_recall concentration by field/source
- level concentration by field/source
- singleton vs multi-question canonical Node distribution
- current strong/weak different-Q availability
- whether future repair-supply additions remain targeted rather than indiscriminate

Any imbalance is a review candidate, not an automatic rewrite.

## Phase 11 relevance

Question-bank distribution describes available evidence supply; it is not learner weakness. Phase 11 must never infer that a learner is weak in a field simply because the bank contains many questions there.
