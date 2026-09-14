# Stage F natural-history shadow audit — 2026-09-14

**Stage F: HOLD. Production connection: NOT YET.**
Audit base: `f153e3f388e3dd787eac9a4ea76600c968c70f55` (#346).
This PR adds only offline audit tooling, tests and documentation.
No Production caller, DB write, schema change, manual deploy or authority promotion.

## Source and reproducibility

Reverified Neon project `sparkling-frost-71060602` (licensetown), default
`production / br-raspy-pond-azxss69f`. Only SELECT statements were issued.
The PT learner with the most question_attempts was selected inside a SQL subquery;
no learner identifier was returned. The anonymous export stays outside Git.
It contains 2545 attempts, 1470 distinct questions, 1086 raw Nodes, accuracy
73.2417%, from 2026-08-17 12:00 UTC to 2026-09-13 23:50 UTC.
Unknown answers: 13. No paid API/LLM was called.

The export schema is documented by `normalize()`: numeric id/event_number,
question_id, knowledge_node_id, timestamp with offset, attempt_position,
selected_answers, confidence, is_correct; optional whitelisted selection_group.
event_number is dense_rank of event_key, preserving its relative lexical order.
Export question_attempts with qualification_id='pt'; internally identify the
largest learner using GROUP BY user_id ORDER BY count(*) DESC,user_id LIMIT 1.
Export selected_answers from question_attempts; optional group comes from matching
learning_events.question_results by event key and attempt_position.
No complete event JSON or personal fields belong in an export.

```sh
DATABASE_URL= PYTHONPATH=. python -B scripts/audit_learning_strategy_shadow.py /private/anonymous.json --output /private/result.json
```

The committed companion JSON contains only aggregate observations and final
field rows, never attempt-level history or learner identifiers. Replaying the
same private input against this base reproduces those aggregates.
The command does not connect to a database. Its private field-evidence loader
supplies an inert DB adapter in that module's own builtins; it does not replace
sys.modules, the environment, or any Production module. The actual existing
field-evidence calculation is executed unchanged.

Truth path: attempts -> existing derived Node transitions / weakness evidence ->
existing field evidence -> field progress -> Stage B/D/E. Q-to-field mapping
comes from the formal repository bank, not hand-written SQL CASE.
Unknown-answer semantics match the current PT dashboard read bundle.

## Checkpoint and comparison method

Every 30 answers, advancing to the end of timestamp ties and deduplicating cuts,
plus the final prefix: **85 checkpoints**. Sorting matches formal attempted time,
event order and position. No partial atomic timestamp group is treated as complete.
83 checkpoints have a full observed next 30 answers; the last two have 25 and 0
and are excluded from agreement denominators. Each shadow input contains only
the prefix. This is an event-time retrospective replay; historical DB insertion
times and past versions of the bank/selector are not reconstructed.

Top1 = shadow first field equals the actual next-30 modal field.
Top3 = that actual modal field is within the shadow ranking's first three fields.
Tied actual modes resolve by field ID; all tied modes and full next-field counts
are retained in JSON. Recommendations need not agree with current behavior.

- Top1: **12/83 = 14.5%**.
- Top3: **23/83 = 27.7%**.
- Recommended field distribution: 生理学 25; 病理学 7; 内科学 17; 神経医学 10; 理学療法治療各論 26.
- Intent distribution: coverage 26; repair 0; retention 0; attainment 0; maintenance 0; safety_review 59; strategy_change 0; defer 0.
- All 85 recommendations have relative Exam Weight >=1; low-weight weak
  recommendations: 0. Thus low-weight mild weakness did not dominate this sample.
- Specifically: treatment 26, physiology 25, internal medicine 17, anatomy 0,
  PT evaluation 0. High weight does not guarantee allocation when Safety ranks higher.
- Coverage intent: 26/85. Safety intent: 59/85. Maintenance/retention are present
  in lower-ranked final rows but never become the top recommendation.
- This is descriptive association, not a weight-ablation experiment or evidence
  that shadow would increase coverage, accuracy or passing probability.

## Supply and repeat safety

All **85/85 (100%)** recommended fields supply at least 30 distinct eligible
exact-evidence identities. No cooldown relaxation or cross-field fill was used.
Minimum supply: 34.
JSON records static raw supply, after raw 72h, after exact equivalence plus formal
Node-state eligibility, and after the selector's recent-30 cooldown.
The same existing blocked_short_term_evidence_ids helper is used. Exact duplicates
count once. The field filter uses the selector's canonical evidence-field mapping.
This is field-level feasible supply, not a constructed session or a guarantee of
30 intent-specific Safety/strong-repair questions. Selector ratios were not changed.

Observed natural history after #337 merge (2026-09-12 04:35:45 UTC):
**535 attempts; same-Q <72h 0; exact-evidence <72h 0; cross-Q exact repeats 0**.
The entire older history contains 658 short-term same-Q/evidence repeats; these
predate the fix and are not concealed or attributed to this audit.
Initial-assessment-specific post-merge acceptance is not expanded by this replay.

## Context, Safety and concentration

Critical unresolved Nodes are reconstructed with the existing selector's
_node_attempt_summary and _priority using formal critical tags and derived states.
Resolved/stable/due behavior follows the current selector. Counts are unique
within each field; cross-field memberships are not unique learner totals.
Critical-context availability is confirmed from the complete PT prefix, not
assumed from absent evidence. Safety priority contradictions: **0/85**.
This tests priority consistency, not clinical correctness of the underlying tags.

Previous progress and stable ratio use the preceding observed checkpoint.
Elapsed field-study time uses the last observed field answer. They are unavailable
before an applicable observation. Individual exam timing is unavailable.
The exact study-block boundaries and completed Stage D/E additional blocks cannot
be recovered from pre-adoption history: additional_blocks_completed and
consecutive_field_blocks are omitted, never invented from lifetime answer count.
Stage D/E internally defaults these omitted numeric values to zero; the audit
explicitly flags them unavailable and therefore does **not** accept its resulting
concentration behavior as demonstrated safe.

Maximum consecutive recommendations: **26 observations**, exceeding three.
These are repeated recommendations on actual-history prefixes, not 26 shadow
blocks completed by a learner. Concentration prevention remains unproven.
Safety may retain priority even where concentration would otherwise reduce it.
No synthetic future states or counterfactual learning gains are created.

## 60-answer gate and small supply

Final categories (overlapping limitations):
- evaluation sufficient under this audit: **11/18**.
- answer floor below60: **5/18** (4,5,10,12,14).
- node spread shortfall: **0/18**.
- bank supply below60: **7/18** (3,4,5,10,11,12,14).

**New policy conflict:** Stage B/D/E returns raw weak for psychology (119 answers,
29 bank questions) and pediatrics (72 answers,58 bank questions). This meets its
existing answer/spread rule but conflicts with this Stage F instruction that a
bank below60 must not be called weak/strong. Audit-facing field_state therefore
stays assessing for small supply; raw_shadow_field_state is preserved separately.
The runtime implementation and ranking were not patched to hide this result.

## Final 18-field snapshot

Coverage, progress, accuracy and targets are fractions. P/S/R = target progress,
stable ratio and resolved ratio. Full precision, required spread, limitations,
raw states and all reason codes also appear in the companion JSON.

| ID / field | answers / accuracy | nodes touched/total / coverage | progress | audit state (raw) / recovery | weight | targets P/S/R | maintenance | priority / intent / rank |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 解剖学 | 304 / 0.671 | 114/140 / 0.814 | 0.202 | weak (weak) / not_recovered | 2.242 | 0.738/0.538/0.738 | true | 0.449 / retention / 9 |
| 2 生理学 | 369 / 0.748 | 143/154 / 0.929 | 0.229 | weak (weak) / not_recovered | 2.487 | 0.743/0.543/0.743 | true | 1.432 / safety_review / 2 |
| 3 心理学 | 119 / 0.790 | 15/15 / 1.000 | 0.333 | assessing (weak) / not_recovered | 0.245 | 0.639/0.439/0.639 | true | 0.197 / retention / 18 |
| 4 人間発達学 | 42 / 0.786 | 18/28 / 0.643 | 0.214 | assessing (assessing) / not_recovered | 0.360 | 0.653/0.453/0.653 | true | 0.254 / coverage / 14 |
| 5 教育学 | 43 / 0.791 | 5/5 / 1.000 | 0.360 | assessing (assessing) / provisional_recovery | 0.098 | 0.618/0.418/0.618 | true | 0.206 / coverage / 17 |
| 6 医学概論 | 71 / 0.775 | 39/61 / 0.639 | 0.179 | weak (weak) / not_recovered | 0.556 | 0.671/0.471/0.671 | true | 0.330 / retention / 10 |
| 7 病理学 | 172 / 0.703 | 65/65 / 1.000 | 0.265 | weak (weak) / not_recovered | 1.031 | 0.702/0.502/0.702 | true | 1.331 / safety_review / 5 |
| 8 内科学 | 233 / 0.704 | 108/151 / 0.715 | 0.195 | weak (weak) / not_recovered | 1.931 | 0.732/0.532/0.732 | true | 1.456 / safety_review / 1 |
| 9 神経医学 | 123 / 0.659 | 73/114 / 0.640 | 0.150 | weak (weak) / not_recovered | 1.064 | 0.703/0.503/0.703 | false | 1.368 / safety_review / 4 |
| 10 精神医学 | 50 / 0.660 | 24/34 / 0.706 | 0.153 | assessing (assessing) / not_recovered | 0.573 | 0.673/0.473/0.673 | false | 0.246 / coverage / 15 |
| 11 小児学 | 72 / 0.833 | 40/44 / 0.909 | 0.236 | assessing (weak) / not_recovered | 0.262 | 0.641/0.441/0.641 | false | 1.185 / safety_review / 6 |
| 12 臨床心理学 | 35 / 0.829 | 14/14 / 1.000 | 0.271 | assessing (assessing) / not_recovered | 0.213 | 0.635/0.435/0.635 | false | 0.212 / coverage / 16 |
| 13 基礎運動学 | 194 / 0.753 | 58/65 / 0.892 | 0.258 | weak (weak) / not_recovered | 0.818 | 0.690/0.490/0.690 | true | 0.327 / retention / 11 |
| 14 臨床運動学 | 15 / 0.733 | 7/7 / 1.000 | 0.414 | assessing (assessing) / provisional_recovery | 0.082 | 0.615/0.415/0.615 | true | 0.277 / coverage / 13 |
| 15 動作分析学 | 200 / 0.775 | 63/98 / 0.643 | 0.220 | weak (weak) / not_recovered | 0.409 | 0.658/0.458/0.658 | true | 0.306 / retention / 12 |
| 16 運動器 | 87 / 0.701 | 52/104 / 0.500 | 0.113 | weak (weak) / not_recovered | 0.867 | 0.693/0.493/0.693 | false | 1.379 / safety_review / 3 |
| 17 理学療法評価各論 | 215 / 0.763 | 93/158 / 0.589 | 0.147 | weak (weak) / not_recovered | 1.424 | 0.717/0.517/0.717 | true | 0.466 / repair / 8 |
| 18 理学療法治療各論 | 188 / 0.761 | 143/291 / 0.491 | 0.129 | weak (weak) / not_recovered | 3.338 | 0.754/0.554/0.754 | true | 0.579 / repair / 7 |

| Field | reason_codes |
| --- | --- |
| 1 解剖学 | repeated_weakness, high_exam_weight, large_attainment_gap, coverage_insufficient, retention_due, maintenance_needed |
| 2 生理学 | repeated_weakness, high_exam_weight, large_attainment_gap, coverage_insufficient, retention_due, stable_ratio_declined, maintenance_needed, critical_safety |
| 3 心理学 | initial_supply_limited, repeated_weakness, large_attainment_gap, retention_due, maintenance_needed |
| 4 人間発達学 | initial_supply_limited, initial_evidence_insufficient, large_attainment_gap, coverage_insufficient, stable_ratio_declined, maintenance_needed |
| 5 教育学 | initial_supply_limited, initial_evidence_insufficient, large_attainment_gap, coverage_insufficient, retention_due, maintenance_needed |
| 6 医学概論 | large_attainment_gap, coverage_insufficient, retention_due, maintenance_needed |
| 7 病理学 | repeated_weakness, high_exam_weight, large_attainment_gap, retention_due, maintenance_needed, critical_safety |
| 8 内科学 | repeated_weakness, high_exam_weight, large_attainment_gap, coverage_insufficient, retention_due, stable_ratio_declined, maintenance_needed, critical_safety |
| 9 神経医学 | repeated_weakness, high_exam_weight, large_attainment_gap, coverage_insufficient, critical_safety |
| 10 精神医学 | initial_supply_limited, initial_evidence_insufficient, large_attainment_gap, coverage_insufficient |
| 11 小児学 | initial_supply_limited, large_attainment_gap, coverage_insufficient, critical_safety |
| 12 臨床心理学 | initial_supply_limited, initial_evidence_insufficient, large_attainment_gap, coverage_insufficient |
| 13 基礎運動学 | repeated_weakness, large_attainment_gap, coverage_insufficient, retention_due, maintenance_needed |
| 14 臨床運動学 | initial_supply_limited, initial_evidence_insufficient, large_attainment_gap, coverage_insufficient, retention_due, maintenance_needed |
| 15 動作分析学 | repeated_weakness, large_attainment_gap, coverage_insufficient, retention_due, stable_ratio_declined, maintenance_needed |
| 16 運動器 | repeated_weakness, large_attainment_gap, coverage_insufficient, critical_safety |
| 17 理学療法評価各論 | repeated_weakness, high_exam_weight, large_attainment_gap, coverage_insufficient, stable_ratio_declined, maintenance_needed |
| 18 理学療法治療各論 | repeated_weakness, high_exam_weight, large_attainment_gap, coverage_insufficient, stable_ratio_declined, maintenance_needed |

## Observed 60/90/120/150 milestones

These are **historical_proxy_only** answer-count crossings for final weak fields,
not certified additional blocks, nor proof the field was weak at each crossing.
Dates are retained in JSON. They are not supplied as completed blocks to Stage D/E.

| Final weak field | actual cumulative answer milestones reached |
| --- | --- |
| 解剖学 | 60 → 90 → 120 → 150 |
| 生理学 | 60 → 90 → 120 → 150 |
| 医学概論 | 60 |
| 病理学 | 60 → 90 → 120 → 150 |
| 内科学 | 60 → 90 → 120 → 150 |
| 神経医学 | 60 → 90 → 120 |
| 基礎運動学 | 60 → 90 → 120 → 150 |
| 動作分析学 | 60 → 90 → 120 → 150 |
| 運動器 | 60 |
| 理学療法評価各論 | 60 → 90 → 120 → 150 |
| 理学療法治療各論 | 60 → 90 → 120 → 150 |

## Acceptance and next work

HOLD / NOT YET is based on concrete unresolved conditions, not an agreement-rate
threshold chosen after observing the data: 26-observation repetition, missing
two block contexts, two small-supply policy conflicts, and no prospective evidence
that replacing #342 would preserve coverage. Supply85/85 and Safety0 contradictions
are positive findings but do not close those gaps.

Observed current coverage at the end: internal medicine71.5%, neurology64.0%,
orthopedics50.0%, PT evaluation58.9%, PT treatment49.1%. These are current-history
outcomes; no shadow coverage outcome exists. #342 remains accepted and unchanged.
No recent-year trend is inferred: Stage C remains 36 known-year past items /
1064 provenance gaps with repository frequency weights only.

Next promotion work (separate PR/decision): define observable per-field block
context, resolve small-supply classification policy, validate Safety-specific
supply/intent routing, and collect prospective shadow-following evidence without
weakening repeat guards. These are **strategy-promotion blockers / v1.1+ backlog**,
not newly established PT v1.0 runtime defects.

Local audit unit/privacy/no-DB/no-network/no-mutation tests: 8 passed.
Full local suite (including Stage D/E, #337/#342/equivalence): 1433 passed,
6 skipped, 1 deselected, 141 subtests; DATABASE_URL empty and dummy API tokens.
Question Bank validator: 2000 records, 0 issues. No Production Python caller
imports the audit module. PR CI, main CI and read-only Render auto-deploy results
are recorded against their exact commit in the delivery PR and final report.
