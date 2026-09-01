# Phase 11 Retrospective Shadow Audit v0.1

Date: 2026-09-02
Status: design fixed / implementation pending

## 1. Purpose

Accelerate Phase 11 promotion evaluation without manufacturing Production activity or adding a new write path.

The learner-facing `/goukaku-no-michi` route persists a `recommendation_plan` activity event when a Baseline recommendation exists. For each trustworthy historical plan anchor, replay the **current Phase 11 v0.1 policy** using only learner evidence available before that timestamp and compare it with the Baseline target that was actually stored.

This is retrospective observational QA. It is not proof that Shadow would have caused a better outcome.

## 2. Replay semantics

This is not full code time-travel.

The question is:

> If the current J1→J7 Shadow policy were evaluated against the learner evidence available at historical time T, what would it decide?

Current canonicalization/formal policy is used. The audit does not restore every historical version of application code, Question Bank files, or category metadata.

Every result must therefore be labeled as a **current-policy historical replay**, never as “the Phase 11 recommendation made at that time.”

## 3. What is actually persisted

`record_activity_event()` creates a JST-date-scoped key and uses conflict-safe insertion.

Therefore:

- at most one `recommendation_plan` anchor is persisted per learner per JST day
- it represents the first successfully persisted learner-facing Baseline plan that day
- later same-day recommendation changes are not stored as additional anchors
- supporter/read-only dashboard views do not create plan anchors

Do not treat these events as a complete history of every recommendation shown during a day.

## 4. Valid plan anchor

Use only events where:

- `mode = 'recommendation_plan'`
- `question_results` is an object
- `question_results.activity_type = 'recommendation_plan'`
- `question_results.field` is a usable field name
- `question_results.goal` is a positive usable question count
- `answered_at` is parseable

Malformed anchors are unavailable; do not guess missing values.

## 5. Historical Baseline phase

The stored target and goal are authoritative. The phase is not persisted, but its source is known.

Production Baseline `total_answers` comes from:

`SUM(learning_events.answered_count)`

Therefore for snapshot timestamp `T`, reconstruct:

```python
historical_total_answers = sum(
    event["answered_count"]
    for event in learning_events
    if event["answered_at"] < T
)
```

Activity events such as `recommendation_plan` naturally add zero because their `answered_count` is 0.

Then:

- `< 100` -> `foundation`
- `>= 100` -> `analysis`

This mirrors the Baseline phase threshold.

If historical event timestamps/counts are malformed or unavailable, mark phase unknown rather than guessing.

## 6. Formal history coverage gate

Knowing Baseline total answers is not enough to replay Shadow. Shadow needs trustworthy question-level formal history.

Legacy `learning_events` can contain answered activity that is not guaranteed, from code inspection alone, to have a complete corresponding `question_attempts` stream.

For all events before `T`:

- if `answered_count == 0`, the event does not require formal attempt rows
- if `answered_count > 0`, require a list-style `question_results` payload that can account for the formal answers
- count valid formal result items with Q IDs
- match expected formal results to `question_attempts` by `(event_key, attempt_position)` where possible
- verify question ID / correctness / confidence consistency
- activity-event objects are not formal answer rows

Snapshot statuses:

- `history_coverage_complete`
- `history_coverage_incomplete`
- `history_coverage_unreliable`

A snapshot is replay-eligible only when history coverage is complete.

Important: a snapshot may have a reconstructable Baseline phase while still being ineligible for Shadow replay because formal question-level history is incomplete.

## 7. Historical attempt cutoff

For eligible timestamp `T`:

- include attempts with `answered_at < T`
- exclude attempts at or after `T`
- preserve unknown attempts
- unknown attempts still do not create confirmed weakness
- use `as_of=T` for formal retention/state calculations

No future evidence may leak backward.

## 8. Historical Baseline control object

Do not rerun today's Baseline algorithm and pretend it was the historical recommendation.

Use:

```python
{
    "phase": historical_phase,
    "recommended_study": [(stored_field, stored_goal)],
}
```

The persisted field remains authoritative even if rerunning today's Baseline logic would choose something else.

## 9. Current-policy Shadow replay

For every eligible plan anchor:

1. reconstruct Baseline phase from `learning_events.answered_count`
2. validate cumulative formal history coverage before `T`
3. truncate `question_attempts` at `T`
4. build field evidence with `as_of=T`
5. run current `build_shadow_judgment(..., as_of=T)`
6. build symmetric formal field profiles from the same historical evidence
7. compare stored Baseline target vs reconstructed Shadow target

Capture:

- snapshot JST timestamp
- policy label, e.g. `phase11_v0.1_current_policy`
- coverage status
- historical total answers
- historical formal attempt count
- Baseline target / goal / phase
- Shadow intent / target / count
- Shadow reason code / confidence
- Baseline-target formal profile
- Shadow-target formal profile
- comparison label
- Shadow reason/profile consistency

