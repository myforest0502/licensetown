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

## Source-aware reconstruction finding

A stronger audit is possible because every Q2234-Q2743 item maps deterministically to exactly
one Q1-Q2000 source item: its five rationale choices are the five reviewed choice explanations
from that source.

Using the source question's polarity (for example, whether the source asks for the correct
choice or the incorrect choice) reveals **21 true direction inversions** in the live
provisional batch. These are stronger defects than short wording or templating because the
derived question asks the learner to justify the opposite truth status from the source item.

On 2026-09-22, **6 of those 21 inverted items were actually presented**:
Q2411, Q2265, Q2242, Q2482, Q2271 and Q2300. Q2242 produced a confidence-1 wrong answer.

A dedicated correction branch/PR reconstructs all 510 stems from their unique Q1-Q2000 source
context and source truth polarity instead of patching only the visibly obvious cases. It keeps
Q IDs, rationale choices, accepted answer keys, explanations, tags, Nodes and field supply
unchanged. This prevents contextless/inverted wording from manufacturing false weakness while
still leaving broader editorial-depth review as a separate task.

## Historical cross-check of today's suspect Nodes

Several confidence-1 wrong provisional items occurred on Nodes that had previously been
strong for this learner. This is important because it prevents us from automatically treating
every new wrong answer as a true knowledge regression.

Examples:

- **KN1469**: prior **9/9 correct**, today **0/2** on Q2247/Q2276.
- **KN1085**: prior **8/8 correct**, today 2/3; Q2242 is one of the mechanically confirmed
  stem-direction contradictions.
- **KN0747**: prior **11/11 correct**, today 0/1.
- **KN0505**: prior 2/2 correct, today 1/3.
- **KN0563**: prior 3/3 correct, today 1/2.
- **KN0612**: prior 3/3 correct, today 2/3.
- **KN1205**: prior 4/4 correct, today 1/2.
- **KN1546**: prior 2/2 correct, today 2/3.
- **KN1551**: prior 2/2 correct, today 1/3.

By contrast, some Nodes were already weak before today and remain credible repair targets:

- **KN1151**: prior 3/11 correct, today 0/4.
- **KN1361**: prior 0/4 correct, today 1/2.
- **KN0987**: prior 3/5 correct, today 1/4.
- **KN1376**: prior 5/8 correct, today 1/2.

Interpretation:
- prior-strong -> sudden provisional failure = **audit the item first**;
- prior-weak -> repeated failure across old and new items = stronger evidence of a **real learner repair need**;
- both can coexist, so the system must not let defective provisional items manufacture
  false weakness.

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

## Remediation outcome and formal interpretation

The source-context rewrite is now live for all Q2234-Q2743 items. The formal evidence boundary
for this wording version is `2026-09-22T13:48:28Z`.

For the primary learner:

- raw PT attempts in durable history: **4086**
- Q2234-Q2743 attempts made before the corrected wording became live: **135**
- post-rewrite attempts in Q2234-Q2743 at the time of this closeout: **0**
- unaffected formal attempts outside that rewritten range: **3951**

Therefore the 135 provisional attempts from the 2026-09-22 daytime session remain valid as
historical product-quality audit evidence, but they are **not current formal learning evidence**
for Knowledge Node state, field evidence, readiness or adaptive strategy.

This changes the interpretation of the same-day field/Node breakdown above: it is useful for
identifying product defects and review priorities, but should not be used to declare new learner
weakness caused by the old wording. Current formal learner evidence must be recomputed from the
3951 unaffected attempts plus any new post-rewrite attempts collected after the boundary.

The dashboard / learner-navigation formal attempt paths are also filtered at the same boundary,
while raw history is preserved for historical reporting and short-term repeat protection.

## Current-formal learner baseline after remediation

After applying the Q2234-Q2743 wording-version boundary, the primary learner's current formal
history contains **3951 attempts**, **2812 correct (71.2%)**, **2229 unique questions**, and
**1562 touched Knowledge Nodes**. The 135 superseded daytime Q2234-Q2743 attempts are excluded
from this baseline.

Current-formal field performance:

