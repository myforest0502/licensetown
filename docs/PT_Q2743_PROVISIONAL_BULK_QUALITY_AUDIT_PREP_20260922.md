# PT Q2234-Q2743 provisional_bulk quality audit prep — 2026-09-22

## Scope and safety

This is a read-only structural/editorial-prep audit of the 510 questions added in the
2026-09-b22 minimum-100 field expansion. It does not change runtime behavior,
Production DB, selector policy, Phase11, Render configuration, or LINE behavior.

The purpose is to distinguish two separate claims:

1. **Supply-floor claim** — all 18 PT fields now have at least 100 formal questions.
2. **Editorial-depth claim** — the added questions are independently strong national-exam
   learning items.

The first claim is supported. The second is **not assumed** because the batch is explicitly
tagged `provisional_bulk`.

## Formal supply result

Q2234-Q2743 contains 510 questions.

| Field ID | Added |
|---|---:|
| 3 | 71 |
| 4 | 59 |
| 5 | 90 |
| 6 | 21 |
| 7 | 8 |
| 10 | 53 |
| 11 | 39 |
| 12 | 77 |
| 13 | 7 |
| 14 | 85 |

The dedicated regression test confirms every formal field has at least 100 total questions.

## Structural checks observed

- 510/510 have parallel question, answer, explanation and tag records.
- 510/510 are marked source original and `tag_status=provisional_bulk`.
- Every question has five choices and exactly one accepted answer.
- Accepted-answer keys all exist in their corresponding choice map.
- All 510 stems are unique and do not exactly duplicate a pre-Q2234 stem.
- No new Knowledge Node is required by this expansion.

These are strong data-integrity properties. They do not by themselves prove editorial depth.

## Editorial-shape findings

### 1. Formulaic stem concentration

Observed stem-shape counts:

- inappropriate-reason format: **327**
- correct-reason format: **107**
- explicit support-reason format: **16**
- other formats: **60**

Also, **236 / 510** use the generic pattern equivalent to
「○○の判断について…」.

This is consistent with the documented rationale-discrimination authoring method.
It means the batch should be treated as a supply/repair layer rather than 510 fully
independent clinical scenarios.

### 2. Title repetition

There are **119 unique titles across 510 questions**.

Examples of repeated generic titles include:
- 心理学の判断・理由判断1: 43
- 人間発達学の判断・理由判断1: 43
- 精神医学の判断・理由判断1: 41
- 臨床心理学の判断・理由判断1: 40
- 教育学の判断・理由判断1: 30
- 教育学の判断・理由判断2: 30

Repeated titles are not a data-integrity defect, but they are evidence that the batch is
templated and should not be mistaken for full breadth expansion.

### 3. Knowledge Node concentration

The 510 questions map to **172 observed Knowledge Nodes**.

Some Nodes are reused heavily; observed high concentrations include:
- KN0547: 30
- KN1332: 30
- KN0554: 17
- KN0987: 17
- KN1027: 12
- KN1264: 12

This is expected from the authoring contract, but it means the new minimum-100 field count
does not imply equivalent Knowledge Node breadth.

### 4. Short accepted rationales

**98 / 510** accepted rationale choices contain 12 or fewer non-space characters.
Accepted-rationale text length distribution:
- min: 3
- p10: 10
- median: 21
- p90: 33
- max: 69

Shortness alone is not a medical error. It is a useful editorial-review signal because very
short answer rationales can collapse a "reason discrimination" item back into simple fact
recognition.

Example for manual review:
- Q2600 asks why P-Fスタディ is correct and includes the choice
  「P-Fスタディ。」. This is structurally valid but weak as an explanatory rationale.

## Interpretation

### Supported now

- The 60-answer field-assessment supply starvation problem is structurally resolved.
- Q2743 is a coherent formal bank boundary.
- The 510 questions can function as provisional rationale-discrimination supply.

### Not supported by this audit

- That every added item is equivalent to an independently authored national-exam question.
- That reaching 100 questions means every field has 100 distinct concepts/Nodes.
- That further uniform volume growth is currently useful.

## Recommended next use

Do **not** blanket-rewrite all 510 questions now.

Use real learner evidence to prioritize editorial replacement:
1. questions actually selected in normal learning;
2. questions associated with wrong -> repair failure or repeated uncertainty;
3. heavily reused Nodes where the learner is repeatedly exposed to near-same evidence;
4. short-rationale items that fail to teach "why";
5. fields where the September 27 diagnostic exam exposes a genuine knowledge gap.

Replacement should preserve the >=100 field supply floor and existing Q IDs unless a formal
data-migration decision is made separately.

## Current conclusion

The Q2743 expansion is a successful **supply-floor fix** and a deliberately provisional
**editorial-depth layer**. The next highest-value work is evidence-driven quality replacement,
repair/depth coverage, retention, and exam readiness — not another uniform question-count
increase.
