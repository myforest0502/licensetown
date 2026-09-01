# Phase 11 v0.1 Deterministic Decision Table

Date: 2026-09-02
Status: implemented in diagnostics-only Shadow mode / learner-facing promotion pending

## Principle

Phase 11 chooses learning intent and scope. It does not choose exact Q IDs and does not mutate formal Node state.

Phase 10 remains responsible for exact question selection, Safety ordering inside the candidate pool, repair-evidence preference, Node diversity, and Recent Cooldown.

Evaluate rules top-to-bottom; first matching rule wins.

## J1 — Critical Safety repair

Trigger: currently unresolved critical-Safety Node with wrong evidence.

- intent: repair
- reason_code: safety_repair
- question_count: 10

Tie-break evidence order:

1. cross-question confident wrong
2. cross-question wrong
3. confident wrong
4. repeated same-question wrong
5. most recent wrong
6. field_id

A single critical-Safety wrong may justify targeted checking. Moderate Safety alone does not trigger J1.

## J2 — Confirmed confident weakness

Trigger when a field has either:

- CROSS_QUESTION_CONFIDENT_WRONG Node, or
- confident-wrong evidence across at least two distinct repairing Nodes

- intent: repair
- reason_code: confident_wrong_cluster
- question_count: 10

Tie-break:

1. cross-question confident-wrong Node count
2. distinct confident-wrong repairing Nodes
3. repairing Node count
4. lower field accuracy only when that field has at least 10 answers
5. field_id

Sparse accuracy is not allowed to win the J2 tie-break merely because it is numerically extreme.

## J3 — Repeated weakness cluster

Trigger when no J1/J2 applies and a field has:

- CROSS_QUESTION_WRONG, or
- at least two Nodes with repeated weakness evidence

A lone SINGLE_WRONG or lone repeated-same-Q wrong does not commandeer a whole field recommendation.

- intent: repair
- reason_code: repeated_wrong_cluster
- question_count: 10

Tie-break:

1. cross-question wrong Node count
2. repeated weakness Node count
3. repairing Node count
4. field_id

## J4 — Retention recheck

Trigger when no urgent repair applies and one or more Nodes are recheck_due.

- intent: recheck
- reason_code: recheck_due
- question_count: 10

Tie-break:

1. recheck_due Node count
2. maximum overdue days
3. total overdue days
4. field_id

## J5 — Foundation / insufficient coverage

### Before 100 total answers

If total answers < 100 and J1-J4 do not apply, preserve the current deterministic foundation target.

- intent: coverage
- reason_code: insufficient_coverage
- question_count: 10

The persisted/current baseline target is reused when available. If no usable current target exists, choose conservatively from the basic fields by least exposure.

### From 100 total answers onward

v0.1 intentionally uses only the conservative trigger:

- field `question_answer_count < 10`

If multiple sparse fields qualify, tie-break by:

1. fewer answered questions
2. lower Node coverage percentage
3. field_id

Node coverage percentage is a tie-break signal here, not an independent J5 trigger in v0.1.

Do not choose a field merely because the Question Bank contains many questions there.

## J6 — Uncertain-correct stabilization

Trigger when no prior rule applies and a field has:

- at least 5 answered questions
- at least 3 correct answers with confidence 2/3

- intent: stabilization
- reason_code: uncertain_correct_cluster
- question_count: 10

Tie-break:

1. uncertain-correct count
2. uncertain-correct proportion
3. checking Node count
4. field_id

## J7 — Maintenance / broad adaptive learning

If none of J1-J6 applies:

- intent: maintenance
- reason_code: maintenance_only
- question_count: 30
- target_field: None
- recommended_route: adaptive_daily

Phase 10 then selects exact questions.

## Recommendation adherence

An incomplete recommendation plan is context, not an automatic priority rule. Do not infer motivation/compliance failure from incompletion.

Persisted `recommendation_plan` events may be used as read-only historical Baseline anchors for retrospective QA. They must not be rewritten or treated as proof that the learner followed the plan.

## Same-day volume observation

Record `high_same_day_volume` when today answered_count >= 60 in Asia/Tokyo, but v0.1 Shadow must not block further learning solely from this threshold. Observe first.

## Output contract

```python
{
    "learning_intent": "repair",
    "target_field_id": 10,
    "target_field": "精神医学",
    "question_count": 10,
    "recommended_route": "dashboard_recommendation",
    "reason_code": "confident_wrong_cluster",
    "confidence": "high",
    "evidence": [
        "cross_question_confident_wrong_nodes=1",
        "repairing_nodes=3"
    ],
    "shadow_only": True
}
```

Confidence describes confidence in the recommendation rationale, never examination pass probability.

## Symmetric diagnostic comparison

For current-vs-Shadow QA, both target fields receive the same J1→J7 evidence profile.

- lower reason rank = stronger formal evidence
- either Current or Shadow may be stronger
- equal rank or unavailable profile = insufficient evidence to judge

This comparison is diagnostic only. It does not prove future learning outcome superiority.

## Non-negotiable exclusions

Do not:

- infer field weakness from one ordinary wrong answer
- use consultation content
- use selection score as mastery score
- infer learner weakness from bank distribution
- bypass Recent Cooldown to satisfy a soft repair quota
- mutate formal Node state from Phase 11
- hard-code Q IDs from the judgment layer
- expose internal scores to the learner

## Promotion gate

Learner-facing replacement requires evidence of:

1. no critical Safety misses
2. no repeated overreaction to single wrong answers
3. appropriate sparse-learner coverage
4. recheck_due not starved indefinitely
5. Phase 11 intent consistent with Phase 10 audit
6. symmetric Baseline-vs-Shadow review including Current wins
7. no unexplained adaptive repeat regression
8. natural-use evidence showing recommendation relevance is at least no worse than Baseline

Retrospective replay can support safety and consistency review, but it does not replace prospective natural-use evidence.
