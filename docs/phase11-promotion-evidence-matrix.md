# Phase 11 Promotion Evidence Matrix

Date: 2026-09-02
Status: diagnostics-only implementation complete; learner-facing promotion not yet approved.

This document separates evidence already established from evidence that still requires learner evidence. It is a promotion decision aid, not a learner-facing score.

## A. Architecture and safety — COMPLETE

- Phase 11 judgment is deterministic and read-only.
- No Production DB write is performed by the judgment layer.
- No formal Knowledge Node state mutation is performed by Phase 11.
- Exact Q selection remains owned by Phase 10 adaptive selection.
- Recent Question Cooldown remains owned by Phase 10.
- Consultation text is not an input.
- Learner-facing recommendation is unchanged.
- Phase 12 consumes Phase 11 output for presentation only and does not redefine mastery.
- Current-vs-Shadow target comparison is symmetric and uses the same formal J1→J7 evidence hierarchy for both targets.

## B. Phase 10 dependency — COMPLETE

Natural adaptive_daily observation confirmed:

- 6 events / 30 questions / 30 unique Q
- all six saved adaptive audit fields present
- observed recent repeats fully explained by Safety/bank-supply exception
- ordinary repair/checking/exploration selections did not bypass cooldown

Phase 10 is operationally closed.

## C. Question Bank repair supply — IMPROVED, NOT COMPLETE GLOBALLY

The initial Production repairability diagnostic showed:

- repairing Nodes: 135
- strong different-Q available: 1
- weak-only: 5
- same-Q/formally blocked: 129

A Safety strong-repair pilot then added Q1595-Q1605 to 11 existing Safety Nodes.

Current formal bank snapshot after the pilot:

- Q1-Q1605
- canonical Nodes: 1509
- singleton canonical Nodes: 1422
- multi-question canonical Nodes: 87
- validator PASS

The 11 pilot source/new pairs all classify as `different_question_strong`.

This materially improves Safety repair supply but does not make the entire bank repairable. Global repair-supply expansion remains a separate content-development task and is not itself a reason to alter Phase 11 ranking logic.

## D. Shadow judgment static behavior — COMPLETE

J1→J7 order:

1. safety_repair
2. confident_wrong_cluster
3. repeated_wrong_cluster
4. recheck_due
5. insufficient_coverage
6. uncertain_correct_cluster
7. maintenance_only

Confirmed properties:

- one ordinary wrong does not automatically commandeer a field
- unknown answers do not create confirmed weakness
- sparse fields are treated conservatively
- high same-day volume is an observation, not an automatic blocker
- Shadow does not select exact Q IDs

## E. Current-vs-Shadow comparison — COMPLETE AS DIAGNOSTIC

Both target fields receive the same formal evidence profile.

Possible disagreement labels:

- `different_target_shadow_has_stronger_evidence`
- `different_target_current_has_stronger_evidence`
- `insufficient_evidence_to_judge`

Same-target labels remain available.

Important limitation:

A stronger formal evidence rank at one snapshot does not prove better future learning outcome. Promotion still requires learner evidence across multiple examples.

## F. Known natural disagreement example — OBSERVED

Previously observed Production snapshot:

- Baseline target: 小児学 10問
- Shadow target: 内科学 10問
- Shadow reason: confident_wrong_cluster
- Shadow confidence: high

Internal-medicine diagnostics showed five confident-wrong repairing Nodes, including one cross-question confident-wrong Node. This supports the existence of a genuine repair signal, but the example alone is insufficient for promotion.

The symmetric comparison diagnostic should be used on current and historical snapshots before drawing a winner conclusion.

## G. Repeat structure audit — IMPLEMENTED, PRODUCTION INTERPRETATION PENDING

Repeat Structure Diagnostics is on main.

It separates same-Q repeats into:

- justified_cooldown_bypass
- adaptive_repair_or_recheck
- adaptive_unexplained_repeat
- nonadaptive_repeat
- audit_metadata_unavailable

It also separates same-node different-question encounters from same-Q repeats.

Promotion-relevant target:

