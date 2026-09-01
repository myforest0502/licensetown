# Phase 11 Retrospective Shadow Audit v0.1

Date: 2026-09-02
Status: design fixed / implementation pending

## 1. Purpose

Accelerate Phase 11 promotion evaluation without manufacturing Production activity and without adding a new write path.

The system already stores one daily `recommendation_plan` activity event when the learner opens the dashboard and a baseline recommendation exists. That event contains the baseline target field and question goal, together with the event timestamp.

For each stored historical recommendation snapshot, replay Phase 11 using only attempts that existed at that time and compare the reconstructed Shadow decision with the baseline recommendation that was actually stored.

This is retrospective observational QA. It is not a causal proof that one recommendation would have produced a better examination outcome.

## 2. Why this is valid

Existing data is sufficient to reconstruct the evidence state before a recommendation snapshot:

- `learning_events` contains `recommendation_plan` activity events
- the plan metadata contains `field` and `goal`
- the event has `answered_at`
- `question_attempts` contains timestamped formal attempts
- `build_field_evidence(attempts, as_of=...)` supports an explicit historical time
- `build_shadow_judgment(...)` accepts `as_of`
- current-vs-Shadow comparison is now symmetric

No Production event needs to be fabricated.

## 3. Snapshot anchor

Use only persisted activity events where:

- `mode = 'recommendation_plan'`
- `question_results` is an object
- `question_results.activity_type = 'recommendation_plan'`
- `question_results.field` is present
- `answered_at` is present

`record_activity_event()` creates a JST daily event key, so at most one persisted recommendation-plan anchor per learner/day is expected.

Do not invent missing historical plans.

## 4. Historical attempt cutoff

For each plan event at timestamp `T`:

- include attempts with `answered_at < T`
- exclude attempts at or after T
- preserve unknown attempts in the history
- unknown attempts must still not create confirmed weakness

Use the stored plan time as `as_of=T` for retention/state calculations.

This prevents future attempts from leaking backward into the historical Shadow judgment.

## 5. Reconstructed current guidance control

Do not rerun the present-day baseline algorithm and pretend it was the historical recommendation.

The historical baseline target must come from the persisted `recommendation_plan` event.

Construct the minimum control object needed by Phase 11 from persisted facts:

```python
{
    "phase": "foundation" if historical_total_answers < 100 else "analysis",
    "recommended_study": [(stored_field, stored_goal)],
}
```

The phase threshold follows the existing baseline foundation threshold. The stored target remains authoritative for the retrospective control.

If the stored event lacks a usable field or goal, classify the snapshot as unavailable rather than guessing.

## 6. Historical Shadow replay

For each valid snapshot:

1. truncate attempts at `T`
2. build historical field evidence with `as_of=T`
3. build Shadow judgment with `as_of=T`
4. build symmetric field evidence profiles from the same truncated attempts/evidence
5. compare persisted baseline target vs reconstructed Shadow target

Capture:

- snapshot date/time
- historical attempt count
- baseline target / goal / phase
- Shadow intent / target / question count
- Shadow reason code / confidence
- current-target formal evidence profile
- Shadow-target formal evidence profile
- comparison label
- Shadow reason/profile consistency

## 7. Outcome observation window

The retrospective audit may inspect what happened after the plan, but it must not claim causality.

Suggested window:

- attempts after plan timestamp and before the next recommendation-plan snapshot
- cap at 24 hours if no next snapshot exists

Capture observationally:

- subsequent attempt count
- fields actually attempted
- whether baseline target was attempted
- whether Shadow target was attempted
- correct / wrong / confidence counts in each target field
- same-Q repeats
- same-node different-Q attempts
- formal Node transitions observed in the window

Do not write labels such as `Shadow would have caused improvement`.

Safe wording:

- `baseline_target_followed`
- `shadow_target_also_sampled`
- `neither_target_sampled`
- `outcome_not_observable`

## 8. Promotion-focused categories

For each historical snapshot assign one diagnostic review category:

### Agreement

- same target

### Shadow stronger disagreement

- different target
- symmetric comparison says Shadow formal evidence is stronger

### Current stronger disagreement

- different target
- symmetric comparison says current formal evidence is stronger

### Inconclusive disagreement

- different target
- evidence ranks equal or profile unavailable

Never hide current-guidance wins.

## 9. Safety checks across history

Retrospective replay is especially useful for checking:

- whether an unresolved Critical Safety signal ever existed while Shadow selected a weaker J2-J7 target
- whether one ordinary wrong ever caused field takeover
- whether sparse learners were kept in coverage
- whether naturally historical `recheck_due` snapshots were selected ahead of J5-J7

These can be reviewed without waiting for future recurrence if suitable historical snapshots already exist.

## 10. Limits

Retrospective replay cannot establish:

- what the learner would have done if Shadow had actually been shown
- causal superiority of Shadow
- long-term pass probability
- whether an unattempted Shadow target would have produced better learning

It is evidence for safety/relevance consistency, not an A/B experiment.

## 11. Read-only implementation boundary

Implementation must remain read-only.

Allowed:

- SELECT recommendation-plan events
- SELECT question attempts
- pure historical reconstruction
- supporter diagnostics rendering

Forbidden:

- new Production DB writes
- migration
- changing historical events
- selector changes
- Node-state changes
- baseline recommendation changes
- learner-facing changes

## 12. Suggested implementation

Prefer pure helpers such as:

```python
def build_retrospective_shadow_audit(attempts, recommendation_plan_events):
    ...
```

and a SELECT-only database helper for recommendation-plan events.

Do not put reconstruction logic into the template.

## 13. Supporter UI

Add a development-only section to `/supporter/pilot-diagnostics`:

`Phase11 過去推薦リプレイ`

Summary:

- valid snapshots
- agreements
- Shadow stronger disagreements
- current stronger disagreements
- inconclusive disagreements
- Critical Safety miss candidates
- ordinary-single-wrong takeover candidates

Show the latest 10-20 snapshots with expandable evidence profiles.

## 14. Minimum tests

1. attempts after snapshot do not leak into replay
2. stored baseline target is used, not current recalculation
3. under-100 snapshot reconstructs foundation phase
4. unknown does not create weakness
5. same-target agreement
6. Shadow-stronger disagreement
7. current-stronger disagreement
8. inconclusive disagreement
9. Critical Safety historical candidate detected
10. ordinary single wrong does not become a false confirmed weakness
11. future recheck state does not leak backward
12. no DB write helper
13. no selector call for exact-Q selection
14. no learner-facing change
15. existing Phase 11 tests remain green

## 15. Promotion use

Retrospective evidence can reduce uncertainty before a limited learner-facing pilot, especially for safety and rule-consistency checks.

It does not replace prospective natural-use evidence. Final promotion should combine:

- retrospective historical replay
- current natural-use diagnostics
- prospective limited pilot evidence when approved

This avoids waiting unnecessarily while also avoiding fabricated Production learning events.
