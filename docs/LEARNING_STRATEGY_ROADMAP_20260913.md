# LicenseTown Learning Strategy Roadmap — 2026-09-13

## Purpose

This document turns the agreed 「合格への道修正」 plan into an ordered implementation and acceptance sequence. It does not change Production behavior by itself.

## Non-negotiable principles

1. 「学習の現在地」 explains state; 「今日やること」 is the single learner action instruction.
2. Formal truth remains: `question_attempts -> derived Knowledge Node state -> field/strategy/readiness -> selector/presentation`.
3. Safety remains the highest-priority constraint.
4. Weakness state and next-study priority are separate concepts.
5. Raw accuracy alone never defines weakness, recovery, or readiness.
6. Existing #342 coverage-aware exploration stays in place until Production evidence justifies changing it.
7. No Production selector ratio change is made without Production evidence.

## Stage A — Production acceptance status

### PR #342 — ACCEPTED on natural Production use

Production read-only audit after merge timestamp 2026-09-12 05:49:17 UTC, targeting the PT learner with the most attempts internally without exposing user_id:

- adaptive items with `selection_group`: 495
- repair: 25
- checking: 157
- exploration: 313
- exploration unique Q: 313 / 313 = 100%
- `recent_question_repeat=true`: 0 / 495
- `recent_cooldown_bypassed=true`: 0 / 495

This exceeds the formal acceptance floor of adaptive >=300 and exploration >=50.

Low-coverage field re-audit using the same static Q->field semantics and canonical-node alias normalization used by the previous audit shows material improvement versus the pre-#342 baseline:

| Field | Pre-#342 | Current | Change |
| --- | ---: | ---: | ---: |
| 内科学 | 56/151 = 37.1% | 97/151 = 64.2% | +27.1 pt |
| 神経医学 | 28/114 = 24.6% | 73/114 = 64.0% | +39.4 pt |
| 運動器 | 23/104 = 22.1% | 49/104 = 47.1% | +25.0 pt |
| 理学療法評価各論 | 51/158 = 32.3% | 90/158 = 57.0% | +24.7 pt |
| 理学療法治療各論 | 52/291 = 17.9% | 138/291 = 47.4% | +29.5 pt |

Conclusion: #342 is accepted. Coverage-aware exploration is materially improving the fields that were most under-covered without introducing repeat/cooldown bypass regressions.

### PR #337 — CODE/GENERAL PRODUCTION ACCEPTED; direct initial_assessment natural sample pending

Production read-only audit after merge timestamp 2026-09-12 04:35:45 UTC:

- attempts: 495
- distinct Q: 495
- same-Q repeat within 72h: 0
- reviewed exact-equivalence evidence repeat within 72h: 0
- cross-Q exact-equivalent repeat within 72h: 0
- `initial_assessment` attempts in the post-merge natural sample: 0

Conclusion: code/test acceptance and general Production no-regression evidence are accepted. Direct `initial_assessment` natural-use evidence remains unavailable and must not be manufactured merely to close the audit. This pending observation is non-blocking for shadow-only strategy work because the repeat guard itself remains authoritative.

## Stage B — field evaluation rules

Implement deterministic pure logic first, disconnected from Production selection.

### B1. Evidence sufficiency

Default initial evaluation floor per field:
- at least 60 evaluable answers;
- AND sufficient Canonical Knowledge Node spread.

Before both requirements are met, learner-facing field status remains `unassessed` / `assessing`; do not label the field strong or weak.

The Node-spread threshold is relative to the field's Canonical Node supply and capped by the initial evidence budget so a large field cannot require more unique Nodes than 60 questions can physically expose.

### B2. Provisional field state

Once evidence is sufficient, classify field state into:
- `strong`;
- `ordinary`;
- `weak`.

Inputs include:
- evaluable question accuracy;
- Canonical Node spread;
- Node-state distribution;
- repeated weakness evidence;
- different-Q repair confirmation;
- unresolved Safety evidence.

Thresholds are versioned and regression-tested rather than hidden in UI copy.

### B3. Re-evaluation cadence

For a weak field:
- 60 -> add up to 30 relevant questions -> re-evaluate at 90;
- if still weak, repeat at 120, then 150, etc.;
- each 30-question increment is a new decision point, not an automatic command to remain in that field.

### B4. Weakness vs priority

Keep separate:
- field state: what the evidence says about the learner;
- strategy priority: where the next learning block has highest expected exam value.

A field may remain weak while another field receives the next block.

### B5. Recovery semantics

Recovery requires more than improved raw accuracy. Base semantics:
`wrong -> repairing -> different-Q confirmation -> repaired -> spaced recheck -> stable`.

Levels:
- `provisional_recovery`: enough evidence to lower immediate repair priority;
- `durable_recovery`: spaced evidence supports stability.

### B6. Anti-overconcentration

A field must not absorb unlimited blocks simply because it remains weak. Repeated 30-question blocks with poor marginal progress create a `strategy_change_candidate` while preserving Safety overrides.

## Stage C — Exam Weight data audit

Derive what is reproducible from the closed Q1-Q2000 dataset before adding outside assumptions.

Required outputs per field:
- official-question count;
- share of official questions;
- practical/general split when provenance supports it;
- year distribution when provenance supports it;
- recent-window trends only when the stored provenance actually supports the window;
- stability/volatility of field appearance.

Current repository evidence includes audited official provenance for parts of rounds 47-51 and round 60, but a complete 20-year per-question provenance series has not yet been established. Missing years must not be guessed. The next task is to inventory all source-audit artifacts and quantify exactly which rounds are supported before defining Exam Weight v0.1.

## Stage D — field-specific targets

Keep raw Field Progress unchanged. Add separate strategy targets per field:
- minimum evidence amount;
- target progress/readiness;
- weak-field additional-block ceiling;
- recovery threshold.

Represent current and target separately; never inflate displayed progress.

## Stage E — final strategy engine

Create a deterministic shadow-only strategy score using:
- Exam Weight;
- current weakness;
- target deficit;
- unassessed/coverage deficit;
- time-to-exam adjustment;
- Safety override.

Product question:
> 次の30問をどこに使えば、最も合格に近づくか。

## Stage F — promotion and documentation

Before Production promotion:
- compare old vs new recommendation on real history;
- verify no repeat/Safety regression;
- verify field overconcentration does not worsen;
- verify allocation shifts toward high-value deficits;
- preserve rollback;
- document all thresholds and versions.

## Codex execution policy

Codex may be used for repository-wide inspection, pure-module implementation, tests, reports, branch/PR work, and deterministic data analysis after the acceptance contract is fixed.

Before starting a Codex task, available usage must be sufficient to finish inspection -> implementation -> tests -> commit/push -> final report. Do not start a task likely to stop halfway.

Production DB writes, paid operations, and Production behavior changes remain separate approval/promotion decisions.

## Immediate next action

1. Merge the shadow-only Stage B implementation after green CI.
2. Inventory official-exam provenance available in Q1-Q2000 and produce a reproducible Stage C support matrix.
3. Derive Exam Weight v0.1 only from supported evidence; explicitly mark unsupported historical windows.
4. Then derive field-specific targets and implement the final strategy engine shadow-only.
