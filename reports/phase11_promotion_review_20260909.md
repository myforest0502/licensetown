# Phase11 promotion review — 2026-09-09

Scope: primary learner, Production-shaped persisted history available at review time.

This is a read-only acceptance record. It does not authorize learner-facing promotion and does not mutate Production data.

## Snapshot

- attempts: 1525
- correct: 1103
- unique questions: 740
- unique raw Knowledge Nodes: 572
- latest persisted attempt: 2026-09-09 08:24 JST
- valid historical `recommendation_plan` anchors: 9
- historical replay linkage at all 9 anchors: 0 missing attempts, 0 question-ID mismatches

## Promotion gate matrix

| Gate | Status | Evidence / disposition |
| --- | --- | --- |
| Safety retrospective | PASS | Formal J1 uses current-cycle evaluable Critical Safety evidence and is evaluated before J2–J7. Real history contains unresolved Critical `KN0613` / `Q621`; later weaker baseline recommendations cannot count as a Phase11 Safety miss when Shadow correctly prioritizes Safety. |
| Repeat audit | PASS | adaptive unexplained recent repeat = 0; adaptive metadata inconsistent = 0. Historical metadata-unavailable rows remain observable but are not defined as blocking defects. |
| Formal trigger consistency | PASS | J2/J3 candidate builders and retrospective mismatch detector use the same thresholds; single ordinary wrong evidence cannot validly trigger J2/J3. Regression tests cover valid and invalid trigger shapes. |
| Retention | OPEN | No qualified natural spaced strong outcome exists yet. First confirmed strong repair checkpoint (`KN0394`) is due 2026-09-09 18:32:30 JST; no persisted attempt exists after that due timestamp at review time. |
| Intent-selection alignment | OPEN | Saved adaptive history contains 0 `recheck_due` selections, therefore no evaluable J4 exact-Q alignment sample exists yet. |
| Comparison diversity | OPEN | Real history clearly exercises Shadow-stronger-than-baseline conditions after unresolved Critical Safety appears. A second independently reproduced comparison direction has not been established from the available natural history; do not infer one to satisfy the gate. |
| Current profile consistency | PASS | Current unresolved Critical `KN0613` makes formal Shadow reason `safety_repair`; symmetric field profiles are built from the same active facts and therefore expose the same strongest reason for the target field. |

## Current decision

- BLOCKED gates: **none identified**
- OPEN gates: **retention, intent-selection alignment, comparison diversity**
- automatic state: **HOLD / Shadow-only**
- learner-facing promotion allowed automatically: **no**
- manual review required after all checkable gates clear: **yes**

## Why comparison diversity remains OPEN

The gate requires at least two observed comparison direction buckets among agreement, Shadow stronger, current/baseline stronger, and inconclusive. The current history provides strong evidence for the Shadow-stronger direction once unresolved Critical Safety exists. Earlier anchors do not yet have a second direction reproduced with the exact historical formal-state derivation strongly enough to claim PASS. The correct action is to preserve OPEN rather than manufacture or approximate evidence.

## Natural next acceptance events

1. After a natural `recheck_due` question is actually answered, re-run retention outcome audit.
2. On the same event, re-run exact-Q intent-selection alignment; a valid retention selection should use STRONG different-question evidence against the retention reference.
3. Continue accumulating recommendation-plan anchors. If a second comparison direction appears naturally, re-run comparison diversity.
4. Only after all checkable gates are PASS, perform explicit human learner-facing promotion review.

## Policy

OPEN means evidence is not yet sufficient. It is not a defect by itself. Do not force learner behavior, synthesize Production evidence, weaken a gate, or reinterpret historical metadata merely to convert OPEN to PASS.
