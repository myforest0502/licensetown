# Codex brief — Question Bank 2000 Lot01 / Chunk 04

This is **authoring chunk 4/6 only**. It is not an independently integrable batch. Formal baseline is Q1-Q1761.

## Edit exactly

`staging/question_bank_2000_lot01_chunks_v01/chunk_04.json`

Change top-level `status` to `completed_chunk` only when all eight drafts are genuinely complete.

## Mandatory repository context

Before authoring, read:

1. `docs/question-bank-2000-lot01-authoring-contract-v01.md`
2. `reports/question_bank_2000_lot01_validate.py`
3. each listed formal reference question, answer, explanation and tag
4. relevant formal-bank questions/Node labels found during semantic duplicate search

## Eight drafts

- `L01-C17-S05` | cat 17 | singleton_second | Node `KN0834` | refs Q843 | suggested `assessment_selection/MEASURE` | level 2 | safety none
  - target: 選択肢内容から本問の疾患はPerthes病を指すと判断する
- `L01-C17-S06` | cat 17 | singleton_second | Node `KN0840` | refs Q849 | suggested `assessment_selection/MEASURE` | level 2 | safety none
  - target: 棘果長は上前腸骨棘から内果までを測定する
- `L01-C17-S07` | cat 17 | singleton_second | Node `KN0843` | refs Q852 | suggested `assessment_selection/MEASURE` | level 2 | safety none
  - target: 、後脛骨筋の段階2は重力の影響を除いた条件で足部の内反・底屈方向の運動を評価する
- `L01-C17-S08` | cat 17 | singleton_second | Node `KN0844` | refs Q853 | suggested `assessment_selection/MEASURE` | level 2 | safety none
  - target: TUGは椅子座位から立ち上がり3m歩行し方向転換して戻り、再び背もたれに座るまでの時間を測る
- `L01-C17-M01` | cat 17 | multi_reinforcement | Node `KN0984` | refs Q994, Q1310 | suggested `functional_goal_decision/DECIDE` | level 3 | safety none
  - target: SF-36による健康関連QOLの8下位尺度評価
- `L01-C17-M02` | cat 17 | multi_reinforcement | Node `KN0003` | refs Q3, Q1565 | suggested `assessment_selection/MEASURE` | level 2 | safety none
  - target: 一側前庭機能低下の代償訓練
- `L01-C17-M03` | cat 17 | multi_reinforcement | Node `KN0323` | refs Q325, Q1584 | suggested `functional_goal_decision/DECIDE` | level 3 | safety none
  - target: 半月板損傷を確認するMcMurray系徒手検査の選択
- `L01-C18-S01` | cat 18 | singleton_second | Node `KN0501` | refs Q509 | suggested `finding_interpretation/INTERPRET` | level 3 | safety none
  - target: アンマスキングは、もともと存在していたが抑制されていた神経回路が、障害後に抑制解除されて機能を示す現象である

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
