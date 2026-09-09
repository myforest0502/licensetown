# LicenseTown Current State

Last updated: 2026-09-09
Safe integration base: `work/pt-finalization-post-q2000`
Production branch: `main`

## How to resume
1. Read `AGENTS.md`.
2. Read this file.
3. Read `docs/PT_V1_PRODUCT_GOAL.md`.
4. Verify only facts affected by newer commits/data.
5. Continue from the open productization step; do not rediscover the whole repository.

Always distinguish: **code exists / tests pass / real data observed / production behavior accepted**.
Practical learner effect and national-exam success outrank architectural elegance.

---

# 0. Fixed PT v1.0 finish line

The authoritative contract is `docs/PT_V1_PRODUCT_GOAL.md`.

PT v1.0 means: a learner can register, study, save history, receive weakness-aware next study, pause/resume safely, understand what to do today, and continue ordinary learning without serious study-blocking/data-loss defects. It does **not** require perfection or complete long-term proof.

New findings must be classified as either:
- **v1.0 product blocker**, or
- **v1.1+/backlog**.

Do not expand the finish line merely because another improvement is possible.

Car model remains:
- **走る**: quiz -> answer -> save -> score -> explanation -> continue.
- **曲がる**: next questions change according to weakness/repair/retention state.
- **止まる**: pause/resume/end/reset safely.
- **壊れない**: question/history/Node/session invariants remain coherent.
- **壊れた所を特定できる**: Q/Node/state/selection/event evidence identifies the fault.
- **特定したら修復できる**: learner weakness returns through repair/retention; system defects are reproducible/fixable.

Core learner loop:
`wrong -> observable wrong-pattern analysis -> same-Node/different-Q repair -> repair confirmation -> day3 -> day7 -> one-month -> durable OR back to repairing`

---

# 1. Productization status — ①〜③ only

Boss explicitly narrowed current work to these three items:

1. **Deploy the tested current main-line candidate to Production.**
2. **Use the existing learner history and continue natural real use; do not restart data collection.**
3. **Confirm the learner can understand what to do today; fix only observed v1.0 blockers.**

Important data rule fixed by Boss:
- The existing primary learner history is the starting evidence base, not disposable pre-test data.
- Production read-only verification on 2026-09-09 still shows **1525 attempts / 1103 correct / 740 unique questions** for the primary learner.
- Do **not** reset/rebaseline and do **not** say "data collection starts today".
- New ordinary attempts simply append to the existing history.
- Time-dependent evidence (day3/day7/month, natural relevance, etc.) is allowed to accumulate naturally while the learner keeps studying.
- Do not delay productization by deeply analyzing evidence that cannot exist until the learner actually uses the new behavior.
- When enough natural data exists, inspect it and fix only demonstrated learner-impacting defects.

### ① Production promotion — DONE

- Promotion PR #286: `work/pt-finalization-post-q2000` -> `main`.
- Pre-merge CI run #628: **GREEN**.
- PR #286 merged to `main` at commit `634ac70d8d3bf27a7587cc4bc1711e3ab4a8331e`.
- Render service `line-bot-project` auto-deploys from `main`.
- Render deploy `dep-daggcvjbc2fs73fgh460` finished **live** on 2026-09-09.
- Render startup completed normally; root health request returned HTTP 200.
- No Production DB reset/migration was performed for this promotion.
- Post-deploy read-only Neon verification still showed **1525 / 1103 / 740**, confirming existing learner history was not reset by promotion.

Evidence boundary:
- code exists: YES
- full tests pass: YES
- Production candidate deployed: YES
- existing learner history preserved: YES
- real-device learner acceptance of the new Production behavior: OPEN

### ② Real learner use — OPEN, NATURAL USE ONLY

Do not manufacture a fresh trial dataset. The primary learner already has substantial history and should simply continue normal study.

Acceptance observation is limited to ordinary use:
- study starts and continues normally;
- answers are saved;
- score/explanation are usable;
- pause/resume remains safe;
- next-study behavior changes sensibly with existing + new history;
- no abnormal repeat loop or study-blocking error appears.

Natural 3-day/7-day/month evidence is useful when it arrives but is not an excuse to keep coding now.

### ③ "今日何をすればいいか" — CODE PATH READY, REAL-DEVICE ACCEPTANCE OPEN

Current learner-facing authority is formal learner navigation.
- duplicate competing legacy recommendations are hidden when formal navigation exists;
- learner `repair / recheck / exploration` intent reaches exact-question selection;
- factual accuracy and formal attainment/recommendation are kept conceptually separate;
- core wrong-pattern/repair/next-review evidence exists in `companion_record.py`.

