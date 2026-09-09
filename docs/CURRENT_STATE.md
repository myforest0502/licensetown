# LicenseTown Current State

Last updated: 2026-09-09
Branch baseline when created: `work/pt-finalization-post-q2000`

## Purpose of this file

This is the durable source of truth for **what is already working, what is not finished, current problems/risks, and what the system should ultimately be**.

Do not restart every development session by rediscovering the whole repository. Read this file first, verify only the parts affected by new changes, then continue from the open work.

### Update rule

Update this file in the same development cycle whenever any meaningful implementation, validation, design decision, production behavior, data contract, or known issue changes.

For each changed area, update all applicable sections:
- **Done / working now**
- **Not finished yet**
- **Known problems / risks**
- **Target state / how it should be**
- **Next concrete work**
- **Evidence / important implementation notes**

Do not mark something complete only because code exists. Completion requires the intended production behavior and its acceptance evidence.

---

# 1. Question Bank / Q2000

## Done / working now
- Formal Question Bank has reached Q2000, bank version `2026-09-b20`.
- Question delivery uses saved Question Bank data rather than generating each normal-learning question through OpenAI.
- Q-number remains the stable immutable question ID.
- Question, answer/explanation, tags, Knowledge Node relationships, and validators are separated into structured data/contracts.
- Strong different-question repair pairs exist and are used by repair logic.
- Final cross-sectional audit refined duplicate identity from generic stem equality to item-level equality (`normalized stem + ordered choices`).
- The 33 same-stem groups resolve to **29 legitimate same-stem/different-choice official items plus 4 exact official provenance-repeat groups**.
- On review branch `work/q2000-question-equivalence-v01`, the four exact official repeats are formally registered as one derived learning-evidence identity while preserving both raw Q IDs/provenance:
  - Q972 / Q1354
  - Q1067 / Q1391
  - Q1230 / Q1526
  - Q1411 / Q1585
- Equivalent official repeats cannot masquerade as STRONG different-question repair evidence, cannot create artificial cross-question weakness, and cannot bypass Recent Cooldown merely by using the alternate raw Q ID.
- Q1411/Q1585 are identical official content historically attached to different raw Nodes; review-branch logic reconciles them only for **derived evidence** under KN1387. Raw Production rows are not rewritten.
- Primary learner impact check found only Q1585 among the eight exact-repeat Q IDs had prior attempts (4/4 correct); the other seven had no attempts at review time.
- High-similarity non-exact sampling found no evidence supporting bulk rewriting of official items. Examples reviewed include AFO settings, fracture-name mappings, ASIA key muscles, prosthetic alignment, reproductive physiology, muscle action, metabolism and pathology.
- 14 short-stem heuristic candidates were reviewed as ordinary national-exam prompts with sufficiently specific options/explanations.
- 3 short global-explanation candidates were reviewed; all contain useful option-by-option rationales, so short summary length alone is not a blocker.
- Duplicate raw Node label `交感神経の作用` for KN0597/KN0807 was already formally resolved by reviewed canonical alias `KNC0001` (KN0807 -> KN0597). The audit now distinguishes raw duplicate labels already resolved by canonicalization from genuinely unresolved same-label Nodes.
- Duplicate raw label `筋と作用の組合せ` for KN1142/KN1252 was medically reviewed as **different content** (facial/masticatory muscles vs lower-limb muscles); do not merge. The generic labels may be refined later for learner-facing clarity.
- Review-branch full CI has already produced green runs including **1207 passed, 6 skipped, 1 deselected, 125 subtests passed** before the latest audit-report refinements.
- Detailed review record: `reports/q2000_final_quality_review_20260909.md`.

## Not finished yet
- Latest review-branch audit/canonical-label refinements still need their final CI result recorded before the final-quality audit is formally closed.
- Final zero-blocker audit output and final regression evidence must be captured in the durable record.
- Review PR #277 must be merged only into the safe post-Q2000 working branch after final green verification; it is not a `main`/Production promotion.
- Diagnostic PR #276 must be closed without merge after its evidence is fully captured.

