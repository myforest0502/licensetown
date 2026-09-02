# Repair Supply Phase 2 Execution Plan

Date: 2026-09-02
Status: READY FOR PRODUCTION TARGET CAPTURE / CONTENT BATCH NOT YET CREATED

## Goal

Increase the amount of **formal STRONG different-question repair confirmation** available to the learner where it has the highest current value, without weakening the meaning of `repairing -> repaired`.

Production Review v0.1 showed the mechanical bottleneck clearly:

- repairing Nodes: 131
- formal STRONG available: 3
- weak-only: 6
- formally blocked / same-question-only: 122
- repairable rate: 2.3%

This phase therefore targets **repair evidence supply**, not Phase 11 ranking weights.

## Source of truth for target selection

Use the Production Supporter `/supporter/pilot-diagnostics` `PHASE11_PROMOTION_EVIDENCE_V1` bundle after PR #51/main includes Repair Supply details.

The bundle exports:

- target Node count
- Priority A/B/C/D counts
- weak-pair review vs new strong-alternate counts
- ranked TOP supply candidates
- current repair-cycle wrong Q IDs
- all existing Q IDs for the Node
- weak candidate Q IDs
- unseen different-Q candidates
- Safety levels and current-cycle confident-wrong burden

Do not rank targets from stale static snapshots when current Production evidence is available.

## Priority order

### Priority A — Safety without usable STRONG supply

Order by:

1. critical
2. high
3. moderate
4. larger current-cycle wrong count
5. larger confident-wrong count
6. larger distinct-wrong-Q count

These are the first content targets because a Safety Node that can only repeat the same question cannot obtain strong independent repair confirmation.

### Priority B — non-Safety, confident-wrong count >= 2

These are high-value learner-specific weaknesses. Prefer Nodes where the current repair cycle already contains multiple evaluable wrong attempts or multiple distinct wrong questions.

### Priority C — non-Safety, confident-wrong count = 1

Work after A/B unless a content-authoring opportunity can cheaply upgrade an existing weak pair.

### Priority D — other repairing Nodes

Do not mass-produce D content merely to increase the repairable percentage. Treat as backlog unless later learner evidence raises them.

## Action choice

### `review_existing_weak_pair`

Before creating a new question, inspect the existing weak candidate pair.

Upgrade to a reviewed STRONG pair only if the two questions genuinely require **different retrieval / interpretation / decision demand** while confirming the same canonical knowledge Node.

Do not mark STRONG merely because wording, scenario, numbers, or option order differ.

### `create_strong_alternate`

Create one new question for the same canonical Node with a genuinely different demand from the learner's current-cycle wrong Q.

The formal requirement is necessary but not sufficient. The new item must also have enough discriminative quality to serve as meaningful repair evidence.

## Content quality gate

Every Phase 2 item must satisfy all of the following before merge:

1. same canonical Knowledge Node as the repair target
2. different question ID
3. formal `classify_repair_confirmation(source_wrong_q, new_q) == different_question_strong`
4. task and/or primary ability difference is real, not tag-only decoration
5. exactly one medically best answer unless explicitly documented as multiple-correct
6. distractors are clinically plausible for the tested decision
7. no answer can be obtained from obvious wording asymmetry alone
8. no trivial extreme/absurd distractor set that makes the answer obvious without repairing the target knowledge
9. no near-duplicate / paraphrase / number-swap of the source wrong question
10. explanation includes correct rationale and every wrong-option rationale
11. National Exam-level wording and LINE readability remain within the Question Bank rules
12. existing historical question/attempt evidence is preserved; do not rewrite an already-deployed source Q merely to improve repairability

## Lessons from Q1595-Q1605

The first Safety strong-repair pilot proved that structural STRONG supply can be added safely, but the manual audit found substantial variation in discriminative quality.

Therefore Phase 2 must explicitly separate:

- **formal strength**: same Node + genuinely different demand
- **educational strength**: a learner who has not repaired the knowledge should still be meaningfully challengeable by the item

A formal STRONG item with weak distractors is not a sufficient success criterion.

## Batch size

Default content batch: **5–10 Nodes maximum**.

Reason:

- small enough for manual medical/discrimination review
- large enough to materially improve current repair supply
- easy to compare validator/state/selector behavior before and after
- prevents a low-quality bulk content change from contaminating formal repair evidence

Priority A may be completed before Priority B even if the first batch is smaller than 5.

## Per-batch workflow

1. capture current Production Repair Supply TOP priorities
2. freeze target Node list and source/current-cycle wrong Q IDs
3. inspect all existing Qs for each target Node
4. choose `review_existing_weak_pair` or `create_strong_alternate`
5. write candidate item(s)
6. medical/content discrimination review
7. add Question Bank / answer / explanation / tag data using new immutable Q IDs
8. run formal STRONG classification against every relevant current-cycle wrong Q for the target Node
9. run focused repair/state/selector tests
10. run full pytest
11. run Q-bank validator
12. compare repairability before/after for the target Nodes
13. verify Recent Cooldown behavior is unchanged
14. merge only after the batch is fully green
15. observe natural learner use before expanding the next batch

## Acceptance metrics

A batch is mechanically successful if:

- validator remains PASS
- no existing Q IDs are mutated unexpectedly
- target new/reviewed pairs classify STRONG as intended
- no cross-Node STRONG is introduced
- target Nodes move from blocked/weak-only to STRONG_AVAILABLE where intended
- selector can use the new strong confirmation without violating cooldown

A batch is educationally promising only after natural use shows the questions are not trivially easy and repair transitions remain interpretable.

## Stop conditions

Stop the batch and review before merge if any of these occurs:

- keyed answer ambiguity
- weak/implausible distractors undermine confirmation value
- source/new question is effectively the same demand
- formal STRONG depends only on questionable tagging
- new item unexpectedly changes another canonical Node's repairability
- validator or full QA regression
- duplicate/near-duplicate content concern

## Next action

Capture the updated Production `PHASE11_PROMOTION_EVIDENCE_V1` after the Repair Supply bundle extension is deployed. Use `repair_supply` and `repair_supply_top_*` lines to freeze the first Phase 2 target batch.
