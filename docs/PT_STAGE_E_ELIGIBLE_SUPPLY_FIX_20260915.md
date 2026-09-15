# Stage E eligible-supply incident, 2026-09-15

Baseline main: `70374195f84eee64bd5c6dcd95515b08431a23c0`.
Scope: the existing single-user gated LINE adaptive_daily 30-question adapter.
No selector, Stage E ranking, bank, DB schema, flags or Render changes.

## Cause and reproduction

`refine_session` checked for 30 eligible evidence identities in the proposed field
and requested 30 selector records **before** retaining baseline protected slots.
Its documented soft-preference contract actually fills only the unprotected
slots. It therefore rejected enough supply for a mixed session. Four real-bank
regression cases (needed/supply 2/12, 2/11, 1/11, 2/2) fail with the original
function loaded in memory and pass with the fix.

Production SELECT-only aggregates confirm 24 batches / 120 answers / one learner
on September15 with eligible_supply_insufficient. These are four 30-question
session decisions, not 120 independent strategy decisions: app saves the session
audit on each confirmed answer. The reported evening90 are the final three.

## Numeric evidence and its limits

Bank-derived field2 selector mapping contains 187 raw Qs / 186 distinct evidence
identities. The old minimum was30; neither Safety nor intent is part of this
precheck. Safety_review maps to selector repair preference later. That later
selector call was never reached in the reported failures.

Below are SELECT-only aggregates at each session's **first confirmed batch**,
using history strictly before that batch (not a recorded exact start timestamp).
No account IDs, detailed attempts or answers were exported.

| First batch JST | Protected /30 | Slots needed | Field2 unseen evidence | After hard72h only (upper bound) | Field2 protected answers |
|---|---:|---:|---:|---:|---:|
| 08:16:54 | 28 | 2 | 12 | 159 | 0 |
| 17:49:41 | 28 | 2 | 12 | 159 | 1 |
| 18:15:16 | 28 | 2 | 11 | 159 | 0 |
| 19:00:26 | 29 | 1 | 11 | 166 | 3 |

Protected means exploration OR Safety reason OR due reason OR critical/high/
moderate tag, exactly the adapter rule. The 72h-only figures are **not** final
eligible supply: old attempted evidence remains blocked unless its derived Node
is recheck_due, and recent30 is also excluded. Saved fallback proves the actual
old precheck was below30. Unseen identities are never previously attempted or
recent; conservatively subtracting all protected field2 answers leaves at least
12/11/11/8 unused identities in these aggregates, above the 2/2/2/1 requirement.
This supports the defect without pretending the exact historical derived-state
eligible counts were saved.

Exact final eligible counts and exact recent30/retention contributions cannot be
reconstructed from these aggregates alone. Detailed history retrieval was rejected
by automatic approval review due to sensitive local-export risk; it was not
retried through another channel. Only aggregate reads continued. No claim is made
that an exact replay of all four production starts was completed. The regression
fixtures explicitly model limited supply, not invented learner history.

## Why field2 / safety_review persisted

There is no fixed field2 in the adapter or ranking. Saved components for the first
60 versus last60 answers are:

| Component | First60 | Last60 |
|---|---:|---:|
| safety_score | 1 | 1 |
| weakness_score | .5 | .5 |
| retention_score | .5 | .5 |
| exam_weight_score | .7132429614 | .7132429614 |
| coverage_gap_score | .0714285714 | .0649350649 |
| attainment_gap_score | .9484527770 | .9488107439 |
| concentration_penalty | 0 | 0 |
| time_urgency_score | 0 | 0 |

Snapshot input is formal attempts -> derived Node states -> field evidence and
progress. Unresolved critical Safety is counted through the existing selector
priority rule. Stage E adds a separate +1 Safety tier and selects safety_review;
ordinary fields cannot cancel that tier. Candidate availability is deliberately
not part of pure Stage E's score. Thus a field may remain strategically urgent
while many of its questions cannot legally be replayed. The scores change with
coverage, so metadata does not show a constant/stubbed snapshot.

Concentration context credits completed recommendation work / completed soft-pilot
work, not a fallback-labelled session's proposed field. These four sessions add
no soft-pilot completion credit. The data confirms penalty0; changing that context
contract or lowering Safety to force rotation is outside this minimal repair.
The full competing-field ranking and unresolved Node identities at each exact
start were not exported, so no stronger claim about their individual causes is
made. Keep Safety and all score coefficients unchanged.

## Minimal correction and retained behavior

1. Determine the existing protected baseline first.
2. Need only `30 - len(protected)` candidates; exclude protected evidence from
   both the supply count and selector request to avoid double counting.
3. Ask the unchanged selector for that many candidates in the same field/intent.
4. Preserve original fallback on real eligible/selector shortage or guard conflict.
5. If every slot is protected, retain baseline with no_unprotected_slots.

No category widening, adjacent-field strategy, Safety override, repeat padding or
new authority is introduced. The selector already fills other groups within its
field after its preferred intent; this remains unchanged. Protected singleton
Safety/due choices keep their original audit. Existing final guard checks remain.
Return type is the same 30 quiz objects, and metadata still uses the original
confirmed-answer JSONB path. The version remains v0.1 so existing completion
context recognizes prior pilot sessions. soft_pilot means applied field preference,
not that every question is a Safety repair or that every selected ID changed.

## Validation / release boundary

Focused tests include exact required supply, true shortage, protected overlap,
selector shortage, fully protected no-op, existing Safety/due/exploration retention,
72h/exact/recent guards, and non-adaptive route isolation. Original fixed-30
small-bank test now explicitly exhausts the field to preserve its true-shortage
intent rather than encoding the defect. No app/selector tests were weakened.
Full results are recorded in CURRENT_STATE and the PR.

Before production reflection: review CI and the mixed-slot contract; keep the
single-user gates unchanged. Observe soft_pilot/fallback by **session**, actual
field mix, Safety/due preservation, recent repeat/bypass and partial-session
completion context. Do not treat fewer fallbacks as proof of better learning.
Deployment, main merge, Phase11 promotion and pilot expansion are not performed.
