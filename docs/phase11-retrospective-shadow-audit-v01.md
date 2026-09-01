# Phase 11 Retrospective Shadow Audit v0.1

Date: 2026-09-02
Status: design fixed / implementation pending

## 1. Purpose

Accelerate Phase 11 promotion evaluation without manufacturing Production activity or adding a new write path.

The learner-facing `/goukaku-no-michi` route persists a `recommendation_plan` activity event when a Baseline recommendation exists. The event contains the Baseline target field, question goal, and timestamp.

For each trustworthy historical recommendation anchor, replay the **current Phase 11 v0.1 policy** using only learner evidence that existed at that time and compare it with the Baseline recommendation that was actually stored.

This is retrospective observational QA, not proof that Shadow would have caused a better learning outcome.

### Replay semantics

This is not full code time-travel.

The audit asks:

> If the current J1→J7 Shadow policy were evaluated against the learner evidence available at historical time T, what would it decide?

It does not attempt to restore every historical version of application code, Question Bank files, or category metadata. Current canonicalization/formal policy is used unless a future implementation explicitly supplies versioned historical metadata.

Therefore the UI and reports must label the result as a **current-policy historical replay**, not “the recommendation Phase 11 made at that time.” Phase 11 may not have existed at that time.

## 2. What is actually persisted

`record_activity_event()` creates a JST-date-scoped event key and uses conflict-safe insertion. Therefore:

- at most one `recommendation_plan` event is persisted per learner per JST day
- it represents the first successfully persisted learner-facing plan for that day
- later same-day recommendation changes are not historical snapshots because the daily event key already exists
- supporter/read-only dashboard views do not create `recommendation_plan` events

Do not describe these events as a complete history of every recommendation shown that day.

## 3. Valid snapshot anchor

Use only events where:

- `mode = 'recommendation_plan'`
- `question_results` is an object
- `question_results.activity_type = 'recommendation_plan'`
- `question_results.field` is a usable field name
- `question_results.goal` is a usable positive question count
- `answered_at` is present and parseable

If any required value is missing, mark the snapshot unavailable rather than guessing.

## 4. Historical evidence coverage gate

A historical replay is valid only if the formal attempt history available at snapshot time is sufficiently complete.

Legacy `learning_events` may contain question-result lists that are not guaranteed, from code inspection alone, to have a corresponding `question_attempts` row for every historical result. Therefore do not assume `question_attempts` is complete merely because rows exist.

For each snapshot time `T`, calculate a history-coverage audit from records before `T`:

- count valid formal question-result items in `learning_events`
- count corresponding `question_attempts`
- where possible match by `(event_key, attempt_position)` and verify question ID / correctness / confidence consistency
- exclude activity-event objects such as `recommendation_plan` from formal-answer counts

Snapshot eligibility:

- complete/matched history -> replay eligible
- missing/conflicting attempt coverage -> `history_coverage_incomplete`
- malformed historical question-result data -> `history_coverage_unreliable`

Do not use an incomplete snapshot to claim a Phase 11 win/loss or Safety miss.

A reusable pure audit helper is preferred over copying backfill logic into the template.

## 5. Historical attempt cutoff

For eligible snapshot timestamp `T`:

- include formal attempts with `answered_at < T`
- exclude attempts at or after `T`
- preserve unknown attempts in the history
- unknown attempts remain excluded from confirmed weakness
- use `as_of=T` for Node-state retention calculations

This prevents future evidence from leaking backward.

## 6. Historical Baseline control

The stored plan target is authoritative.

Do not rerun today's Baseline algorithm and pretend the result was the historical recommendation.

Minimum control object:

```python
{
    "phase": historical_phase_or_none,
    "recommended_study": [(stored_field, stored_goal)],
}
```

### Phase handling

The Baseline target is persisted; the Baseline phase is not.

Do not silently assert an exact historical phase unless it can be reconstructed from complete historical answer totals consistent with the Baseline's own data source.

If trustworthy historical total-answer reconstruction is available:

- `< 100` -> `foundation`
- `>= 100` -> `analysis`

Otherwise set phase to unavailable/unknown for retrospective display.

Important: current `build_shadow_comparison()` uses Baseline phase to distinguish some same-target labels. Therefore when historical phase is unknown, the retrospective audit must not interpret `same_target_same_reason` vs `same_target_stronger_reason` as trustworthy. Treat the snapshot simply as `target_agreement_phase_unknown` for retrospective review.

## 7. Historical Shadow replay

For each eligible snapshot:

1. verify history coverage before `T`
2. truncate attempts at `T`
3. build field evidence with `as_of=T`
4. build current-policy Shadow judgment with `as_of=T`
5. build symmetric formal field profiles from the same truncated evidence
6. compare stored Baseline target vs reconstructed Shadow target

Capture:

- snapshot JST date/time
- coverage status
- replay policy/version label, e.g. `phase11_v0.1_current_policy`
- historical formal-attempt count
- Baseline target / goal / phase if known
- Shadow intent / target / question count
- Shadow reason code / confidence
- Current-target formal profile
- Shadow-target formal profile
- symmetric comparison label when safe to interpret
- Shadow reason/profile consistency

## 8. Outcome observation window

Later activity is observational only.

Suggested window:

- after snapshot timestamp
- until the next persisted recommendation-plan snapshot
- cap at 24 hours if no next snapshot exists

