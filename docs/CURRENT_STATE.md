# LicenseTown Current State

Last updated: 2026-09-09
Active implementation branch: `work/dashboard-formal-consolidation-v01`
Safe integration base: `work/pt-finalization-post-q2000`

## How to resume
On every new LicenseTown development/chat session:
1. read `AGENTS.md`;
2. read this file;
3. verify only facts affected by newer commits/data;
4. continue from the current open work instead of rediscovering the repository.

Update this file in the same development cycle whenever implementation status, validation evidence, design decisions, production behavior, data contracts, risks or next work change.

Distinguish: **code exists / tests pass / real data observed / product accepted**.

---

# 1. Question Bank / Q2000 — CLOSED

- Formal PT Question Bank: **Q1-Q2000 / 2000**, bank version **`2026-09-b20`**.
- Final cross-sectional quality audit is closed on the safe post-Q2000 branch.
- 33 same-stem groups were reduced to:
  - 29 legitimate same-stem/different-choice official items;
  - 4 exact official provenance repeats.
- Exact-repeat groups:
  - Q972 / Q1354
  - Q1067 / Q1391
  - Q1230 / Q1526
  - Q1411 / Q1585
- Exact official repeats remain separate raw Q/provenance records but are one derived learning-evidence identity via `question_equivalence_groups.json`.
- They cannot inflate cross-question weakness, STRONG repair confirmation, or Recent Cooldown behavior.
- Q1411/Q1585 identical cross-Node content is reconciled only in derived evidence under KN1387; Production history is not rewritten.
- 72 near-duplicate candidates were sampling targets; high-risk samples did not justify bulk rewriting official questions.
- 14 short-stem and 3 short-summary-explanation candidates were sampled and accepted under the current explanation/option-rationale contract.
- KN0597/KN0807 duplicate raw label was already formally canonicalized by KNC0001.
- KN1142/KN1252 share a generic label but test different muscle regions; do not merge.
- PR #277 merged only to `work/pt-finalization-post-q2000` at **`8792e5f542d726286f5420085d7964f648500548`**.
- Final pre-merge full CI: **1208 passed, 6 skipped, 1 deselected, 125 subtests passed**.
- Diagnostic PR #276 closed without merge.
- No `main`, Render, LINE or Production DB promotion occurred.

Detailed record: `reports/q2000_final_quality_review_20260909.md`.

---

# 2. Formal learning-data authority

- `question_attempts` is the authoritative durable attempt history.
- Formal Node state is pure-derived from attempts; `user_node_state` is not formal truth.
- Authority path:
  `question_attempts -> derived Node state -> field/strategy/readiness -> selector/presentation`.
- Primary learner snapshot measured 2026-09-09:
  - **1525 attempts**
  - **1103 correct = 72.3%**
  - **740 unique questions**
  - **572 unique raw Knowledge Nodes**

Do not infer formal state from legacy persisted state alone.

---

# 3. Repair / retention

Working:
- same-question / weak different-question / STRONG different-question evidence are separated;
- confident STRONG confirmation can move `repairing -> repaired`;
- later wrong evidence can regress to `repairing`;
- retention states include `repaired`, `recheck_due`, `stable`;
- natural STRONG repair supply is already exercised.

Natural example:
- KN0394, Q399 / Q1572;
- repair reference Q399 at 2026-09-02 18:32:30 JST;
- first 7-day recheck boundary 2026-09-09 18:32:30 JST.

OPEN:
- natural proof of the complete spaced cycle
  `wrong -> STRONG repair -> spacing -> recheck_due -> stable/repairing`.

Do not manufacture learner activity to close this gate.

---

# 4. Phase11 strategy engine — HOLD / Shadow-only

Implemented intents include Safety repair, confident/repeated wrong repair, ongoing repairing, retention recheck, uncertain checking, coverage expansion and maintenance.

Phase11 decides **what/why/how many/intent**; Phase10/selector owns exact Q.

Automatic gate status:
- Repeat audit: **PASS**
- Critical Safety retrospective: **PASS-to-date**
- J2/J3 trigger consistency: **PASS**
- current profile consistency: **PASS**
- retrospective replay coverage across 9 recommendation anchors: **PASS**
- Retention: **OPEN**
- recheck intent -> exact-Q alignment: **OPEN**
- retrospective comparison diversity: **OPEN**
- current automatic FAIL/BLOCKED: **none**

