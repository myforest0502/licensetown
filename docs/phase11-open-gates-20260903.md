# Phase 11 Current Open Gates — 2026-09-03

Status: **learner-facing promotion remains HOLD / Shadow-only.**

This document supersedes the 2026-09-02 short operational snapshot. It records the latest natural-use evidence and Repair Supply status without changing Phase11 ranking or learner-facing behavior.

## Latest Production evidence

Current Baseline/Shadow comparison:

- Baseline target: 神経医学
- Baseline reason: `insufficient_coverage`
- Shadow target: 心理学
- Shadow intent: `repair`
- Shadow reason: `confident_wrong_cluster`
- comparison: `different_target_shadow_has_stronger_evidence`
- Shadow profile consistency: true
- unexplained recent repeat: 0
- adaptive metadata inconsistency: 0
- saved adaptive set: 30 questions / 30 unique / recent repeats 0 / bypasses 0
- retrospective anchors: 2 eligible, both Shadow-stronger
- Phase11 Critical Safety miss: 0
- Baseline Critical Safety miss: 0
- J2/J3 trigger mismatch: 0

Node states:

- unseen: 1156
- checking: 213
- repairing: 121
- repaired: 19
- recheck_due: 0
- stable: 0

## Repair Supply status after Batch11

Production confirms that the Repair Supply mechanism is working as intended.

After Batch10:

- repairing Nodes: 121
- STRONG available: 37
- weak-only: 1
- blocked: 83
- repairable rate: 30.6%

After Batch11:

- repairing Nodes: 121
- STRONG available: 42
- weak-only: 1
- blocked: 78
- repairable rate: 34.7%
- repair-supply targets: 79
- create-strong-alternate targets: 78

The exact expected Batch11 delta was observed: five blocked Nodes became STRONG-repairable without changing the learner history. This validates the content-supply approach, but **does not by itself justify Phase11 promotion**.

## Prospective learner evidence currently available

One natural prospective Baseline-vs-Shadow disagreement has direct learner feedback.

For the 2026-09-02 case:

- Baseline recommended 神経医学.
- Shadow recommended 心理学.
- Learner selected 神経医学 as the next priority and rated the need as 5/5.
- 心理学 was still considered important at 4/5.
- Overall LicenseTown study usefulness was positive, difficulty was appropriate, and willingness to let LicenseTown choose study was 5/5.

Interpretation: this is a useful **Baseline-stronger prospective counterexample**. It is important because the retrospective sample currently contains only Shadow-stronger cases. One case is not enough to modify weights or promote either policy.

## Gates that remain genuinely open

### Gate 1 — Natural J4 retention

Still unobserved in Production:

- `recheck_due=0`
- `stable=0`

Promotion remains HOLD until naturally occurring repaired Nodes reach recheck timing and the system demonstrates sensible prioritization and outcomes. Artificially forcing timestamps solely to satisfy this gate is not promotion evidence.

### Gate 2 — Prospective disagreement sample size and direction diversity

Current useful evidence is directionally mixed but sparse:

- retrospective eligible anchors: 2 Shadow-stronger
- direct learner-rated prospective disagreements: 1 Baseline-stronger

Continue collecting natural disagreements only when Baseline and Shadow differ. Do not repeatedly questionnaire the learner on the same day or manufacture samples.

The promotion review should eventually contain multiple natural examples across:

- Shadow clearly better
- Baseline clearly better
- same-target agreement
- inconclusive/tie
- Safety-sensitive situations
- retention/recheck situations

No fixed sample count should override quality, but promotion should not be based on the present three directional observations alone.

### Gate 3 — Repair content effectiveness, not just supply

Repair Supply has materially improved formal availability. The next evidence question is whether those alternates improve learning.

Observe naturally:

- whether STRONG alternates are actually selected
- correctness and confidence on those alternates
- `repairing -> repaired`
- later `repaired -> recheck_due`
- `recheck_due -> stable` versus return to repairing
- ambiguity, cueing, or memorization effects

### Gate 4 — Continue safety/repeat/selector surveillance

Promotion is blocked by any meaningful recurrence of:

- Phase11 Critical Safety miss
- unexplained recent adaptive repeat
- metadata inconsistency affecting auditability
- J2/J3 formal-trigger mismatch
- systematic takeover from one ordinary wrong answer
- conflict where Phase11 intent and Phase10 exact-Q selector behavior work against each other

Current latest bundle shows none of these red flags.

## Repair Supply next action

The previous five-question experimental cadence is no longer necessary. Batch10 and Batch11 demonstrated predictable live effects.

The remaining create-strong-alternate pool has been audited as a whole:

- 78 target Nodes after excluding the one weak-pair review target
- 77 planned new questions because KN0549 and KN1401 share one consolidated concept/question
- planned range Q1661-Q1737
- implementation groups B12A (20), B12B (20), B12C (20), B12D (17)

This is an implementation-efficiency decision, not a Phase11 ranking change.

## Promotion decision

**HOLD / Shadow-only remains the correct decision.**

Reasons:

1. no natural J4 retention cases yet;
2. prospective Baseline-vs-Shadow learner evidence is still sparse;
3. Repair Supply effectiveness on later retention is not yet observed;
4. there is no current Safety/repeat defect forcing emergency policy change;
5. changing weights now would confound evaluation just as repairability is improving.

Continue natural evidence collection while finishing Repair Supply. Revisit learner-facing promotion only when retention evidence and additional prospective comparisons exist.