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

## Current completion contract — MAIN LINE ONLY

Boss fixed the active completion rule on 2026-09-09. Until the core PT learning loop is accepted, do not drift into speculative polish or branch/leaf work.

Car model:
- **走る**: quiz -> answer -> save -> score -> explanation -> continue.
- **曲がる**: next questions change according to real weakness/repair/retention state.
- **止まる**: pause/resume/end/reset safely.
- **壊れない**: formal question/history/Node/session invariants stay coherent.
- **壊れた所を特定できる**: evidence shows which Q/Node/state/selection caused the issue.
- **特定したら修復できる**: learner weakness returns through repair and spaced retention; system defects are reproducible and safely fixable.

Core learner loop:

`wrong -> observable wrong-pattern analysis -> same-Node/different-Q repair -> repair confirmation -> day3 -> day7 -> one-month -> durable OR back to repairing`

A candidate change is in scope now only when it fixes a real current defect, is necessary for this main line, or directly changes learner outcome. Otherwise backlog it.

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

# 3. Core repair / retention loop — CODE + TESTS COMPLETE

Formal repair semantics:
- any evaluable wrong or `unknown` starts/returns the Node to `repairing`;
- same-Q correct does **not** confirm repair;
- weak different-Q correct does **not** confirm repair;
- repair confirmation requires **STRONG different-Q + confidence=1**;
- exact official equivalent repeats are one evidence identity and cannot fake different-Q confirmation.

Spaced retention contract implemented in `knowledge_node_state_transition.py`:
1. STRONG different-Q confidence=1 after wrong -> `repaired`, next check at **3 days**.
2. Valid day3 check before day7 horizon -> `day3_passed`, next check at **7 days** from repair confirmation.
3. Valid check on/after day7 horizon -> `stable`, `day7_passed`, one-month check scheduled.
4. Valid one-month check -> remains `stable`, `durable`, no further required checkpoint in v0.1.
5. Wrong/unknown at any retention checkpoint -> fresh `repairing` cycle and old retention schedule is cleared.
6. If the learner misses day3 and first valid spaced check happens on/after day7, it counts as the day7 horizon instead of manufacturing an overdue backlog.

Selector integration:
- `recheck_due` is an explicit checking priority;
- an actually due time-based retention check may deliberately bypass last-30-attempt Recent Cooldown;
- this bypass is saved as `recent_cooldown_bypassed=True` for auditability;
- ordinary recent-repeat avoidance and Safety behavior remain intact.

Wrong-pattern analysis is evidence-based, not a hidden psychological diagnosis. `companion_record.py` can classify:
- retention regression;
- confidence-1 wrong;
- repeated cross-question wrong;
- repeated same-question wrong;
- unknown answer;
- uncertain wrong;
- single wrong.

It explicitly declares `wrong_pattern_semantics = observable_evidence_not_psychological_diagnosis`.

Full PR #285 CI after the core implementation and policy-aligned regression updates:
- **1232 passed**
- **6 skipped**
- **1 deselected**
- **125 subtests passed**
- run #626: GREEN

Evidence boundary:
- **code exists: YES**
- **full tests pass: YES**
- **natural learner day3/day7/one-month sequence observed end-to-end: NOT YET**
- **Production behavior deployed/accepted: NO**

The missing natural 3d/7d/one-month evidence is time-dependent evidence, not a reason to keep adding speculative code today.

---

# 4. Phase11 strategy engine — HOLD / Shadow-only

Implemented strategy intents include Safety repair, confident/repeated wrong repair, ongoing repairing, retention recheck, uncertain checking, coverage expansion and maintenance.

Boundary:
- Phase11 decides **what / why / how many / intent**.
- Phase10/selector owns **which exact Q**.

PR #284 closed an actual main-line gap: learner navigation `learning_intent` now reaches web recommendation session and exact-Q adaptive selection. Explicit `repair`, `recheck`, and `exploration` intents fill the matching selector group first; normal callers without explicit intent retain mixed composition.

