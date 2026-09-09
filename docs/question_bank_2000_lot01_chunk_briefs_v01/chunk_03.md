# Codex brief — Question Bank 2000 Lot01 / Chunk 03

This is **authoring chunk 3/6 only**. It is not an independently integrable batch. Formal baseline is Q1-Q1761.

## Edit exactly

`staging/question_bank_2000_lot01_chunks_v01/chunk_03.json`

Change top-level `status` to `completed_chunk` only when all eight drafts are genuinely complete.

## Mandatory repository context

Before authoring, read:

1. `docs/question-bank-2000-lot01-authoring-contract-v01.md`
2. `reports/question_bank_2000_lot01_validate.py`
3. each listed formal reference question, answer, explanation and tag
4. relevant formal-bank questions/Node labels found during semantic duplicate search

## Eight drafts

- `L01-C16-S06` | cat 16 | singleton_second | Node `KN0635` | refs Q643 | suggested `safety_priority/DECIDE` | level 4 | safety critical
  - target: Monteggia骨折は尺骨近位〜骨幹部骨折に橈骨頭脱臼を合併する損傷である
- `L01-C16-S07` | cat 16 | singleton_second | Node `KN0636` | refs Q644 | suggested `finding_interpretation/INTERPRET` | level 3 | safety none
  - target: 国家試験対策では腰椎を正答として覚える
- `L01-C16-M01` | cat 16 | multi_reinforcement | Node `KN0686` | refs Q694, Q1575 | suggested `finding_interpretation/INTERPRET` | level 3 | safety moderate
  - target: Malgaigne骨折は骨盤輪の垂直不安定性を伴う骨盤骨折である
- `L01-C16-M02` | cat 16 | multi_reinforcement | Node `KN0962` | refs Q972, Q1354 | suggested `safety_priority/DECIDE` | level 4 | safety critical
  - target: Galeazzi骨折とJefferson骨折の定義
- `L01-C17-S01` | cat 17 | singleton_second | Node `KN0493` | refs Q501 | suggested `assessment_selection/MEASURE` | level 2 | safety none
  - target: Daniels らの徒手筋力テストの特徴
- `L01-C17-S02` | cat 17 | singleton_second | Node `KN0631` | refs Q639 | suggested `assessment_selection/MEASURE` | level 2 | safety none
  - target: Daniels法の肘関節伸展MMTでは、段階5で肘をわずかに屈曲させた位置から伸展保持させ、前腕遠位へ屈曲方向の抵抗を加える
- `L01-C17-S03` | cat 17 | singleton_second | Node `KN0680` | refs Q688 | suggested `assessment_selection/MEASURE` | level 2 | safety none
  - target: T1が小指外転筋に対応する
- `L01-C17-S04` | cat 17 | singleton_second | Node `KN0774` | refs Q782 | suggested `assessment_selection/MEASURE` | level 2 | safety none
  - target: 日本整形外科学会・日本リハビリテーション医学会の参考可動域では股関節伸展15°が基準値である

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
