# Question Bank 2000 — Lot01 authoring contract v01

## Scope

This contract governs the first production-sized 48-question original lot after the successful 24-question calibration. It is staging-first. No formal Q IDs, Knowledge Node IDs for new concepts, DB writes, Render changes, LINE runtime changes, selector changes, or Phase11 changes are allowed during authoring.

Formal baseline: Q1-Q1761 / bank version `2026-09-b14`.

## Structural quota

- 48 accepted original drafts
- categories: C9=12, C16=10, C17=12, C18=14
- existing Node targets: 44
  - singleton second: 32
  - multi reinforcement: 12
- new Node concept slots: 4, one each in categories 9 / 16 / 17 / 18
- minimum strong different-demand formations: 41
- Safety moderate/critical total: exactly 12 for the lot budget

Task quota:

- assessment_selection 9
- device_selection 2
- fact_recall 1
- finding_interpretation 14
- functional_goal_decision 4
- intervention_selection 9
- prognosis_prediction 3
- safety_priority 6

Level quota:

- Level 1: 1
- Level 2: 16
- Level 3: 20
- Level 4: 11

## Existing-Node drafting rule

The target roster is `reports/question_bank_2000_lot01_targets_v01.json`.

For a singleton-second target, the new question must differ from the reference in `(task, primary_ability)` and in the actual reasoning demand. Renaming a disease, changing age/side, reversing the stem, or asking the same fact through a scenario is not enough.

For a multi-reinforcement target, the intended strong candidate must add a `(task, primary_ability)` demand not already present in that canonical Node. Weak multi Nodes are intentionally prioritized. A target may be replaced from the same category/slot inventory if a distinct medically sound demand cannot be produced.

Calibration Nodes containing Q1738-Q1761 are excluded from Lot01 so supply broadens rather than repeatedly strengthening the same concepts.

## New-Node drafting rule

The four new-Node slots reserve category capacity only. No new Knowledge Node ID exists in staging.

A new-Node draft must:

1. represent a PT-national-exam-relevant concept not adequately represented by an existing canonical Node;
2. be searched against formal stems and Node labels before acceptance;
3. include a proposed label and a concise reason why no existing Node is suitable;
4. remain `target_node_id = null` until formal integration;
5. receive a formal Node ID only in the atomic integration step after staging is green.

## Question quality

- five choices;
- single best answer by default;
- correct reason plus five choice explanations;
- Japanese stem <=300 characters unless clinically necessary, with a hard ceiling of 400 and an explicit exception note;
- no unnecessary information;
- clinical reasoning preferred over recall;
- do not create a fact-recall question merely to satisfy the one-question fact-recall quota if no meaningful concept fits;
- medical ambiguity is a rejection reason, not a reason to weaken the validator.

Safety questions should test clinically meaningful danger recognition, contraindication, stop criteria, escalation, or urgent response. Safety labels are not awarded merely because a patient is in a hospital setting.

## Evidence and semantic review

Every accepted draft requires:

- at least one HTTPS evidence source with a precise support note;
- a completed semantic review;
- reference demand;
- candidate demand;
- explanation of why they are genuinely different;
- related formal questions when a collision risk exists;
- reviewer and reviewed date;
- content seal after review.

Lexical similarity is only an escalation signal. Low textual similarity is not proof of semantic novelty.

## Duplicate gates

Check every candidate against:

- all Q1-Q1761 formal stems;
- all other Lot01 candidates;
- existing Node labels;
- related questions discovered during authoring.

Reject:

- exact normalized duplicates;
- cosmetic rewrites;
- same clinical decision with only demographics/side/disease substitution;
- inverse wording that tests the same association;
- answer choices that make the intended answer obvious by wording rather than knowledge.

## Quota reconciliation

Quotas are lot-level constraints, not per-category independent promises. A candidate replacement must preserve:

- category total;
- slot-type total;
- final task total;
- final level total;
- Safety total;
- minimum strong formation count.

If medical quality conflicts with a quota, replace another target or explicitly recalculate the remaining 233-question budget. Do not force a poor question to make the table add up.

## Staging acceptance gate

Before any Q ID allocation, final staging must prove:

1. accepted count 48 and unique draft IDs;
2. exact category/task/level/slot/Safety quota;
3. Q IDs not allocated;
4. all existing target Nodes still resolve to the reviewed canonical groups;
5. references exist in all four formal stores;
6. target membership/status has not changed since roster creation;
7. no calibration Node reuse;
8. all existing-Node accepted drafts have distinct metadata demand;
9. semantic review completed and sealed;
10. exact duplicate count zero;
11. near-similarity escalations explicitly reviewed;
12. new-Node candidates pass Node-label/concept collision review;
13. five choices, single-best answer, complete explanations;
14. evidence present;
15. minimum 41 strong formations are structurally possible from accepted metadata;
16. no formal/DB/Production/runtime writes.

## Formal integration gate

Only after staging passes:

- allocate the next contiguous Q IDs from the live manifest;
- allocate IDs for accepted new Nodes;
- update questions, answers, explanations, question_tags, Knowledge Nodes, manifest and schema atomically;
- do not alter canonical/relation data unless a separately reviewed new-Node canonical mapping is actually required;
- verify runtime strong classification for every intended existing-Node strong pair;
- run Question Bank validator, schema/manifest checker, Lot01 lifecycle validator, prior Batch regressions, full pytest, and `git diff --check`;
- merge only after final generated diff review and green Actions;
- verify the matching Render commit reaches `live`.

After formal merge, rerun `question_bank_2000_remaining_allocation_v01.py` against the new live bank and derive Lot02 from actual consumption rather than assuming the plan stayed unchanged.
