# Phase 11 v0.1 Deterministic Decision Table

Date: 2026-09-01
Status: design only / shadow mode

## Principle

Phase 11 v0.1 must be deterministic, inspectable, and conservative.

It chooses the learning **intent and scope**. It does not choose exact Q IDs and does not mutate Node state.

Phase 10 remains responsible for exact question selection, Safety ordering inside the candidate pool, repair-evidence preference, Node diversity, and Recent Cooldown.

## Input policy

Reuse existing evidence wherever possible:

- `field_evidence.py` for field coverage, Node state counts, confidence, repeated weakness, retention evidence
- formal Node states for repairing/recheck_due/stable status
- repeated weakness evidence for SINGLE/CROSS/CONFIDENT patterns
- current recommendation as the control judgment
- latest recommendation plan/progress and learning source for activity context
- selection audit only for post-selection consistency checks

Do not consume consultation text.

## Decision order

Evaluate top to bottom. First matching rule wins.

### J1 — Critical Safety repair

Trigger when a currently unresolved critical-Safety Node has wrong evidence.

Target intent:

`repair`

Reason code:

`safety_repair`

Question count:

10

Target field:

field containing the most urgent critical-Safety unresolved Node.

Tie-break order:

1. cross-question confident wrong
2. cross-question wrong
3. confident wrong
4. repeated same-question wrong
5. most recent wrong
6. field_id

Important:

A single critical-Safety wrong may justify a targeted check because the content is safety-sensitive. Moderate Safety does not automatically trigger J1 by itself.

### J2 — Confirmed confident weakness

Trigger when any field has either:

- a `CROSS_QUESTION_CONFIDENT_WRONG` Node, or
- confident wrong evidence across at least two distinct repairing Nodes in the same field

Intent:

`repair`

Reason code:

`confident_wrong_cluster`

Question count:

10

Target field tie-break:

1. number of cross-question confident-wrong Nodes
2. number of distinct confident-wrong repairing Nodes
3. total repairing Nodes
4. lower current field accuracy, if based on enough answers
5. field_id

### J3 — Repeated weakness cluster

Trigger when no J1/J2 applies and a field has strong repeated weakness evidence.

Qualifying evidence:

- `CROSS_QUESTION_WRONG`, or
- at least two Nodes with repeated weakness evidence in the same field

A lone `SINGLE_WRONG` does not trigger J3.
A lone repeated-same-Q wrong may remain a Node-level repair target in Phase 10, but should not by itself commandeer the whole day's field recommendation.

Intent:

`repair`

Reason code:

`repeated_wrong_cluster`

Question count:

10

Tie-break:

1. cross-question wrong Node count
2. repeated weakness Node count
3. repairing Node count
4. field_id

### J4 — Retention recheck

Trigger when no urgent repair rule applies and one or more Nodes are `recheck_due`.

Intent:

`recheck`

Reason code:

`recheck_due`

Question count:

10

Target field tie-break:

1. largest recheck_due Node count
2. largest maximum overdue days
3. largest total overdue days
4. field_id

This prevents repaired material from being forgotten merely because coverage work is still available elsewhere.

### J5 — Foundation / insufficient coverage

This is the default early-learning rule.

If total answers < 100 and none of J1-J4 applies, preserve the current foundation philosophy rather than inventing a new strategy.

Intent:

`coverage`

Reason code:

`insufficient_coverage`

Question count:

10

Target field:

use the same foundation-field ordering as the current deterministic recommendation so the shadow system differs only when stronger evidence justifies it.

After 100 total answers, coverage may still trigger when a field has insufficient evidence to judge ability.

Initial conservative condition after 100 answers:

- field answered_count < 10, or
- field Node coverage remains materially below the user's other fields

Do not choose a field solely because it has many total bank questions.

### J6 — Uncertain-correct stabilization

Trigger when no prior rule applies and a field has enough answered evidence but a meaningful amount of confidence 2/3 correct answers.

Intent:

`stabilization`

Reason code:

`uncertain_correct_cluster`

Question count:

10

Minimum evidence for v0.1:

- at least 5 answered questions in the field
- at least 3 correct answers with confidence 2/3

Tie-break:

1. uncertain-correct count
2. uncertain-correct proportion
3. checking Node count
4. field_id

### J7 — Maintenance / broad adaptive learning

If none of J1-J6 applies:

Intent:

`maintenance`

Reason code:

`maintenance_only`

Question count:

30

Target field:

None

Recommended route:

`adaptive_daily`

Phase 10 then builds the broad session.

## Recommendation adherence does not outrank learning evidence

An incomplete recommendation plan is context, not an automatic top-priority rule.

Examples:

- Yesterday's recommendation was incomplete, but today a critical Safety weakness exists: Safety wins.
- Recommendation was completed through normal study rather than the recommendation button: count it completed.
- Recommendation was not completed: do not infer motivation or compliance failure.

## Daily volume guardrail — shadow only initially

Phase 11 should eventually avoid mechanically recommending another 30 questions after substantial same-day work.

For v0.1 shadow evaluation, record a flag:

`high_same_day_volume`

Suggested initial observation threshold:

- today answered_count >= 60

Do not yet use this threshold to block learning. First observe real behavior and decide whether a rest/short-review recommendation improves outcomes.

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

## Confidence mapping

Confidence describes confidence in the **recommendation rationale**, not examination pass probability.

High:

- J1 critical Safety with clear wrong evidence
- J2 cross-question confident weakness
- J3 multiple consistent repeated-weakness signals

Medium:

- J4 retention due
- J6 uncertain-correct cluster with minimum evidence met
- J3 weaker multi-signal combination

Low:

- J5 sparse-data coverage
- J7 maintenance default

## Shadow comparison labels

For every snapshot, compare current recommendation with Phase 11 and classify:

- `same_target_same_reason`
- `same_target_stronger_reason`
- `different_target_shadow_has_stronger_evidence`
- `different_target_current_has_stronger_evidence`
- `insufficient_evidence_to_judge`

Human review should focus on the two `different_target_*` groups.

## Non-negotiable v0.1 exclusions

Do not:

- infer weakness from one ordinary wrong answer at field level
- use consultation content
- use selection score as a mastery score
- turn question-bank distribution into learner weakness
- bypass Recent Cooldown to satisfy a soft repair quota
- mutate formal Node state from Phase 11
- directly hard-code Q IDs from the judgment layer
- expose internal scores to the learner

## Promotion gate

The deterministic table may replace the current recommendation only after shadow cases show:

1. no critical Safety miss
2. no repeated overreaction to single wrong answers
3. coverage remains appropriate for sparse learners
4. recheck_due is not starved indefinitely
5. Phase 11 intent and Phase 10 selected-question audit are consistent
6. real-user review shows fewer obviously irrelevant recommendations than the current baseline
