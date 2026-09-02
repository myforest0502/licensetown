# LicenseTown core completion contract — 2026-09-03

Status: design / execution contract. No runtime behavior changes in this document.

## Purpose

Finish the current learning-engine "core" before shifting primary attention to the next productization phase.

The source roadmap defines items 1-12. Item 8 is intentionally continuous because it depends on natural learner-use evidence. Every other item should have a concrete completion condition rather than remain indefinitely "in progress".

This document converts that roadmap into an executable order and acceptance contract based on the current repository state.

## Current interpretation

### 1-5

Substantially implemented and operational. Phase10 adaptive selection, audit metadata, recent cooldown, tags/canonical Node foundations, and related diagnostics are already present.

### 6 — repair confirmation with a different question

Mechanism exists, but repair supply is still being expanded. The current blocker is Repair Supply B12 (Q1661-Q1737).

Completion requires:

- B12A-D complete;
- final validator/audit green through Q1737;
- no classifier manipulation or reviewed STRONG overrides added merely to force evidence;
- original Question Bank content before the batch preserved except explicitly approved fixes;
- repair evidence supply re-measured after the batch;
- KN0779 weak-pair audit handled separately rather than silently folded into B12.

### 7 — do not over-drill repaired material

Implemented through Node state plus Recent Question Cooldown semantics. Keep regression coverage; do not reopen unless natural evidence shows a problem.

### 8 — compare LT judgment with human / learner reality

Continuous evidence program, not a blocking "finish once" task.

Continue collecting natural-use evidence without repeatedly surveying the learner merely to increase sample count. Key evidence includes:

- Baseline vs Shadow disagreement outcomes;
- repair -> repaired -> recheck_due -> stable transitions;
- later accuracy/confidence after repair;
- unexplained repeats / cooldown bypasses;
- learner acceptance when a meaningful disagreement naturally occurs.

Phase11 remains Shadow-only while evidence is thin or mixed.

## The remaining finishable core

### 9 — make "合格への道" real-data driven

Do not treat this as a cosmetic dashboard rewrite.

First create a deterministic evidence layer that can answer:

- how much of the canonical syllabus has been touched;
- how stable the touched knowledge is;
- what is actively weak vs merely unobserved;
- what should be repaired, rechecked, explored, or maintained next.

Reuse the design in `docs/dashboard-real-data-v01-20260903.md` and Issue #93. Do not create a second independent scoring model.

Completion condition for the internal evidence layer:

- unique canonical Nodes are the overall denominator;
- all 18 fields have deterministic coverage/mastery/progress values;
- no demo values remain in the real-data path;
- weakness TOP3 distinguishes weak evidence from insufficient coverage;
- Safety can outrank ordinary weakness;
- recommendation output is an intent/reason passed to the formal selector, not exact-Q selection inside the dashboard;
- empty/sparse/mixed/repair/recheck/stable/Safety/confident-wrong cases are covered by pure tests;
- output runs in shadow first and is explainable against current production-shaped history.

### 10 — align with the PT abilities required by the national exam

This is a permanent design constraint, not a standalone one-time feature.

Question/tag/Node/selection/dashboard decisions must preserve the ability dimensions already represented by the formal model (e.g. know, measure, interpret, predict, prescribe, decide/safety) rather than collapse progress into memorized-question accuracy.

For the current core, item 10 is considered operationally satisfied when items 9, 11, and 12 consume these structured abilities and do not reduce learner judgment to raw accuracy alone.

### 11 — formal pass-readiness judgment system

Build an internal deterministic "LT pass-readiness" result from evidence. This is not a prediction that guarantees passing and must not be presented as one.

The evaluator should expose separate components before any single summary label is considered:

1. syllabus coverage;
2. Node-state stability/mastery;
3. unresolved repair burden;
4. retention evidence (recheck_due / stable, once naturally available);
5. Safety readiness;
6. confidence-calibrated error evidence (especially confident-wrong/repeated wrong);
7. ability-domain coverage/stability;
8. full-exam / Trial100 reproduction evidence when available;
9. learning pace/activity only as supporting context, not mastery.

### Do not invent a magic weighted score first

