# Phase 11 Promotion Review Runbook

Date: 2026-09-02
Status: implementation-ready review procedure; learner-facing promotion still gated by Production/natural-use evidence.

This runbook defines exactly what to inspect before deciding whether Phase 11 may move from Shadow-only diagnostics to a limited learner-facing pilot.

## 1. Preconditions

Do not start promotion review unless all are true:

- main includes the current formal Phase 11 policy
- Question Bank validator passes through Q1605
- Phase 10 Recent Cooldown remains unchanged
- saved adaptive session completeness diagnostics are green
- Supporter diagnostics are read-only
- learner-facing Baseline recommendation is still authoritative

## 2. Production evidence to collect

### A. Current Shadow snapshot

Record:

- Baseline target field
- Shadow target field
- Shadow reason_code / confidence
- current target strongest formal evidence
- Shadow target strongest formal evidence
- symmetric comparison label
- current and Shadow evidence counts
- evaluable answer count / accuracy percent / Node coverage for both fields

Review both agreements and disagreements.

### B. Repeat Structure Audit

Record:

- total attempts
- unique Q
- same-Q repeats
- justified cooldown bypass count
- adaptive spaced repeat count
- adaptive unexplained recent repeat count
- metadata inconsistent count
- non-adaptive repeat count
- audit metadata unavailable count

Promotion red flag:

`recent_question_repeat=True` with `recent_cooldown_bypassed=False`.

Do not classify legitimate non-recent checking/recheck as a regression.

### C. Saved adaptive_daily session audit

Record:

- session_status
- parsed set numbers
- event-key parse failures
- event count
- question count
- unique Q count
- audit-fields-complete status
- recent repeat Qs
- cooldown bypass Qs

Expected healthy complete session:

- status `complete`
- set numbers 1,2,3,4,5,6
- parse failures 0
- events 6
- results 30
- unique Q 30

### D. Retrospective Shadow Replay

For every eligible recommendation_plan anchor, record:

- anchor timestamp
- persisted Baseline target
- reconstructed Baseline phase
- replayed Shadow target/reason
- symmetric comparison label
- coverage status
- exclusion reason if ineligible

Review all eligible snapshots, not only Shadow-favorable cases.

### E. Safety

Check for any case where:

- unresolved Critical Safety evidence exists
- but Phase 11 chooses a lower-priority field

Target for a limited pilot: no recurring Critical Safety miss pattern.

Safety unknown remains unresolved evidence and may retain high priority, but it must not be labeled as confirmed `safety_wrong` unless an evaluable wrong exists.

### F. Single-wrong overreaction

Look for ordinary non-Safety single wrongs that cause field takeover without cluster/cycle evidence.

Target: no repeated pattern.

### G. Sparse coverage

When a learner lacks sufficient evaluable evidence, verify that Phase 11 favors useful coverage rather than manufacturing weakness from zero-answer attempts or sparse accuracy.

### H. recheck_due

When naturally present, verify that J4 work is not starved by J5-J7.

Do not manufacture Production events to create this case.

### I. Intent vs exact Q selection

Compare Phase 11 intent with Phase 10 exact selection:

- repair intent should lead to directionally appropriate repair candidates
- recheck intent should preserve retention work
- coverage intent should not violate Safety/cooldown

Phase 11 does not own exact Q IDs.

### J. Repair-transition quality

If Q1595-Q1605 produce `repairing -> repaired`:

- verify formal mechanics separately
- consult `docs/strong-repair-pilot-content-audit-v01.md`
- do not treat a structurally STRONG but low-discrimination item as full educational validation

## 3. Evidence table

For each reviewed natural or retrospective case, capture:

| Timestamp | Baseline | Shadow | Shadow reason | Comparison | Safety issue | Single-wrong issue | Coverage issue | recheck_due | Intent-vs-Q | Repeat red flag | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|

Verdict values:

- PASS
- REVIEW
- FAIL
- INELIGIBLE_HISTORY

## 4. Limited-pilot decision rule

A limited feature-flagged learner-facing pilot may be considered only if:

- corrected Production repeat audit shows no unexplained recent-repeat regression
- no Critical Safety miss pattern appears
- no systematic single-wrong overreaction appears
- sparse coverage is acceptable
- recheck_due behavior has been observed and is not starved
- Phase 11 intent and Phase 10 selection are compatible
- retrospective review includes Current/Baseline wins as well as Shadow wins
- prospective natural examples are clearly no worse than Baseline
- repair transitions are interpreted with item-quality caution

If evidence is mixed or thin, remain Shadow-only.

## 5. What does not count as promotion proof

Do not promote based on:

- one favorable screenshot
- one Shadow win
- one high-confidence reason_code
- raw selector score
- one repaired transition
- structural STRONG status alone
- sparse 100% accuracy from very few evaluable answers
- retrospective replay alone

## 6. Current blocker

The current Neon connector cannot perform the pending Production re-read because the exposed argument schema and execution schema disagree before SQL execution. This is an external tooling blocker. Failed connector attempts did not execute Production SQL and did not write Production data.

Until Production evidence is accessible, continue Shadow-only operation and natural use without manufacturing evidence.
