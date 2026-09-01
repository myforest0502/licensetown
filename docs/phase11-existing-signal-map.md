# Phase 11 Existing Signal Map

Date: 2026-09-02
Status: active signal inventory for shipped Shadow diagnostics

## Purpose

Phase 11 reuses evidence LicenseTown already has instead of inventing a parallel state system or collecting unnecessary sensitive data.

## Formal learner evidence already available

### Attempt-level evidence

- question_id
- knowledge_node_id
- is_correct
- confidence
- answer_status
- answered_at
- learning source / route metadata

### Formal Node state

- unseen
- checking
- repairing
- repaired
- recheck_due
- stable

### Repeated weakness evidence

Existing logic distinguishes:

- single wrong
- repeated same-question wrong
- cross-question wrong
- cross-question confident wrong

These are stronger judgment signals than field accuracy alone.

### Field evidence

Existing field evidence/progress can supply:

- answered question count
- correct count / accuracy
- covered Node count
- Node-state distribution
- confidence evidence
- repeated weakness evidence
- retention/recheck evidence

### Recommendation/activity context

Existing learning events can distinguish records such as:

- dashboard_recommendation
- adaptive_daily
- initial_assessment
- manual
- random
- recommendation_plan activity
- consultation activity presence without consultation content

`recommendation_plan` stores the learner-facing Baseline target field and goal as a daily activity fact. Because the activity event key is JST-date-scoped, at most one plan anchor is persisted per learner/day; it is not a complete log of every same-day recommendation change.

Recommendation completion can be measured through formal learning in the target field regardless of route.

### Phase 10 selection audit

Adaptive_daily can persist:

- selection_reason
- selection_group
- selection_score
- repair_evidence_quality
- recent_question_repeat
- recent_cooldown_bypassed

Use this for post-selection consistency and explainability, not as mastery evidence.

### Historical learning-event evidence

`learning_events` also provides:

- answered_count
- correct_count
- answered_at
- question_results

Baseline `total_answers` is the sum of `answered_count`, which allows historical foundation/analysis phase reconstruction at a saved plan timestamp.

Historical Shadow replay requires an additional formal-history coverage check because old learning events are not assumed to have complete `question_attempts` coverage merely from code inspection.

### Knowledge relations

The repository contains reviewed canonical alias mappings and a small set of prerequisite/transfer relation candidates. Prerequisite relations remain diagnostic support; they do not independently promote Node state.

## Safe derived Phase 11 signals

Phase 11 may deterministically derive:

- critical Safety unresolved weakness
- confident wrong clusters
- repeated wrong clusters
- recheck_due pressure
- insufficient coverage
- uncertain-correct clusters
- same-day learning volume/context
- recommendation completion context
- current-vs-Shadow recommendation differences
- symmetric formal evidence profiles for both compared target fields
- current-policy historical replay when the historical formal-attempt coverage gate passes

## Signals that are missing or intentionally not formalized

- explicit learner study objective for the day
- exam/deadline distance as a Phase 11 policy input
- available study-time budget
- formal field-level exam weighting inside the judgment layer
- calibrated learner-specific probability of success
- validated fatigue/rest threshold
- complete versioned history of every algorithm/recommendation shown in the past

Do not silently infer these from weak proxies.

## Privacy boundary

Consultation usage may be represented as an activity fact. Consultation text/content is not a Phase 11 judgment input.

## Architectural rule

Phase 11 is a policy layer above Phase 10:

1. choose learning intent/scope
2. pass the scope to Phase 10 for exact question selection
3. inspect Phase 10 audit afterward for consistency

Phase 11 does not own exact Q IDs, repair-evidence classification, Recent Cooldown, or formal Node-state mutation.

Retrospective Phase 11 QA applies the current policy to eligible historical learner evidence; it is not historical code time-travel and must not claim causality.
