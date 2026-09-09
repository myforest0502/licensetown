# Q2000 final quality review — 2026-09-09

Scope: formal PT Question Bank `Q1-Q2000`, bank version `2026-09-b20`.

Status: **OPEN — count/structure is complete; final quality acceptance has been narrowed to four true duplicate-item dispositions plus editorial/Node review candidates.**

This record is based on read-only CI audits against `qb2000-finish` plus read-only Production attempt-history cross-checks. No Production DB write, Render change, LINE change, or `main` mutation was performed.

## CI evidence

Temporary draft PR #276 runs a read-only final-quality probe against `qb2000-finish`. It is diagnostic only and must not be merged.

### First pass — stem-only duplicate detector

Run `34309025255`:
- existing suite apart from the intentionally failing audit probe: **1198 passed, 6 skipped, 1 deselected, 125 subtests passed**
- question count: 2000
- bank version: `2026-09-b20`
- normalized same-stem groups: 33
- near-duplicate candidates (same category, normalized similarity >= 0.90): 72
- duplicate normalized Knowledge Node label candidates: 2
- editorial heuristics: stem-length candidates 14, explanation-length candidates 3

Review of the 33 groups showed that all are MHLW past-exam records from different exam years. A repeated generic exam stem is not, by itself, a duplicate learning item when the choices test different facts. Therefore the original stem-only blocker semantics were too coarse.

### Refined pass — item-level duplicate detector

Run `34309589005` refined duplicate identity to:

`same normalized stem + same normalized ordered choice set`

Result:
- same-stem groups: **33**
- same-stem but different-choice groups: **29** -> review-only, not blockers
- true exact duplicate item groups: **4** -> blockers pending explicit disposition
- existing suite apart from the intentionally failing audit probe: **1198 passed, 6 skipped, 1 deselected, 125 subtests passed**

The permanent audit implementation on `work/pt-finalization-post-q2000` was updated to the same item-level semantics in commit `2a4403d188ddd0ea82572abbb1bcfba79ebcacfd`.

## Four true exact duplicate official-item groups

All four are repeated MHLW official items from different exam years. They must not be mechanically rewritten merely to make text unique.

### 1. Q972 / Q1354
- identical stem and identical five choices
- identical official answer: `3・4`
- Q972: 第56回 午前86
- Q1354: 第59回 午後49
- same canonical learning Node: `KN0962`
- primary learner attempts: Q972=0, Q1354=0

### 2. Q1067 / Q1391
- identical stem and identical five choices
- identical official answer: `3`
- Q1067: 第57回 午前41
- Q1391: 第60回 午前27
- same Node: `KN1057`
- primary learner attempts: Q1067=0, Q1391=0

### 3. Q1230 / Q1526
- identical stem and identical five choices
- identical official answer: `4`
- Q1230: 第58回 午前91
- Q1526: 第61回 午後42
- same Node: `KN1215`
- primary learner attempts: Q1230=0, Q1526=0

### 4. Q1411 / Q1585
- identical stem and identical five choices
- identical official answer: `3・4`
- Q1411: 第60回 午前56
- Q1585: 第49回 午前68
- **currently assigned to different raw Nodes**:
  - Q1411 -> `KN1387`: 下垂体後葉からはオキシトシンとバソプレシンが放出される
  - Q1585 -> `KN0659`: バソプレシン（ADH）は視床下部で合成され、下垂体後葉から放出される
- primary learner attempts: Q1411=0, Q1585=4/4 correct

The fourth pair is the highest-priority semantic issue because identical evidence can currently be represented as two different Node concepts.

## Same-stem / different-choice groups

The other 29 groups are **not automatically duplicates**. They preserve distinct official exam items whose generic stems recur while the choice sets test different facts. Many of these Q IDs have already been used in the primary learner's real history, so preserving Q-number/provenance is especially important.

Examples with both/all members already attempted include:
- Q542 / Q1412 / Q1591: 7 attempts total
- Q605 / Q815: 10 attempts total
- Q617 / Q1225: 9 attempts total
- Q1153 / Q1263: 8 attempts total
- Q1261 / Q1358 / Q1535: 10 attempts total

These groups remain editorial/semantic review targets, not blocker-class duplicates.

## Duplicate Knowledge Node label candidates

Two normalized label collisions remain:

### KN0597 / KN0807 — `交感神経の作用`
Q605 and Q815 use the same generic stem with different choices and strongly overlapping concepts. This pair needs canonical/semantic review; simple label equality should not by itself decide the merge.

### KN1142 / KN1252 — `筋と作用の組合せ`
Q1155 tests facial/masticatory muscle actions while Q1268 tests lower-limb muscle actions. The identical label is too generic, but the concepts are not the same Node. Preferred disposition is more specific labeling, **not** an automatic merge.

## Learner-history preservation rule

Read-only Production inspection confirms that many repeated-stem Q IDs already have real attempt history. Therefore:

1. Q-number remains immutable historical identity.
2. Existing official past-exam records are not silently deleted or rewritten.
3. A provenance repeat must not be counted as independent learning evidence merely because it has a different Q number.
4. Any equivalence handling must preserve raw attempt history while canonicalizing only the evidence/selection interpretation.

## Duplicate/equivalence implementation target

The preferred design is to retain all official exam records and formally register the four exact official provenance-repeat groups as **question-equivalence groups**.

Required semantics:
- selector/cooldown treats equivalent Qs as the same evidence identity for recent/seen logic;
- weakness evidence does not count two equivalent Q IDs as cross-question confirmation;
- repair confirmation treats equivalent Q IDs as same-question evidence, never STRONG different-question evidence;
- exact duplicate records remain traceable to both official exam years;
- Q1411/Q1585 also requires Node-semantic reconciliation so identical content cannot independently influence two unrelated Node states.

This is preferable to rewriting an official MHLW item or inventing replacement wording under an official Q ID.

## Other review candidates

- near-duplicate candidates at >=0.90 similarity: 72
- stem-length heuristic candidates: 14
- explanation-length heuristic candidates: 3

These are sampling/review targets rather than automatic failures. Medical correctness and learning value decide disposition.

## Current completion judgment

`Q1-Q2000 / 2000` is a valid **count milestone**. The final bank is not yet accepted under the current completion contract because four true exact official-item repeats still need formal equivalence/Node disposition and the remaining review candidates need sampled closure.

Next concrete work:
1. formalize question-equivalence semantics for the four exact groups without changing Q identity;
2. resolve Q1411/Q1585 Node semantics and the two duplicate-label Node candidates;
3. inspect the highest-value near-duplicate/editorial candidates;
4. re-run Question Bank validator, Node/selector/repair tests, final quality audit, and full regression suite;
5. close temporary PR #276 after its evidence is fully captured; never merge it.
