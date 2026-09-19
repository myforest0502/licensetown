# Root compatibility alias cleanup — batch 3

Baseline: `8896c6f317691f5e6eec0a6f8c0ea357dd6ea82e` (PR #390 merged).
Date: 2026-09-19.

## Scope

Retire the root compatibility aliases for the two durable session modules:

- `durable_paused_session.py`
- `durable_web_learning_session.py`

Canonical implementations remain under `licensetown/common/`.

## Changes

- production composition in `wsgi.py` now imports both installers from their canonical common modules
- durable-session tests import canonical modules directly
- PT qualification-scope regression tests import canonical stores directly
- shared legacy-import compatibility coverage no longer requires these two root aliases
- delete the two five-line root shims

No durable-session implementation logic, persistence SQL, qualification semantics, DB schema, selector, Stage E, Phase11, Takken configuration, Question Bank data, or Render settings are changed.

## Safety

The change is import-path-only. The same canonical module objects previously exposed through `sys.modules` aliases are now imported directly.

Production DB writes are not performed. No migration or manual Render operation is performed. Main is not edited directly.

CI result is recorded in PR #391 before merge.
