# Phase 11 Production Evidence Review v0.1

Date: 2026-09-02
Source: `PHASE11_PROMOTION_EVIDENCE_V1` copied from Production Supporter `/supporter/pilot-diagnostics` with period = all.
Status: **HOLD — remain Shadow-only. Evidence is materially positive, but learner-facing promotion is not yet approved.**

This review uses Production diagnostic output only. It does not change J1→J7 policy, selector behavior, Node state, DB schema/write behavior, Question Bank content, Baseline learner-facing recommendation, or Phase 12 presentation.

## 1. Current Baseline vs Shadow

Current snapshot:

- Baseline target: 小児学
- Shadow target: 動作分析学
- Shadow intent: `repair`
- Shadow reason: `confident_wrong_cluster`
- Shadow confidence: `high`
- comparison: `different_target_shadow_has_stronger_evidence`
- Shadow profile consistency: true

Baseline formal profile:

- reason: `insufficient_coverage` (J5)
- evaluable answers: 4
- accuracy: 100.0%
- Node coverage: 4.7%
- Critical Safety: 0
- active confident/cross/repeated weakness: 0

Shadow formal profile:

- reason: `confident_wrong_cluster` (J2)
- evaluable answers: 88
- accuracy: 64.8%
- Node coverage: 37.1%
- active cross-question confident-wrong Nodes: 2
- active confident-wrong repairing Nodes: 5
- active cross-question wrong Nodes: 1
- active repeated-weakness Nodes: 5
- Critical Safety: 0

Interpretation: this is not a one-wrong takeover. The Shadow target has materially stronger current-cycle formal repair evidence than the Baseline target. **Current disagreement quality = GREEN for this snapshot.**

## 2. Repeat Structure Audit

All-history repeat audit:

- attempts: 665
- unique Q: 360
- same-Q repeats: 305
- justified cooldown bypass: 11
- legitimate spaced adaptive repeat: 43
- true unexplained recent repeat without bypass: 0
- metadata inconsistent: 0
- nonadaptive repeat: 0
- audit metadata unavailable: 251

The category counts explain all 305 same-Q repeats (`11 + 43 + 251 = 305`). No repeat is currently classified as an unexplained recent adaptive repeat or inconsistent saved metadata.

`metadata_unavailable=251` is historical evidence that predates or lacks the newer adaptive audit metadata. It is **not itself evidence of a current cooldown regression**, but it also cannot be retroactively promoted to explained adaptive behavior.

**Corrected repeat classifier gate = GREEN for classified current-capable history; historical metadata-unavailable portion remains informational/unknown.**

## 3. Latest saved adaptive_daily session

Latest saved adaptive session at the moment of capture:

- exists: true
- session status: `event_count_incomplete`
- events: 1
- questions: 5
- unique Q: 5
- audit fields complete: true
- recent repeats: 0
- bypasses: 0

Interpretation: this is an **in-progress 5-question set**, not a malformed completed 30-question session. Do not use it as a Phase10 30-question completion sample. The saved metadata on the existing 5 results is complete.

This does not reopen the previously verified complete 30-question Phase10 natural-use session.

## 4. Retrospective replay

Replay summary:

- recommendation anchors: 2
- eligible snapshots: 2
- coverage excluded: 0
- same-target agreement: 0
- Shadow stronger disagreement: 2
- Current/Baseline stronger disagreement: 0
- inconclusive disagreement: 0
- Phase11 Critical Safety miss candidate: 0
- Baseline stronger-Safety miss candidate: 0
- J2/J3 formal-trigger mismatch: 0

Eligible snapshots:

### Snapshot 1 — 2026-09-02 08:10 JST

- Baseline: 小児学 / goal 10 / phase analysis
- Shadow: 心理学
- Shadow reason: `confident_wrong_cluster`
- comparison: Shadow stronger
- profile consistent: true
- Phase11 Safety miss: false
- Baseline Safety miss: false
- J2/J3 trigger mismatch: false
- coverage issues: none

### Snapshot 2 — 2026-09-01 19:10 JST

- Baseline: 人間発達学 / goal 10 / phase analysis
- Shadow: 心理学
- Shadow reason: `confident_wrong_cluster`
- comparison: Shadow stronger
- profile consistent: true
- Phase11 Safety miss: false
- Baseline Safety miss: false
- J2/J3 trigger mismatch: false
- coverage issues: none

Interpretation: replay mechanics and policy consistency are **GREEN on the two available eligible snapshots**. However, both snapshots favor Shadow. This is encouraging but insufficient for a balanced disagreement review because there is not yet a Current/Baseline-win or same-target eligible replay example.

## 5. Safety gate

