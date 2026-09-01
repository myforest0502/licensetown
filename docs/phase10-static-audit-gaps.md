# Phase 10 Static Audit Gaps

Date: 2026-09-01

## Purpose

Record static/offline QA items that can be advanced without Render or production DB writes, and define what must be refreshed before Phase 10 is formally closed.

## Current verified baseline

- Question Bank runtime/validator baseline: Q1-Q1594, 1594 questions.
- Canonical Knowledge Node architecture and repairability audit are already implemented.
- Recent Question Cooldown v0.2 is the current main behavior.
- Adaptive selection audit-lite is implemented on branch `feature/adaptive-selection-audit-lite-v01` at commit `9a0d4a0dbf3c087808040a7c2722862be4cc9c40`, not yet merged to main.

## Static artifact freshness gap

`data/question_bank/question_tags_audit.txt` is stale relative to the current Question Bank.

It reports:

- source through Q1564
- records: 1564

The current Question Bank is Q1-Q1594.

Therefore this file must not be used as the final Phase 10 distribution snapshot until it is regenerated against the 1594-question bank.

### Required refresh output

Regenerate the tag audit and confirm at minimum:

- records = 1594
- Q range = Q1-Q1594
- duplicates = 0
- missing = 0
- errors = 0
- task distribution
- primary ability distribution
- level distribution
- safety distribution
- source distribution if available

This is a static QA refresh only. It must not modify question content or tags merely to make the distribution look balanced.

## Canonical Node / repairability baseline

The existing formal repairability audit classifies canonical Nodes without changing state transitions.

Important design rule:

- strong different-question evidence may formally repair
- weak/same-question evidence does not formally repair
- relation candidates remain diagnostic-only
- written confirmation remains non-formal

This rule remains the Phase 10 baseline unless a later validated experiment explicitly replaces it.

## Node relations baseline

`knowledge_node_relations.json` currently contains reviewed prerequisite candidates plus a transfer candidate.

These relations are useful for diagnosis and future Phase 11 judgment, but must not silently become repair evidence.

Phase 11 may consume them as contextual signals such as:

- suspected prerequisite weakness
- downstream transfer opportunity
- explanation for why a question was recommended

but should initially remain shadow/read-only.

## Merge/canonical artifacts

`knowledge_node_canonical_map.json` is the formal alias-to-canonical mapping artifact.

Historical candidate files are evidence/review artifacts, not the runtime source of truth. Future audits should distinguish:

- runtime canonical mapping
- historical merge candidates
- relation candidates

so old candidate counts are not mistaken for current unresolved work.

## Phase 10 close conditions

Phase 10 should not be called complete until all of the following are true:

1. Adaptive selection audit-lite is merged and verified.
2. The 1594-question tag audit is regenerated.
3. Recent Cooldown behavior has a real-use observation after deployment.
4. No unexpected high overlap appears in consecutive adaptive sessions except documented Safety/bank-shortage fallback.
5. Selection audit metadata can explain any repeated Q that does occur.
6. Repair/checking/exploration soft composition remains subordinate to cooldown, not vice versa.
7. No Node-state or question-attempt regression is observed.

## What not to optimize yet

Do not tune distributions merely because a histogram looks uneven.

Question counts, task types, difficulty, and safety levels should reflect educational need and source material. Optimization should be driven by observed learning behavior, coverage holes, or measurable recommendation failure.

## Phase 11 handoff implication

Phase 11 should begin as a judgment layer over existing evidence rather than a new answer engine.

Inputs should include, where available:

- formal Node state
- recent correctness/confidence
- selection reason/group/score
- repair evidence quality
- recent cooldown/bypass facts
- field progress
- learning source
- latest recommendation plan/progress
- diagnostic prerequisite/transfer relations

Outputs should initially be shadow-only recommendations with an explanation and confidence, never automatic state mutation.
