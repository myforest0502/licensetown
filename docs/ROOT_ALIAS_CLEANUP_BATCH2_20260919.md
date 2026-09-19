# Root compatibility alias cleanup — batch 2

Baseline: `f9929902197f89b758fdc3829d694661e815bbca` (PR #389 merged).
Date: 2026-09-19.

## Scope

This batch removes only the repository-root `payment_access.py` compatibility alias.

The canonical implementation remains:

`licensetown/common/payment_access.py`

Batch 1's inventory identified `payment_access` as a common alias candidate with no runtime/startup caller and only test-side legacy import coverage. This batch retires that legacy import contract only for this module.

## Changes

- delete root `payment_access.py` shim
- update `tests/test_payment_access.py` to import
  `licensetown.common.payment_access` directly
- update the same test to import canonical `payment_entitlement` directly
- remove `payment_access` from
  `tests/test_common_infrastructure_import_compatibility.py`

No assertions, fixtures, payment policy, entitlement policy, DB code, startup wiring, Question Bank data, selector logic, Stage E, Phase11, Takken configuration, Render configuration, or migration files are changed.

## Safety

This batch does not delete `payment_entitlement.py`; its compatibility contract remains in place.

Production DB writes are not performed. No manual Render operation is performed. Main is not edited directly.

CI result is recorded in PR #390 before merge.
