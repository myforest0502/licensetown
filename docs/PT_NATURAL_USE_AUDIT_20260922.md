# PT natural-use audit — 2026-09-22 JST

## Scope

READ-ONLY analysis of the primary PT learner's ordinary Production use on 2026-09-22 JST.
No Production DB write, selector change, Render change, Phase11 promotion, or learner-state
mutation was performed.

## Daily summary

- Attempts: **170**
- Unique questions: **170**
- Correct: **121 / 170 = 71.2%**
- First recorded answer: about **08:19 JST**
- Last recorded answer: about **19:59 JST**
- Recorded learning time events sum: **115.1 minutes**
- All attempts were `study` mode.
- Same-day duplicate Q: **0**
- `recent_question_repeat=true`: **0**
- `recent_cooldown_bypassed=true`: **0**

Confidence:
- confidence 1: 102 attempts, 84 correct = **82.4%**
- confidence 2: 65 attempts, 36 correct = **55.4%**
- confidence 3: 3 attempts, 1 correct = **33.3%**
- confidence-1 wrong: **18**

The confidence gradient remains educationally meaningful: accuracy drops as uncertainty rises.

## Critical finding: provisional_bulk exposure

Today's 170 attempts split as follows:

| Bank range | Attempts | Correct | Accuracy | Confidence-1 wrong |
|---|---:|---:|---:|---:|
| Pre-Q2234 formal items | 35 | 28 | 80.0% | 1 |
| Q2234-Q2743 `provisional_bulk` | 135 | 93 | 68.9% | 17 |

Therefore:
- **135 / 170 = 79.4%** of today's ordinary learning came from the provisional 510-question batch.
- **17 / 18** confidence-1 wrong answers came from that batch.

This does **not** prove that provisional items are medically wrong or inherently lower quality;
the item demands and sampled fields differ. It does prove that `provisional_bulk` is no
longer a low-impact future editorial concern. It is heavily exposed in ordinary learning and
directly shapes repair candidates.

## Field results

| Field | Attempts | Correct | Accuracy | Bulk attempts | Bulk accuracy | Conf-1 wrong |
|---|---:|---:|---:|---:|---:|---:|
| 解剖 | 3 | 1 | 33.3% | 0 | — | 1 |
| 生理 | 2 | 2 | 100.0% | 0 | — | 0 |
| 心理 | 24 | 12 | **50.0%** | 24 | 50.0% | **6** |
| 人間発達 | 17 | 13 | 76.5% | 17 | 76.5% | 1 |
| 教育 | 15 | 10 | 66.7% | 14 | 64.3% | 2 |
| 医学概論 | 7 | 5 | 71.4% | 6 | 66.7% | 0 |
| 病理 | 6 | 5 | 83.3% | 4 | 75.0% | 0 |
| 内科 | 9 | 7 | 77.8% | 0 | — | 0 |
| 精神 | 20 | 17 | 85.0% | 20 | 85.0% | 2 |
| 小児 | 20 | 16 | 80.0% | 15 | 80.0% | 0 |
| 臨床心理 | 20 | 15 | 75.0% | 20 | 75.0% | 2 |
| 基礎運動学 | 2 | 2 | 100.0% | 2 | 100.0% | 0 |
| 臨床運動学 | 13 | 6 | **46.2%** | 13 | 46.2% | **4** |
| 動作分析 | 4 | 2 | 50.0% | 0 | — | 0 |
| 運動器 | 1 | 1 | 100.0% | 0 | — | 0 |
| 理学療法評価各論 | 4 | 4 | 100.0% | 0 | — | 0 |
| 理学療法治療各論 | 3 | 3 | 100.0% | 0 | — | 0 |

Do not over-interpret very small denominators. The most actionable same-day signals are
psychology and clinical kinesiology because they combine meaningful exposure with multiple
confidence-1 wrong answers.

## Same-day Node clusters

High-value clusters from today's attempts:

