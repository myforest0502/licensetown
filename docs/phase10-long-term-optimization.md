# LicenseTown ⑩ 長期最適化 — 正式仕様メモ

Date: 2026-09-01
Status: runtime invariants fixed; natural-use observation and static audit refresh remain before formal Phase 10 closure.

This document records architecture and QA rules. It does not change runtime behavior.

## 1. Formal Node-state invariants

States:

- unseen
- checking
- repairing
- repaired
- recheck_due
- stable

Repair evidence rules:

- same-Q success alone does not advance repairing to repaired
- weak different-Q success alone does not advance repairing to repaired
- strong different-Q + correct + confidence1 advances to repaired
- wrong/unknown returns unresolved material to repairing

Retention:

- repaired after 7 days -> recheck_due
- stable after 30 days -> recheck_due
- recheck_due + strong different-Q + correct + confidence1 -> stable
- wrong/unknown -> repairing

Written confirmation and AI semantic confirmation remain diagnostic/research aids only; they are not formal repair evidence.

## 2. Canonical Knowledge Node rule

Historical Node IDs are preserved and resolved to canonical roots. State/evidence calculations operate on canonical Nodes rather than treating approved aliases as independent knowledge units.

Current formal counts from Phase 10 research:

- canonical Nodes: 1509
- singleton canonical Nodes: 1462
- multi-question canonical Nodes: 47
- strong different-Q repair possible: 3
- weak-only different-Q: 44
- formally unrepairable under strong-evidence rule: 1506

This high singleton rate is a structural fact of the current bank and must be considered in adaptive QA.

## 3. Recent Question Cooldown v0.2

Recent means the newest maximum 30 attempts ordered by answered_at.

Policy order:

1. Safety emergency exception
2. non-recent repair/checking/exploration candidates
3. non-recent maintenance/other candidates to complete the requested count
4. recent candidates only if the requested count cannot otherwise be filled

The 15/10/5 repair/checking/exploration composition for a 30-question session is a soft target. Recent questions are not reintroduced merely to satisfy that ratio.

Explicit `exclude_ids` are absolute and never return through fallback.

Safety singleton exception:

- prefer non-recent strong different-Q
- then non-recent weak different-Q
- only if no non-recent alternative exists may recent same-Q be reused

A cooldown bypass must be auditable.

## 4. Adaptive selection audit — merged

Merged on main in:

`9a0d4a0dbf3c087808040a7c2722862be4cc9c40`

For adaptive_daily Node-adaptive selections, the learning event result may persist exactly these lightweight fields:

- selection_reason
- selection_group
- selection_score
- repair_evidence_quality
- recent_question_repeat
- recent_cooldown_bypassed

This metadata is for post-selection explanation and QA. It does not mutate Node state and does not become question-attempt evidence.

Non-adaptive random/manual/dashboard/nekketsu flows do not receive this adaptive selection metadata.

## 5. Responsibility boundary

Phase 10 selector decides exact candidate questions. It owns:

- Safety ordering within candidate selection
- repair evidence preference
- Node diversity
- recent cooldown
- fallback behavior
- exact Q selection

The future Phase 11 judgment layer decides intent and scope, not Q IDs. It must not duplicate or override Phase 10's formal Node-state rules.

## 6. Real-use QA invariants

Red flags:

- consecutive adaptive sessions overlap when enough non-recent bank exists
- recent_cooldown_bypassed without Safety or true supply shortage
- duplicate Q inside one session
- excluded Q returns
- recent same-Q chosen while usable non-recent different-Q exists

Observed overlap is not automatically a bug if the audit metadata proves a valid Safety/supply fallback.

## 7. Phase 10 closure gate

Code-level work is structurally complete when:

- cooldown v0.2 is on main
- audit-lite is on main
- regression tests preserve state/repair/retention behavior
- static Q1-Q1594 tag audit is current

Operational closure additionally requires at least one natural post-deploy adaptive session showing that production history contains the audit fields and that any overlap is explainable.

Do not create synthetic Production DB records solely to close the gate.

## 8. Phase 11 handoff

Phase 11 begins as deterministic, read-only shadow judgment. It may use:

- field evidence
- formal Node-state distribution
- confident/repeated wrong evidence
- recheck_due evidence
- coverage shortage
- uncertain-correct evidence
- recent learning volume/context
- recommendation plan/progress
- Phase 10 selection audit for consistency checks

It must not:

- consume consultation text
- infer mastery from selector score
- mutate Node state
- hard-code exact question IDs
- replace learner-facing guidance until shadow evidence supports promotion
