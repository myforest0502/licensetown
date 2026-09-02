# Phase 11 Promotion Evidence Bundle Operations

Date: 2026-09-02
Status: Supporter-only evidence capture path available on main.

## Purpose

`/supporter/pilot-diagnostics` exposes a one-click `PHASE11_PROMOTION_EVIDENCE_V1` copy bundle so Promotion evidence can be exported from the Production Supporter diagnostic page without manual transcription.

This bundle is a transport and review aid only. It does not change Phase 11 J1-J7 policy, Phase 10 exact-question selection, Node-state semantics, learner-facing recommendation, or promotion thresholds.

## Evidence scopes

The copied bundle intentionally preserves the page's mixed scopes:

- selected-period metrics: learning volume and Repeat Structure Audit
- current formal state: all formal history
- retrospective replay: all persisted recommendation-plan anchors, fail-closed when history coverage is insufficient
- saved adaptive audit: latest persisted adaptive_daily session

Do not interpret every line as belonging to the selected 7-day/30-day tab.

## Promotion review workflow

1. Open the Production Supporter pilot-diagnostics page for the learner.
2. Select the desired period for period-scoped metrics.
3. Use `Phase11 Promotion evidenceをコピー`.
4. Review the complete bundle, including every `replay_snapshot_*` line.
5. Review both Shadow-stronger and Current/Baseline-stronger outcomes, agreements, inconclusive cases, and coverage-excluded snapshots.
6. Treat excluded snapshots as fail-closed, not as wins for either policy.
7. Check the Promotion gate criteria in the readiness gate/evidence matrix before any learner-facing decision.

The copied text is not independent evidence by itself; its authority comes from the Production Supporter diagnostic values from which it was generated.

## Neon connector status

Direct Neon SQL read remains useful when available for deeper inspection and cross-checking. The current connector argument-schema mismatch can still prevent direct SQL before execution. This no longer blocks evidence capture from the Production Supporter page, but it can still block ad-hoc DB-level forensic queries.

No Production DB write is required by this workflow.
