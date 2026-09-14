# PT learning strategy v0.1 — Stage C/D/E, Shadow only

Runtime preparation update: `PT_LEARNING_STRATEGY_RUNTIME_PILOT_V1.md` specifies
the separate default-OFF LINE adaptive30 adapter. Stage E remains a pure field
strategy; the existing selector supplies all Q candidates. Safety/due/#342 slots
and repeat exclusions override the soft field target. No Production activation.

Stage F.2 update: see `PT_LEARNING_STRATEGY_STAGE_F2_20260914.md`.
PASS WITH CONDITIONS permits separate default-OFF pilot preparation only.
PR #348 requires bank supply>=60 as well as answer/spread sufficiency; repeated
answers from smaller banks cannot establish weak/strong. PR #349 context uses
completed recommendation questions before the decision, floored at /30; goals
and generic study counts are not completions. Additional weakness blocks remain
unavailable. Historical Stage F status below describes the pre-#348 audit.

Status (2026-09-14): deterministic code and synthetic/fixture tests exist.
Natural-history comparison is now recorded in
`PT_LEARNING_STRATEGY_STAGE_F_AUDIT_20260914.md`: HOLD / NOT YET, 85 checkpoints,
85/85 eligible30 supply, but missing block context and two small-bank policy
conflicts prevent promotion. Raw Stage B/D/E semantics remain unchanged. This is
not a claim of improved exam outcomes or an estimate of passing probability.

## Boundary and input contract

Formal truth remains `question_attempts -> derived Knowledge Node state ->
field / strategy / readiness -> selector / presentation`.

`build_learning_strategy(evidence_bundle, progress_bundle, context_by_field=...,
days_to_exam=...)` consumes the existing `build_field_evidence` and
`build_field_progress` output shapes. It requires exactly one aligned row for
each field 1-18; mismatched state totals/scores/field IDs, negative counts and
non-finite values are rejected. Inputs are not mutated. It does not import the
DB-backed field-evidence adapter, load the bank, call services, or use the clock.
Callers must provide one learner's snapshots derived at the same observation time.
Canonical Nodes belonging to several fields retain existing per-field membership;
this strategy does not sum field counts into a unique learner total.

The separately gated LINE adaptive30 adapter can now call the pure modules for
explicit pilots; OFF/non-pilot preserves the original behavior. `today_action`,
the existing selector implementation, #337/#342, Recent Cooldown, Safety rules,
DB schema and learner presentation are unchanged. Pilot field preference and
metadata are described in the runtime contract above.
Phase11 remains HOLD / Shadow only. Every strategy/target output has
`shadow_only=True`, `selection_authority=False`.

## Stage B: evidence, state and recovery (unchanged)

`field_evaluation_shadow.evaluate_field` remains the classification authority.
Require >=60 evaluable answers AND Canonical Node spread. Required spread is
`min(total_nodes, 60, max(6, ceil(total_nodes * .35)))`, or zero for empty supply.
Zero-node supply cannot be sufficient. Before sufficiency the state is
unassessed/assessing, never weak/strong; high accuracy alone is insufficient.

After sufficiency: critical Safety, accuracy <.65, repairing/touched >=.25, or
>=2 repeated-weakness evidences mark weak. Strong requires accuracy >=.80,
repairing/touched <=.10, resolved/touched >=.60, and no weak reason. Otherwise
ordinary. Resolved includes repaired, recheck_due and stable; these are distinct
from durable stable state.

Weak re-evaluation points remain 90, 120, 150, ... after the 60-answer floor.
These are review points, not automatic consecutive allocations. Recovery follows
the existing different-Q repair / spaced recheck semantics: provisional recovery
requires resolved/touched >=.40 and a different-Q repair confirmation, with no
critical Safety; durable recovery requires stable/touched >=.40, no repairing
Nodes and no critical Safety. Recovery metadata is not a substitute for the
separate evidence-sufficiency gate.

## Stage C: audited repository frequency, not recent-year prevalence

PR #345 provides `exam_weight_shadow`: 900 original and 1100 past_exam records.
Per-field past-exam counts in field-ID order:
`137,152,15,22,6,34,63,118,65,35,16,13,50,5,25,53,87,204`.
Relative weight is `count / 1100 * 18`, arithmetic mean 1.0. A repository-data
test re-counts the formal questions/tags, so a changed bank cannot silently drift
from these versioned constants.

Explicit year provenance is audited for 36 items; 1064 remain a provenance gap.
No 5y/10y/20y windows, recent increases or volatility are invented. This is a
provisional repository sampling proxy, not an official national-exam blueprint.
The inherited C field `temporal_adjustment=1.0` is a **neutral multiplier**;
`temporal_adjustment_available=False` means no year adjustment. Stage E reports
`temporal_adjustment=False` explicitly. All weights remain provisional.

## Stage D: first-pass budget, targets, review ceiling and maintenance

`field_learning_target_shadow` separates **first-pass allocation** from
**classification sufficiency**. `minimum_initial_questions=min(60, field supply)`
varies with actual question supply; `minimum_node_spread` uses the Stage B rule.
`classification_question_floor=60` is never lowered. E.g. a 15-question field can
finish its first pass in 15 answers but cannot be declared strong/weak then.
Further evidence must accrue through legitimate later learning, not repetitions
that violate the existing 72-hour guard. Static field supply does not imply
currently eligible question supply.

