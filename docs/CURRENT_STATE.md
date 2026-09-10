# LicenseTown Current State

## 2026-09-10 Production blocker: global short-term same-Q repeats

- Production attempts showed the same evidence question recurring within minutes through non-adaptive learner paths, despite the adaptive Recent Cooldown repair.
- Root cause: the PR #296 protection lived inside the adaptive/daily selectors; ordinary random/category session creation and prerequisite backtrack did not consistently apply the authoritative `question_attempts` history.
- Fix branch: `fix/global-short-term-repeat-guard-v01`. All ordinary learner session paths now derive one shared blocked exact-evidence set from formal Node-state replay. Previously attempted evidence stays blocked until the formal state is `recheck_due`; same-Node different-Q repair remains eligible.
- Random/category selection accepts that blocked set, category shortage fills from other non-recent evidence instead of immediately repeating a Q, and prerequisite backtrack cannot reinsert blocked evidence. Initial assessment remains unchanged.
- Status: **real Production defect observed: YES / cause identified: YES / focused regression: GREEN / full local pytest: one unrelated Windows CRLF idempotence failure only; Linux CI pending / Production deployed: NO / real learner acceptance: PENDING**.

Last updated: 2026-09-10
Safe integration base: `work/pt-finalization-post-q2000`

## How to resume
1. Read `AGENTS.md`.
2. Read this file.
3. Read `docs/PT_V1_PRODUCT_GOAL.md`.
4. Verify only facts affected by newer commits/data.
5. Continue from the open work instead of rediscovering the repository.

Always distinguish: **code exists / tests pass / real data observed / product accepted**.
Do not casually change `main`, Production Neon, Render or LINE behavior.
Practical learner effect and national-exam success outrank architectural elegance.

## 2026-09-10 Production blocker: global short-term same-Q repeats

- Production evidence showed same raw questions recurring within minutes across ordinary learning sessions, including Q1702 at 17:34 / 17:39 / 17:45 and Q1595 at 19:16 / 19:24.
- PR #296 protected the Node-adaptive and legacy daily builders, but ordinary random/category starts and prerequisite backtrack still had paths that did not apply the formal attempt-based guard.
- Fix branch: `fix/global-short-term-repeat-guard-v01`. Every non-initial-assessment start reads `question_attempts` as formal truth, canonicalizes exact-repeat evidence identity, and blocks previously attempted evidence until the formal Node replay reaches `recheck_due`; same-Node different-Q repair remains eligible.
- Random/category selection accepts the same evidence exclusions, and prerequisite backtrack cannot inject a blocked recent evidence question. Initial assessment remains on its fixed contract.
- Status: **real Production defect observed: YES / code fix exists: YES / focused regression green / full CI pending / Production deployed: NO / real-device acceptance: PENDING**.

## Fixed PT v1.0 product finish line

Boss and Aoi fixed the shared definition of **「修正は今後もあるが、一旦完成として商品として出せる物」** on 2026-09-09.

The authoritative detailed contract is `docs/PT_V1_PRODUCT_GOAL.md`.

Do not broaden the finish line in later chats merely because another improvement is possible. New findings must be classified as either:
- **v1.0 product blocker**, or
- **v1.1+/backlog**.

PT v1.0 is considered product-ready when a new learner can register, study, have attempts saved, receive weakness-aware next study, pause/resume safely, understand what to do today, and complete ordinary learning without serious data-loss/study-blocking defects; required automated checks are green; production-equivalent flow works; and several days of real use show no major blocker.

The completion target is not perfection, complete long-term proof, or implementation of every future feature.

## Public Question Bank display

- Public marketing stats must show the closed Q2000 composition as **新規問題 900問 / 過去問 1100問 / 合計 2000問収録**.
- Do not expose stale preview-source counts such as 643 / 1094.

## 2026-09-09 Production blocker: 合格への道 500

- Real learner reported HTTP 500 on `/goukaku-no-michi`. Render traceback confirmed `ValueError: attempts must belong to one user and one canonical Node`.
- Root cause: `phase11_active_weakness.build_active_repair_weakness()` grouped histories by raw/canonical Knowledge Node only, while exact-repeat evidence can deliberately remap a question to a different derived evidence Node (`Q1585`: raw `KN0659` -> evidence `KN1387`). This mixed two evidence Nodes in one history and violated the formal state-transition invariant.
- Fix branch: `fix/goukaku-500-evidence-node-grouping-v01`. Group active-weakness histories by `canonicalize_question_evidence_node(question_id, raw_node_id)` so grouping matches the same derived evidence authority used by `knowledge_node_state_transition.py`.
- Regression coverage explicitly includes the cross-node exact-repeat case.
- Resolution status: **real Production failure observed: YES / root cause identified: YES / targeted regression: 21 passed / full CI run #632: 1233 passed, 6 skipped, 1 deselected, 125 subtests passed / PR #288 merged to main at `c1209ebb2c7a38df95e532831e5a31e49cff400d` / Render deploy `dep-dagjv59srm7s73fh96ug`: live / real post-fix learner-device acceptance: PENDING**.