Manual/product status:
- architecture boundaries: PASS
- Phase10 adaptive dependency: PASS
- ordinary single-wrong overreaction: PASS-to-date / monitor
- sparse coverage conservatism: PASS-to-date / monitor
- STRONG repair mechanics: PASS-to-date
- repair durability: OPEN
- prospective recommendation relevance vs baseline: OPEN
- symmetric disagreement breadth: OPEN
- final human promotion review: OPEN by design

No promotion until natural evidence is sufficient. First promotion, if approved, must be limited/feature-gated.

Detailed record: `reports/phase11_promotion_review_20260909.md`.

---

# 5. Adaptive selector / cooldown

- Node-level adaptive selection works.
- STRONG different-question repair can be preferred.
- Recent Question Cooldown is active with limited Safety exception behavior.
- Adaptive audit metadata persists selection reason/group/score, repair evidence quality, recent repeat and bypass flags.
- Current real history has no unexplained/internally inconsistent adaptive-repeat defect.
- Exact official provenance repeats now share one derived evidence identity for selection/cooldown interpretation on the safe branch.

OPEN: natural recheck-specific alignment evidence.

---

# 6. Dashboard / learner navigation — ACTIVE WORK

## What already works
- `/goukaku-no-michi` calls `build_dashboard(..., include_learner_navigation=True)`.
- Formal learner-navigation is already built from authoritative attempts/readiness/shadow evidence.
- Formal `現在地`, `今日やること`, formal priority items, repair/coverage/retention guidance are already visible.
- Formal overall-progress presentation is already used on the learner page because learner navigation forces that calculation path.
- Factual counters (answers, study time, recent/average accuracy, streak) come from saved dashboard aggregates and remain useful.

## Source map completed
Detailed source map: `reports/dashboard_source_map_20260909.md`.

Main findings:
1. **Two recommendation authorities are visible on the same learner page.**
   - Top `今日やること` / formal TOP3 = formal learner navigation.
   - Lower `優先課題 TOP3` and `今日のおすすめ学習` = legacy `build_learning_guidance`.
   - These can disagree and must not remain independent authorities.
2. **Field progress is semantically mixed.**
   - Formal overall progress is shown.
   - `分野別 到達度` remains legacy accuracy bars unless `ENABLE_FIELD_PROGRESS_UI` is enabled.
   - Accuracy is useful, but it is not the same concept as formal field progress.
3. `源さんの一言` still depends on legacy weak/recommendation inputs and is therefore mixed presentation.
4. Factual counters and reward/milestone counts are not competing strategy authorities and should remain.

## Target state
- One recommendation authority: formal learner navigation/derived evidence.
- Formal per-field progress on the learner page; accuracy shown explicitly only as accuracy.
- Legacy guidance remains fallback/compatibility until all supporter/read-only callers are mapped, but must not compete on the learner page.
- Preserve auth, recommendation-start behavior and factual counters.

## Next implementation — NOW
1. Make formal field-progress presentation active whenever learner navigation is enabled.
2. Make lower learner-page priority/recommendation mirror the formal learner-navigation source or remove the duplicate authority.
3. Preserve legacy behavior for contexts that do not enable formal learner navigation.
4. Add regression tests for learner-page source authority.
5. Run targeted dashboard tests, then full CI before safe-branch integration.

---

# 7. Weakness analysis / companion record

Working:
- formal active weakness at Node/field level;
- confident wrong, repeated wrong, repairing, Safety and recheck signals;
- current-state learner/supporter summaries.

Not finished:
- first-class longitudinal companion record.

Target record:
- weakness episode and triggering evidence;
- intervention/selection;
- repair confirmation;
- spaced retention outcome;
- major strategy changes;
- concise learner/supporter summary with raw evidence references.

Start after dashboard authority consolidation.

---

# 8. Learning-time linkage

- Learning time persists separately.
- `:time`-style event keys may intentionally differ for idempotency.
- Do not treat event-key equality as a relational join.
- Explicit session/batch linkage for fatigue/time-efficiency analysis remains lower priority.

---

# 9. Current priority

1. **Dashboard formal-vs-legacy consolidation** — active branch `work/dashboard-formal-consolidation-v01`.
2. Re-evaluate Phase11 when new natural retention/recheck/comparison evidence appears.
3. Longitudinal companion record.
4. Session/time linkage later.

Do not restart Q2000 audit from zero unless new evidence exposes a genuine issue.

Practical learner effect and national-exam success outrank architectural elegance.
