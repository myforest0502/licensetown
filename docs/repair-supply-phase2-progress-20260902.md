# Repair Supply Phase 2 — progress checkpoint (2026-09-02)

Status: **Q1606-Q1625 merged to main after manual medical/content review.**

Baseline Production evidence snapshot before this work:
- repairing Nodes: 131
- STRONG available: 3
- weak-only: 6
- blocked: 122
- repairable rate: 2.3%
- repair-supply targets: 128
- priority A/B/C/D: 5 / 10 / 23 / 90

## Implemented batches

| Batch | New Q | Target Nodes | Source priority |
|---|---|---|---|
| 1 | Q1606-Q1610 | KN0194, KN0676, KN0025, KN0329, KN0697 | top 5 Priority A |
| 2 | Q1611-Q1615 | KN1399, KN1151, KN1256, KN1263, KN0607 | next 5 Priority B |
| 3 | Q1616-Q1620 | KN1186, KN0611, KN0714, KN0725, KN1281 | next 5 Priority B |
| 4 | Q1621-Q1625 | KN1395, KN0678, KN0002, KN1468, KN0065 | first 5 Priority C |

All 20 new items were designed as materially different demands from the active-wrong source questions and passed formal `different_question_strong` checks. Existing near-duplicate weak pairs were not promoted by override merely to make tests pass.

Each batch passed focused tests, full pytest with only the known unmanaged UTF fixture deselected, and the Question Bank validator before merge. Manual medical/content review records are stored alongside the batch design documents.

## Static impact estimate

The original repair-supply top 20 represented 20 distinct repairing Nodes that were not in `strong_available` in the baseline snapshot. Therefore, **if the current learner state is otherwise unchanged and Q1606-Q1625 are available to the Production selector**, the same snapshot would move from 3 STRONG-available repairing Nodes to up to 23/131, approximately **17.6%** repairable.

This is a static counterfactual, not a claim about current Production. Learner attempts, Node-state transitions, deployment timing, cooldown, or a changed history can alter the live value.

## Decision gate before batch5

Do **not** automatically create another 5-20 questions from Priority D using the old snapshot. First obtain a fresh Production `PHASE11_PROMOTION_EVIDENCE_V1` after main Q1625 is actually available. Confirm:

1. `repairability` live STRONG-available count increased as expected;
2. the newly added Qs appear as available different-Q repair evidence rather than being blocked by registry/selector semantics;
3. adaptive simulation still preserves the 15/10/5 composition and Recent Cooldown behavior;
4. the new priority list reflects current learner state rather than the pre-Q1606 snapshot;
5. Phase11 promotion gates (especially recheck_due/J4 and symmetric replay diversity) have not changed in the meantime.

Only then choose batch5 targets. This prevents spending Question Bank growth on stale Priority D candidates when the first 20 new repair tools may already change the learner's effective repair path substantially.

Checkpoint branch: `checkpoint/repair-supply-phase2-q1625-20260902`.
