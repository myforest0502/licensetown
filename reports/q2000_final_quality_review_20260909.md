# Q2000 final quality review — 2026-09-09

Scope: formal PT Question Bank `Q1-Q2000`, bank version `2026-09-b20`.

Status: **NEAR-CLOSE — structural blockers are resolved on the review branch; remaining work is acceptance sampling/documentation and final regression evidence.**

No Production DB write, Render change, LINE change, or `main` mutation was performed.

## 1. Audit progression

The first read-only audit found:
- 2000 questions / bank version `2026-09-b20`
- 33 normalized same-stem groups
- 72 near-duplicate candidates at normalized similarity >= 0.90 within the same category
- 14 short-stem heuristic candidates
- 3 short-explanation heuristic candidates
- 2 duplicate raw Knowledge Node label groups

The original stem-only duplicate detector was too coarse because official MHLW exams reuse generic stems with different choice sets. The permanent audit was therefore refined so a true item-level duplicate requires:

`same normalized stem + same normalized ordered choices`

That reduced the real exact-item repeat set from 33 stem groups to four groups.

## 2. Four exact official provenance repeats — RESOLVED on review branch

All four groups are MHLW official items repeated in different exam years. They are preserved as immutable raw Q records but registered as one **derived learning-evidence identity**.

1. Q972 / Q1354 -> canonical evidence Q972 / `KN0962`
2. Q1067 / Q1391 -> canonical evidence Q1067 / `KN1057`
3. Q1230 / Q1526 -> canonical evidence Q1230 / `KN1215`
4. Q1411 / Q1585 -> canonical evidence Q1411 / `KN1387`

Formal master: `data/question_bank/question_equivalence_groups.json`.

Implemented semantics:
- equivalent Q IDs can never become STRONG different-question repair evidence;
- weakness evidence counts equivalent Q IDs as one question identity;
- Recent Cooldown / exclude / same-session selection applies to the whole equivalence group;
- raw Q IDs, official provenance, and Production attempt rows remain unchanged;
- Q1411/Q1585 are reconciled only in **derived learning evidence**, because identical content was historically assigned to different raw Nodes.

Primary learner impact check:
- Q972/Q1354/Q1067/Q1391/Q1230/Q1526/Q1411: no recorded attempts at review time;
- Q1585: 4 attempts, all correct;
- Q1585's historical raw Node `KN0659` also has Q667 attempts, but no raw history is rewritten.

This avoids treating a repeated official item as independent understanding evidence while preserving historical identity.

## 3. Same-stem / different-choice groups — REVIEWED AS NON-BLOCKERS

The other 29 same-stem groups have materially different choice sets and are legitimate distinct official exam records. They must not be deleted merely because the exam stem is reused.

Examples include recurring generic stems for SIAS, GMFM, ASIA, sympathetic actions, endocrine physiology, anatomy and pathology. Their distinct options test different facts.

Disposition: **retain raw questions; review-only, not duplicate blockers.**

## 4. Near-duplicate sampling — no bulk rewrite justified

The highest-similarity non-exact sample was reviewed with stems, choices, answers, tags and explanations.

### Highly similar but acceptably distinct
- Q1306 / Q855 — same AFO concept and same Node; very similar official questions. Retain. Same task/ability means they are not promoted to independent STRONG repair evidence merely from wording difference.
- Q1575 / Q694 — same fracture-name knowledge and same Node; near-redundant official questions. Retain as provenance-distinct records.
- Q949 / Q734 — same template but eye-muscle vs lower-limb nerve knowledge; clearly different content.
- Q688 / Q1098 — both ASIA key muscles, but one is factual mapping while the other is broader assessment selection; different learning demand.
- Q517/Q936 vs Q1192 — inner-foot lift vs outer-foot lift prosthetic alignment; opposite findings/causes, not duplicates.
- Q1540 / Q891 — male reproductive system, but different facts and answer structures.
- Q553 / Q611 — hip vs shoulder muscle action; template similarity only.
- Q1489 / Q1392 — different basal-metabolism facts.
- Q750 / Q616 — different disease/pathology combinations.

Disposition: **similarity >=0.90 remains a sampling trigger, not an automatic rewrite rule.** Current high-risk sample does not support bulk rewriting official items.

## 5. Editorial heuristics — sampled and accepted

### 14 short stems
Examples such as `血液凝固因子はどれか。`, `発達評価はどれか。`, `錐体路徴候はどれか。`, `排便中枢はどれか。` are short because they are ordinary national-exam fact prompts. The options and explanations provide sufficient specificity.

Q2000 itself (`排便中枢はどれか。`) has a substantive explanation identifying S2-S4 and the pelvic-nerve parasympathetic pathway.

Disposition: **short stem alone is not a quality defect.**

### 3 short global explanations
- Q1434: 加齢で骨塩量は低下する。
- Q1532: 三叉神経は橋外側から出る。
- Q1576: 腸骨筋は大腿神経支配である。

Each also has useful option-by-option rationale covering the distractors. Therefore the short summary explanation alone is not a blocker.

Disposition: **accepted under the current explanation contract because option rationales are present and informative.**

## 6. Duplicate Knowledge Node label review

### KN0597 / KN0807 — `交感神経の作用`
This was already formally resolved before the Q2000 audit:
- `KNC0001` is reviewed;
- `KN0807` aliases to canonical `KN0597` in `knowledge_node_canonical_map.json`.

Q605/Q815 are overlapping sympathetic-action fact questions; Q1960 extends the canonical concept into critical safety judgment. The raw duplicate labels are therefore **already one formal canonical Node**, not an unresolved duplicate.

The audit has been corrected to report same-label raw Nodes that already canonicalize to one Node as informational rather than unresolved candidates.

### KN1142 / KN1252 — `筋と作用の組合せ`
These are **not the same Node** despite identical generic labels:
- Q1155 tests facial/masticatory muscle actions (e.g. frontalis, temporalis);
- Q1268 tests lower-limb muscle actions (e.g. fibularis brevis, gracilis).

Disposition: **do not merge**. The label is overly generic and may be refined later for learner-facing clarity, but this is not evidence duplication and is not a structural blocker.

## 7. CI evidence on the question-equivalence review branch

Draft PR #277 targets `work/pt-finalization-post-q2000` and remains non-Production.

Confirmed green full-suite runs include:
- run `34310188257`: success
- run `34310333706`: success
- observed full-suite result: **1207 passed, 6 skipped, 1 deselected, 125 subtests passed**

The temporary diagnostic PR #276 intentionally contains failing probes and must never be interpreted as an application regression or merged.

## 8. Completion contract remaining

Before calling the Q2000 final-quality audit fully closed:
1. confirm the latest audit/Node-canonicalization changes remain green in PR #277;
2. record the final zero-blocker audit output;
3. update `docs/CURRENT_STATE.md` with the accepted dispositions and final CI evidence;
4. merge PR #277 only into the safe post-Q2000 working branch after green verification;
5. close diagnostic PR #276 without merge.

No `main`, Render, LINE, or Production DB promotion is part of this closure step.
