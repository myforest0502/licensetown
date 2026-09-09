# LicenseTown Current State

Last updated: 2026-09-09
Active safe branch: `work/pt-finalization-post-q2000`

## Purpose

This file is the durable source of truth for **what is working, what is not finished, known problems/risks, the intended target state, and the next concrete work**.

On every new LicenseTown development/chat session:
1. read `AGENTS.md`;
2. read this file;
3. verify only facts affected by newer changes;
4. continue from the open work instead of rediscovering the repository.

Whenever implementation status, validation evidence, design decisions, production behavior, data contracts, risks, or next work change, update this file in the same development cycle.

Distinguish these states explicitly:
- code exists;
- tests pass;
- real data observed;
- production/product behavior accepted.

---

# 1. Question Bank / Q2000

## Status: CLOSED for final-quality audit on the safe post-Q2000 branch

## Done / working now
- Formal PT Question Bank: **Q1-Q2000 / 2000 questions**.
- Bank version: **`2026-09-b20`**.
- Normal learning uses stored Question Bank data; it does not generate each ordinary question through OpenAI.
- Q-number remains immutable historical identity.
- Questions, answers, explanations, tags, Knowledge Nodes and related contracts are structured data.
- Q2000 final cross-sectional audit has been completed with automatic audit plus targeted human/medical sampling.

### Duplicate audit disposition
- 33 normalized same-stem groups were initially detected.
- After refining identity to `normalized stem + ordered choices`, the result was:
  - **29 legitimate same-stem / different-choice MHLW items**;
  - **4 exact official provenance-repeat groups**.
- The four exact official repeats are:
  - Q972 / Q1354
  - Q1067 / Q1391
  - Q1230 / Q1526
  - Q1411 / Q1585
- These official records are preserved, not rewritten or deleted.
- They are registered in `data/question_bank/question_equivalence_groups.json` as one **derived learning-evidence identity** per group.
- Equivalent Q IDs cannot:
  - count as independent cross-question weakness evidence;
  - become STRONG different-question repair confirmation;
  - bypass Recent Question Cooldown merely by switching to the equivalent raw Q ID.
- Raw Q IDs, provenance and persisted learner attempts remain unchanged.

### Cross-Node exact repeat
- Q1411/Q1585 are identical official content but historically had different raw Knowledge Nodes.
- Derived learning evidence is reconciled under **KN1387** without rewriting Production history.
- Primary learner impact check at review time:
  - Q1585 had 4 attempts, all correct;
  - the other seven exact-repeat Q IDs had no recorded attempts.

### Near-duplicate / editorial sampling
- 72 near-duplicate candidates (`>=0.90` normalized similarity in the same category) were audit targets, not automatic failures.
- Highest-risk samples were inspected with stem, options, answers, tags and explanations.
- Sampled high-similarity pairs were either legitimate official variants, opposite/related findings, different body regions, different facts, or different learning demands.
- No evidence justified bulk rewriting official past-exam items.
- 14 short-stem candidates were reviewed as ordinary national-exam fact prompts with sufficient options/explanations.
- 3 short global-explanation candidates were reviewed; each had informative option-by-option rationales, so summary length alone was not a quality defect.

### Knowledge Node label audit
- KN0597 / KN0807 (`交感神経の作用`) were already formally canonicalized by reviewed `KNC0001`: KN0807 -> KN0597. This is not an unresolved duplicate Node.
- KN1142 / KN1252 (`筋と作用の組合せ`) test different concepts (facial/masticatory vs lower-limb muscle actions). **Do not merge.** Their generic labels may be refined later for learner-facing clarity.

### Final integration / CI
- Review PR #277 was promoted out of draft only after green CI and merged **only into `work/pt-finalization-post-q2000`**.
- Safe-branch merge commit: **`8792e5f542d726286f5420085d7964f648500548`**.
- Latest pre-merge head: `9691404dee87026e7f928d3c6641957685e34809`.
- Latest full CI on that head: **SUCCESS**.
- Full suite evidence immediately before merge: **1208 passed, 6 skipped, 1 deselected, 125 subtests passed**.
- Diagnostic PR #276 was closed **without merge** after evidence capture.
- No `main`, Render, LINE or Production Neon mutation was part of this Q2000 audit closure.

## Remaining non-blocking improvement
- Knowledge Node labels can still be improved for learner-facing clarity where technically correct labels are too generic.
- Future medical/editorial issues discovered through real use remain eligible for normal correction; “audit closed” does not mean the bank can never change.

