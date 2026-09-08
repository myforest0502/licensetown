# Codex brief — Question Bank 2000 Lot01 / Chunk 05

This is **authoring chunk 5/6 only**. It is not an independently integrable batch. Formal baseline is Q1-Q1761.

## Edit exactly

`staging/question_bank_2000_lot01_chunks_v01/chunk_05.json`

Change top-level `status` to `completed_chunk` only when all eight drafts are genuinely complete.

## Mandatory repository context

Before authoring, read:

1. `docs/question-bank-2000-lot01-authoring-contract-v01.md`
2. `reports/question_bank_2000_lot01_validate.py`
3. each listed formal reference question, answer, explanation and tag
4. relevant formal-bank questions/Node labels found during semantic duplicate search

## Eight drafts

- `L01-C18-S02` | cat 18 | singleton_second | Node `KN0504` | refs Q512 | suggested `intervention_selection/PRESCRIBE` | level 3 | safety none
  - target: フレイルの説明の基本事項
- `L01-C18-S03` | cat 18 | singleton_second | Node `KN0506` | refs Q514 | suggested `intervention_selection/PRESCRIBE` | level 3 | safety none
  - target: 延髄には舌下神経核があり、舌の運動を担う舌下神経機能が障害されやすい
- `L01-C18-S04` | cat 18 | singleton_second | Node `KN0511` | refs Q519 | suggested `intervention_selection/PRESCRIBE` | level 3 | safety none
  - target: 鵞足は縫工筋、薄筋、半腱様筋の腱が脛骨近位内側に付着して形成される
- `L01-C18-S05` | cat 18 | singleton_second | Node `KN0569` | refs Q577 | suggested `functional_goal_decision/DECIDE` | level 3 | safety none
  - target: 重心が前方へ移り、足関節戦略で後方へ戻すため腓腹筋など足関節底屈筋が早期に活動する
- `L01-C18-S06` | cat 18 | singleton_second | Node `KN0570` | refs Q578 | suggested `intervention_selection/PRESCRIBE` | level 3 | safety none
  - target: 高強度運動で疲労が進むと解糖系への依存が高まり、乳酸と水素イオンが増加する
- `L01-C18-S07` | cat 18 | singleton_second | Node `KN0571` | refs Q579 | suggested `intervention_selection/PRESCRIBE` | level 3 | safety none
  - target: ムコ多糖類が皮下に蓄積する粘液水腫を生じ、圧迫しても圧痕を残しにくい非圧痕性浮腫となる
- `L01-C18-S08` | cat 18 | singleton_second | Node `KN0614` | refs Q622 | suggested `intervention_selection/PRESCRIBE` | level 3 | safety none
  - target: 老研式活動能力指標の手段的自立には公共交通機関の利用、買物、食事準備、金銭管理などが含まれる
- `L01-C18-S09` | cat 18 | singleton_second | Node `KN0630` | refs Q638 | suggested `intervention_selection/PRESCRIBE` | level 3 | safety none
  - target: SOAPは問題志向型診療記録で、Sは主観情報、Oは客観情報、Aは評価・解釈、Pは今後の計画を記載する

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
