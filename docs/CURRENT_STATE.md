# LicenseTown Current State

Last updated: 2026-09-09
Safe integration base: `work/pt-finalization-post-q2000`

## How to resume
1. Read `AGENTS.md`.
2. Read this file.
3. Verify only facts affected by newer commits/data.
4. Continue from the open work instead of rediscovering the repository.

Always distinguish: **code exists / tests pass / real data observed / product accepted**.
Do not casually change `main`, Production Neon, Render or LINE behavior.
Practical learner effect and national-exam success outrank architectural elegance.

---

# 1. Question Bank / Q2000 — CLOSED

- Formal PT Question Bank: **Q1-Q2000 / 2000 questions**.
- Bank version: **`2026-09-b20`**.
- Final cross-sectional medical/editorial quality audit is closed on the safe post-Q2000 branch.
- 33 same-stem groups resolved to 29 legitimate same-stem/different-choice official items plus 4 exact official provenance repeats.
- Exact-repeat groups: Q972/Q1354, Q1067/Q1391, Q1230/Q1526, Q1411/Q1585.
- Raw official Q IDs/provenance remain immutable, but exact repeats are one derived learning-evidence identity through `question_equivalence_groups.json`.
- Equivalent official repeats cannot inflate cross-question weakness, STRONG repair confirmation, or Recent Cooldown behavior.
- Q1411/Q1585 cross-Node identity is reconciled only in derived evidence under KN1387; raw Production rows are unchanged.
- KN0597/KN0807 duplicate raw label is already resolved by reviewed canonical alias KNC0001.
- KN1142/KN1252 share a generic label but are medically different concepts; do not merge.
- Q2000 final-quality PR #277 was merged only to this safe branch. No `main`/Production promotion occurred.

Detailed record: `reports/q2000_final_quality_review_20260909.md`.

---

# 2. Formal learning-data authority

Formal truth path:

`question_attempts -> derived Knowledge Node state -> field/strategy/readiness -> selector/presentation`

- `question_attempts` is the authoritative durable attempt history.
- `user_node_state` is not formal truth.
- Formal Node state is pure-derived by `knowledge_node_state_transition.py`.
- Question equivalence is applied only to derived evidence; raw history is preserved.

Primary learner Production snapshot measured 2026-09-09:
- **1525 attempts**
- **1103 correct / 72.3%**
- **740 unique questions**
- **572 unique raw Knowledge Nodes**
- observation window: 2026-08-17 through 2026-09-09 JST

Detailed real-history analysis: `reports/primary_learner_history_analysis_20260909.md`.

Important learner-history findings:
- confidence 1: 850 attempts / 88.5% accuracy;
- confidence 2: 623 / 54.3%;
- confidence 3: 42 / 31.0%;
- confidence-1 wrong: 98 high-value misconception/repair candidates;
- confidence-2/3 correct: 351 uncertain-correct/checking candidates;
- 344 questions were attempted at least twice;
- first wrong -> latest correct: 76;
- first correct -> latest wrong: 52;
- first wrong -> latest wrong: 37;
- first correct -> latest correct: 179.

Conclusion: confidence and longitudinal transitions are materially informative. Do not reduce learner state to raw accuracy alone. Do not expand above Q2000 merely to add volume.

---

# 3. Repair / retention

Working:
- same-question, weak different-question and STRONG different-question evidence are separated;
- confident STRONG confirmation can move `repairing -> repaired`;
- later wrong evidence can regress to `repairing`;
- retention states include `repaired`, `recheck_due`, `stable`;
- exact official repeats cannot masquerade as STRONG different-question evidence;
- natural STRONG repair supply is already exercised.

Natural reference example:
- KN0394, Q399/Q1572;
- repair reference Q399 at 2026-09-02 18:32:30 JST;
- first 7-day recheck boundary 2026-09-09 18:32:30 JST.

OPEN:
- natural proof of the complete spaced cycle `wrong -> STRONG repair -> spacing -> recheck_due -> stable/repairing`.

Do not manufacture learner activity just to close this gate.

---

# 4. Phase11 strategy engine — HOLD / Shadow-only

Implemented strategy intents include Safety repair, confident/repeated wrong repair, ongoing repairing, retention recheck, uncertain checking, coverage expansion and maintenance.

Boundary:
- Phase11 decides **what / why / how many / intent**.
- Phase10/selector owns **which exact Q**.

Automatic evidence:
- repeat audit: PASS;
- Critical Safety retrospective: PASS-to-date;
- J2/J3 trigger consistency: PASS;
- current profile consistency: PASS;
- retrospective replay coverage for current recommendation anchors: PASS;
- current automatic FAIL/BLOCKED gates: none.

