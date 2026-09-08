# Codex brief — Question Bank 2000 Production Lot01

Do not restate or redesign the plan. Read and obey the repository artifacts below, then author the Lot01 staging set.

## Read first

1. `docs/question-bank-2000-lot01-authoring-contract-v01.md`
2. `staging/question_bank_2000_lot01_authoring_seed_v01.json`
3. `reports/question_bank_2000_lot01_targets_v01.json`
4. `reports/question_bank_2000_lot01_assignment_v01.json`
5. `reports/question_bank_2000_lot01_validate.py`
6. `reports/question_bank_2000_lot01_seal.py`
7. `tests/test_question_bank_2000_production_plan.py`
8. `tests/test_question_bank_2000_lot01_validator.py`

Formal baseline is Q1-Q1761. This task is **staging-only**.

## Deliverable

Create exactly:

`staging/question_bank_2000_lot01_v01.json`

Start from the authoring seed, not the blank template. The seed already contains quota-exact suggested task/primary ability/level/Safety values for all 48 slots. They are **structural suggestions, not medical approval**. Fill medically sound PT national-exam-level content, evidence, semantic reviews, and new-Node collision reviews. If a suggested assignment is medically poor, change assignments across drafts while preserving the exact final lot quotas enforced by the validator.

## Hard prohibitions

- no formal Q ID allocation;
- no edits to formal Question Bank files;
- no Knowledge Node registry edits;
- no DB/Render/LINE/selector/Phase11 writes;
- no weakening/removing validator or tests to make content pass;
- no semantic-review fields invented without actually checking the formal references/collision risk;
- no citations/evidence fabricated;
- no merge.

## Required workflow

1. Read each target's formal reference question(s), answer/explanation/tag and Node label.
2. Draft distinct-demand questions. For existing Nodes, do not repeat any existing `(task, primary_ability)` demand.
3. For the four new-Node slots, search formal stems and Node labels before proposing a label; keep `target_node_id=null`.
4. Use trustworthy HTTPS medical sources and precise support notes.
5. Check all 48 against Q1-Q1761 and against each other for semantic/cosmetic duplication.
6. Complete semantic review fields honestly.
7. Change top-level status to `staging_only` and each completed draft to `accepted` only when the complete lot is ready for validation.
8. Run `python reports/question_bank_2000_lot01_seal.py` only after content/reviews are complete. The seal tool must not be used to approve unfinished content.
9. Run `python reports/question_bank_2000_lot01_validate.py` and require `hard_errors=[]`.
10. Run the relevant Lot01/production tests, Question Bank validator, schema/manifest checker, full CI-equivalent pytest, and `git diff --check`.
11. Commit/push to the existing branch `analysis/qb2000-remaining-allocation-v01` / PR #268. Keep PR Draft and do not merge.

## Final report

Report accepted 48, category/task/level/slot/Safety counts, strong-formation count, new-Node proposals, replacements/rejections, duplicate/semantic audit, evidence status, test counts, commit SHA, Actions result, and confirm formal/DB/Production writes = 0.