- **KN1151 / 心理**: 4 attempts, **0 correct / 4 wrong**
- **KN0547 / 教育**: 5 attempts, 2 correct / **3 wrong**
- **KN0987 / 臨床運動学**: 4 attempts, 1 correct / **3 wrong**
- **KN0505 / 臨床心理**: 3 attempts, 1 correct / **2 wrong**
- **KN1551 / 臨床運動学**: 3 attempts, 1 correct / **2 wrong**
- **KN1469 / 心理**: 2 attempts, **0 correct / 2 wrong**

These are stronger repair signals than field accuracy alone.

## Selector / lifecycle evidence

Across all 170 question-result records:
- different-question STRONG repair evidence: **92**
- same-question repair evidence: **15**
- no repair-quality value: **48**
- recent repeats: **0**
- cooldown bypasses: **0**

Frequent selection reasons:
- `confident_wrong`: 51
- `uncertain_correct`: 37 total across authority variants
- `spaced_repeat_fallback`: 27
- `cross_question_wrong`: 16
- `repairing`: 12
- `safety_wrong`: 11 total across variants
- `recheck_due`: 9 total across variants

Observed lifecycle metadata continues to identify `depth_repair`.
Some early events used `strategy_fallback_reason=eligible_supply_insufficient` with
`safety_review`; later records also contain soft-pilot coverage authority. This should be
interpreted as audit evidence, not as proof of educational efficacy.

## Provisional-bulk editorial priority

The 510-item batch should not be blanket-deleted. Priority should be driven by actual exposure
and failure.

### Highest-priority natural-use review candidates

The first group is today's **confidence-1 wrong** provisional items, especially where the
stem/rationale is templated or the Node is heavily reused. Examples include:

- Q2395 / 教育 / KN1376 — short rationale: 「1980年代ではない。」
- Q2276 / 心理 / KN1469 — generic judgment stem
- Q2425 / 教育 / KN0547 — Node has 30 provisional items
- Q2687 / 臨床運動学 / KN0987 — Node has 17 provisional items
- Q2697 / 臨床運動学 / KN0987 — same high-concentration Node
- Q2698 / 臨床運動学 / KN1551 — Node has 11 provisional items
- Q2242 / 心理 / KN1085 — generic judgment stem
- Q2247 / 心理 / KN1469 — generic judgment stem
- Q2595 / 臨床心理 / KN0505 — generic judgment stem
- Q2249 / 心理 / KN1151 — part of today's 0/4 Node cluster
- Q2285 / 心理 / KN1470
- Q2341 / 人間発達 / KN0612
- Q2520 / 精神 / KN0563
- Q2631 / 臨床心理 / KN1205
- Q2507 / 精神 / KN1361 — short rationale

These are **review candidates**, not automatic medical FAILs.

## Seven-day context

Daily results from 2026-09-16 through 2026-09-22:

| Date | Attempts | Accuracy | Conf-1 wrong |
|---|---:|---:|---:|
| 9/16 | 100 | 71.0% | 5 |
| 9/17 | 190 | 75.8% | 12 |
| 9/18 | 80 | 57.5% | 1 |
| 9/19 | 190 | 68.4% | 9 |
| 9/20 | 371 | 60.9% | 25 |
| 9/21 | 200 | 70.5% | 12 |
| 9/22 | 170 | 71.2% | 18 |

Today's 71.2% is not an isolated collapse. The notable feature is the high count of
confidence-1 wrong answers and the dominance of newly added provisional questions.

## Decision

1. **Do not expand question count again simply for volume.**
2. **Promote Q2234-Q2743 editorial review from backlog to active quality work** because real
   learner exposure is already high.
3. Start review with today's confidence-1 wrong items and repeated-wrong Node clusters.
4. Preserve Q IDs and the >=100-per-field supply floor where possible; improve item content
   in place only after medical/editorial review and regression checks.
5. Continue natural-use monitoring for repeat behavior, repair success and whether revised
   items improve evidence quality.
