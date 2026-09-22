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

## Editorial-shape findings after source-context rewrite

The original bulk-generation audit found substantial generic-stem concentration and, more
importantly, source-truth direction inversions. Those stem findings are now historical: all 510
question stems were reconstructed from their uniquely matched Q1-Q2000 source question and
source-choice truth status.

Current post-rewrite properties:

- all **510 / 510** stems retain explicit source-question context;
- all **510 / 510** source-choice truth directions are covered by a regression test;
- all **510 / 510** stems remain exact-text unique;
- the batch still maps to **172 observed Knowledge Nodes**, so question-count breadth is not the
  same thing as concept breadth;
- repeated source/Node derivations remain intentionally tagged `provisional_bulk`.

High-concentration Nodes still include:
- KN0547: 30
- KN1332: 30
- KN0554: 17
- KN0987: 17
- KN1027: 12
- KN1264: 12

### Residual short-rationale review signal

After the source-context rewrite, accepted-rationale length remains an editorial-depth flag:

- **79 / 510** accepted rationale choices have 12 or fewer non-space characters;
- **22 / 510** have 8 or fewer non-space characters.

Shortness alone is not a correctness failure because the source question is now carried into
the stem. It remains a review-priority signal for items where the accepted option merely names
the concept rather than explaining it.

Examples still worth later editorial enrichment include:
- Q2600: 「P-Fスタディ。」
- Q2622: 「反動形成。」
- Q2623: 「知性化。」
- Q2624: 「昇華。」

These items should not be auto-rewritten from generic heuristics. Their tags already contain
richer Knowledge Node descriptions, but changing the rationale set is a separate medical/editorial
change and should be reviewed deliberately rather than inferred mechanically.

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
