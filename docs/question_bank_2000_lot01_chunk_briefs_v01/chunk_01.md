# Codex brief — Question Bank 2000 Lot01 / Chunk 01

This is **authoring chunk 1/6 only**. It is not an independently integrable batch. Formal baseline is Q1-Q1761.

## Edit exactly

`staging/question_bank_2000_lot01_chunks_v01/chunk_01.json`

Change top-level `status` to `completed_chunk` only when all eight drafts are genuinely complete.

## Mandatory repository context

Before authoring, read:

1. `docs/question-bank-2000-lot01-authoring-contract-v01.md`
2. `reports/question_bank_2000_lot01_validate.py`
3. each listed formal reference question, answer, explanation and tag
4. relevant formal-bank questions/Node labels found during semantic duplicate search

## Eight drafts

- `L01-C9-S01` | cat 9 | singleton_second | Node `KN0553` | refs Q561 | suggested `finding_interpretation/INTERPRET` | level 2 | safety moderate
  - target: 中心性脊髄損傷は高齢者の頸椎過伸展外傷などで生じやすく、脊髄中心部の障害により下肢より上肢の麻痺が強いことが特徴である
- `L01-C9-S02` | cat 9 | singleton_second | Node `KN0558` | refs Q566 | suggested `prognosis_prediction/PREDICT` | level 4 | safety moderate
  - target: 多発性硬化症は中枢神経の炎症性脱髄疾患で、若年成人女性に多く、時間的・空間的多発性を示して再発と寛解を繰り返すことが典型である
- `L01-C9-S03` | cat 9 | singleton_second | Node `KN0574` | refs Q582 | suggested `finding_interpretation/INTERPRET` | level 2 | safety moderate
  - target: 上位・下位運動ニューロン障害により四肢麻痺、舌萎縮、構音・嚥下障害が進行するが、眼球運動は比較的末期まで保たれやすい
- `L01-C9-S04` | cat 9 | singleton_second | Node `KN0613` | refs Q621 | suggested `safety_priority/DECIDE` | level 4 | safety critical
  - target: 脊髄損傷の自律神経過反射の典型所見
- `L01-C9-S05` | cat 9 | singleton_second | Node `KN0638` | refs Q646 | suggested `finding_interpretation/INTERPRET` | level 2 | safety moderate
  - target: NIHSSには意識水準・質問・命令など意識状態の評価が含まれる
- `L01-C9-S06` | cat 9 | singleton_second | Node `KN0687` | refs Q695 | suggested `finding_interpretation/INTERPRET` | level 2 | safety none
  - target: 動作緩慢、安静時振戦、自律神経症状として便秘、前駆症状としてREM睡眠行動障害などがみられる
- `L01-C9-S07` | cat 9 | singleton_second | Node `KN0781` | refs Q789 | suggested `finding_interpretation/INTERPRET` | level 4 | safety none
  - target: 筋萎縮、筋力低下、線維束性収縮、腱反射低下などがみられる
- `L01-C9-S08` | cat 9 | singleton_second | Node `KN0830` | refs Q839 | suggested `finding_interpretation/INTERPRET` | level 4 | safety moderate
  - target: てんかんは病因により特発性と症候性などに分類され、意識障害を伴わない発作もある

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
