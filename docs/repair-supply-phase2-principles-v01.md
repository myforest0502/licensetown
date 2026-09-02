# Repair Supply Phase 2 — content principles v0.1

## Purpose

Increase the number of currently repairing Knowledge Nodes that have a genuinely useful `different_question_strong` confirmation question.

Production review on 2026-09-02 showed 131 repairing Nodes with only 3 formal STRONG candidates (2.3%). The first implementation batch should therefore optimize **usable repair evidence**, not raw question count.

## First-batch priority

Start with the five Priority A Safety-moderate Nodes from the Production Repair Supply bundle:

1. KN0194 — Q195 / Q1599 — 玄関上がり框への手すり
2. KN0676 — Q684 / Q1602 — 神経原性ショック
3. KN0025 — Q25 / Q1596 — 頸髄症の上肢巧緻・歩行障害とUMN徴候
4. KN0329 — Q331 / Q1600 — 前頸部熱傷瘢痕拘縮と頸部伸展位
5. KN0697 — Q705 / Q1603 — 重症COPDの運動強度設定

All five currently have both existing questions in the active wrong set, so a third independent question is the shortest path to actionable STRONG supply.

## Evidence-quality requirements

A new repair question must satisfy all of the following:

- Same canonical Knowledge Node as its source pair.
- Different question ID and materially different wording/scenario.
- Prefer a `(task, primary_ability)` demand pair different from **both** active wrong questions, not merely one of them.
- If demand diversity alone is not sufficient, use the reviewed strong-pair registry only after manual content review.
- Correct answer must require understanding of the Node, not recognition of copied wording.
- Distractors must be clinically plausible enough that confidence=1 has evidentiary value. Avoid absurd, obviously unsafe, irrelevant, or category-mismatched distractors.
- For Safety Nodes, do not make the correct option obvious solely because every distractor is dangerous.
- Preserve LINE readability: usually <=300 Japanese characters for the stem, <=400 only when clinically necessary.
- One best answer unless the content truly requires multiple accepted answers; no trick wording.
- Explanation must state why the correct option is correct and why every distractor is wrong.

## Immediate educational target

A correct confidence=1 response to the new question should be meaningful evidence that the learner can apply the same Knowledge Node under a **different demand/context** than the two questions already missed.

## Do not do

- Do not silently rewrite Q1–Q1605.
- Do not retire or reinterpret historical attempts in this batch.
- Do not change selector weights, Node-state transitions, Phase11 ranking, DB schema, or learner-facing recommendation policy.
- Do not count a structurally STRONG tag as educationally strong unless the item itself passes distractor/independence review.

## QA gate

Before merge:

1. Question Bank validator PASS with no gaps/duplicates/reference/schema errors.
2. New questions classify to the intended canonical Nodes.
3. Each new candidate is `different_question_strong` against both active wrong questions where possible; otherwise explicitly document which pair is reviewed and why.
4. Focused repair-evidence/state-transition tests PASS.
5. Full pytest PASS, allowing only the already-known unmanaged UTF fixture deselection if still applicable.
6. Manual medical/content review of all new items before main merge.