| Field | Attempts | Accuracy | Last-7d attempts | Last-7d accuracy | Conf-1 wrong |
|---|---:|---:|---:|---:|---:|
| 解剖 | 450 | 65.3% | 130 | 61.5% | 28 |
| 生理 | 450 | 75.1% | 77 | 75.3% | 29 |
| 心理 | 132 | 78.8% | 11 | 72.7% | 12 |
| 人間発達 | 69 | 73.9% | 22 | 63.6% | 6 |
| 教育 | 52 | 82.7% | 7 | 100.0% | 4 |
| 医学概論 | 122 | 73.0% | 37 | 64.9% | 5 |
| 病理 | 218 | 68.8% | 39 | 59.0% | 7 |
| 内科 | 343 | 67.1% | 73 | 61.6% | 17 |
| 神経 | 207 | 64.7% | 68 | 64.7% | 9 |
| 精神 | 75 | 62.7% | 22 | 50.0% | 3 |
| 小児 | 114 | 78.9% | 39 | 74.4% | 7 |
| 臨床心理 | 48 | 83.3% | 13 | 84.6% | 1 |
| 基礎運動学 | 259 | 74.5% | 56 | 75.0% | 19 |
| 臨床運動学 | 28 | 78.6% | 7 | 85.7% | 0 |
| 動作分析 | 296 | 75.7% | 81 | 71.6% | 11 |
| 運動器 | 175 | 69.7% | 62 | 72.6% | 14 |
| 理学療法評価各論 | 395 | 73.4% | 157 | 73.2% | 18 |
| 理学療法治療各論 | 518 | 67.8% | 265 | 62.6% | 30 |

These are descriptive measurements, not fixed weakness labels. The strongest current repair
signals are Node-level repeated errors on unaffected wording, especially:

- **KN1399** — 9 attempts / 4 correct / 5 confident-wrong:
  quiet-standing gravity-line position around the knee.
- **KN1151** — 11 / 3 correct / 3 confident-wrong:
  the five-stage disability-acceptance sequence.
- **KN0194** — 18 / 11 correct / 3 confident-wrong:
  handrail/support planning at an entrance step.
- **KN1186** — 10 / 4 correct / 3 confident-wrong:
  extrinsic muscles of the hand.
- **KN1263** — 9 / 3 correct / 3 confident-wrong:
  functional implications of preserved C6 spinal-cord level.
- **KN1281** — 10 / 7 correct / 3 confident-wrong:
  working-memory task interpretation.
- **KN0483** — 4 / 1 correct / 3 confident-wrong:
  corrected age for preterm infants.
- **KN0594** — 3 / 0 correct / 3 confident-wrong:
  centriole/centrosome involvement in cell division.
- **KN0530** — 7 / 1 correct / 2 confident-wrong:
  dual innervation of adductor magnus.
- **KN1256** — 9 / 3 correct / 2 confident-wrong:
  sagittal-plane gravity-line landmarks.

The current system should prioritize these through the normal formal selector/strategy path.
No manual hard-coded learner route is introduced from this audit.

## Formal-consumer closeout

The wording-version boundary is now applied to all known formal decision consumers:

- adaptive LINE selection and web recommendation inputs;
- Knowledge Node state / field evidence inputs;
- learner dashboard and learner-navigation attempts;
- dashboard field/unique-question question-result rows;
- pass-readiness service;
- pilot diagnostics and shadow-audit attempt histories;
- learner and supporter subject-detail field displays;
- supporter field accuracy / weak-field guidance.

Raw effort/history remains durable: answer counts, learning time, streaks, latest-learning history,
milestones and short-term repeat protection are not deleted or rewritten.

This is the intended separation:

**raw history = what the learner actually did**

**current formal evidence = what may influence current weakness, readiness, strategy and field
performance after the item wording changed**

## Post-remediation selection quality preference

The 510 reconstructed items remain `tag_status=provisional_bulk`. They are valid supply but are
not treated as editorially equivalent to reviewed items.

The adaptive selector now prefers reviewed items when both can serve the same learning need:

- exploration/checking/maintenance provisional candidates: **-250** priority;
- repair provisional candidates: **-80** priority;
- provisional items remain available when reviewed supply is insufficient;
- Safety, repair-evidence quality, repeat/cooldown, coverage and retention rules are unchanged.

This specifically addresses the natural-use finding that provisional items accounted for
135/170 daytime attempts without destroying the supply floor that motivated the Q2743 expansion.

## Decision

1. **Do not expand question count again simply for volume.**
2. **Promote Q2234-Q2743 editorial review from backlog to active quality work** because real
   learner exposure is already high.
3. Start review with today's confidence-1 wrong items and repeated-wrong Node clusters.
4. Preserve Q IDs and the >=100-per-field supply floor where possible; improve item content
   in place only after medical/editorial review and regression checks.
5. Continue natural-use monitoring for repeat behavior, repair success and whether revised
   items improve evidence quality.