Automatic evidence before this core-loop update:
- repeat audit: PASS;
- Critical Safety retrospective: PASS-to-date;
- J2/J3 trigger consistency: PASS;
- current profile consistency: PASS;
- retrospective replay coverage for current recommendation anchors: PASS;
- current automatic FAIL/BLOCKED gates: none.

Still OPEN where real natural/prospective evidence is required:
- natural spaced retention outcome under the new day3/day7/one-month contract;
- natural `recheck_due` intent -> exact-Q alignment;
- retrospective comparison diversity;
- prospective learner relevance vs baseline;
- final human promotion review.

Do not self-promote Phase11. Do not keep coding just to force these time-dependent gates closed.

Detailed record: `reports/phase11_promotion_review_20260909.md`.

---

# 5. Adaptive selector / Recent Cooldown

- Node-level adaptive selection works.
- STRONG different-question repair can be preferred.
- Formal learner `repair/recheck/exploration` intent reaches exact-Q selection.
- Recent Question Cooldown avoids gratuitous recent repeats.
- Time-based `recheck_due` can bypass cooldown intentionally so a scheduled retention check is not starved by the large bank.
- Adaptive audit metadata persists selection reason/group/score, repair evidence quality, recent repeat and cooldown bypass.
- Current learner history shows no unexplained or internally inconsistent adaptive-repeat defect.
- Exact official repeats share one evidence identity for selection/cooldown interpretation.

No further selector polish is in scope unless real use exposes a main-line defect.

---

# 6. Dashboard / learner navigation — v0.1 CONSOLIDATED

Learner route `/goukaku-no-michi` builds formal learner navigation from authoritative attempts/readiness/shadow evidence.

Completed consolidation v0.1:
- top `現在地`, `今日やること`, formal priority TOP3, repair/coverage/retention guidance are the learner-facing decision authority;
- duplicate lower legacy TOP3/recommendation are hidden when formal learner navigation exists;
- legacy field percentages, when shown, are labeled **`分野別 正答率（参考）`**, not formal `到達度`;
- factual counters remain factual counters.

Source map: `reports/dashboard_source_map_20260909.md`.

Dashboard polish is **not current main-line work**. Do not resume it until core real use exposes a learner-impacting need or Boss explicitly chooses it.

---

# 7. Longitudinal companion record — CORE EVIDENCE LAYER IMPLEMENTED

`companion_record.py` derives compact longitudinal episodes from `question_attempts`; it does not create a second persisted truth.

Current core-useful fields/events include:
- weakness detection;
- observable wrong pattern;
- repair confirmation;
- retention stage/checkpoint/next review;
- day3/day7 checkpoint pass;
- retention due;
- durable retention confirmation;
- regression back to repairing.

Do not build a large journal UI now. The derivation exists to support the main learner loop and later concise presentation if needed.

---

# 8. Learning-time/session linkage — DEFERRED

- Learning time persists separately.
- Current `attempt_position` resets inside 5-question batches, so `question_attempts` alone cannot validly measure position 1-30 fatigue in a 30-question session.
- `:time`-style event keys may intentionally differ for idempotency; do not treat event-key equality as a relational join.
- Add explicit durable session linkage only if real use shows it changes learner outcome.

---

# 9. Current priority / finish line

The current implementation task is considered complete when PR #285 is merged into `work/pt-finalization-post-q2000` after GREEN CI and this state file is updated.

After that, **do not invent another branch/leaf task**.

Next legitimate step is real learner use of the main line:
- normal study produces wrong/correct/confidence evidence;
- wrong Node enters repair;
- STRONG different-Q confirmation closes repair;
- scheduled day3/day7/one-month checks surface naturally;
- wrong retention check reopens repair;
- observed defects are fixed only when they affect the main line.

Natural time-dependent evidence cannot be completed instantly and is not an excuse to keep construction open. Code/test completion and natural/product acceptance must remain separate facts.

Do not restart Q2000 audit, dashboard polish, speculative safety scaffolding, session analytics, or unrelated product expansion unless Boss explicitly reprioritizes them or real main-line evidence exposes a genuine defect.
