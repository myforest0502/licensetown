# Q2000 final quality review — 2026-09-09

Scope: formal PT Question Bank `Q1-Q2000`, bank version `2026-09-b20`.

Status: **OPEN — count/structure is complete, final quality acceptance is not yet complete.**

This record is based on a read-only CI audit against `qb2000-finish`. No Production DB, Render, LINE, or `main` mutation was performed.

## CI evidence

Temporary draft PR #276 runs a read-only final-quality probe against `qb2000-finish`.

First audit run:
- workflow: `tests`
- run id: `34309025255`
- existing suite outcome apart from the intentional audit failure: **1198 passed, 6 skipped, 1 deselected, 125 subtests passed**
- audit result: **1 blocker class**
- blocker class: `exact_duplicate_stems`
- question count: 2000
- bank version: `2026-09-b20`
- near-duplicate candidates (same category, normalized similarity >= 0.90): 72
- duplicate normalized Knowledge Node label candidates: 2
- editorial heuristics: stem-length candidates 14, explanation-length candidates 3

The audit test intentionally fails while blocker findings remain. This is not an unrelated application regression.

## Exact duplicate stem groups — blocker disposition required

33 normalized exact-stem groups were found:

1. Q511 / Q892
2. Q517 / Q936
3. Q542 / Q1412 / Q1591
4. Q550 / Q1424
5. Q557 / Q1036
6. Q605 / Q815
7. Q608 / Q1027
8. Q613 / Q1073
9. Q617 / Q1225
10. Q621 / Q1165
11. Q648 / Q929 / Q1523
12. Q725 / Q1228
13. Q744 / Q1086
14. Q749 / Q1367
15. Q756 / Q1042
16. Q803 / Q1389
17. Q925 / Q1578
18. Q947 / Q955
19. Q972 / Q1354
20. Q1065 / Q1248
21. Q1067 / Q1391
22. Q1091 / Q1544
23. Q1123 / Q1301
24. Q1153 / Q1263
25. Q1155 / Q1268
26. Q1230 / Q1526
27. Q1246 / Q1593
28. Q1261 / Q1358 / Q1535
29. Q1274 / Q1324
30. Q1316 / Q1480
31. Q1317 / Q1420
32. Q1330 / Q1499
33. Q1411 / Q1585

These are not to be bulk-deleted or mechanically rewritten. Each group must be reviewed for provenance, choices/answer, learning demand, Knowledge Node role, existing learner history, and repair-pair dependencies.

## Other review candidates

The audit found 72 normalized near-duplicate pairs/groups at >=0.90 similarity within the same category. Exact duplicates account for part of this set; the remaining high-similarity candidates are editorial review targets, not automatic failures.

Two normalized Knowledge Node labels are duplicated and need semantic review:
- KN0597 / KN0807
- KN1142 / KN1252

## Disposition policy

For every exact duplicate group:
1. Preserve Q-number stability and existing learner history.
2. Identify source/provenance before changing wording.
3. Do not rewrite an official past-exam item merely to make text unique.
4. If a newer LT-original/repair-supply question duplicates an older item, prefer redesigning the LT-original question into a medically valid materially different demand while preserving its intended Node role.
5. Before changing a question used in STRONG repair confirmation, re-check Knowledge Node and strong-pair semantics.
6. Medical correctness and learning value take priority over cosmetic uniqueness.
7. After each accepted repair batch, re-run the bank validator, Node/selector checks, duplicate audit, and full regression suite.

## Current completion judgment

`Q1-Q2000 / 2000` is a valid **count milestone**, but the PT Question Bank must not yet be called final under the current acceptance contract because exact duplicate-stem dispositions remain OPEN.

Next action: inspect the 33 groups individually, establish repeatable dispositions, repair only genuine redundancy, and re-run the full audit until blocker count is zero.