## Target state
- Preserve official provenance while preventing duplicate evidence from inflating learning-state confidence.
- Keep medical validity and learning value above cosmetic uniqueness.
- Any future bank change must rerun affected validator / Node / repair / selector tests and regression checks.

---

# 2. Formal data authority / learning evidence

## Done / working now
- `question_attempts` is the authoritative durable attempt history for formal learner-state derivation.
- Knowledge Node state is formally derived from attempt history with pure logic; `user_node_state` is not formal truth.
- Formal path is:
  `question_attempts -> derived Node state -> field/strategy/readiness -> selector/presentation`.
- Unknown/unanswered-like evidence is distinguished from evaluable answers.
- Primary learner snapshot measured on 2026-09-09:
  - **1525 attempts**
  - **1103 correct (72.3%)**
  - **740 unique questions**
  - **572 unique raw Knowledge Nodes**

## Known risk
- Reading legacy/supporting persisted state alone can produce false conclusions about repair/retention.

## Target state
- One explicit authority chain; any persisted derived state must be treated only as cache/supporting data unless formally promoted.

---

# 3. Repair / retention

## Done / working now
- Same-question, weak different-question and STRONG different-question evidence are separated.
- A confident (`confidence=1`) STRONG different-question correct answer after wrong evidence can move a Node to `repaired`.
- Later wrong evidence can regress it to `repairing`.
- Retention states include `repaired`, `recheck_due`, `stable`.
- Natural real use has exercised STRONG repair supply.
- 2026-09-06 natural use included 35 STRONG different-question repairing attempts, 26 correct, including 13 confidence-1 formal-confirmation candidates.
- Confirmed natural example: KN0394 using Q399 / Q1572.
- Q399 repair reference: 2026-09-02 18:32:30 JST.
- First 7-day recheck boundary: 2026-09-09 18:32:30 JST.

## Not finished yet
- Natural evidence for the full cycle
  `wrong -> STRONG repair -> spacing -> recheck_due -> stable/repairing`
  is still insufficient.
- Repair durability after spacing remains **OPEN**.

## Rule
- Do not manufacture special learner activity just to close the retention gate.

---

# 4. Phase11 learning-strategy judgment engine

## Current rollout state: HOLD / Shadow-only

The engine exists and is substantially implemented. The remaining issue is evidence for promotion, not a known blocking code defect.

## Strategy responsibilities already implemented
Phase11 can distinguish major intents including:
- Safety repair
- confident-wrong repair
- repeated/cross-question wrong repair
- ongoing repairing
- retention recheck
- uncertain correct/checking
- coverage expansion
- maintenance

Phase11 decides **what/why/how many/intent**. Phase10/selector owns the exact Q numbers.

## Automatic promotion gates — current evidence
- Repeat audit: **PASS**
  - adaptive spaced repeat 293
  - justified cooldown bypass 12
  - non-adaptive repeat 237
  - audit metadata unavailable 252
  - adaptive unexplained repeat **0**
  - metadata inconsistent **0**
- Critical Safety retrospective: **PASS-to-date**
- J2/J3 formal trigger consistency: **PASS**
- Current profile consistency: **PASS**
- Retrospective replay coverage: **PASS** for 9 recommendation-plan anchors
  - missing attempts 0
  - question-ID mismatch 0
- Retention: **OPEN**
- recheck intent -> exact-Q alignment: **OPEN** because no natural persisted `recheck_due` selection existed at review time
- retrospective comparison diversity: **OPEN**
- currently identified automatic BLOCKED/FAIL gates: **none**

## Manual/product promotion criteria
- architecture/ownership boundaries: **PASS**
- Phase10 adaptive dependency: **PASS**
- ordinary single-wrong overreaction: **PASS-to-date / monitor**
- sparse-coverage conservatism: **PASS-to-date / monitor**
- repair mechanics / STRONG supply: **PASS-to-date**
- repair durability after spacing: **OPEN**
- prospective recommendation relevance vs Baseline: **OPEN**
- symmetric disagreement breadth: **OPEN**
- final human learner-facing promotion review: **OPEN by design**

One prospective 2026-09-02 disagreement favored the Baseline field (神経医学) over the Shadow field (心理学) for immediate learner-perceived priority, while the Shadow field was still rated important. This is useful mixed evidence and is not sufficient to tune or promote either policy.

## Promotion rule
- Automatic diagnostics never self-promote Phase11.
- Do not convert OPEN into PASS using manufactured data.
- First learner-facing promotion, if approved later, should be a limited feature-flagged pilot rather than a full replacement.