Because only the first plan per JST day is persisted, the absence of a later same-day plan event does not prove the Baseline recommendation never changed later that day.

Capture:

- subsequent formal attempt count
- fields actually attempted
- whether Baseline target was attempted
- whether Shadow target was also sampled
- correct/wrong/confidence counts in those target fields
- same-Q repeats
- same-Node different-Q encounters
- formal Node transitions observed

Safe observational labels include:

- `baseline_target_followed`
- `shadow_target_also_sampled`
- `both_targets_sampled`
- `neither_target_sampled`
- `outcome_not_observable`

Never write `Shadow would have improved the learner`.

## 9. Review categories

### Agreement

Stored Baseline target equals reconstructed Shadow target.

If historical Baseline phase is known, the normal same-target comparison details may be shown.

If phase is unknown, record agreement but do not claim same reason. Use a conservative retrospective label such as:

`target_agreement_phase_unknown`

### Shadow stronger disagreement

Different target and symmetric formal profile ranks favor Shadow.

### Current stronger disagreement

Different target and symmetric formal profile ranks favor the stored Baseline target.

### Inconclusive disagreement

Different target but ranks are equal, profile data is unavailable, historical interpretation is unsafe, or history coverage is incomplete.

Never hide Current-guidance wins.

## 10. Promotion-focused historical checks

Eligible snapshots can help test whether:

- unresolved Critical Safety evidence was missed by the current Phase 11 policy
- one ordinary wrong would cause unjustified field takeover under the current policy
- sparse evidence would remain in coverage behavior
- historical recheck_due work, if any, would outrank J5-J7
- disagreement patterns systematically favor one side or remain mixed

A candidate Safety miss requires complete historical evidence coverage. Incomplete history cannot be counted as a miss.

## 11. Limits

Retrospective replay cannot establish:

- what the learner would have done if Shadow had actually been shown
- causal superiority of Shadow
- long-term pass probability
- whether an unattempted Shadow target would have produced better learning
- every recommendation the learner saw during a day
- the exact decision an older, historical version of Phase 11 code would have made

It is evidence for current-policy rule consistency and safety, not an A/B experiment or historical code reconstruction.

## 12. Read-only implementation boundary

Allowed:

- SELECT recommendation-plan events
- SELECT historical learning events needed for coverage audit
- SELECT question attempts
- pure historical reconstruction
- supporter diagnostics rendering

Forbidden:

- Production DB writes
- migration
- editing historical events
- selector changes
- Node-state changes
- Baseline recommendation changes
- learner-facing changes

## 13. Suggested implementation

Prefer pure helpers such as:

```python
def audit_historical_attempt_coverage(learning_events, attempts, *, before):
    ...

def build_retrospective_shadow_audit(attempts, learning_events, plan_events):
    ...
```

Recommended SELECT-only database helper shape:

```python
def get_learning_events(user_id: str, before: datetime | None = None) -> list[dict]:
    ...
```

It should mirror the local/Neon behavior style of `get_question_attempts()` and return event_key, user_id, mode, answered_count, correct_count, answered_at, and question_results ordered chronologically.

Do not put replay or eligibility logic into the template.

## 14. Supporter UI

Add development-only section:

`Phase11 過去推薦リプレイ`

Summary:

- plan anchors found
- replay-eligible snapshots
- history-coverage excluded snapshots
- agreements
- Shadow stronger disagreements
- Current stronger disagreements
- inconclusive disagreements
- Critical Safety miss candidates
- ordinary-single-wrong takeover candidates

Show latest 10-20 eligible/recent snapshots with expandable evidence. Excluded snapshots should show the exclusion reason rather than disappear silently.

Every replay result should visibly state that it uses the current Phase 11 policy against historical learner evidence.

## 15. Minimum tests

1. later same-day Baseline changes are not invented from one daily plan anchor
2. supporter/read-only rendering does not create plan anchors
3. future attempts do not leak backward
4. persisted Baseline field is used rather than current recalculation
5. incomplete question_attempt coverage excludes the snapshot
6. matching historical learning-event results and attempts makes snapshot eligible
7. activity-event dicts are not counted as formal answers
8. historical phase stays unknown when trustworthy total reconstruction is unavailable
9. trustworthy `<100` and `>=100` phase reconstruction works when coverage is complete
10. phase-unknown agreement does not claim same Baseline reason
11. replay output identifies the current-policy version
12. unknown attempts do not create confirmed weakness
13. same-target agreement
14. Shadow-stronger disagreement
15. Current-stronger disagreement
16. equal evidence -> inconclusive
17. Critical Safety candidate requires complete history coverage
18. ordinary single wrong does not become false weakness
19. future recheck state does not leak backward
20. no DB write helper
21. no exact-Q selector call
22. learner-facing unchanged
23. existing Phase 11 tests remain green

## 16. Promotion use

Retrospective evidence can reduce uncertainty before a limited learner-facing pilot, particularly for Safety and rule-consistency review.

It does not replace prospective natural-use evidence. Final promotion should combine:

- retrospective eligible historical replay using clearly identified current policy
- current natural-use diagnostics
- prospective limited-pilot evidence when approved

This gains evidence faster without fabricating Production learning activity, overstating incomplete historical data, or pretending to reproduce old code versions.