## Known problems / risks
- A green structural validator does not by itself prove every item is medically ideal; similarity and editorial heuristics still require human/medical interpretation.
- Official exam provenance repeats must remain traceable, but counting them as independent learning evidence would falsely strengthen repair/weakness signals.
- Generic Knowledge Node labels can be educationally unhelpful even when the underlying Node separation is correct; label quality and Node identity are separate concerns.
- Temporary diagnostic PR #276 intentionally fails probes and must never be mistaken for a product regression.

## Target state / how it should be
- 2000 questions are structurally valid, medically defensible, correctly tagged, and usable by adaptive selection.
- Official duplicate provenance is preserved without double-counting learning evidence.
- Similarity review is conservative: official items are not cosmetically rewritten merely to be unique.
- Knowledge Node identity reflects the minimum meaningful repair target; labels should become specific enough for useful learner-facing weakness explanations.
- Every final-bank change is followed by validator + affected Node/selector/repair checks + full regression.

## Next concrete work
1. Confirm latest PR #277 CI remains green after canonical-label audit refinement/report update.
2. Record final zero-blocker audit result and CI evidence.
3. Merge PR #277 into `work/pt-finalization-post-q2000` only if green.
4. Close diagnostic PR #276 without merge.
5. Then move the active completion focus to formal-vs-legacy dashboard source consolidation while Phase11 OPEN gates continue collecting natural evidence.

---

# 2. Formal data authority / learning evidence

## Done / working now
- `question_attempts` is the authoritative durable attempt history for formal learner-state derivation.
- Knowledge Node state is formally derived from attempt history using pure derivation logic rather than trusting `user_node_state` as the source of truth.
- Dashboard/formal logic identifies its authoritative Node-state source as `pure_derive_all_user_node_states`.
- Unknown/unanswered-like attempts are distinguished from evaluable answers in the formal logic.
- Current primary learner snapshot measured from Production Neon on 2026-09-09: **1525 attempts, 1103 correct, 740 unique questions, 572 unique raw Knowledge Nodes**. Latest recorded attempt at the time of measurement was 2026-09-09 08:24 JST.

## Not finished yet
- The role of legacy/supporting `user_node_state` should remain explicitly documented so future work does not accidentally restore it as formal truth.
- Long-term migration/cleanup policy for legacy state storage is not finalized.

## Known problems / risks
- Inspecting `user_node_state` alone can falsely suggest that repair/retention is broken.
- Duplicate state authorities would create hard-to-debug inconsistencies.

## Target state / how it should be
- One formal truth path: `question_attempts -> derived Node state -> field/strategy/readiness -> selector/presentation`.
- Persisted caches, if any, are explicitly caches and are never allowed to silently override formal derivation.

## Next concrete work
- Keep formal derivation authoritative during all future dashboard, strategy, and retention changes.

---

# 3. Repair / retention cycle

## Done / working now
- Repair rules distinguish same-question repeat, weak different-question evidence, and strong different-question confirmation.
- A strong different-question correct answer with the required confidence can move an active weakness to `repaired`.
- Regression after repair can return the Node to `repairing`.
- Real production-shaped learner history already contains at least one concrete strong-pair repair example: KN0394 using Q399 / Q1572.
- Retention states include `repaired`, `recheck_due`, and `stable`.
- The confirmed KN0394 repair reference is Q399 answered correctly with confidence 1 at **2026-09-02 18:32:30 JST**. Its 7-day retention checkpoint is **2026-09-09 18:32:30 JST**.
- As of the current 2026-09-09 midday measurement, no later attempt has yet supplied the natural spaced-retention outcome for this checkpoint.
- Natural 2026-09-06 use already exercised Repair Supply: 35 STRONG different-question repairing attempts, 26/35 correct, 13 confidence-1 correct formal-confirmation candidates, with zero recent-repeat flags and zero cooldown bypasses among those STRONG attempts.

## Not finished yet
- Natural real-data confirmation of the full sequence `repair -> time gap -> recheck_due -> stable or repairing` is not yet sufficiently accumulated.
- Retention outcome evidence is still a promotion gate rather than a fully proven production behavior across many Nodes/users.
- Repair mechanics and STRONG supply are exercised, but **repair durability after spacing** is still OPEN.

## Known problems / risks
- Synthetic tests passing is not equivalent to natural spaced-retention evidence.
- Forcing special learner behavior only to satisfy a test would reduce the value of the natural pilot.
- A structurally STRONG alternate is not automatically educationally discriminative; content-quality cautions remain separate from formal mechanics.

