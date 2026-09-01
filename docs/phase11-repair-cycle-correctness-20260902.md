# Phase11 Repair-Cycle Correctness Gates — 2026-09-02

Status: diagnostics / implementation preparation only. Learner-facing Phase11 promotion remains blocked.

## Core invariant

A completed formal repair cycle must not remain a permanent active weakness.

Active Phase11 J1-J3 weakness is defined from the **current formal repair cycle only**.

- historical wrongs before a completed `repaired` / `stable` boundary are historical context
- time-only `recheck_due` is retention work (J4), not automatic revival of historical J1-J3 weakness
- a new wrong/unknown after a completed repair starts a new repair cycle
- unknown may trigger unresolved `repairing` state but is not confirmed weakness
- if recurrence across completed cycles becomes useful later, design an explicit relapse/recurrence signal rather than silently reusing all-history weakness

## Confirmed correctness issue — failed recheck reset

Issue #19.

Current state-machine code previously reset `repair_wrong_questions` after wrongs from `repaired` / `stable`, but not when the previous state had already become `recheck_due` at the attempt timestamp.

Risk: after a failed retention check, a later answer could be STRONG relative to an old pre-repair wrong while only SAME/WEAK relative to the newly failed recheck Q, allowing a false `repairing -> repaired` confirmation.

Prepared stacked draft:

- PR #21 — shared current-repair-cycle helper
- PR #22 — add `recheck_due` to the repair-reference reset boundary

PR #22 production-code change is intentionally one condition only. It remains unmerged until executable tests are available.

## Confirmed Phase11 issue — stale historical weakness

Issue #20.

Current `judgment_shadow.py` derives repeated weakness from all historical evaluable attempts. That can allow old CROSS_QUESTION_WRONG / CROSS_QUESTION_CONFIDENT_WRONG evidence from a completed repair cycle to affect current J1-J3 decisions.

Approved semantics:

1. derive each Node's current formal repair cycle
2. if current state is not `repairing`, active J1-J3 repair-cycle evidence is empty
3. filter unknown from confirmed weakness
4. classify repeated/cross/confident weakness only inside the current cycle
5. use the same active evidence in both `build_shadow_judgment()` and symmetric field profiles

Prepared infrastructure:

- PR #23 — `phase11_active_weakness.py`

PR #23 does **not** change Phase11 recommendations yet. It fixes the evidence contract first.

## Evaluable evidence interaction

Separate but related issues:

- #6 — unknown must not enter repeated-weakness field evidence
- #11 — J2 accuracy tie-break uses evaluable answers/accuracy
- #12 — J5 field sufficiency uses evaluable coverage
- #13 — J6 uncertain-correct threshold/proportion uses evaluable denominator
- #18 — J2/J3 repairing-burden tie-break uses repairing Nodes with evaluable current wrong evidence, not all repairing Nodes

Prepared evidence stack:

- PR #9 — unknown exclusion from repeated weakness
- PR #17 — `evaluable_answer_count`, `evaluable_correct_count`, `evaluable_accuracy`

Do not implement separate unknown filters independently in J2/J5/J6.

## Multi-field canonical Node attribution

Issue #24.

Generic field evidence intentionally duplicates a multi-field canonical Node into every member field for evidence display. That generic membership policy must not silently become the Phase11 field-target allocation rule.

For J1-J3, preferred attribution is based on the field/category of the **active evaluable wrong Qs** in the current repair cycle, not every static member field.

For J4, the state machine internally tracks `retention_reference_question`, but the returned state record currently does not expose it. Therefore accurate J4 source-field attribution needs derived reference-Q metadata first. Until then, multi-field J4 attribution remains ambiguous and must not be justified by numeric `field_id` alone.

## Current stacked branch order

Repair-cycle stack:

1. PR #21 — shared `current_repair_cycle` pure helper
2. PR #22 — failed `recheck_due` reset fix
3. PR #23 — current-cycle active Phase11 weakness facts
4. future integration — consume PR #23 in both Phase11 judgment and symmetric profiles (Issue #20)

Evaluable-evidence stack:

1. PR #9 — unknown exclusion from repeated weakness evidence
2. PR #17 — shared evaluable field metrics
3. future integration — Issues #11/#12/#13/#18

These stacks should be rebased/combined deliberately after tests rather than merged blindly as independent feature fragments.

## Test / CI limitation

GitHub workflow lookup for current draft heads returned no workflow runs. Local executable pytest is not available from the current connector/container path.

Therefore:

- do not merge the prepared code PRs yet
- static diff review is useful but not sufficient
- before merge, run focused tests, full pytest and Question Bank validator
- quantify whether Issue #19 changes any real derived Production Node states before treating the corrected state history as operational evidence

## Promotion consequence

Phase11 learner-facing promotion is blocked until at least:

- failed recheck repair-cycle boundary is correct
- J1-J3 use current-cycle active weakness rather than stale all-history weakness
- unknown/evaluable denominators are consistent
- multi-field field-target attribution is no longer arbitrary for active repair evidence
- repeat diagnostics Issue #4 is corrected and Production repeat history is re-read

Do not compensate for these correctness issues by tuning J1-J7 weights. The evidence semantics must be correct first.