Initial implementation should produce an inspectable component vector plus deterministic status/reasons. Do not choose arbitrary percentage weights simply because a single overall number is convenient.

A later composite percentage may be introduced only after:

- component behavior is validated on real histories;
- missing-data behavior is defined;
- Safety cannot be hidden by strong performance elsewhere;
- sparse coverage cannot look "high mastery";
- retention unavailable because of time is distinguished from retention failure;
- Trial100 absence is distinguished from Trial100 poor reproduction.

Suggested internal readiness statuses:

- `insufficient_evidence`
- `building_coverage`
- `repair_required`
- `retention_confirmation_needed`
- `safety_attention_required`
- `approaching_readiness`
- `readiness_supported`

These are implementation candidates, not learner copy.

Completion criteria for item 11:

- deterministic evaluator exists as pure logic over canonical/evidence inputs;
- every output includes inspectable reason codes and component values;
- no single ordinary wrong answer can flip overall readiness;
- Critical Safety problems can block a positive readiness status;
- sparse/unseen data cannot be mistaken for mastery;
- repaired but not yet retention-checked evidence is distinguishable from stable evidence;
- missing Trial100/full-exam evidence is explicit rather than scored as failure;
- tests cover empty, sparse, high-accuracy-low-coverage, confident-wrong, repeated-wrong, Safety, repairing, repaired, recheck_due, stable, and mixed-ability histories;
- production-shaped shadow output is reviewed before learner-facing use.

### 12 — visualize "合格への道"

Only after the internal evidence/readiness result is trustworthy should the learner-facing navigation be finalized.

The learner should see plain-language answers to:

- where am I now;
- what is already stable;
- what still needs repair;
- what has not been checked enough;
- whether retention confirmation is pending;
- whether there is a Safety concern;
- what should I study today.

Do not expose internal Node IDs, STRONG/WEAK, Phase labels, selector reason codes, or diagnostic jargon directly.

The final screen is a navigation aid, not merely a score sheet.

Completion criteria for item 12:

- learner-facing values come from the real-data evidence/readiness path, not demo values;
- every major displayed conclusion can be traced to an internal reason/evidence value;
- the screen gives a clear next action;
- mobile presentation is understandable without internal terminology;
- learner-facing recommendation continues to respect the formal selector and cooldown rules;
- Phase11 recommendation promotion remains a separate explicit decision;
- parent/supporter and developer diagnostic requirements are not allowed to bloat this learner screen.

## Execution order

The practical order from the current state is:

1. Resume and complete Issue #89 (B12) from the existing worktree; never reset/discard or recreate already completed local work.
2. Freeze/audit Q1-Q1737 under the existing post-B12 foundation work (Issue #86).
3. Audit KN0779 separately under Issue #88.
4. Implement the item-9 evidence layer in shadow mode under Issue #93.
5. Implement the item-11 pass-readiness evaluator using the same evidence pipeline.
6. Review production-shaped shadow outputs; keep item 8 natural evidence collection running in parallel.
7. Complete item 12 learner-facing "合格への道" from the validated evidence/readiness output.
8. Only after the core is complete, make the previously agreed productization four-point program the primary workstream: learning-route reliability, supporter/developer separation, supporter performance simplification, and commercialization/revenue.

## Core completion definition

The current "core" is considered complete when:

- B12/final Question Bank baseline is green;
- repair confirmation has sufficient STRONG alternate supply for the planned model, with remaining exceptions explicitly known;
- Recent Cooldown/Node-state behavior remains regression-green;
- item-9 real-data evidence exists and is validated in shadow;
- item-11 readiness judgment exists with reasoned deterministic output and acceptance tests;
- item-12 learner navigation uses those real values;
- item 8 remains explicitly continuous rather than falsely marked done;
- no production DB migration or Phase11 learner-facing promotion is smuggled into these steps without a separate decision.

## Non-goals

- no arbitrary score-weight tuning from one learner;
- no guarantee-of-passing claim;
- no per-render OpenAI dependency for factual dashboard/readiness values;
- no second exact-Q selector;
- no forced synthetic learner attempts/timestamps to make retention gates pass;
- no broad product UI redesign before the current core completion gates are met.