## Target state / how it should be
- The learner naturally studies; the system detects weakness, repairs it preferably with a different strong question, waits an appropriate interval, and later confirms retention with minimal unnecessary repetition.
- Retention evidence influences strategy and learner-facing guidance only after formal evidence is sufficient.

## Next concrete work
1. Observe the natural KN0394 retention cycle and later cycles without forcing special behavior.
2. Evaluate retention outcome diagnostics and promotion-gate status from those real attempts.
3. Interpret later retention outcomes separately from item-discrimination quality.

---

# 4. Strategy engine / Phase11

## Done / working now
- Strategy logic already distinguishes major intents such as Safety repair, confident-wrong repair, repeated-wrong repair, ongoing repairing, retention recheck, uncertain correct/checking, coverage expansion, and maintenance.
- Strategy produces a recommendation intent; exact Q-number selection remains the selector's responsibility.
- Phase11 has retrospective diagnostics, repeat audits, retention diagnostics, intent/selection alignment checks, and a promotion-gate status.
- Automatic diagnostics are intentionally unable to self-promote learner-facing Phase11; manual review is required.
- Current rollout state remains **HOLD / Shadow-only**; code existence is not treated as learner-facing promotion.
- Detailed 2026-09-09 review is recorded in `reports/phase11_promotion_review_20260909.md`.

### Current automatic gate evidence (2026-09-09 midday)
- **Repeat audit: PASS.** Same-question repeat categories measured from Production data: adaptive spaced repeat 293, justified cooldown bypass 12, non-adaptive repeat 237, audit-metadata-unavailable 252, **adaptive unexplained repeat 0, metadata inconsistent 0**.
- **Safety retrospective: PASS-to-date.** Current policy is fail-closed for Phase11 Critical Safety misses, and real history contains unresolved Critical `KN0613` / `Q621`. No contradictory Phase11 Safety defect is currently identified.
- **Formal trigger consistency: PASS.** J2/J3 candidate builders and retrospective mismatch detector use the same thresholds. Single ordinary wrong evidence cannot validly trigger J2/J3, and regression tests cover the valid/invalid shapes.
- **Current profile consistency: PASS.** Current unresolved Critical evidence makes the formal Shadow reason `safety_repair`; the symmetric target profile is built from the same active facts and exposes the same strongest reason.
- **Retrospective replay coverage prerequisite: PASS for all 9 current recommendation-plan anchors.** Persisted formal result rows match `question_attempts` by `(event_key, attempt_position)` with **0 missing attempts and 0 question-ID mismatches**.
- **Retention: OPEN.** No qualified natural spaced strong outcome exists yet. The first confirmed KN0394 checkpoint becomes due 2026-09-09 18:32:30 JST, and there were no persisted attempts after that due timestamp at the review time.
- **Intent-selection alignment: OPEN.** Saved adaptive history contains **0 `recheck_due` selections**, so J4 exact-Q alignment has no evaluable natural sample yet.
- **Comparison diversity: OPEN.** Earlier evidence established eligible retrospective Shadow-stronger snapshots. A separate 2026-09-02 prospective sample favored Baseline for learner-perceived immediate priority, but the automatic diversity gate is retrospective and requires a second retrospective direction; prospective evidence must not be substituted for it.
- **Currently identified automatic BLOCKED gates: none.**

### Manual / product promotion criteria
The seven automatic gates are necessary but not sufficient. The Phase11 ship checklist and promotion review runbook also require learner-facing/product evidence before a limited pilot.