Observed Production evidence:

- current Critical Safety count on both compared profiles: 0
- retrospective Phase11 Critical Safety miss candidates: 0 / 2 eligible snapshots
- Baseline stronger-Safety miss candidates: 0 / 2

**Safety evidence = GREEN for observed snapshots.**

This does not prove future Safety behavior under every state. Continue prospective monitoring.

## 6. Single-wrong / formal-trigger gate

Observed Production evidence:

- retrospective J2/J3 formal-trigger mismatch: 0 / 2 eligible snapshots
- current Shadow J2 has 2 active cross-question confident-wrong Nodes and 5 active confident-wrong repairing Nodes

**Formal single-wrong-overreaction diagnostic = GREEN for observed evidence.**

Prospective relevance still needs more natural examples.

## 7. Node states and retention evidence

Current formal states:

- unseen: 1176
- checking: 198
- repairing: 131
- repaired: 4
- recheck_due: 0
- stable: 0

Observed transitions:

- repairing → repaired: 4
- repaired → repairing: 0
- recheck_due → stable: 0
- recheck_due → repairing: 0

Interpretation:

- formal repair transitions now exist in Production, which is mechanically positive;
- no `recheck_due` Node exists yet, so J4 retention-priority behavior is **NOT OBSERVABLE YET**;
- no stable transition has occurred yet.

Do not manufacture recheck_due data. Keep J4 promotion gate pending until it occurs naturally.

## 8. Repairability / bank supply

Current repairing Nodes: 131

- STRONG alternate available: 3
- weak-only: 6
- blocked/same-only: 122
- repairable rate: 2.3%

Interpretation: formal evidence semantics are improved, but **repair supply remains the dominant structural limitation**. A large majority of repairing Nodes still cannot formally confirm repair with current strong different-Q supply.

This is not a Phase11 ranking failure, but it limits how much real `repairing → repaired → recheck_due → stable` behavior can be observed and therefore limits retention validation speed.

## 9. Adaptive simulation

Current 30-question simulation:

- count: 30
- unique Q: 30
- unique Nodes: 30
- repair: 15
- checking: 10
- exploration: 5
- maintenance: 0

Composition and uniqueness remain consistent with the intended Phase10 soft-target behavior.

## 10. Promotion gate status after this Production review

### GREEN / materially supported

- no observed Phase11 Critical Safety miss
- no observed J2/J3 formal-trigger mismatch
- current J2 disagreement has strong multi-Node evidence, not one-wrong takeover
- corrected repeat classifier shows zero unexplained recent repeat-without-bypass
- corrected repeat classifier shows zero metadata inconsistency
- retrospective history coverage is complete for both available anchors
- both replay snapshots are profile-consistent
- both replay snapshots favor Shadow on formal evidence
- adaptive simulation remains 30 unique Q / 30 unique Nodes / 15-10-5 composition
- formal `repairing → repaired` transitions are now occurring

### PENDING / insufficient evidence

- J4 recheck_due behavior: **0 naturally available Nodes**
- stable retention transitions: none yet
- balanced retrospective disagreement review: **2 Shadow wins, 0 Current wins, 0 same-target**
- broader prospective recommendation relevance across more natural days/states
- more Safety-bearing natural snapshots if/when Critical Safety evidence appears
- strong repair supply remains low (3/131 repairing Nodes; 2.3%)

### Not a blocker by itself

- `metadata_unavailable=251`: historical unclassifiable repeat metadata, not a current-regression signal
- latest saved adaptive session has only 1 event/5 Q because it is currently incomplete; it must not be interpreted as a malformed completed 30-question session

## 11. Decision

**DO NOT promote Phase11 to learner-facing recommendation yet.**

Remain Shadow-only.

Reason: the available Production evidence is strongly encouraging and reveals no current formal-policy regression, but the evidence set is still too narrow for the explicit promotion rule. In particular, recheck_due retention behavior has not occurred naturally and retrospective disagreement evidence is one-sided (2 Shadow wins only).

No ranking-weight change is justified by this review.

## 12. Next evidence to collect

1. Continue natural use without manufacturing special events.
2. Capture another `PHASE11_PROMOTION_EVIDENCE_V1` after additional natural study.
3. Watch specifically for:
   - first naturally occurring `recheck_due` Node and its J4 handling;
   - first Current/Baseline stronger or same-target retrospective snapshot;
   - any Critical Safety-bearing natural state;
   - any true unexplained recent repeat-without-bypass;
   - continued prospective Baseline-vs-Shadow relevance.
4. Reassess for a **limited feature-flagged learner-facing pilot** only after these missing evidence classes become available.

No Production mutation is required for this review.
