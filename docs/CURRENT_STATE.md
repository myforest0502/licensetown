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
- Formal Question Bank has reached Q2000 in the post-Q2000 working branch.
- Question delivery uses saved Question Bank data rather than generating each normal-learning question through OpenAI.
- Q-number remains the stable question ID.
- Question, answer/explanation, tags, Knowledge Node relationships, and validators are separated into structured data/contracts.
- Strong different-question repair pairs exist and are used by repair logic.

## Not finished yet
- Final medical/editorial quality audit for all Q2000 content is not closed.
- Exact duplicates / hard-near duplicates and any medically questionable items found by the final audit still need explicit disposition.
- Final release-grade evidence for the Q2000 bank should be consolidated into one reproducible acceptance record.

## Known problems / risks
- A green structural validator does not by itself prove every item is medically ideal.
- Similarity audits can identify pairs requiring human/editorial judgment rather than automatic deletion.
- Q2000 must not be treated as a marketing claim if the final medical/editorial acceptance is not complete.

## Target state / how it should be
- 2000 questions are structurally valid, medically defensible, non-duplicative enough for learning value, correctly tagged, and usable by adaptive selection.
- Every final-bank change is followed by validator + relevant Knowledge Node / selector / full regression checks.

## Next concrete work
1. Close final Q2000 quality findings one by one.
2. Re-run full Question Bank validation and affected selector/Node tests.
3. Record final acceptance evidence here.

---

# 2. Formal data authority / learning evidence

## Done / working now
- `question_attempts` is the authoritative durable attempt history for formal learner-state derivation.
- Knowledge Node state is formally derived from attempt history using pure derivation logic rather than trusting `user_node_state` as the source of truth.
- Dashboard/formal logic identifies its authoritative Node-state source as `pure_derive_all_user_node_states`.
- Unknown/unanswered-like attempts are distinguished from evaluable answers in the formal logic.

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
- The first natural 7-day retention checkpoint for the confirmed KN0394 repair becomes due around 2026-09-09 18:32 JST.

## Not finished yet
- Natural real-data confirmation of the full sequence `repair -> time gap -> recheck_due -> stable or repairing` is not yet sufficiently accumulated.
- Retention outcome evidence is still a promotion gate rather than a fully proven production behavior across many Nodes/users.

## Known problems / risks
- Synthetic tests passing is not equivalent to natural spaced-retention evidence.
- Forcing special learner behavior only to satisfy a test would reduce the value of the natural pilot.

## Target state / how it should be
- The learner naturally studies; the system detects weakness, repairs it preferably with a different strong question, waits an appropriate interval, and later confirms retention with minimal unnecessary repetition.
- Retention evidence influences strategy and learner-facing guidance only after formal evidence is sufficient.

## Next concrete work
1. Observe the natural KN0394 retention cycle and later cycles without forcing special behavior.
2. Evaluate retention outcome diagnostics and promotion-gate status from those real attempts.

---

# 4. Strategy engine / Phase11

## Done / working now
- Strategy logic already distinguishes major intents such as Safety repair, confident-wrong repair, repeated-wrong repair, ongoing repairing, retention recheck, uncertain correct/checking, coverage expansion, and maintenance.
- Strategy produces a recommendation intent; exact Q-number selection remains the selector's responsibility.
- Phase11 has retrospective diagnostics, repeat audits, retention diagnostics, intent/selection alignment checks, and a promotion-gate status.
- Automatic diagnostics are intentionally unable to self-promote learner-facing Phase11; manual review is required.

## Not finished yet
- Phase11 is not yet formally promoted as fully learner-facing/authoritative strategy based on sufficient natural production evidence.
- The remaining open promotion gates need to be evaluated against the current real learner history, not guessed from code existence.

## Known problems / risks
- Promoting because the code looks complete would bypass the intended evidence-gated rollout.
- A mismatch between recommendation intent and actual selector output would make learner guidance misleading even if both modules individually work.

## Target state / how it should be
- Strategy decides **what / why / how many / repair-vs-recheck-vs-exploration / new-vs-review / Safety priority**.
- Selector decides **which exact questions** while respecting cooldown, repair evidence quality, and supply constraints.
- Saved audit metadata makes each adaptive choice explainable after the fact.

## Next concrete work
1. Run the Phase11 promotion-gate evaluation against current real data.
2. List each gate as PASS / OPEN / BLOCKED with concrete counts.
3. Fix only genuine BLOCKED defects; do not manufacture data to close OPEN evidence gates.

---

# 5. Adaptive selector / recent cooldown

## Done / working now
- Adaptive selection works at Knowledge Node level and can prefer strong different-question repair confirmation.
- Recent Question Cooldown avoids recent repeats when enough non-recent questions exist, with limited Safety exceptions.
- Adaptive selection audit metadata is persisted for adaptive-daily events so later diagnostics can inspect selection reason/group/score, repair evidence, recent repeat, and cooldown bypass.

## Not finished yet
- Continued production validation is needed to ensure strategy intent and selector output stay aligned under real learner histories and Q2000 supply.

## Known problems / risks
- Same-Q repetition can be educationally harmful if used merely because it is available.
- Metadata gaps can make a repeat impossible to classify after the fact.

## Target state / how it should be
- Prefer useful different-question confirmation, avoid gratuitous repeats, preserve Safety behavior, and retain enough saved metadata to reconstruct why a question was selected.

## Next concrete work
- Keep intent-selection alignment in the Phase11 acceptance gate and inspect any misalignment as a first-class defect.

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

1. Final Q2000 quality findings and acceptance evidence.
2. Phase11 promotion-gate evaluation using current real learner data.
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
