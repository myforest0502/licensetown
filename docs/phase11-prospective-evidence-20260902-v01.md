# Phase 11 Prospective Natural-Use Evidence — 2026-09-02

Status: **HOLD — remain Shadow-only.**

## 1. Natural-use volume

On 2026-09-02, the learner completed 90 questions in Production.

- attempts: 90
- correct: 75
- accuracy: 83.3%
- natural use spanned the day

This is sufficient to treat the day as a meaningful prospective natural-use sample.

## 2. Baseline vs Shadow prospective disagreement

At the relevant current snapshot:

- Baseline target: 神経医学
- Shadow target: 心理学
- Shadow intent: repair
- Shadow reason: confident_wrong_cluster
- Shadow confidence: high
- formal comparison: different_target_shadow_has_stronger_evidence

Learner feedback collected without disclosing which recommendation was Baseline or Shadow:

- next priority: **神経医学**
- reason: many different neurological diseases are easy to confuse, so the learner wants to strengthen discrimination among them
- 心理学 review need: 4/5
- 神経医学 review need: 5/5
- overall recommendation relevance: 4/5
- perceived repetition: 3/5
- desired content: more past-exam questions
- felt another field should have been studied instead: no
- difficulty: 3/5, appropriate
- willingness to let LicenseTown decide what to study: 5/5

Interpretation:

- Shadow correctly identified 心理学 as a real weakness/review need.
- However, for the learner's immediate priority ranking, **Baseline matched the learner better than Shadow in this prospective sample**.
- Therefore this case is not a prospective Shadow win.
- It is positive that the evaluation process captured a Baseline-favorable case rather than only Shadow-favorable evidence.

No ranking-weight change is justified from one prospective sample.

## 3. Post-Batch10 Production repairability confirmation

After PR #80 / Batch10 Q1651-Q1655 was merged and Production redeployed, a fresh `PHASE11_PROMOTION_EVIDENCE_V1` showed:

Before Batch10:

- repairing_nodes: 121
- strong_available: 32
- weak_only: 1
- blocked: 88
- repairable_rate: 26.4%
- repair_supply targets: 89

After Batch10:

- repairing_nodes: 121
- strong_available: 37
- weak_only: 1
- blocked: 83
- repairable_rate: 30.6%
- repair_supply targets: 84

The five Batch10 target Nodes disappeared from the top blocked repair-supply list, confirming that all five new STRONG alternates are recognized in Production.

Net structural effect:

- STRONG-available repairing Nodes: +5
- blocked repairing Nodes: -5
- repairable rate: +4.2 percentage points
- repair-supply targets: -5

## 4. Current promotion judgment

Remain Shadow-only.

Reasons:

- prospective evidence is now mixed rather than one-sided: this natural sample favors Baseline for immediate learner-perceived priority;
- retrospective replay still has only 2 eligible snapshots and both favor Shadow on formal evidence;
- naturally occurring recheck_due / J4 retention behavior is still not observed;
- no stable retention transition is yet available;
- the prospective sample supports continuing the comparison framework without changing weights prematurely.

## 5. Practical product feedback retained

Learner feedback worth carrying forward separately from Phase11 ranking:

- more past-exam questions are desired;
- current difficulty felt appropriate;
- the learner reported high willingness to delegate study selection to LicenseTown.

These are product/selection-quality signals, not direct proof that Shadow should be promoted.

## 6. Decision

**Phase 11 learner-facing promotion remains HOLD.**

Do not alter J1-J7 ranking weights from this sample alone. Continue natural use and collect additional prospective Baseline-vs-Shadow disagreements, especially cases with naturally available recheck_due or Safety-bearing evidence.