## Next re-evaluation trigger
Re-run Phase11 evidence when natural data supplies:
- first qualified `recheck_due` execution/outcome;
- exact-Q alignment evidence for that recheck;
- additional retrospective comparison direction;
- additional ordinary learner-relevance evidence.

---

# 5. Adaptive selector / Recent Question Cooldown

## Done / working now
- Adaptive selection works at Knowledge Node level.
- STRONG different-question repair supply can be preferred.
- Recent Question Cooldown avoids recent repeats when adequate non-recent supply exists, with limited Safety exceptions.
- Adaptive audit metadata persists selection reason/group/score, repair evidence quality, repeat and bypass flags.
- Current real data contains no unexplained or internally inconsistent adaptive-repeat defect.
- Exact official provenance repeats are now collapsed to one evidence identity for cooldown/selection interpretation on the safe post-Q2000 branch.

## Not finished yet
- Continue natural validation under Q2000 supply.
- recheck-specific intent/selection compatibility still waits for natural `recheck_due` evidence.

---

# 6. Dashboard / learner navigation

## Done / working now
- A formal real-data dashboard/shadow implementation exists.
- It can compute Node coverage, mastery/state, field progress, weakness priorities, strategy intent, Safety/repair/recheck/coverage signals and learner navigation.
- `/goukaku-no-michi` already constructs learner navigation from formal inputs.
- Learner CTA carries field, count, learning intent and reason code.
- Formal pass-readiness is an evidence-gated status machine, **not a pass probability**.

## Not finished yet
- Legacy aggregates and formal derived metrics still coexist in parts of the UI/code path.
- Visible cards do not yet have one fully consolidated source-of-truth hierarchy.

## Known risk
- Mixing legacy and formal metrics can confuse both learner and developer and can create apparently conflicting progress numbers.

## Target state
- One coherent learner-facing dashboard driven by formal evidence.
- Clearly separate:
  - ordinary accuracy
  - coverage
  - repair/stability
  - readiness evidence
  - recommended next action
- No fake precision and no pass-guarantee wording.

## Next concrete work — ACTIVE
1. Map every visible dashboard card to its actual data source.
2. Classify each card as formal / legacy / mixed / demo.
3. Decide retain / replace / demote / remove.
4. Consolidate to one formal hierarchy without breaking current learner flow.

---

# 7. Weakness analysis / companion record

## Done / working now
- Formal active weakness derivation exists at Node and field level.
- Confident wrong, repeated wrong, active repairing, Safety and recheck signals are available.
- Learner/supporter summaries already cover substantial current-state information.

## Not finished yet
- A true longitudinal companion record is not yet a finished first-class product feature.

## Target state
Record the learning story, not only the current snapshot:
- important weakness episode
- evidence that triggered it
- what intervention/selection was tried
- whether repair was confirmed
- whether it remained repaired after spacing
- major strategy changes
- concise learner/supporter summary
- references back to raw evidence for auditability

## Next concrete work
- Design the minimum useful longitudinal schema after dashboard source consolidation.

---

# 8. Learning-time linkage

## Done / working now
- Learning time is persisted separately.
- Time-event keys may intentionally use suffixes such as `:time` for idempotency.

## Not finished yet
- There is no finalized explicit relational key tying a learning session/batch to all net learning-time events for higher-quality fatigue/time-efficiency analysis.

## Rule / priority
- Do not misuse raw event-key equality as a relational join.
- Defer session/time-link redesign until higher-value dashboard/companion work is complete.

---

# 9. Current priority order

1. **Formal-vs-legacy dashboard source map and consolidation** — active now.
2. Phase11 promotion-gate re-evaluation when new natural retention/recheck/comparison evidence appears.
3. Longitudinal weakness/companion-record design and implementation.
4. Lower-priority session/time linkage improvement.

Q2000 final-quality audit is closed on the safe post-Q2000 branch; do not restart it from zero unless new evidence reveals a genuine issue.

Practical effect for the learner and national-exam success take priority over architectural elegance.

---

# 10. Working rules

- Before proposing a change, check whether the capability already exists.
- Do not rediscover the whole system every session; start from `AGENTS.md` + this file and verify only affected facts.
- Distinguish **code exists / tests pass / real data observed / production behavior accepted**.
- Do not casually change `main`, Render, LINE or Production DB.
- Prefer small verified changes: hypothesis -> implementation -> real use -> result -> correction.
- If a change alters any fact here, update this file in the same development cycle.
