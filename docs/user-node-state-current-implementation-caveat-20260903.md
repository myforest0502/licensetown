# `user_node_state` current implementation caveat — 2026-09-03

Status: documentation clarification only. No Production DB write or learner-facing behavior change.

## Summary

The architectural target remains that `user_node_state` is a rebuildable materialized learner state derived from durable attempt evidence. The current implementation does **not yet fully satisfy that target**.

As of 2026-09-03, the authoritative evidence for formal Knowledge Node states is:

`question_attempts` → `knowledge_node_state_transition.py` → `field_evidence.py`

Do not treat the persisted `user_node_state.state` column as authoritative for `repaired`, `recheck_due`, or `stable` until Issue #103 is resolved and persisted-vs-derived parity is proven.

## Why this caveat exists

The formal pure state engine supports:

- `unseen`
- `checking`
- `repairing`
- `repaired`
- `recheck_due`
- `stable`

It also implements the formal evidence/timing rules, including:

- wrong answer → `repairing`;
- confidence=1 + STRONG different-question confirmation after a wrong answer → `repaired`;
- repaired retention review after 7 days;
- stable retention review after 30 days;
- due + confidence=1 + STRONG different-question confirmation → `stable`;
- wrong after repair/stability → `repairing`.

The current persistence path in `database.py` is simpler. `record_learning_batch` records attempt facts and updates `user_node_state`, but the persisted state update does not execute the full formal state derivation. A correct new row starts as `checking`; a wrong answer sets `repairing`; subsequent correct attempts do not currently materialize the full repaired/retention/stable transitions.

Read-only Production inspection on 2026-09-03 was consistent with this implementation difference: persisted `user_node_state` rows were present as `checking` and `repairing`, while formal diagnostics derived from durable attempts had previously produced `repaired` states.

## Source-of-truth clarification

For learner evidence:

1. `question_attempts` is the normalized durable attempt ledger.
2. Formal Node state is currently derived from that ledger by the versioned pure state engine.
3. `user_node_state` is currently a partial/legacy materialization and must not override the derived formal state.
4. Dashboard, Phase11, readiness, and retention logic must remain reproducible from durable evidence.

This clarification does not change the broader JSON/Neon architecture decision. The Question Bank remains version-controlled JSON loaded into memory; Neon remains the learner-history/state store.

## Near-term implementation rule

Until Issue #103 is complete:

- dashboard real-data shadow (#93) must use `question_attempts -> build_field_evidence(...)`;
- readiness evaluator (#95) must consume the same derived evidence path;
- retention/J4 diagnostics must use the formal derived state rather than persisted state labels;
- no Production backfill is implied by this document.

## Target end state

Preferred target: make `user_node_state` a faithful, rebuildable materialization of the same pure formal state engine, with an idempotent rebuild path and parity tests.

If that materialization does not provide a measured runtime benefit, an acceptable alternative is to keep formal derivation from `question_attempts` authoritative and explicitly deprecate the persisted state field for advanced-state semantics.

## References

- `docs/json-db-architecture-20260903.md`
- `knowledge_node_state_transition.py`
- `field_evidence.py`
- `database.py`
- Issue #103