- **Architecture / ownership boundaries: PASS.** Phase11 stays deterministic/read-only; Phase10 owns exact Q; automatic diagnostics cannot promote themselves.
- **Phase10 adaptive dependency: PASS.** Natural adaptive use and audit metadata persistence have been validated; current repeat evidence has no unexplained/inconsistent adaptive-repeat defect.
- **Natural ordinary-single-wrong overreaction: PASS-to-date / monitor.** Formal mismatch is zero and prior natural reviews found no current systematic red-flag pattern. Continue surveillance because the natural-behavior criterion is broader than the formal invariant.
- **Sparse-coverage conservatism: PASS-to-date / monitor.** Formal policy separates unknown/zero-answer evidence from confirmed weakness, and earlier natural snapshots exercised `insufficient_coverage` behavior without a recorded policy-consistency defect.
- **Repair mechanics / STRONG supply use: PASS-to-date.** Natural STRONG repair selection is being exercised.
- **Repair durability after spacing: OPEN.** Tied to the retention evidence boundary.
- **Prospective recommendation relevance vs Baseline: OPEN.** The 2026-09-02 direct learner-rated disagreement favored Baseline (神経医学) over Shadow (心理学) for immediate priority while still rating the Shadow field as important. This is useful mixed evidence and means learner-facing superiority cannot be claimed yet.
- **Symmetric disagreement breadth: OPEN.** Retrospective evidence remains one-directional for the automatic diversity gate; the Baseline-favorable prospective case must not be used as a substitute for a missing retrospective direction.
- **Final human learner-facing promotion review: OPEN by design.** It occurs only after the evidence set is sufficiently green.

## Not finished yet
- Phase11 is not yet formally promoted as fully learner-facing/authoritative strategy.
- Automatic OPEN gates: **retention, intent-selection alignment, comparison diversity**.
- Additional manual/product OPEN criteria: **repair durability, prospective recommendation relevance, symmetric disagreement breadth, final human promotion review**.
- Retention and recheck intent-selection alignment require natural real data rather than manufactured examples.
- Prospective recommendation relevance requires additional natural cases; one Baseline-favorable sample is not enough to tune weights or to promote either policy.

## Known problems / risks
- Promoting because the code looks complete would bypass the intended evidence-gated rollout.
- A mismatch between recommendation intent and actual selector output would make learner guidance misleading even if both modules individually work.
- `audit_metadata_unavailable` repeat rows are historical observability gaps, but they are not currently defined as promotion-blocking defects; do not confuse them with unexplained or internally inconsistent adaptive repeats.
- Do not manufacture retention/recheck activity or learner-feedback samples merely to turn OPEN into PASS.
- Do not merge prospective learner preference with retrospective formal-comparison buckets just to satisfy comparison diversity.

## Target state / how it should be
- Strategy decides **what / why / how many / repair-vs-recheck-vs-exploration / new-vs-review / Safety priority**.
- Selector decides **which exact questions** while respecting cooldown, repair evidence quality, and supply constraints.
- Saved audit metadata makes each adaptive choice explainable after the fact.
- Promotion requires all checkable gates sufficiently green plus explicit human review; automatic diagnostics never self-promote Phase11.
- First learner-facing move, if approved, should be a **limited feature-flagged pilot**, not immediate full replacement.

## Next concrete work
1. After the first natural `recheck_due` execution, re-run retention outcome and exact-Q intent-selection alignment immediately.
2. Continue natural recommendation-plan history; if a second retrospective comparison direction appears, re-run comparison diversity.
3. Continue learner-relevance evidence through ordinary use only; do not repeatedly questionnaire solely to manufacture favorable samples.
4. Fix only genuine BLOCKED defects; OPEN evidence gates stay OPEN until the evidence exists.
5. When the evidence set is sufficiently green, perform explicit human review for a limited learner-facing pilot.

---

# 5. Adaptive selector / recent cooldown

## Done / working now
- Adaptive selection works at Knowledge Node level and can prefer strong different-question repair confirmation.
- Recent Question Cooldown avoids recent repeats when enough non-recent questions exist, with limited Safety exceptions.
- Adaptive selection audit metadata is persisted for adaptive-daily events so later diagnostics can inspect selection reason/group/score, repair evidence, recent repeat, and cooldown bypass.
- Production evidence currently shows no `adaptive_unexplained_repeat` and no `adaptive_metadata_inconsistent` same-question repeats in the primary learner history.

## Not finished yet
- Continued Production validation is needed to ensure strategy intent and selector output stay aligned under real learner histories and Q2000 supply.
- Recheck-specific intent/selection compatibility cannot yet be judged because there are no persisted `recheck_due` selections in the current learner history.

## Known problems / risks
- Same-Q repetition can be educationally harmful if used merely because it is available.
- Metadata gaps can make a repeat impossible to classify after the fact.

## Target state / how it should be
- Prefer useful different-question confirmation, avoid gratuitous repeats, preserve Safety behavior, and retain enough saved metadata to reconstruct why a question was selected.

