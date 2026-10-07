# LicenseTown Qualification Architecture — Current State

Date: 2026-09-14
Base: `main` at `f7cee6e4616469ea6ed726406044f7ebff5ca066`
Status: documentation of the existing implementation; no runtime behavior change.

## Purpose

This document freezes the current common / PT / Takken boundary before further physical reorganization.
It is an inventory of what already exists, what is live, what remains compatibility code, and what must stay disabled.

The goal is not to move files for appearance. The goal is to let each qualification reuse stable common contracts without risking the current PT learner path.

## 1. Current package boundary

### Common

`qualifications/common/` is the shared qualification contract layer.

Current shared pieces:
- `base.py` — `QualificationConfig`
- `bank_provider.py` — shared Question Bank provider protocol
- `provider_registry.py` — qualification-scoped Question Bank provider lookup
- `learning_store.py` — shared learning-history/storage contract
- `learning_store_registry.py` — qualification-scoped learning-store lookup

Compatibility shims still exist at the old `qualifications/` root import paths. They are transition compatibility, not a signal to duplicate new shared logic there.

### PT

`qualifications/pt/` is the active qualification implementation boundary.

Current PT-specific pieces:
- `config.py`
- `provider.py`
- `learning_store.py`
- `learning_writer.py`

PT remains the only active learner runtime.

### Takken

`qualifications/takken/` currently contains qualification metadata/config only.

There is no Takken Question Bank provider, learning store, writer, selector/runtime connection, or Production activation.
Known-but-unconfigured Takken paths must continue to fail closed rather than fall back to PT.

## 2. Production PT qualification scope already live

The Production composition root is `wsgi.py`.
It installs PT-scoped history, dashboard history, learning writer, durable paused sessions, durable Web learning sessions, and learning-time scope into the legacy learner runtime.

The current architecture therefore distinguishes two facts:

1. much of the historical PT implementation still physically lives at repository root;
2. durable learner-state access is already being composed through explicit PT qualification boundaries.

Do not confuse physical file location with storage/runtime qualification authority.

## 3. Storage migration status

The repository contains:
- `migrations/20260911_qualification_scope_phase1.sql`
- `migrations/20260912_qualification_scope_unique_keys_phase2a.sql`

The multi-qualification work was introduced additively so existing PT rows remain PT and current PT behavior is preserved.
Legacy compatibility keys/structures have not been removed merely for cleanup.

Any future destructive removal or key replacement needs a separate migration decision and Production evidence. It must not be bundled into file reorganization.

## 4. Reset semantics — two different operations

There are intentionally two different concepts and they must not be silently merged.

### Qualification-scoped PT learning reset

`PTLearningHistoryStore.reset_qualification_state(user_id)` clears PT-qualified learning/session/time state while preserving account/profile identity such as name, mode, and monitor/account access.

This boundary exists and is covered by `tests/test_pt_qualification_reset.py`.

### Full account/profile reset

The existing learner command `ふりだしにもどる` still calls the legacy `reset_user_profile(user_id)` path.
That path is explicitly tested as a complete user-profile reset: it removes the profile identity so the learner becomes a first-time user again.

Therefore replacing the live `ふりだしにもどる` call with `reset_qualification_state()` would be a product-semantics change, not a mechanical Phase-D cleanup.
Do not make that change without a separate product decision and learner-facing copy/test review.

## 5. Root-level modules are not automatically "common"

A large amount of PT-shaped code still lives at repository root, including learner runtime, selector, Knowledge Node, field strategy, dashboard, and database modules.

Their current root location is historical/compatibility structure. It does not mean they should all become common code.

Before moving any root module, classify it as one of:
- **common contract / qualification-neutral** — reusable without PT field/category/Node assumptions;
- **PT domain** — depends on PT Question Bank, PT field taxonomy, PT Knowledge Nodes, PT exam policy, or PT-specific learner presentation;
- **composition / compatibility** — keeps existing Production entrypoints/imports stable while qualification-specific implementations are introduced.

A module must not be moved to `qualifications/common/` merely because more than one future qualification may need something similar.
Shared code should be extracted only when the contract is genuinely qualification-neutral.

## 6. What is intentionally not done yet

Do not treat the following as missing bugs that should be fixed immediately:
- physical relocation of all PT runtime files under `qualifications/pt/`;
- physical relocation of the formal PT Question Bank data;
- deletion of compatibility shims;
- removal of legacy database keys/columns/tables solely for cleanup;
- Takken bank/provider/storage/runtime activation;
- automatic reuse of PT Knowledge Node or PT field strategy logic for Takken;
- Phase11 promotion.

These are separate later decisions. PT learner stability remains the priority.

## 7. Safe next sequence

1. Inventory root modules by **common / PT domain / composition-compatibility**.
2. Identify one low-fan-out PT-specific module whose relocation can be proven behavior-preserving.
3. Move only that small unit behind compatibility import(s) if required.
4. Run focused tests, full CI, and Question Bank validation as applicable.
5. Merge only after CI is green; Render main auto-deploy remains the normal delivery path.
6. Confirm Production PT parity before starting another relocation unit.
7. Start Takken Phase E only after PT parity is established and a Takken-specific bank/provider/storage design exists.

## 8. Non-negotiable invariants

- PT Production data/history must remain readable with no cross-qualification contamination.
- Unknown or unavailable qualification IDs fail closed; never silently fall back to PT.
- Qualification identity remains a separate axis; raw PT Q IDs and Knowledge Node IDs are not renamed just to namespace them.
- Existing Safety, repeat guard, retention, selector, and learner-flow behavior must not be weakened by architecture cleanup.
- `main`, Production Neon, Render settings, and live LINE behavior are not used as a scratchpad.
- Phase11 remains HOLD/shadow-only unless separately promoted with evidence.

## 9. Current classification

### Completed / established
- qualification metadata for PT and Takken;
- common qualification contracts/registries;
- PT Question Bank provider boundary;
- PT learning-history/store boundary;
- PT-qualified Production history/write/session/time composition;
- PT-scoped dashboard/history reads;
- additive qualification-aware storage migrations/keys.

### Started but deliberately transitional
- root PT runtime gradually depending on qualification-specific adapters;
- compatibility shims and legacy call-site rebinding;
- coexistence of legacy full-account reset and qualification-scoped PT learning reset.

### Not activated
- Takken Question Bank/provider/storage/runtime;
- automatic multi-qualification learner switching;
- broad physical PT module relocation.

This document records architecture state only. It does not authorize runtime, DB, Render, LINE, Takken, or Phase11 changes.
