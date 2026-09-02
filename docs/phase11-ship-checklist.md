# Phase 11 Ship Checklist

Date: 2026-09-02
Status: diagnostics/formal-policy ship COMPLETE / learner-facing promotion NOT YET APPROVED

## A. Diagnostics-only implementation gate — COMPLETE

All implementation safeguards are satisfied:

- judgment is deterministic/read-only
- J1→J7 formal policy is covered by tests
- current-vs-Shadow comparison is symmetric
- current repair-cycle weakness is separated from old repaired weakness
- unknown is separated from confirmed weakness
- evaluable-answer evidence is available for Phase 11 coverage/tie-break semantics
- recheck_due failure resets the formal repair cycle
- retention-reference metadata is explicit
- retrospective Shadow replay is implemented and fail-closed for incomplete history
- repeat diagnostics distinguish spaced adaptive repeat from true recent repeat-without-bypass
- saved adaptive_daily session completeness validates one session, set numbers 1..6, 30 result rows, and 30 unique Q
- Supporter diagnostics exposes the relevant completion/repeat/replay evidence
- learner dashboard recommendation remains unchanged
- no Phase 11 Production DB write is introduced
- no adaptive selector ownership transfer occurs
- consultation content is absent from inputs
- full QA passes apart from the known unmanaged external fixture exclusion
- Question Bank validator passes through Q1605

Phase 11 diagnostics/formal-policy implementation is therefore shipped on main.

## B. Phase 10 dependency — COMPLETE

Phase 10 no longer blocks Phase 11 evaluation.

Natural adaptive use previously confirmed:

- audit metadata persistence
- six adaptive sets / 30 saved results / 30 unique Q
- repeat/bypass explainability
- observed bypasses were Safety same-question cases explained by bank supply at that time

The later diagnostics hardening prevents future false PASS but does not invalidate the already inspected natural session.

## C. Learner-facing promotion gate — OPEN

Phase 11 must NOT yet replace Baseline learner-facing recommendation.

Remaining gates are evidence gates:

- no Critical Safety miss pattern
- no repeated ordinary single-wrong takeover
- sparse-coverage behavior remains useful
- naturally occurring recheck_due work is not starved
- Phase 11 intent and Phase 10 exact-Q behavior are compatible
- disagreement review includes both Shadow and Current/Baseline wins
- corrected Production repeat audit has no true recent-repeat-without-bypass regression
- eligible Production retrospective replay has no policy-consistency regression
- prospective natural recommendations are clearly no worse than Baseline
- formal pilot repair transitions are interpreted with the completed Q1595-Q1605 content-quality caution

Production repeat/replay re-reading is currently blocked by the Neon connector argument-schema mismatch before SQL execution; this is not a LicenseTown DB/schema defect and no Production SQL/write occurred from the failed connector attempts.

## D. Promotion decision

Possible outcomes after evidence review:

1. remain diagnostics-only
2. adjust formal policy and continue Shadow evaluation
3. start a **limited feature-flagged learner-facing pilot**

Do not jump directly to full replacement.

See:

- `docs/phase11-shadow-evaluation.md`
- `docs/phase11-promotion-evidence-matrix.md`
- `docs/phase11-retrospective-shadow-audit-v01.md`
- `docs/strong-repair-pilot-content-audit-v01.md`
