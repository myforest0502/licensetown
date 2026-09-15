# PT strategy runtime pilot preparation

Stage F.2 #351: PASS WITH CONDITIONS. This is integration preparation, not
Production activation, a Phase11 promotion, or evidence of educational benefit.

## Entry and gates

Only the existing LINE `adaptive_daily` 30-question Node-adaptive entry is wired.
It still requires its existing Node-adaptive flag/allowlist. New additional gates:

- `ENABLE_LEARNING_STRATEGY_V1`: default false.
- `LEARNING_STRATEGY_PILOT_USER_IDS`: default empty; exact membership required.

No Render variable is changed. Startup logs expose only enabled/configured booleans,
never IDs. OFF, non-pilot, unsupported counts and non-Node-adaptive routes execute
their original selector call with no new event read or strategy-module import.
Web/manual/initial assessment and learner-facing navigation remain unchanged.
The first controlled pilot is the existing LINE adaptive30 route, not all surfaces.

## Decision and selector contract

The existing selector first creates the baseline and its selection audit.
Only after successful baseline creation do opted-in calls read existing learning
events and derive formal attempts -> Node -> evidence -> progress -> Stage B/D/E.
Stage E outputs field/intent/score/reasons only; it never outputs question IDs.
Its pure shadow/authority flags remain unchanged. The pilot adapter requests
candidate questions from the existing selector using the field and mapped intent.

Verified completed Web recommendation sessions and completed metadata-labelled
pilot sessions supply consecutive-field context through #349. Goals are not
completion. New pilot sessions contain mixed safety/exploration fields; only
actual questions mapped to the proposed field are credited toward its streak.
Partial pilot sessions fail closed. Missing history/context or malformed evidence
returns to the already-built baseline. Additional post-weakness blocks, historical
progress baseline and individual exam date are not fabricated.

The adapter preserves all baseline exploration choices (#342 floor), Safety-tagged
questions, Safety-reason choices and due-retention choices. Only remaining slots
are filled from existing selector candidates for the strategic field. This is a
soft field preference: protected slots can make the actual mix differ from30
questions in the proposed field. Protected choices keep their original metadata.

Both candidate supply and final set respect the existing formal blocked evidence,
hard72h/exact-equivalence and recent30 cooldown. Supply is checked against
`30 - protected_baseline_count`, excluding protected evidence identities from
the candidate pool. The selector is asked for that remaining count, with the
same field and intent. Eligible supply below that count, selector shortage,
invalid final set or a strategy exception uses the original
baseline. No guard is relaxed to make a strategy fit. Baseline safety behavior
and its fallback contract are unchanged. No selector code is modified.

The original fixed-30 precondition over-rejected mixed sessions; the September15
incident had only 2/2/2/1 unprotected slots. Fully protected sessions retain the
baseline with `no_unprotected_slots`, rather than claiming soft-pilot activity.
There is no new adjacent-field or intent fallback: the selector's existing
within-field group fill remains, and an actual shortage returns the baseline.
Details: `PT_STAGE_E_ELIGIBLE_SUPPLY_FIX_20260915.md`.

## Persistence and observation

Existing adaptive selection metadata carries strategy version, proposed field,
intent, priority score/components/reasons and soft_pilot/fallback disposition.
It is saved only through ordinary confirmed-answer batches in existing JSONB.
No schema, migration, new database write path or audit-triggered write is added.
No learner identifiers are added to logs or audit artifacts.

## Validation and activation conditions

Tests cover OFF/non-pilot lazy behavior, pilot exception fallback, actual strategy
snapshot, field handoff, Safety/due/#342 preservation, supply fallback, hard72h/
equivalence exclusions, incomplete/goal-only completion context, and metadata
reaching the existing batch payload. Local full suite passed1458 tests,6 skipped,
1 deselected,141 subtests; the final11-test adapter suite also passed after two
additional completion cases. Validator:2000 records,0 issues. CI reruns the full
final suite before merge; the same-SHA auto-deploy is checked afterward.

Enabling a real pilot requires a **separate explicit activation decision**, an
agreed exact target and observation window, verified completion history, review
of fallback/field/Safety/repeat metadata, and a rollback decision (flag OFF).
No need to manufacture data or rewrite histories to satisfy context. A stopped
partial pilot session may keep later calls on baseline until its context is
resolved; this is deliberate fail-closed behavior, not a completion claim.
Single-learner replay does not establish learning gains, coverage noninferiority,
or long-run concentration outcomes. Those remain prospective pilot conditions.
