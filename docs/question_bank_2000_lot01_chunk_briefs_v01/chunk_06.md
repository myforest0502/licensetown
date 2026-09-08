# Codex brief — Question Bank 2000 Lot01 / Chunk 06

This is **authoring chunk 6/6 only**. It is not an independently integrable batch. Formal baseline is Q1-Q1761.

## Edit exactly

`staging/question_bank_2000_lot01_chunks_v01/chunk_06.json`

Change top-level `status` to `completed_chunk` only when all eight drafts are genuinely complete.

## Mandatory repository context

Before authoring, read:

1. `docs/question-bank-2000-lot01-authoring-contract-v01.md`
2. `reports/question_bank_2000_lot01_validate.py`
3. each listed formal reference question, answer, explanation and tag
4. relevant formal-bank questions/Node labels found during semantic duplicate search

## Eight drafts

- `L01-C18-M01` | cat 18 | multi_reinforcement | Node `KN0509` | refs Q517, Q936 | suggested `device_selection/PRESCRIBE` | level 2 | safety none
  - target: 静的立位で下腿義足の足部内側が床から浮き上がったから病態・機能障害を解釈
- `L01-C18-M02` | cat 18 | multi_reinforcement | Node `KN0576` | refs Q584, Q1588 | suggested `intervention_selection/PRESCRIBE` | level 3 | safety none
  - target: 水中運動療法の生理作用には水圧、浮力、粘性抵抗、熱伝導などが関与する
- `L01-C18-M03` | cat 18 | multi_reinforcement | Node `KN0643` | refs Q651, Q1573 | suggested `device_selection/PRESCRIBE` | level 2 | safety none
  - target: 大腿義足の異常歩行と原因の対応関係
- `L01-C18-M04` | cat 18 | multi_reinforcement | Node `KN0645` | refs Q653, Q1577 | suggested `functional_goal_decision/DECIDE` | level 3 | safety none
  - target: 腹圧性尿失禁に対する骨盤底筋群の筋力強化
- `L01-C9-N01` | cat 9 | new_node | Node `None` | refs - | suggested `finding_interpretation/INTERPRET` | level 2 | safety none
  - target: 
- `L01-C16-N01` | cat 16 | new_node | Node `None` | refs - | suggested `prognosis_prediction/PREDICT` | level 4 | safety none
  - target: 
- `L01-C17-N01` | cat 17 | new_node | Node `None` | refs - | suggested `fact_recall/KNOW` | level 1 | safety none
  - target: 
- `L01-C18-N01` | cat 18 | new_node | Node `None` | refs - | suggested `intervention_selection/PRESCRIBE` | level 3 | safety none
  - target: 

## Required for every draft

- medically sound PT national-exam-level stem and exactly five choices;
- single-best answer unless an explicit, validator-compatible exception is justified;
- concise correct-answer explanation and explanation for all five choices;
- clinical intent;
- trustworthy HTTPS medical evidence with support notes;
- semantic duplicate search against Q1-Q1761 and the other seven drafts;
- `semantic_review.why_not_same_demand`, related formal Q IDs, decision, reviewer/date and expert_signoff completed honestly;
- for existing Nodes, the actual semantic demand must differ from all listed existing `(task, primary_ability)` demands, not merely the metadata label.

Suggested task/level/Safety fields are starting points, not permission to force an implausible question. If one must change for medical quality, record the reason in the draft and leave final 48-question quota reconciliation for the full Lot01 merge stage.

## Hard prohibitions

- no formal Q IDs;
- no formal Question Bank edits;
- no Knowledge Node registry edits or new KN IDs;
- no DB/Render/LINE/selector/Phase11 writes;
- no validator/test weakening;
- no fabricated citations, duplicate checks or signoff;
- no merge to main.

## Before commit

Run a JSON parse check and inspect all eight drafts for blanks. Do **not** run the 48-question seal yet. Commit/push only this completed chunk plus any strictly necessary authoring notes. Keep PR #268 Draft.
