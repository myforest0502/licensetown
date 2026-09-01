# LicenseTown ⑩ 実利用QAマトリクス

Date: 2026-09-02
Status: natural-use closure evidence obtained / permanent regression + observation matrix

## A. 自動テストで固定する項目

### Recent Cooldown

- newest max30 attempts are recent regardless of correct/wrong
- 15 repairing singleton + enough non-recent bank -> overlap 0
- 30 repairing singleton + enough non-recent bank -> overlap 0
- if non-recent can fill the requested count -> recent bypass 0
- if only 25 non-recent exist for 30 requested -> exactly 5 recent fallback candidates may fill
- Safety singleton may bypass only when no non-recent alternative exists
- exclude_ids never return through fallback

### Repair / retention

- strong different-Q > weak different-Q > same-Q
- same-Q success alone does not repair
- weak different-Q success alone does not repair
- strong different-Q + correct + confidence1 -> repaired
- repaired + 7d -> recheck_due
- stable + 30d -> recheck_due
- recheck_due + strong different-Q + correct + confidence1 -> stable
- wrong/unknown -> repairing

### Composition

15/10/5 repair/checking/exploration for 30 is soft.

- do not use recent Q merely to hit the ratio
- do not suppress Safety merely to preserve the ratio
- complete question_count when supply is available
- avoid unnecessary one-Node concentration

### Audit

adaptive_daily Node-adaptive results may persist exactly these six adaptive audit fields:

- selection_reason
- selection_group
- selection_score
- repair_evidence_quality
- recent_question_repeat
- recent_cooldown_bypassed

Non-adaptive flows must not persist this adaptive audit extension.

## B. Natural-use closure evidence obtained

A natural post-deploy adaptive_daily 30-question session confirmed:

- 6 learning events
- 30 question results
- 30 unique Q IDs
- all six adaptive audit fields present
- 15 repair / 10 checking / 5 exploration in the observed session
- 8 recent repeats
- 8 cooldown bypasses

The eight repeat/bypass Qs were:

Q8, Q379, Q1305, Q705, Q109, Q1504, Q195, Q25.

All eight were saved as Safety repair selections with same-question repair evidence. Static repairability review confirmed that all eight affected moderate-Safety singleton Nodes lacked a non-recent strong alternate at that time.

Therefore those observed bypasses were explained by the intended Safety/supply exception. Ordinary repair/checking/exploration selections did not show unexplained cooldown bypass in that audited session.

This evidence closed the Phase 10 operational gate. It does not remove the need for ongoing regressions below.

## C. Continued natural-use observation

### Consecutive adaptive sessions

Continue observing:

- Q overlap count
- canonical Node reappearance
- recent_cooldown_bypassed count
- bypass reasons

Expected: Q overlap 0 when enough non-recent bank exists.

### Repetition feeling beyond Q IDs

Even with Q overlap 0, similar themes can feel repetitive. Observe separately:

- canonical Node concentration
- field concentration
- closely related Node concentration

Do not confuse this with the solved recent-Q bug.

### Weakness follow-up

Observe whether confident wrong and repeated wrong evidence lead to useful non-recent different-Q repair when supply exists. For singleton Nodes, temporary deferral caused by cooldown is expected and is not equivalent to forgetting the weakness.

Q1595-Q1605 now provide strong alternate supply for 11 previously blocked Safety Nodes, so later natural use can test whether formal `repairing -> repaired` transitions occur when the learner answers those alternate questions correctly with confidence 1.

### Confidence consistency

Watch especially:

- wrong conf1 -> high-priority repair evidence
- wrong conf2/3 -> repair evidence
- correct conf2/3 -> checking/stabilization evidence
- correct conf1 -> avoid unnecessary immediate repetition

### Long same-day use

For patterns such as recommendation10 + adaptive30 + adaptive30, inspect whether later sessions show rising fallback or concentration.

## D. Red flags

- enough non-recent bank but consecutive-session Q overlap > 0
- unexplained recent_cooldown_bypassed
- duplicate Q inside one session
- excluded Q appears
- recent same-Q chosen while valid non-recent different-Q exists

Yellow flags for review, not automatic bugs:

- same canonical Node appears 3+ times in 30
- repair intent but almost no repair candidates selected
- coverage intent dominated by old questions
- long same-day use sharply increases maintenance/fallback

## E. Minimum log fields for later review

- question_id
- knowledge_node_id
- canonical_node_id (reconstructable)
- is_correct
- confidence
- answer_status
- learning_source
- selection_reason
- selection_group
- selection_score
- repair_evidence_quality
- recent_question_repeat
- recent_cooldown_bypassed
- answered_at

## F. Diagnostics robustness note

The saved-session diagnostic currently identifies a complete 30-question session primarily from event/result counts and uniqueness. A separate diagnostics-only hardening issue is open to also validate the expected six set suffixes/session identity so malformed event sequences cannot theoretically receive a false PASS.

This is a QA-display robustness task and does not reopen the already established Phase 10 natural-use closure.

## G. Permanent Phase 10 regressions

Keep these even after Phase 11/12:

1. consecutive adaptive overlap=0 with sufficient bank
2. singleton-heavy overlap=0
3. Safety singleton fallback only when alternate supply is unavailable
4. strong > weak > recent same-Q
5. exclude_ids absolute exclusion
6. Node diversity
7. repaired/recheck_due/stable transitions
8. adaptive audit persistence
9. unexplained adaptive repeat/bypass remains a red flag