## Next concrete work
- Keep intent-selection alignment in the Phase11 acceptance gate and inspect any first `recheck_due` sample as a first-class acceptance event.

---

# 6. Dashboard / learner navigation

## Done / working now
- A formal real-data dashboard shadow exists.
- It computes Node coverage, state mastery, field progress, weakness priorities, recommendation intent, Safety/repair/recheck/coverage signals, and learner-facing navigation.
- Learner-facing presentation converts technical states into plain language such as current position, today's action, priority items, repaired/stable areas, coverage gaps, retention message, and Trial100 message.
- `/goukaku-no-michi` already builds learner navigation from formal inputs and the CTA carries field, count, learning intent, and reason code.
- Formal pass-readiness exists as an evidence-gated status machine, not a pass probability.

## Not finished yet
- Legacy dashboard aggregates and the newer formal derived metrics still coexist in parts of the UI/code path.
- The final single-source learner experience is not yet fully consolidated.
- Some UI sections still display legacy concepts while the formal navigation uses newer evidence.

## Known problems / risks
- Showing legacy and formal numbers side-by-side without a clear hierarchy can confuse learners and developers.
- Calling a progress number a probability of passing would be misleading; the current formal readiness design correctly avoids that.

## Target state / how it should be
- One coherent learner-facing dashboard driven by formal evidence.
- Separate concepts clearly: learning progress, coverage, repair/stability, readiness evidence, and ordinary accuracy.
- No fake precision and no pass-guarantee wording.

## Next concrete work
1. Map every visible dashboard card to its current data source.
2. Decide which legacy cards are retained, replaced, or demoted.
3. Consolidate to one formal hierarchy without breaking existing learner flow.

---

# 7. Weakness analysis / companion record

## Done / working now
- Formal active weakness derivation exists at Node and field level.
- Confident-wrong, repeated-wrong, active repairing, Safety and recheck signals are available.
- Learner-facing guidance and supporter diagnostics can already summarize substantial parts of the learning state.

## Not finished yet
- A true longitudinal companion record (what weakness appeared, what was tried, whether it repaired, whether it stayed repaired, what strategy changed) is not yet a finished first-class product feature.

## Known problems / risks
- Recomputing only the present state loses the educational story of how a weakness changed over time.
- Dumping raw technical logs into a "record" would not help a learner or parent.

## Target state / how it should be
- Maintain a compact longitudinal learning chart: important weakness episodes, interventions/selections, repair confirmation, retention outcome, major strategy changes, and learner-facing/supporter summaries.
- Preserve raw evidence references so summaries remain auditable.

## Next concrete work
- Design the smallest useful companion-record schema after Phase11 and dashboard source-of-truth consolidation.

---

# 8. Learning-time linkage

## Done / working now
- Learning time is persisted separately and event keys may intentionally use a suffix such as `:time` for idempotency.

## Not finished yet
- There is no finalized explicit relational identifier that cleanly ties a 5/30-question learning session to its net learning-time events for analysis.

## Known problems / risks
- Treating event_key equality as a relational join is incorrect under the current design.
- Without an explicit `session_id` / `learning_event_key`, fatigue and time-efficiency analysis will remain weaker than the answer-history analysis.

## Target state / how it should be
- Preserve current idempotency semantics and add an explicit relationship field only if/when session-level time analysis becomes a priority.

## Next concrete work
- Defer until higher-value Phase11/dashboard/Q2000 closure work is done.

---

# 9. Current priority order

1. Final Q2000 quality audit closure and safe-branch integration.
2. Phase11 promotion-gate re-evaluation when new natural retention/recheck/comparison evidence appears.
3. Formal-vs-legacy dashboard source map and consolidation plan.
4. Longitudinal companion-record design and implementation.
5. Lower-priority session/time linkage improvement.

Practical effect for the learner takes priority over architectural elegance.

---

# 10. Working rules

- Before proposing a change, check whether the capability already exists.
- Do not re-investigate the whole system every session; start from this document and verify only affected facts.
- Distinguish **code exists**, **tests pass**, **real data observed**, and **production feature accepted**.
- Do not change Production DB, Render, LINE behavior, or `main` casually.
- Prefer small verified changes: hypothesis -> implementation -> real use -> result -> correction.
- If a change alters any fact in this document, update this document in the same work cycle.