Do not build a large new UI before use. The remaining question is product acceptance: on the real device, does the learner naturally understand the next action and does the actual question set match it?

If real use exposes a contradiction/confusion that blocks ordinary study, fix that exact issue. Otherwise classify polish as v1.1+.

---

# 2. Question Bank — CLOSED

- Formal PT Question Bank: **Q1-Q2000 / 2000 questions**.
- Bank version: `2026-09-b20`.
- Final medical/editorial/Q-ID integrity review is closed.
- Official exact repeats are preserved as raw provenance but share derived learning-evidence identity where required.
- Do not expand above Q2000 merely to add volume.

Detailed record: `reports/q2000_final_quality_review_20260909.md`.

---

# 3. Formal learning-data authority

Formal truth path:
`question_attempts -> derived Knowledge Node state -> field/strategy/readiness -> selector/presentation`

- `question_attempts` is authoritative durable history.
- `user_node_state` is not formal truth.
- Question equivalence is applied to derived evidence without rewriting raw history.

Primary learner baseline currently retained:
- 1525 attempts
- 1103 correct / 72.3%
- 740 unique questions
- historical observation began 2026-08-17

Detailed analysis: `reports/primary_learner_history_analysis_20260909.md`.

---

# 4. Core repair / retention — CODE + TESTS COMPLETE

Formal semantics:
- wrong/unknown -> `repairing`;
- same-Q correct does not confirm repair;
- weak different-Q correct does not confirm repair;
- STRONG different-Q + confidence=1 confirms repair;
- exact official equivalents cannot fake STRONG different-Q evidence;
- wrong at a retention checkpoint reopens repair.

Spaced contract:
1. repair confirmation -> next check at day3;
2. day3 pass -> next horizon day7;
3. day7 pass -> one-month check scheduled;
4. one-month pass -> durable;
5. missed earlier checkpoint does not create artificial backlog if a later valid horizon is reached.

Selector can surface genuinely due rechecks and audit deliberate cooldown bypass.

Full validation before production promotion included **1232 passed, 6 skipped, 1 deselected, 125 subtests passed**; promotion PR CI was also GREEN.

Natural end-to-end retention evidence is still time-dependent. Do not force it.

---

# 5. Wrong-pattern / companion evidence

`companion_record.py` derives longitudinal episodes from authoritative attempts; it is not a second persisted truth.

Observable patterns include:
- retention regression;
- confidence-1 wrong;
- repeated cross-question wrong;
- repeated same-question wrong;
- unknown answer;
- uncertain wrong;
- single wrong.

Do not claim hidden psychology. Do not build a large journal UI for v1.0 unless actual learner use proves a concise missing summary is a blocker.

---

# 6. Phase11 / adaptive strategy

Phase11 decides intent; selector decides exact Q.

Implemented intents include repair, recheck, exploration and other safety/coverage priorities. Explicit learner intent now reaches exact-Q adaptive selection.

Long-term/prospective Phase11 proof is not a v1.0 blocker by itself. Do not self-promote based on invented evidence, but do not keep construction open waiting for time-dependent evidence either.

Detailed record: `reports/phase11_promotion_review_20260909.md`.

---

# 7. Dashboard / learner navigation

Formal learner navigation is the learner-facing decision authority. Duplicate legacy recommendation blocks are suppressed when formal navigation exists. Accuracy may remain as a factual/reference metric.

Do not resume general dashboard polish. Only a demonstrated contradiction that prevents the learner from knowing what to do today is a v1.0 blocker.

Source map: `reports/dashboard_source_map_20260909.md`.

---

# 8. Deferred / not default v1.0 blockers

- full long-term Phase11 statistical proof;
- observing every natural day3/day7/month pattern before release;
- large companion/journal UI;
- dashboard polish beyond contradiction-free guidance;
- new session/fatigue analytics;
- HP/Town/avatar/social/future features;
- speculative safeguards for unobserved edge cases.

---

# 9. Immediate next step

**No new engineering branch should be invented now.**

The Production candidate is live. The next legitimate step is normal learner use on the real device with the existing 1525-attempt history intact.

Only when real use reveals a concrete v1.0 blocker should code be changed. Otherwise allow natural data to accumulate and move toward the v1.0 acceptance decision.

Human acceptance needed next:
- learner opens/uses the Production app normally;
- learner studies without a special test script;
- Boss/learner reports only genuine confusion, contradiction, repeat abnormality, data-loss, or study-stopping behavior.

Until such evidence appears, do not deepen speculative analysis and do not restart data collection.