Let `w=relative Exam Weight`, `W=w/(1+w)`. Provisional policy targets are:

| Target | Formula | Denominator |
| --- | --- | --- |
| Progress | .60 + .20W | All canonical Nodes in the field |
| Stable ratio | .40 + .20W | Touched Nodes |
| Resolved ratio | .60 + .20W | Touched Nodes |

These targets do not rewrite current Field Progress or displayed attainment.
Weakness and priority remain separate. Even strong fields may have coverage,
attainment or retention deficits.

Additional weak-field review budget: 30 questions per block, maximum 3 blocks.
At the cap, ordinary further allocation is disabled pending strategy review,
even if progress gain is unknown. Stage B's `strategy_change_candidate` remains
its narrower rule: weak + >=3 completed additional blocks + observed gain <.03.
Critical Safety can override the allocation cap, with both Safety and cap reasons
retained; the recommendation is safety review, not permission for repeat-Q use.

Maintenance interval is 7 days when relative weight >=1, otherwise 14 days.
Maintenance is needed on recheck_due, an observed stable-ratio decline, or elapsed
days reaching that interval. Without timing data, no elapsed days are invented.

Optional per-field context consists of observed:
`critical_safety_unresolved_count`, `additional_blocks_completed`,
`consecutive_field_blocks`, `previous_progress_score`, `previous_stable_ratio`,
`days_since_last_field_study`.
The progress baseline must be the start of the reviewed additional-learning
window; total lifetime answers are not silently treated as consecutive blocks.
Missing Safety context is explicitly `safety_evidence_available=False`, not
proof that the field is safe. Missing timing remains unavailable. These gaps
must be filled by audited history adapters before promotion; none are wired here.

## Stage E: components and priority

All components are bounded to [0,1]:

- Weakness: max(repairing ratio, normalized deficit below .80 accuracy,
  .5 when repeated weakness is present); forced to zero before evidence suffices.
- Attainment gap: maximum relative deficit against the three Stage D targets.
- Coverage gap: maximum of untouched-Node ratio and deficit against 60 answers.
- Exam weight: W above.
- Retention: maximum of due/touched ratio, observed stable-ratio drop and .5
  when maintenance is needed.
- Safety: 1 if unresolved critical Safety is explicitly observed, otherwise 0.
- Concentration penalty: min(consecutive field blocks / 3, 1); 1 at additional cap.
- Time urgency: max(0, (90-days_to_exam)/90), capped at 1. Missing time is neutral
  and marked unavailable. Time-to-exam is not historical exam-year weighting.

For weakness A, gap G, coverage C, weight W, retention R, penalty P, urgency U:

```
B = .15A + .20G + .30C + .20W + .15R
normal_priority = clamp(B * (.5 + .5W) + .10U * max(G*W, R) - .20P, 0, 1)
critical_priority = 1 + normal_priority
```

A weighted sum avoids the zero-factor failure of pure multiplication. Weight
modulation allows a high-weight under-covered ordinary/assessing field to outrank
a low-weight mild weak field. Critical Safety has a separate top tier, so it
cannot be cancelled by concentration. Coefficients are explicit v0.1 hypotheses
requiring natural-use evaluation, not fitted or clinically validated constants.

Fields sort by score descending, then field ID ascending for deterministic ties.
The top **eligible** positive-score field is recommended. Capped fields remain
visible in ranking with `allocation_candidate=False`; they cannot receive an
ordinary further block. Empty-supply fields cannot be selected. Fully maintained,
target-met fields without retention need have zero score. If no candidate remains,
return `defer`, null field ID/name, and count 0 rather than inventing work.

A recommendation has version/gates, field ID/name, candidate count 30, intent,
component scores, reason codes and the complete 18-field ranking/targets.
Intents are shadow-only (`coverage`, `repair`, `retention`, `attainment`,
`maintenance`, `safety_review`, `strategy_change`, `defer`), not Production commands.
Thirty is a budget hypothesis, not a guarantee of 30 eligible same-field Qs.
`question_selection_required=True` and `current_eligible_question_supply_checked=False`
are explicit; existing selector/availability guards would still own actual Qs.

## Validation and promotion gate

Unit tests cover Stage B's 60/spread/state/recovery rules, C's exact formal source
counts and neutral temporal treatment, D's supply/targets/cap/maintenance, and E's
Safety/weight/coverage/concentration/retention/time/deterministic output. Fresh
interpreter tests block runtime/DB/network/write dependencies. Existing #337,
#342 and selector/repeat tests are run unchanged, along with the bank validator
and full suite under empty DATABASE_URL and dummy service credentials.

Before any future selection/presentation wiring:
1. Replay aligned natural learner histories through the current and shadow models.
2. Collect explicit Safety, concentration-window, timing and marginal-gain context.
3. Compare ranking/reasons, maintenance due, high-weight coverage gains and field
   overconcentration; review small-supply fields without relaxing repeat guards.
4. Confirm zero new 72h same-Q/exact-equivalent repeats, no Safety regressions,
   and feasible candidate supply. Initial-assessment natural samples remain pending;
   synthetic tests must not be represented as Production acceptance.
5. Agree acceptance thresholds and rollback, then obtain a separate promotion
   decision. Stage C/D/E code completion does not promote Phase11 or change authority.
