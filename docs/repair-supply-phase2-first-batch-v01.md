# Repair Supply Phase 2 — first batch v0.1

## Production basis

The 2026-09-02 Promotion Evidence bundle reports:

- repairing Nodes: 131
- formal STRONG available: 3
- repairable rate: 2.3%
- repair-supply targets: 128
- Priority A: 5
- Priority B: 10
- Priority C: 23
- Priority D: 90

The first batch is the five Priority A Safety-moderate Nodes because all five currently have **both existing questions in the active wrong set** and no remaining unseen different question. A third independent item is therefore the shortest path to usable formal repair confirmation.

| Rank | Node | Existing active wrong Qs | Current supply action |
|---|---|---|---|
| 1 | KN0194 | Q195, Q1599 | create_strong_alternate |
| 2 | KN0676 | Q684, Q1602 | create_strong_alternate |
| 3 | KN0025 | Q25, Q1596 | create_strong_alternate |
| 4 | KN0329 | Q331, Q1600 | create_strong_alternate |
| 5 | KN0697 | Q705, Q1603 | create_strong_alternate |

## Target result

Add exactly five new LT-original questions, one per Node, using the next sequential Q IDs after the current Question Bank head. Each new question must be a clinically meaningful third context rather than a paraphrase of either existing wrong question.

For immediate formal utility, prefer a `(task, primary_ability)` pair that differs from both existing active wrong questions. Validate the resulting classifier output against **both** existing wrong Qs, not just one.

## Content-specific emphasis

- **KN0194**: test environmental/support decision or measurement around safe negotiation of an entrance step; avoid making every distractor unrelated to the entrance problem.
- **KN0676**: test recognition/initial PT safety response to the hemodynamic pattern using plausible competing causes/actions; avoid cartoonishly unsafe distractors.
- **KN0025**: test localization/functional interpretation of cervical myelopathy signs without copying the exact Q1596 sign list.
- **KN0329**: test positioning/contracture-prevention reasoning from scar location and tissue shortening direction; distractors should represent plausible positioning errors rather than absurd goals.
- **KN0697**: test individualized exercise-prescription reasoning in severe COPD using symptoms/SpO2/workload response; plausible alternatives should differ by monitoring or prescription principle, not irrelevant measurements.

## Acceptance gate

1. Existing Q1–Q1605 remain byte-for-byte semantically unchanged.
2. Five new questions/answers/explanations/tags are internally consistent.
3. Canonical Node IDs are exactly KN0194, KN0676, KN0025, KN0329, KN0697.
4. Each new question is `different_question_strong` against both corresponding active-wrong Qs where metadata can express that; any exception must be explicitly reviewed and registered.
5. Each item passes manual medical correctness + distractor quality + independence review.
6. Question Bank validator passes.
7. Focused repair-evidence/state-transition tests pass.
8. Full pytest passes, with only the known unmanaged UTF fixture deselected if still applicable.
