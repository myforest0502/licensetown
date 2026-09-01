# Phase 11 Ship Checklist

Phase 11 v0.1 may be committed to a QA branch when:

- judgment module is pure/read-only and deterministic
- decision order is covered by tests
- current-vs-shadow comparison is explicit
- diagnostics UI is clearly marked development-only
- learner dashboard recommendation is unchanged
- no write helper is imported/called by the judgment module
- no formal Node-state mutation occurs
- no adaptive selector policy changes occur
- consultation content is absent from inputs
- related tests, full pytest and Question Bank validator pass

It may be merged to main as diagnostics-only after code review if those conditions hold and there is no migration/production write.

It must not be promoted to learner-facing recommendation until the separate promotion gate is met using natural-use comparisons.