## 2026-09-09 Dashboard whitespace defect

- Real learner screenshot after the `/goukaku-no-michi` 500 repair showed a large unnecessary blank region in the right story column beside `学習の現在地`.
- Cause: `dashboard-layout-v05.js` kept `学習の現在地` in the taller left column but forcibly moved the 7-day learning card to a new full-width row below the two-column story. CSS Grid therefore had to preserve the left-column height and left a large empty right area.
- Fix branch: `fix/dashboard-blank-space-v01`. Keep `学習の現在地` on the left and place the 7-day learning record into the right story stack so the existing space is used naturally; mobile remains one-column through the existing breakpoint.
- Status: **real Production screenshot observed: YES / root cause identified: YES / code fix under validation / Production accepted: NO**.

## 2026-09-09 Dashboard approved production layout

- Boss approved the final desktop composition for `/goukaku-no-michi`: the large `合格までの推奨ルート` is placed immediately below the top date/exam/progress summary and before the daily-action/navigation area.
- No learner-facing information card may be deleted to make the route larger. The preserved content set includes `今日やること`, `分野別到達度`, `源さんの一言`, `知識の確認状況`, `今の学習カルテ`, `定着までの進み方`, `直近7日間の学習記録`, `LTの作戦メモ`, `学習の現在地`, `あなたの足跡を見る`, and `次のチェックポイント`.
- Desktop story rails are intentionally balanced: left = field progress -> LT strategy memo -> learning position -> footprints; right = Gen-san -> knowledge status -> learning chart/profile -> retention flow -> weekly record -> next checkpoint. Mobile remains a single-column flow.
- The formal Gen-san production asset remains `static/images/characters/gensan_main.png`; generated mockup faces are never production assets.
- Implementation branch: `fix/dashboard-approved-layout-v01`, using `dashboard-approved-layout-v01.js/css` loaded last so the approved hierarchy wins over older layout scripts without deleting their content-generation logic.
- Status: **Boss layout approval: YES / code exists: YES / automated validation pending / Production deployed: NO / real-device acceptance: PENDING**.

## 2026-09-09 Dashboard reference-halves correction

- The previous PR #291 production layout did not reproduce Boss's two attached reference screenshots faithfully and produced a broken/chaotic visual composition in real use. That production acceptance is revoked.
- Boss supplied two screenshots that together define the desktop layout: top half = date/priority on the left with overall progress on the right, then summary, learner decision/navigation, and the large `合格までの推奨ルート`; lower half = `分野別到達度` opposite `源さんの一言` -> `知識の確認状況` -> `今の学習カルテ` -> `定着までの進み方`, then `LTの作戦メモ` + `学習の現在地` opposite `直近7日間の学習記録`, finishing with `あなたの足跡を見る` and `次のチェックポイント`.
- No learner-facing card is deleted. The formal Gen-san asset remains `static/images/characters/gensan_main.png`.
- Corrective branch: `fix/dashboard-match-reference-halves-v01`. `dashboard-approved-layout-v01.js/css` is now a final deterministic override loaded last; desktop uses explicit top and lower grids, mobile remains one column.
- Status: **real Production defect observed: YES / Boss reference supplied: YES / corrective code exists: YES / automated validation pending / Production deployed: NO / real-device acceptance: PENDING**.

## 2026-09-09 Dashboard upper-reference lock

- Boss supplied a new authoritative screenshot for the **upper half only** and explicitly froze the previously approved lower half. No independent layout judgement is allowed.
- Upper desktop order is fixed to: left column `date-card -> 今日やること`, right column `合格への到達度`; then full-width `summary-grid`; then full-width `合格までの推奨ルート`; then full-width current/priority overview (`learner-current-card`).
- The redundant source-only learner navigation remains in DOM for data/behavior but is not a visual layout authority; its visible `today` and `current` cards are moved into the approved positions.
- Lower desktop composition is unchanged from the preceding Boss-approved screenshot and is treated as frozen: subjects / Gen-san / knowledge state / study profile / retention / LT strategy / weekly record / learning position / footprints / checkpoint.
- Formal Gen-san production asset remains `static/images/characters/gensan_main.png`. Mobile remains one column.
- Corrective branch: `fix/dashboard-upper-reference-only-v01`; asset cache version bumped to `20260909-v03`.
- Status: **Boss upper reference supplied: YES / lower half frozen: YES / code exists: YES / automated validation pending / Production deployed: NO / real-device acceptance: PENDING**.