- `adaptive_unexplained_repeat` should be zero or individually explained before Phase 11 learner-facing promotion.

Historical/legacy attempts with unavailable audit metadata must not be mislabeled as selector failures.

## H. Retrospective historical replay — DESIGNED, IMPLEMENTATION PENDING

Existing data already stores one daily `recommendation_plan` activity event when the dashboard is opened with a baseline recommendation. The event includes:

- persisted baseline target field
- question goal
- event timestamp

Together with timestamped `question_attempts` and `build_field_evidence(..., as_of=...)`, this makes a read-only historical replay possible.

For each historical plan snapshot:

1. truncate attempts to before the plan timestamp
2. reconstruct formal field evidence at that time
3. replay Phase 11 with `as_of` set to the plan time
4. compare the persisted baseline target with the historical Shadow target using the symmetric evidence profile
5. inspect later activity observationally without claiming causality

This can increase the number of Safety, coverage, disagreement, and recheck examples available for evaluation without manufacturing Production activity or adding a write path.

Retrospective replay is supporting evidence only. It cannot prove what the learner would have done if Shadow had actually been shown.

See:

`docs/phase11-retrospective-shadow-audit-v01.md`

## I. Natural-use promotion checks — PENDING

The following still require real learner evidence and must not be manufactured.

### I1. Critical Safety misses

Target:

- zero cases where a stronger unresolved Critical Safety signal exists but Phase 11 selects a weaker field.

Historical replay may help find past candidate cases; prospective use is still valuable.

### I2. Single-wrong overreaction

Target:

- no repeated pattern of ordinary single wrongs causing unnecessary field takeover.

Retrospective replay can expand the sample beyond current-day screenshots.

### I3. Sparse learner coverage

Target:

- Phase 11 continues to prefer coverage when weakness evidence is insufficient.

Historical under-100-answer snapshots are particularly useful if stored plans exist.

### I4. Recheck due handling

Target:

- once natural `recheck_due` Nodes exist, they are not starved by weaker J5-J7 signals.

Historical replay may reveal an earlier valid recheck_due snapshot. If none exists, no conclusion should be forced.

### I5. Phase 11 intent vs Phase 10 exact-Q behavior

Target:

- when Phase 11 says repair/recheck/coverage, the Phase 10 selected set should be directionally consistent without violating cooldown or Safety rules.

### I6. Baseline disagreement quality

Review both wins and losses.

For each natural or retrospectively reconstructed disagreement capture:

- Baseline target
- Shadow target
- current target formal evidence profile
- Shadow target formal evidence profile
- symmetric comparison label
- whether later learner activity sampled either target

Do not review only examples favorable to Shadow.

### I7. Recommendation relevance

Target:

- across prospective natural examples, Shadow produces fewer obviously irrelevant recommendations than Baseline without introducing Safety misses, repetition problems, or coverage starvation.

Retrospective replay may support consistency review but cannot substitute for the prospective relevance judgment because the learner did not actually receive Shadow guidance.

## J. Promotion decision rule

Do not promote based on one strong screenshot or one favorable disagreement.

A learner-facing promotion decision should require:

- architecture/safety gates remain green
- no unexplained adaptive repeat regression
- no Critical Safety miss
- no systematic single-wrong overreaction
- acceptable sparse-coverage behavior
- recheck_due behavior observed when naturally available
- symmetric disagreement review contains both favorable and unfavorable examples
- retrospective replay, where available, does not reveal rule-consistency regressions
- prospective natural-use evidence remains at least clearly no worse than Baseline and preferably better

If evidence is mixed, remain Shadow-only and collect more learner evidence rather than changing ranking weights prematurely.

## K. Next review order

1. Implement/read the retrospective historical replay diagnostic.
2. Read current Production Repeat Structure Audit.
3. Read current symmetric Baseline-vs-Shadow evidence profiles.
4. Record any adaptive unexplained repeats.
5. Review historical and current disagreement winners, including current-guidance wins.
6. Check historical Safety / coverage / recheck candidates.
7. Continue prospective natural-use sampling.
8. Only then decide whether Phase 11 is ready for a limited learner-facing pilot.
