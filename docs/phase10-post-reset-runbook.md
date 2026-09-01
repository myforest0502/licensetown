# Phase 10 Post-Reset Runbook

Date: 2026-09-01

This runbook defines the exact sequence to resume after Codex quota is restored. It is intentionally staged so that Render is not touched until all code-only checks are complete.

## Stage A — adaptive audit-lite merge readiness

Target commit:

`9a0d4a0dbf3c087808040a7c2722862be4cc9c40`

Expected base:

`e7d208ea70a59c1b848ac76efc1f930defedcfc7`

Verified shape before deployment:

- exactly one commit ahead of current main baseline
- changed files limited to:
  - adaptive_question_selector.py
  - app.py
  - tests/test_adaptive_question_selector.py
  - tests/test_learning_stats.py
- DB migration: none
- production DB write: none
- Question Bank changes: none
- Node transition changes: none
- adaptive ranking/cooldown logic changes: none

### Audit-lite behavior to preserve

Only adaptive_daily + Node-adaptive path receives audit metadata.

Six persisted fields:

- selection_reason
- selection_group
- selection_score
- repair_evidence_quality
- recent_question_repeat
- recent_cooldown_bypassed

Random/manual/dashboard/nekketsu must not receive these fields.

The audit data is metadata only and must not alter question_attempts or user_node_state behavior.

## Stage B — merge/deploy

Only after Stage A remains clean:

1. fast-forward main to the audit-lite commit
2. allow Render auto-deploy
3. no DB migration
4. do not create production learning records for testing unless a real learner naturally uses the feature

## Stage C — post-deploy observation

The most valuable production verification is natural usage, not synthetic clicking.

After the learner completes adaptive_daily learning, verify later from persisted history that:

- learning_source = adaptive_daily
- selection audit fields are present
- repeated Q, if any, has an explainable bypass reason
- ordinary/non-adaptive events do not contain adaptive audit metadata

## Stage D — refresh static Question Bank audit

The committed `question_tags_audit.txt` is stale at Q1564.

Regenerate against Q1-Q1594 and confirm:

- records 1594
- no missing IDs
- no duplicates
- no schema/reference errors
- refreshed task/ability/level/safety distributions

Do not change tags merely to force prettier distributions.

## Stage E — Phase 10 closure decision

Phase 10 can close only after:

- recent cooldown v0.2 deployed
- audit-lite deployed
- at least one real adaptive use observed after deployment
- unexpected consecutive-session overlap is absent, or any overlap is explained by Safety/bank shortage metadata
- static 1594 tag audit refreshed

## Stage F — Phase 11 start

Phase 11 begins in shadow mode only.

No automatic user-facing decisions and no Node-state mutation.

The first shadow output should answer:

1. What should the learner do next?
2. Why?
3. Which evidence supports it?
4. How confident is the judgment?
5. What evidence is still missing?

The judgment layer should consume existing evidence rather than create a second competing recommendation engine.