## 2026-09-09 Dashboard summary-row production correction

- Real Production screenshot showed PR #294 did not visually satisfy Boss's instruction: the five summary cards still wrapped 3+2 on wide desktop and the new route-card guidance could be hidden by stale asset cache.
- Root cause: the five-column override was scoped only to 701-1000px, so widths above 1000px fell back to the legacy three-column rule; `dashboard-product-copy-v01.js` and the approved-layout CSS cache keys were also not bumped.
- Corrective branch: `fix/dashboard-summary-row-cache-v01`. For every viewport >=701px the summary grid is forced to five columns in the fixed order already present in the DOM: total answers / cumulative study time / 7-day accuracy / average accuracy / consecutive learning days. Mobile <=700px is unchanged.
- Route top-card guidance remains the PR #294 copy and is now forced fresh by cache-key updates. No lower-half layout or other dashboard composition is changed.
- Status: **real Production mismatch observed: YES / root cause identified: YES / code fix exists: YES / automated validation performed in branch workflow / Production deployed: NO / real-device acceptance: PENDING**.

## Current completion contract — MAIN LINE ONLY

Until PT v1.0 is accepted, do not drift into speculative polish or branch/leaf work.

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

PR #285 was merged into `work/pt-finalization-post-q2000` at merge commit `314813170a4b25897136e9d67f24428931f24bfa` after GREEN CI.

Full validation on the core implementation:
- **1232 passed**
- **6 skipped**
- **1 deselected**
- **125 subtests passed**
- run #626: GREEN
- run #627 after the state-document update: GREEN

Evidence boundary:
- **code exists: YES**
- **full tests pass: YES**
- **natural learner day3/day7/one-month sequence observed end-to-end: NOT YET**
- **Production behavior deployed/accepted: NO**

The missing natural 3d/7d/one-month evidence is time-dependent evidence, not a reason to keep adding speculative code before v1.0 acceptance.

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

Dashboard polish is **not current main-line work**. Only learner-facing contradictions or missing v1.0-required guidance can block productization.

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

Do not build a large journal UI for v1.0. Only expose the minimum learner-facing summary needed to answer: where weak / how wrong / repaired or not / next review / regressed or not.

---

# 8. Learning-time/session linkage — DEFERRED

- Learning time persists separately.
- Current `attempt_position` resets inside 5-question batches, so `question_attempts` alone cannot validly measure position 1-30 fatigue in a 30-question session.
- `:time`-style event keys may intentionally differ for idempotency; do not treat event-key equality as a relational join.
- Add explicit durable session linkage only if real use shows it changes learner outcome.
- This is not a v1.0 product blocker by itself.

---

# 9. PT v1.0 remaining path

The coding task for the repair/retention core is CLOSED. Do not invent another engineering subproject just because the core can be polished further.

The next work must be judged only against `docs/PT_V1_PRODUCT_GOAL.md`.

Remaining productization path:
1. verify the complete learner-facing path on the safe branch against the v1.0 checklist: registration -> study -> answer/save -> score/explanation -> pause/resume -> next-study guidance;
2. expose only the minimum weakness/repair/next-review information needed for a learner to know what to do, if current UI does not already make it clear;
3. prepare/promote the already-tested main-line changes to a production-equivalent environment using normal safety rules;
4. run real-device acceptance with the primary learner for several days;
5. fix only observed **v1.0 blockers**;
6. once no serious study-blocking defect remains, declare **LicenseTown PT版 v1.0 商品化完了** even if v1.1 improvements remain.

Not v1.0 blockers by default:
- full long-term Phase11 proof;
- completion of every day3/day7/month natural evidence pattern;
- large companion/journal UI;
- dashboard polish beyond contradiction-free guidance;
- session/fatigue analytics;
- future HP/Town/avatar/social features;
- speculative safety work for unobserved edge cases.

Do not restart Q2000 audit, question-count expansion, speculative branch work, or unrelated product expansion unless Boss explicitly reprioritizes them or real main-line evidence exposes a genuine v1.0 defect.