## 10. Review categories

### Agreement

Stored Baseline target equals replayed Shadow target.

### Shadow stronger disagreement

Targets differ and symmetric formal evidence rank favors Shadow.

### Current stronger disagreement

Targets differ and symmetric formal evidence rank favors stored Baseline target.

### Inconclusive disagreement

Targets differ but ranks are equal or evidence/profile is insufficient.

### Excluded snapshot

History coverage or anchor integrity is insufficient.

Excluded snapshots must not be counted as Shadow wins/losses or Safety misses.

Never hide Current-guidance wins.

## 11. Outcome observation window

Later learner activity is observational only.

Suggested window:

- after plan timestamp
- up to the next persisted plan anchor
- cap at 24 hours if needed

Because only one plan/day is persisted, absence of another same-day anchor does not prove that the Baseline recommendation remained unchanged all day.

Capture observationally:

- subsequent formal attempt count
- fields attempted
- whether Baseline target was sampled
- whether Shadow target was sampled
- correct/wrong/confidence counts in those fields
- same-Q repeats
- same-Node different-Q encounters
- formal Node transitions

Safe labels:

- `baseline_target_followed`
- `shadow_target_also_sampled`
- `both_targets_sampled`
- `neither_target_sampled`
- `outcome_not_observable`

Do not claim causality.

## 12. Promotion-focused historical checks

Eligible snapshots can test whether the current Phase 11 policy would:

- miss unresolved Critical Safety evidence
- overreact to one ordinary wrong
- behave conservatively under sparse coverage
- prioritize historical `recheck_due` over J5-J7 when such evidence exists
- produce systematic or mixed disagreement patterns against Baseline

A Safety miss candidate requires complete historical formal coverage.

## 13. Limits

Retrospective replay cannot establish:

- what the learner would have done if Shadow had been shown
- causal superiority
- pass probability
- benefit of an unattempted Shadow target
- every recommendation shown during a day
- the output of an older historical version of Phase 11 code

It evaluates current-policy consistency against historical evidence.

## 14. Read-only implementation boundary

Allowed:

- SELECT learning events
- SELECT question attempts
- pure historical coverage/replay logic
- supporter diagnostics rendering

Forbidden:

- Production DB writes
- migration
- editing historical data
- selector changes
- Recent Cooldown changes
- Node-state changes
- Baseline algorithm changes
- learner-facing changes

## 15. Recommended implementation contract

Database helper:

```python
def get_learning_events(
    user_id: str,
    before: datetime | None = None,
) -> list[dict]:
    ...
```

Return chronologically:

- event_key
- user_id
- mode
- answered_count
- correct_count
- answered_at
- question_results

Mirror the local/Neon behavior style of `get_question_attempts()`.

Pure helpers:

```python
def audit_historical_attempt_coverage(
    learning_events,
    attempts,
    *,
    before,
):
    ...


def build_retrospective_shadow_audit(
    attempts,
    learning_events,
):
    ...
```

Do not place replay logic in the template.

## 16. Supporter UI

Add development-only section:

`Phase11 過去推薦リプレイ`

Summary:

- plan anchors found
- replay-eligible snapshots
- coverage-excluded snapshots
- agreements
- Shadow stronger disagreements
- Current stronger disagreements
- inconclusive disagreements
- Critical Safety miss candidates
- ordinary-single-wrong takeover candidates

Show latest 10-20 snapshots. Excluded snapshots should display an exclusion reason rather than vanish silently.

Every replay must visibly state that it applies the **current Phase 11 policy to historical learner evidence**.

## 17. Minimum tests

1. only one daily persisted plan anchor is assumed
2. supporter/read-only views create no plan anchor
3. stored Baseline field/goal are used
4. Baseline phase uses historical `SUM(answered_count)`
5. activity events with answered_count 0 do not alter phase
6. answered_count>0 with missing formal results makes coverage incomplete
7. missing attempt rows make coverage incomplete
8. matching results/attempts make coverage complete
9. activity-event dicts are not formal attempts
10. future attempts do not leak backward
11. current-policy replay label is present
12. unknown does not create confirmed weakness
13. agreement
14. Shadow stronger disagreement
15. Current stronger disagreement
16. equal-rank disagreement is inconclusive
17. Safety miss candidate requires complete history coverage
18. one ordinary wrong does not become false confirmed weakness
19. future recheck state does not leak backward
20. no DB write helper
21. no exact-Q selector call
22. learner-facing unchanged
23. existing Phase 11 tests remain green

## 18. Promotion use

Retrospective evidence can reduce uncertainty before a limited learner-facing pilot, especially for safety and rule consistency.

It does not replace prospective natural-use evidence. Final promotion should combine:

- eligible current-policy historical replay
- current natural-use diagnostics
- prospective limited-pilot evidence when approved

This gains evidence faster without fabricating learning activity or overstating incomplete history.
