# LicenseTown ⑩ 長期最適化 — 正式仕様メモ

Date: 2026-09-02
Status: runtime/static/natural-use closure COMPLETE through Q1605; permanent regressions retained

This document records Phase 10 architecture and QA rules. It does not change runtime behavior.

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

## 2. Canonical Knowledge Node and current bank

Historical Node IDs are preserved and resolved to canonical roots. State/evidence calculations operate on canonical Nodes rather than treating approved aliases as independent knowledge units.

Current formal bank snapshot:

- Q range: Q1-Q1605
- records: 1605
- canonical Nodes: 1509
- singleton canonical Nodes: 1422
- multi-question canonical Nodes: 87
- validator: PASS

Historical snapshots:

- Q1-Q1564: singleton 1462 / multi 47
- Q1-Q1594: singleton 1433 / multi 76
- Q1-Q1605: singleton 1422 / multi 87

The bank remains singleton-heavy, so adaptive QA must continue to account for repair-evidence supply.

The old pre-Q1565 research totals (strong different-Q 3 / weak-only 44 / formally unrepairable 1506) are historical only and must not be used as current supply counts.

A later Production learner diagnostic found a much more decision-relevant snapshot among currently repairing Nodes:

- repairing: 135
- strong different-Q available: 1
- weak-only: 5
- same-Q/formally blocked: 129

This exposed a real repair-supply constraint. Q1595-Q1605 then added 11 targeted strong different-Q alternatives for existing moderate-Safety Nodes. All 11 source/new pairs classify as formal strong. Availability does not itself mark learner Nodes repaired.

## 3. Recent Question Cooldown v0.2

Recent means the newest maximum 30 attempts ordered by answered_at.

Policy order:

1. Safety emergency exception
2. non-recent repair/checking/exploration candidates
3. non-recent maintenance/other candidates to complete the requested count
4. recent candidates only if the requested count cannot otherwise be filled

The 15/10/5 repair/checking/exploration composition for a 30-question session is a soft target. Recent questions are not reintroduced merely to satisfy that ratio.

Explicit `exclude_ids` are absolute and never return through fallback.

Safety same-Q exception:

- prefer non-recent strong different-Q
- then non-recent weak different-Q
- only if no non-recent alternative exists may recent same-Q be reused

A cooldown bypass must be auditable.

## 4. Adaptive selection audit — COMPLETE

Audit-lite is on main. Adaptive_daily Node-adaptive results may persist:

- selection_reason
- selection_group
- selection_score
- repair_evidence_quality
- recent_question_repeat
- recent_cooldown_bypassed

The result payload also contains normal learning metadata such as `learning_source`; the six fields above are the adaptive audit extension.

This metadata is for post-selection explanation and QA. It does not become formal Node-state evidence by itself.

Non-adaptive flows must not receive the six adaptive audit fields.

## 5. Responsibility boundary

Phase 10 owns exact candidate selection:

- Safety ordering within candidate selection
- repair evidence preference
- Node diversity
- Recent Cooldown
- fallback behavior
- exact Q selection

Phase 11 is now implemented as a deterministic read-only judgment layer for intent and scope. It must not duplicate or override Phase 10's exact-Q/cooldown/state responsibilities.

Phase 12 is presentation only.

## 6. Natural-use closure evidence — COMPLETE

A natural adaptive_daily 30-question session confirmed:

- 6 saved learning events
- 30 question results
- 30 unique Q IDs
- all six adaptive audit fields present
- observed recent repeats/bypasses: 8
- all 8 were `safety_wrong` repair cases with same-question evidence

The eight affected Qs were:

Q8, Q379, Q1305, Q705, Q109, Q1504, Q195, Q25.

Static repairability review confirmed that all eight affected Safety Nodes had no non-recent strong alternate at that time. The observed bypasses were therefore explained by the intended Safety/supply exception rather than ordinary cooldown failure.

No synthetic Production learning events were created to close this gate.

Phase 10 is operationally closed.

## 7. Permanent Phase 10 regressions

Keep these checks even after Phase 11/12:

- enough non-recent supply -> no unnecessary recent Q
- consecutive adaptive sessions avoid recent overlap when supply permits
- Safety exception is explainable
- strong different-Q > weak different-Q > recent same-Q
- exclude_ids remains absolute
- no duplicate Q within a session
- Node diversity remains controlled
- formal repaired/recheck_due/stable transitions remain intact
- adaptive audit persistence remains intact
- unexplained `recent_cooldown_bypassed` is a red flag

A diagnostics hardening item remains open: the 30-question audit completeness check should eventually verify the expected session-set sequence rather than counts alone. This is QA robustness only and does not reopen Phase 10 closure.

## 8. Phase 11 handoff — ACTIVE

Phase 11 diagnostics are on main and may use:

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
- replace learner-facing guidance until promotion evidence supports a limited pilot

Current Phase 11 evaluation adds symmetric Current-vs-Shadow evidence profiles and is preparing retrospective replay of persisted historical recommendation plans.
