# Phase 10 Post-Reset Runbook

Date: 2026-09-01
Status: Stage A/B complete; Stage C/D remain observational/static QA.

This runbook records the Phase 10 closure sequence without requiring synthetic production activity.

## Stage A — adaptive audit-lite readiness — COMPLETE

Merged commit:

`9a0d4a0dbf3c087808040a7c2722862be4cc9c40`

Verified scope:

- adaptive_question_selector.py
- app.py
- tests/test_adaptive_question_selector.py
- tests/test_learning_stats.py
- DB migration: none
- production DB write: none
- Question Bank changes: none
- Node transition changes: none
- adaptive ranking/cooldown logic changes: none

Persisted adaptive_daily audit fields:

- selection_reason
- selection_group
- selection_score
- repair_evidence_quality
- recent_question_repeat
- recent_cooldown_bypassed

The audit payload is metadata only and does not alter question_attempts or user_node_state behavior.

## Stage B — merge/deploy — COMPLETE

Main was fast-forwarded to the audit-lite commit. Render auto-deploy is the normal delivery path; no migration or synthetic Production DB write is required.

## Stage C — natural post-deploy observation — PENDING REAL USE

After a learner naturally completes adaptive_daily learning, verify from persisted history:

- learning_source = adaptive_daily
- selection audit fields are present
- repeated Q, if any, has an explainable Safety/bank-shortage bypass
- ordinary/non-adaptive events do not contain adaptive audit metadata
- consecutive adaptive sessions do not show unexplained recent-Q overlap

Do not create fake production learning records merely to satisfy this gate.

## Stage D — refresh static Question Bank audit

The committed `question_tags_audit.txt` snapshot is stale at Q1564 while the formal bank is Q1-Q1594.

Regenerate against Q1-Q1594 and confirm:

- records 1594
- no missing IDs
- no duplicates
- no schema/reference errors
- refreshed task/ability/level/safety distributions

Do not change tags merely to force prettier distributions.

## Stage E — Phase 10 closure gate

Phase 10 closes after:

- recent cooldown v0.2 deployed
- audit-lite deployed
- static Q1-Q1594 tag audit refreshed
- at least one natural adaptive use observed after deployment
- unexpected consecutive-session overlap is absent, or every overlap is explained by Safety/bank-shortage metadata

## Stage F — Phase 11 start policy

Phase 11 may proceed in design and diagnostics-only shadow mode before the natural-use closure observation is complete, but it must not replace learner-facing recommendations yet.

The first shadow output should answer:

1. What should the learner do next?
2. Why?
3. Which evidence supports it?
4. How confident is the judgment rationale?
5. What evidence is still missing?

The judgment layer consumes existing evidence; it does not create a second Node-state system or mutate formal learning state.
