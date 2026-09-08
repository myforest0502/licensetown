# Question Bank 2000 — Batch 01 staging audit v01

Date: 2026-09-08

## Scope

Staging only. No Q IDs are reserved, no formal Question Bank JSON is changed, no Knowledge Node is created or rewritten, and no DB/Production/runtime write occurs.

Baseline: main after PR #262 (`6ebfcc7c32cccc307b239f1000a311d4a606c34b`).

## Calibration process

The first-pass 12 were deliberately checked against the current four formal stores and Knowledge Node registry before integration. That comparison found:

- B01-05 targeted KN0025, which is already `confirmed_shared` (Q25/Q1596/Q1608), so it was removed from the singleton-first calibration count.
- Six first-pass drafts were metadata-level same-demand repeats of their reference question. They were not accepted as STRONG candidates and were replaced with distinct singleton demands.
- Six first-pass category proposals were corrected from the current reference records through a correction overlay.
- Exact normalized stem duplication is checked by the read-only validator.
- A durable test requires each accepted draft to differ from its reference in task or primary ability.

The immutable first-pass files are retained for audit history; the effective accepted set is built by applying the category and semantic-replacement overlays.

## Effective accepted set — 12

1. B01-01 — KN0400 / Q406 — Guillain-Barré症候群：肺活量推移を解釈する（reference: assessment selection → new: finding interpretation）
2. B01-02 — KN0033 / Q33 — 鶏歩・下垂足からAFOを選択する
3. B01-03 — KN0103 / Q103 — 脳振盪後の高負荷時症状再燃を解釈する（reference: safety decision → new: finding interpretation）
4. B01-04 — KN0043 / Q43 — 肺動脈性肺高血圧症の運動時反応を解釈する（reference: monitoring decision → new: finding interpretation）
5. B01-06 — KN0026 / Q26 — 遅延する疲労から過用を判断し負荷を調整する
6. B01-07 — KN0024 / Q24 — 感覚低下と暗所不安定性を解釈する
7. B01-08 — KN0083 / Q83 — 特発性肺線維症の労作時低酸素血症を解釈する（reference: safety management → new: finding interpretation）
8. B01-09 — KN0032 / Q32 — PROM/AROM差と肩甲骨代償から次の介入を選択する
9. B01-10 — KN0102 / Q102 — 術後立位時の血圧変化から起立性低血圧を解釈する（reference: immediate action → new: finding interpretation）
10. B01-11 — KN0016 / Q16 — 神経性間欠性跛行の症状特性から運動様式を選択する
11. B01-12 — KN0027 / Q27 — 手根管症候群の所見から正中神経障害を局在する
12. B01-R1 — KN0010 / Q10 — 術後急性低酸素・頻脈・呼吸困難から肺血栓塞栓症を疑う（reference: immediate action → new: finding interpretation）

HOLD / audit-only:

- B01-05 / KN0025 — already multi-question; not counted in this singleton-first lot.
- First-pass versions of B01-01, B01-03, B01-04, B01-08, B01-10, B01-R1 — retained only as audit history after exact comparison showed same-demand risk.

## Effective category corrections

Current formal reference records established these first-pass corrections:

- B01-02: C-15
- B01-07: C-15
- original B01-08: C-18 (later semantically replaced by KN0083 / C-17)
- B01-09: C-13
- original B01-10: C-13 (later semantically replaced by KN0102 / C-18)
- B01-11: C-15

The six semantic replacements use the exact current category of their new reference Q.

## Quality gates

Passed at staging level:

- accepted count = 12 and all draft IDs unique;
- all 12 effective targets are unique singleton Nodes;
- all reference Q IDs exist in questions/answers/explanations/question_tags;
- each reference tag points to the target Node;
- effective category matches the current reference question;
- KN0779 is excluded;
- no Q number is preallocated;
- no new Node is proposed in Batch 01;
- no exact normalized stem duplicate exists against the current bank;
- each accepted draft differs from its reference in task or primary ability, preventing the six identified same-demand first-pass repeats from being silently accepted.

## CI evidence

After applying the semantic-replacement overlay and converting the temporary candidate probe into a stable singleton guard, GitHub Actions run #386 completed successfully on branch head `caf600cd23960ecbb04b07b8b741aa098544c509`.

The full suite's `Run test suite` step passed. Earlier red runs were intentional diagnostic gates used to expose category mismatches and same-demand first-pass drafts; those findings were corrected rather than bypassed.

## Remaining boundary before formal-bank integration

This PR remains staging-only. Formal integration is a separate controlled change and must:

- allocate Q IDs only at integration time;
- update questions, answers, explanations and question_tags together;
- update the relevant Knowledge Node question_ids/status and repair evidence consistently;
- revise the manifest/schema/range contract beyond Q1737 in the same controlled change;
- run full validator/test coverage and duplicate checks;
- keep Production DB/runtime unchanged until the bank-level diff is green.

Batch 01 is therefore ready for the next engineering step: build the formal integration mechanism from this effective 12-item staging set, without user-side review or Production write.
