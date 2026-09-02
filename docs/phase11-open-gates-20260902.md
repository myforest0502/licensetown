# Phase 11 Current Open Gates — 2026-09-02

Status: **learner-facing promotion remains HOLD / Shadow-only.**

This document is the short operational status. Detailed evidence lives in `phase11-production-evidence-review-20260902-v01.md`, `phase11-promotion-evidence-matrix.md` and `phase11-promotion-review-runbook.md`.

## Completed implementation gates

The previously open formal-evidence and diagnostic issues are implemented on main and tested:

- unknown excluded from confirmed field weakness while raw exposure remains available;
- evaluable-only J2/J5/J6 semantics;
- current repair-cycle J1/J2/J3 evidence;
- failed `recheck_due` starts a new repair cycle;
- retention reference-Q attribution for J4;
- cross-Node STRONG fail-closed protection;
- Safety unknown audit reason separation (`safety_unresolved`);
- corrected Repeat Structure classification;
- exact adaptive_daily `{1..6}` session-completeness validation;
- retrospective current-policy replay with fail-closed history coverage;
- symmetric profile percentage display and maintenance consistency;
- Supporter wrong/unknown separation;
- current-cycle confident-wrong detail display;
- Supporter scope labels;
- one-click `PHASE11_PROMOTION_EVIDENCE_V1` export;
- Repair Supply Phase2 priorities exported in the same evidence bundle.

There are no known open implementation defects currently blocking Phase11 promotion.

## Production Review v0.1

Decision: **HOLD / continue Shadow-only.**

Observed evidence bundle before Repair Supply Phase2 batch1:

- Baseline target: 小児学
- Shadow target: 動作分析学
- Shadow reason: `confident_wrong_cluster`
- comparison: `different_target_shadow_has_stronger_evidence`
- Shadow profile consistency: true
- unexplained recent adaptive repeat: 0
- adaptive metadata inconsistency: 0
- retrospective anchors: 2 / eligible 2 / excluded 0
- Phase11 Critical Safety miss: 0
- J2/J3 trigger mismatch: 0
- states: unseen 1176 / checking 198 / repairing 131 / repaired 4 / recheck_due 0 / stable 0
- repairability: 131 repairing, STRONG available 3, weak-only 6, blocked 122, repairable rate 2.3%

Interpretation:

- current J2 selection is supported by real cross-question confident-wrong evidence;
- corrected repeat diagnostics show no known red flag in classifiable recent adaptive repeats;
- retrospective coverage is complete for the two available anchors and both favored Shadow evidence;
- promotion is still premature because J4 retention behavior has not yet been naturally observed, replay variety is very small, and repair-confirmation supply was severely constrained.

## Repair Supply Phase2

The low 2.3% STRONG-supply rate is treated as an evidence-plumbing bottleneck, not as a reason to change Phase11 ranking weights.

### Batch1 — COMPLETE

Q1606-Q1610 are merged on main after manual medical/content review.

They target the five Priority A Safety-moderate repairing Nodes from the Production bundle:

- KN0194: Q1606, STRONG vs Q195 and Q1599
- KN0676: Q1607, STRONG vs Q684 and Q1602
- KN0025: Q1608, STRONG vs Q25 and Q1596
- KN0329: Q1609, STRONG vs Q331 and Q1600
- KN0697: Q1610, STRONG vs Q705 and Q1603

All ten source/new formal checks are `different_question_strong`. Existing Q1-Q1605 canonical content was preserved.

The five new questions should add up to five actionable STRONG candidates **if those Nodes remain repairing and the new questions remain eligible/unseen in Production**. Re-measure from a fresh Production evidence bundle rather than treating +5 as a guaranteed live rate.

Manual review record:

`docs/repair-supply-phase2-batch1-medical-review-v01.md`

## Gates that remain genuinely open

### 1. Natural J4 retention evidence

Current Production snapshot had:

- `recheck_due=0`
- `stable=0`

Do not promote until naturally occurring `repaired -> recheck_due` cases are observed and the engine gives them appropriate priority without starving stronger Safety evidence.

### 2. More symmetric retrospective / prospective variety

Only two eligible replay anchors existed and both were Shadow-stronger disagreements.

Need additional natural samples including, when they occur:

- same-target agreement;
- Current/Baseline stronger evidence;
- inconclusive comparison;
- Critical Safety snapshots;
- J4/recheck snapshots.

Absence of these cases is not a failure, but two same-direction anchors are insufficient promotion evidence.

### 3. Repair-supply effectiveness in real use

Formal STRONG availability must translate into useful learning behavior, not merely more `repaired` labels.

Observe:

- whether new alternates are selected when appropriate;
- confidence distribution on those alternates;
- `repairing -> repaired` transitions;
- later `repaired -> recheck_due -> stable` retention;
- signs that an item is too easy, ambiguous or memorization-prone.

### 4. Continue repeat/safety surveillance

Promotion remains blocked by any true:

- Phase11 Critical Safety miss;
- unexplained recent adaptive repeat;
- J2/J3 formal-trigger mismatch;
- systematic single-ordinary-wrong takeover;
- conflict where Phase11 intent and Phase10 exact selection work against each other.

## Current development priority

While natural-use evidence accumulates:

1. re-measure Repair Supply after Q1606-Q1610 are live;
2. manually review Priority B `review_existing_weak_pair` candidates before creating more questions;
3. build the next small Repair Supply batch only where existing content cannot supply independent STRONG evidence;
4. keep batches small and medically reviewed;
5. do not change Phase11 ranking weights merely to make promotion metrics look better.

## Promotion rule

Do not promote Phase11 because of one favorable screenshot, one disagreement, one newly repaired Node or one improved static repairability percentage.

Promotion requires prospective evidence that the Shadow policy is no worse than Baseline on Safety and clearly useful across repair, coverage, uncertainty and retention conditions.
