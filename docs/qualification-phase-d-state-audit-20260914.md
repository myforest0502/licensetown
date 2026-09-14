# Qualification Phase D State Audit — 2026-09-14

## Purpose

Record the verified current boundary between common / PT / Takken after the multi-qualification work around issue #321. This audit changes no learner behavior, database schema, Production data, Render settings, selector policy, Question Bank data, or Phase11 authority.

## Source of truth checked

- current `main` at `f7cee6e4616469ea6ed726406044f7ebff5ca066`
- `AGENTS.md`
- `docs/CURRENT_STATE.md`
- `docs/PT_V1_PRODUCT_GOAL.md`
- issue #321 and the merged qualification PR sequence
- current Production composition in `wsgi.py`
- current qualification package, dashboard read bundle, durable session adapters, learning-time scope, reset implementations, and PT writer
- Render `line-bot-project` configuration/deploy state (read only)

## Verified Phase D state

### Learning history — runtime cutover complete for PT

`qualification_history_scope.install_pt_learning_history_scope()` binds the legacy learner runtime's attempt/history/initial-assessment hooks to `get_learning_history_store("pt")`. Production installs this scope from `wsgi.py`.

Status: **boundary exists / Production composition exists / PT qualification scope active**.

### Learning writer — runtime cutover complete for PT

`PTLearningWriter` writes `qualification_id='pt'` on learning events, question attempts, and Node state writes and uses qualification-aware conflict targets. `qualification_learning_writer_scope.install_pt_learning_writer_scope()` binds the live legacy learner/dashboard write hooks to one PT writer, and `wsgi.py` installs it.

The old module comment saying the writer was still dormant was stale after PR #335 and is corrected in this audit branch. No executable behavior changes.

Status: **boundary exists / Production composition exists / PT qualification scope active**.

### Paused LINE sessions — runtime cutover complete for PT

Durable paused-session persistence carries explicit PT qualification identity and Production installs the adapter from `wsgi.py`. Cross-qualification payloads fail closed while transition-compatible PT payload handling remains available.

Status: **boundary exists / Production composition exists / PT qualification scope active**.

### Web learning sessions — runtime cutover complete for PT

Durable Web session persistence carries explicit PT qualification identity and is installed from `wsgi.py`.

Status: **boundary exists / Production composition exists / PT qualification scope active**.

### Learning time — PT scope active with intentional compatibility layer

The live learning-time path is composed through the PT-qualified history/time boundary. Qualification-specific totals are maintained while the legacy PT total remains synchronized for current compatibility.

Status: **boundary exists / Production composition exists / compatibility mirror intentionally retained**.

### Dashboard and learner-navigation reads — PT scope active on Production path

`dashboard_read_bundle.py` explicitly filters Production `question_attempts`, `learning_events`, and `learning_time_events` by `qualification_id='pt'`, and reads `qualification_learning_time_totals` with the same scope. The main dashboard passes the already PT-scoped question-result rows into field and unique-question calculations.

The remaining direct dashboard history routes (including weekly supporter question history) are rebound by `qualification_dashboard_scope.install_pt_dashboard_history_scope()` to the PT history store at Production composition time.

Status: **boundary exists / Production composition exists / no Phase D cross-qualification dashboard read defect found in this audit**.

### Reset — two different contracts; do not rewire blindly

There are intentionally two different reset meanings:

1. `PTLearningHistoryStore.reset_qualification_state(user_id)` clears PT-qualified learning/session/time state while preserving account/profile identity such as name/mode and monitor access.
2. the existing learner command `ふりだしにもどる` is explicitly a **complete initialization reset**. `app.py` labels it a complete-reset command, clears in-memory learning/conversation state, calls the legacy full reset, and returns the learner to the new-user/name flow. Its failure message explicitly treats name/mode reset as part of the expected contract.

Therefore the fact that the live `ふりだしにもどる` path does not call `reset_qualification_state()` is **not a confirmed Phase D defect**. Replacing it would silently change user-visible semantics from full-account initialization to PT-only learning reset.

If a future product feature needs "reset only this qualification", wire the qualification reset behind a separate explicit command/UI contract. Do not repurpose `ふりだしにもどる` without a product decision.

Status: **qualification-only reset boundary exists / live complete-reset command intentionally remains a different operation**.

## Takken state

Takken currently has qualification metadata/config only. It has no active Question Bank provider, learning store/writer, learner runtime, selector, or Production activation. Unknown/unconfigured qualification paths must continue to fail closed rather than falling back to PT.

Status: **Phase E not started; keep Takken runtime disabled until PT parity/acceptance justifies activation**.

## Physical package split

The common/PT/Takken boundary exists under `qualifications/`, but much of the mature PT implementation still lives at repository root (`app.py`, selectors, Knowledge Node modules, dashboard/domain modules, etc.). This is not itself a product blocker.

Do not bulk-move these modules merely for directory cleanliness. Any further physical split should be incremental, behavior-preserving, and justified by a concrete dependency boundary or by the next qualification implementation.

## A / B / C / D / E classification

- **A — complete:** qualification metadata/contracts, common provider/store registries, PT provider/store/writer boundaries, Production PT history/writer/session/time/dashboard composition.
- **B — started / transitional:** compatibility shims and legacy PT modules remain; learning-time compatibility mirror remains intentionally; physical PT-domain relocation is partial.
- **C — not started:** Takken bank/storage/runtime/selector/domain implementation.
- **D — do not do now:** bulk root-module relocation, compatibility-key removal, implicit Takken activation, or changing the meaning of `ふりだしにもどる` just to use the qualification-reset method.
- **E — next:** keep PT stable, use real defects/product needs to choose the next small boundary; only then start isolated Takken implementation against the existing common contracts.

## Immediate next work

1. Treat issue #321 Phase D as substantially complete for the current PT Production path rather than reopening already-cut-over areas.
2. Keep `ふりだしにもどる` as complete reset unless Boss explicitly changes that product contract.
3. Do not move PT modules in bulk. Inventory candidate PT-specific root modules only when a concrete move is needed.
4. Before Takken Phase E, verify the common contracts needed by its first vertical slice and implement Takken fail-closed from the start.
5. Continue to distinguish code existence, tests, real Production evidence, and learner acceptance; this audit is repository/runtime-state verification, not proof that every multi-qualification behavior has been exercised by real Takken traffic.
