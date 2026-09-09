# Codex brief — Question Bank 2000 Lot01 / Chunk 02

This is **authoring chunk 2/6 only**. It is not an independently integrable batch. Formal baseline is Q1-Q1761.

## Edit exactly

`staging/question_bank_2000_lot01_chunks_v01/chunk_02.json`

Change top-level `status` to `completed_chunk` only when all eight drafts are genuinely complete.

## Mandatory repository context

Before authoring, read:

1. `docs/question-bank-2000-lot01-authoring-contract-v01.md`
2. `reports/question_bank_2000_lot01_validate.py`
3. each listed formal reference question, answer, explanation and tag
4. relevant formal-bank questions/Node labels found during semantic duplicate search

## Eight drafts

- `L01-C9-M01` | cat 9 | multi_reinforcement | Node `KN0513` | refs Q521, Q1581 | suggested `finding_interpretation/INTERPRET` | level 3 | safety none
  - target: Parkinson病の主要徴候には安静時振戦、筋強剛、無動・寡動、姿勢反射障害があり、突進現象や歯車様固縮がみられる
- `L01-C9-M02` | cat 9 | multi_reinforcement | Node `KN0068` | refs Q68, Q191 | suggested `finding_interpretation/INTERPRET` | level 3 | safety none
  - target: 活動記録による疲労管理
- `L01-C9-M03` | cat 9 | multi_reinforcement | Node `KN0208` | refs Q209, Q279 | suggested `prognosis_prediction/PREDICT` | level 4 | safety none
  - target: 両側同時刺激で生じる消去現象の識別
- `L01-C16-S01` | cat 16 | singleton_second | Node `KN0556` | refs Q564 | suggested `finding_interpretation/INTERPRET` | level 3 | safety none
  - target: 上腕骨外側上顆炎の特徴
- `L01-C16-S02` | cat 16 | singleton_second | Node `KN0572` | refs Q580 | suggested `safety_priority/DECIDE` | level 4 | safety critical
  - target: 肘関節脱臼は転倒時に伸展位で手をつく機転などで生じ、尺骨・橈骨が上腕骨に対して後方へ脱臼する後方脱臼が最も多い
- `L01-C16-S03` | cat 16 | singleton_second | Node `KN0579` | refs Q587 | suggested `safety_priority/DECIDE` | level 4 | safety critical
  - target: 腰椎分離症は椎弓の関節突起間部に疲労骨折などによる分離が生じる病態である
- `L01-C16-S04` | cat 16 | singleton_second | Node `KN0616` | refs Q624 | suggested `safety_priority/DECIDE` | level 4 | safety critical
  - target: 上腕骨顆上骨折の基本事項
- `L01-C16-S05` | cat 16 | singleton_second | Node `KN0634` | refs Q642 | suggested `finding_interpretation/INTERPRET` | level 3 | safety none
  - target: Steinbrockerのclass分類は関節リウマチ患者の機能障害を、身の回り動作・職業活動・余暇活動の可否から4段階に分類する

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
