# Phase 11 Session-load Bundle Wiring Plan v0.1

Date: 2026-09-06
Status: implementation boundary recorded; no learner-facing policy change

## Purpose

The same-day session-load helper is now production-safe as a read-only fact builder, including explicit long-gap evidence. The next integration step is to expose these facts through the existing Supporter-only Phase11 promotion evidence bundle without changing learner-facing behavior.

## Required wiring

`pilot_diagnostics.build_pilot_diagnostics` should:

1. call `build_same_day_session_load_facts(all_attempts, as_of=now)`;
2. include the returned dict in the Supporter diagnostic result as `same_day_session_load`;
3. pass it into `build_phase11_promotion_evidence_text` through a new optional argument;
4. serialize only non-identifying facts such as date, answer count, accuracy, unique-question count, first/repeat accuracy, repeat share, study-day span, maximum inter-attempt gap, and cumulative-block accuracy delta.

The promotion bundle change must remain backward-compatible when session-load facts are absent.

## Non-negotiable boundary

The integration must not:

- change J1-J7 decision ordering;
- select exact questions;
- change Phase10 weights, Safety, repair evidence, or Recent Cooldown;
- infer fatigue from the same-day block decline;
- convert a long gap into an automatic session boundary policy;
- expose user IDs, tokens, consultation content, or private identifiers;
- write to Production learner data.

## Acceptance tests

- bundle contains deterministic same-day-load facts when supplied;
- bundle has safe `none`/zero defaults when absent;
- no identity/token/consultation fields are added;
- `build_pilot_diagnostics` returns same-day facts for the requested learner using all same-day attempt history;
- existing promotion-bundle and pilot-diagnostic tests remain green.

This plan exists so the integration can be implemented as a narrow change to the existing diagnostics surface rather than introducing a second recommendation path.
