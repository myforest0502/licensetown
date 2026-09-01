# Phase 11 Existing Signal Map

Date: 2026-09-01

## Goal

Phase 11 should reuse evidence LicenseTown already computes instead of creating parallel statistics. This document maps current reusable signals to the future judgment layer.

## 1. Existing field-level evidence

`field_evidence.py` already provides a read-only evidence snapshot for all 18 fields. It explicitly does not expose an official mastery score, which is the correct boundary for Phase 11 shadow work.

Reusable per-field signals include:

- total question count
- unique answered question count
- question coverage
- total canonical Node count
- attempted canonical Node count
- Node coverage
- unseen/checking/repairing/repaired/recheck_due/stable Node counts
- retention target Nodes
- confidence 1/2/3 counts
- unknown answer count
- answer count / correct count / accuracy
- repeated weakness evidence count and levels
- different-question repair confirmation count
- multi-field Node membership

Phase 11 should call or adapt this existing evidence rather than independently recalculate field weakness from raw attempts.

## 2. Existing deterministic recommendation

`learning_analysis.py` is the current field-level recommendation baseline.

Important current behavior:

- Before 100 total answers: foundation phase.
- Foundation phase prioritizes basic fields with low/no exposure.
- Recommendation size is 10 questions.
- After 100 answers: weakness candidates require enough evidence before strong weakness claims.
- Low engagement/unlearned fields enter only after learning is broad enough.

This becomes the control group for Phase 11 shadow evaluation.

Phase 11 must not be judged against an imaginary ideal; it should be compared with the current deterministic recommendation on the same snapshot.

## 3. Existing Node-level evidence

The Node state engine already supplies:

- unseen
- checking
- repairing
- repaired
- recheck_due
- stable
- due/overdue retention information

Repeated weakness evidence already distinguishes stronger patterns such as repeated or cross-question wrong evidence.

Phase 11 should consume these states, not create a second Node state model.

## 4. Existing question-selection evidence

The adaptive selector already computes:

- priority reason
- priority group
- priority score
- repair evidence quality
- strong different-question status
- same-question repeat
- recent-question repeat
- recent cooldown bypass
- Safety

Audit-lite will persist the six highest-value fields for real-use analysis:

- selection_reason
- selection_group
- selection_score
- repair_evidence_quality
- recent_question_repeat
- recent_cooldown_bypassed

These should be used to evaluate whether Phase 11 intent and actual Phase 10 question selection agree.

Example consistency checks:

- Phase 11 says `repair`, but selected questions contain almost no repair group.
- Phase 11 says `coverage`, but many questions required recent-cooldown bypass.
- A repeated Q occurs without a documented bypass.
- A recommendation targets a field whose evidence is already broad and stable while another field has strong unresolved weakness.

## 5. Existing activity/recommendation evidence

Learning events now provide or are designed to provide:

- learning source
- recommendation plan
- recommendation progress/completion
- consultation usage fact only
- latest activity day
- latest learning day
- field counts and accuracy for recent activity

Phase 11 can use recommendation completion behavior as an adherence signal, but not as a moral/effort score.

Example:

- If a 10-question recommendation was completed through another learning route, treat the goal as completed.
- If it was not completed, do not automatically infer unwillingness or poor motivation.

## 6. Privacy boundary

Consultation content is never a Phase 11 input.

Allowed:

- consultation used: yes/no

Not allowed:

- consultation message text
- inferred personal/emotional state from conversation content
- supporter access to private conversation content

## 7. Recommended Phase 11 v0.1 input adapter

Instead of one giant new query, build the shadow snapshot by composing existing read-only functions.

Conceptually:

```python
{
    "field_evidence": get_user_field_evidence(user_id),
    "current_guidance": build_learning_guidance(...),
    "node_summary": ...,  # existing formal Node states
    "recent_activity": ...,
    "recommendation_plan": ...,
    "selection_audit_summary": ...,
}
```

The first implementation should favor explicit, inspectable data over premature abstraction.

## 8. Shadow judgment outputs

Minimum output:

```python
{
    "learning_intent": "coverage|repair|recheck|stabilization|maintenance",
    "target_field_id": 4,
    "target_field": "人間発達学",
    "question_count": 10,
    "reason_code": "insufficient_coverage",
    "confidence": "low|medium|high",
    "evidence": [
        "answered_question_count=3",
        "node_coverage=..."
    ],
}
```

The `evidence` list is important. Phase 11 should be debuggable without asking an LLM to explain its own hidden reasoning.

## 9. Confidence rules for v0.1

Use conservative evidence confidence.

Suggested initial boundary:

- low: sparse evidence / coverage decision
- medium: sufficient answers but only one weakness signal
- high: multiple consistent signals, e.g. confident wrong + repeated weakness + repairing Node cluster

Do not convert this into a pass/fail probability.

## 10. Key design decision

Phase 11 is an orchestrator, not a replacement for Phase 10.

Phase 11 chooses the learning purpose and scope.
Phase 10 chooses the actual questions within that purpose while enforcing repair evidence, Safety, Node diversity, and recent cooldown.

This separation should remain explicit in code and tests.
