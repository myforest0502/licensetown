# Codex brief — Question Bank 2000 Production Lot01

Do not redesign the plan. This task is **staging-only** and must be executed in **one 8-question chunk per Codex run** to minimize context and quota use.

## Read first

1. `docs/question-bank-2000-lot01-authoring-contract-v01.md`
2. `reports/question_bank_2000_lot01_chunk_validate.py`
3. `reports/question_bank_2000_formal_reference_packet.py`
4. `reports/question_bank_2000_similarity_audit.py`
5. the single requested chunk file under `staging/question_bank_2000_lot01_chunks_v01/`
6. formal question/answer/explanation/tag records only for that chunk's `reference_question_ids`

Formal baseline: Q1-Q1761. Do not load or rewrite unrelated large artifacts unless required by a validator.

## Current state

- Chunk01: completed and validated.
- Chunk02: completed and validated.
- Next: Chunk03, then Chunk04, Chunk05, Chunk06.
- Process **only the requested chunk in each run**.

## Per-run deliverable

For a requested `chunk_XX.json`:

1. Read its 8 targets and exact formal references.
2. Author exactly 8 medically sound PT national-exam-level questions.
3. For existing Nodes, create a genuinely different cognitive demand from every listed existing `(task, primary_ability)` pair; do not make cosmetic reversals or paraphrases.
4. Preserve lot quotas unless a medically necessary reassignment is made; any reassignment must still allow the final 48-question lot to satisfy the validator.
5. Use 5 choices and one best answer, with a correct explanation and an explanation for every choice.
6. Add trustworthy HTTPS evidence with a precise support note. Do not fabricate sources.
7. Complete semantic review honestly. AI review may be recorded, but `expert_signoff` must remain `false` unless a real human expert has approved it.
8. Set each completed draft `status` to `accepted` and the top-level chunk `status` to `completed_chunk` only after all 8 are complete.
9. Run the chunk validator for that exact chunk and require zero hard errors.
10. Run the formal-bank similarity audit against Q1-Q1761 and require exact duplicates 0 and hard-near hits 0; investigate any near hit rather than weakening thresholds.
11. Commit/push only that chunk plus strictly necessary tooling/test fixes to `analysis/qb2000-remaining-allocation-v01` / PR #268.
12. Keep PR #268 Draft. Do not merge.

## Hard prohibitions

- no formal Q ID allocation;
- no edits to formal Question Bank files;
- no Knowledge Node registry edits;
- no DB/Render/LINE/selector/Phase11 writes;
- no weakening/removing validators or tests to make content pass;
- no fabricated evidence or review claims;
- no editing another chunk in the same run;
- no merge.

## After all six chunks are complete

Only then:

1. run `python reports/question_bank_2000_lot01_chunks.py merge`;
2. inspect the merged 48-question staging file;
3. run `python reports/question_bank_2000_lot01_seal.py`;
4. run `python reports/question_bank_2000_lot01_validate.py` and require `hard_errors=[]`;
5. run Lot01/production tests, Question Bank validator, schema/manifest checker, full CI-equivalent pytest, and `git diff --check`;
6. report counts, strong-formation candidates, new-Node proposals, duplicate audit, evidence status, tests and commit SHA;
7. still do **not** merge or write formal data until the separate formal-integration step is explicitly started.