Still OPEN because natural/prospective evidence is required:
- spaced retention outcome;
- first natural `recheck_due` intent -> exact-Q alignment;
- retrospective comparison diversity;
- prospective learner relevance vs baseline;
- repair durability after spacing;
- final human promotion review.

Do not self-promote Phase11. First learner-facing promotion, if later approved, must be limited/feature-gated.

Detailed record: `reports/phase11_promotion_review_20260909.md`.

---

# 5. Adaptive selector / Recent Cooldown

- Node-level adaptive selection works.
- STRONG different-question repair can be preferred.
- Recent Question Cooldown avoids gratuitous recent repeats with limited Safety exceptions.
- Adaptive audit metadata persists selection reason/group/score, repair evidence quality, recent repeat and cooldown bypass.
- Current learner history shows no unexplained or internally inconsistent adaptive-repeat defect.
- Exact official repeats share one evidence identity for selection/cooldown interpretation.

OPEN only where natural recheck-specific evidence is still missing.

---

# 6. Dashboard / learner navigation — v0.1 CONSOLIDATED

Learner route `/goukaku-no-michi` already builds formal learner navigation from authoritative attempts/readiness/shadow evidence.

Completed consolidation v0.1:
- top `現在地`, `今日やること`, formal priority TOP3, repair/coverage/retention guidance remain the learner-facing decision authority;
- lower legacy `優先課題 TOP3` is hidden whenever formal learner navigation exists;
- lower legacy `今日のおすすめ学習` is hidden whenever formal learner navigation exists;
- therefore one learner page no longer shows two competing recommendation authorities;
- if formal field-progress rows are not enabled, legacy field percentages are labeled **`分野別 正答率（参考）`**, not formal `到達度`;
- factual counters such as total answers, study time, recent/average accuracy and streak remain;
- supporter/read-only/legacy fallback behavior was not intentionally changed.

Source map: `reports/dashboard_source_map_20260909.md`.

Remaining small dashboard improvement:
- activate formal per-field progress on the signed learner route so learner-facing `分野別 到達度` uses the same formal evidence family as overall progress, while ordinary accuracy stays a separate sub-metric.

This is a small cleanup, not a reason to redesign the dashboard again.

---

# 7. Longitudinal companion record — v0.1 IMPLEMENTED

`companion_record.py` now derives a compact longitudinal record directly from authoritative `question_attempts` and the existing formal Node-state transition logic.

Properties:
- no new DB table;
- no second persisted state authority;
- raw attempts remain source of truth;
- reviewed question-equivalence semantics are reused;
- exact official repeat Q IDs stay one derived evidence identity;
- learner episodes can capture weakness detection, repair confirmation, retention recheck due, retention confirmation and regression;
- confidence-aware priority reason is retained;
- correct-only checking Nodes are omitted by default to keep the record useful rather than noisy;
- multi-user input is rejected.

PR #279 full CI before safe-branch merge:
- **1217 passed**
- **6 skipped**
- **1 deselected**
- **125 subtests passed**

PR #279 merged only to `work/pt-finalization-post-q2000` at `d645a3167a769e670ea53b59b0f3cf647fc4e5a8`.
No Production write, Render/LINE change, `main` merge or Phase11 promotion occurred.

Next companion step should be product-facing only if it materially helps learner/supporter decisions; do not build a large journal UI just because the derivation exists.

---

# 8. Learning-time/session linkage — DEFERRED

- Learning time persists separately.
- Current `attempt_position` resets inside 5-question batches, so `question_attempts` alone cannot validly measure position 1-30 fatigue in a 30-question session.
- `:time`-style event keys may intentionally differ for idempotency; do not treat event-key equality as a relational join.
- Add explicit durable session linkage only if fatigue/time-efficiency analysis becomes useful enough to change learner behavior.

---

# 9. Current priority

1. Finish the **small learner-route formal field-progress cleanup**; do not redesign the dashboard.
2. Re-evaluate Phase11 automatically when natural retention/recheck/comparison evidence appears; do not force data.
3. Decide the smallest learner/supporter use of `companion_record.py` that changes behavior; avoid a large new UI unless needed.
4. After major post-Q2000 changes settle, use roughly **100-200 new ordinary attempts** as a post-change acceptance sample rather than restarting validation from zero.
5. Session/time linkage remains lower priority.

Do not restart Q2000 audit or question-count expansion unless new evidence exposes a genuine need.
