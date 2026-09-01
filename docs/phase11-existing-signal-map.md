# Phase 11 Existing Signal Map

Date: 2026-09-01
Status: design inventory / no runtime behavior change.

## Purpose

Phase 11 should reuse evidence LicenseTown already has instead of inventing parallel state or collecting unnecessary sensitive data.

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

Existing logic can distinguish patterns such as:

- single wrong
- repeated same-question wrong
- cross-question wrong
- cross-question confident wrong

These are stronger for judgment than field accuracy alone.

### Field evidence

Existing field evidence/progress code can supply:

- answered question count
- correct count / accuracy
- covered Node count
- Node-state distribution
- confidence evidence
- repeated weakness evidence
- retention/recheck evidence

### Recommendation/activity context

Existing learning events can distinguish new records such as:

- dashboard_recommendation
- adaptive_daily
- initial_assessment
- manual
- random
- recommendation_plan activity
- consultation activity presence without consultation content

Recommendation plan/progress can show whether the planned field/goal was completed through any formal learning route.

### Phase 10 selection audit

Adaptive_daily can persist:

- selection_reason
- selection_group
- selection_score
- repair_evidence_quality
- recent_question_repeat
- recent_cooldown_bypassed

Use this for post-selection consistency and explainability, not as mastery evidence.

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
- current-vs-shadow recommendation differences

## Signals that are currently missing or intentionally not formalized

- explicit learner study objective for the day
- exam/deadline distance as a policy input
- available study-time budget
- formal field-level exam weighting inside the judgment layer
- calibrated learner-specific probability of success
- validated fatigue/rest threshold

Do not silently infer these from weak proxies.

## Privacy boundary

Consultation usage may be represented as an activity fact. Consultation text/content is not a Phase 11 judgment input.

## Architectural rule

Phase 11 is a policy layer above Phase 10:

1. choose learning intent/scope
2. pass the scope to the Phase 10 selector
3. inspect Phase 10 audit afterward for consistency

Phase 11 does not own exact Q IDs, repair-evidence classification, cooldown, or formal Node-state mutation.
