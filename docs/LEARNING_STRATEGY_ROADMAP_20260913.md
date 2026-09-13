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
7. No Production selector ratio change is made while the #342 acceptance audit is still unresolved.

## Ordered work

### Stage A — close current Production acceptance first

#### A1. PR #342 acceptance
Acceptance target:
- post-#342 adaptive metadata >= 300 items;
- exploration >= 50 items;
- exploration unique-Q rate remains high;
- `recent_question_repeat=true` = 0;
- `recent_cooldown_bypassed=true` = 0;
- no new Safety/repeat invariant break;
- compare the current 18-field Canonical Node coverage with the pre-#342 baseline.

Pre-#342 baseline:
- 2,010 attempts / 1,002 distinct Q;
- 9 of 18 fields below 50% Node coverage;
- 理学療法治療各論 52/291 = 17.9%;
- 運動器 23/104 = 22.1%;
- 神経医学 28/114 = 24.6%;
- 理学療法評価各論 51/158 = 32.3%;
- 内科学 56/151 = 37.1%.

Current known checkpoint before final re-audit:
- post-#342 adaptive 290;
- repair 15 / checking 126 / exploration 149;
- exploration unique 149/149;
- recent repeat 0 / cooldown bypass 0.

Do not call #342 formally accepted until the metadata-specific >=300 condition is verified.

#### A2. PR #337 acceptance
Keep the 72-hour same-evidence guard authoritative, including reviewed exact-equivalent groups. Distinguish:
- code/test acceptance;
- general Production no-regression evidence;
- direct `initial_assessment` Production evidence.

Do not manufacture an `initial_assessment` sample merely to close the audit.

### Stage B — formalize field evaluation rules (original items 2, 3, 4, 5, 6, 7)

Implement as deterministic pure logic first, disconnected from Production selection.

#### B1. Evidence sufficiency
Default initial evaluation floor per field:
- at least 60 answered questions;
- AND sufficient Canonical Knowledge Node spread.

Before both requirements are met, learner-facing field status must remain `unassessed` / `assessing`; do not label the field strong or weak.

The Node-spread threshold must be expressed relative to the field's total Canonical Node supply, not as one fixed absolute number for every field.

#### B2. Provisional field state
Once evidence is sufficient, classify field state into a small deterministic set such as:
- `strong`;
- `ordinary`;
- `weak`.

Inputs may include:
- question accuracy;
- Canonical Node coverage;
- Node-state distribution (`repairing/checking/recheck_due/repaired/stable`);
- repeated/different-Q reproducibility;
- Safety weakness.

Exact thresholds must be versioned and regression-tested; they must not be silently embedded in UI copy.

#### B3. Re-evaluation cadence
For a weak field:
- 60 -> add up to 30 relevant questions -> re-evaluate at 90;
- if still weak, repeat at 120, then 150, etc.;
- every 30-question increment is a new decision point, not an automatic command to stay in the same field.

#### B4. Weakness vs priority
Persist/derive separately:
- field state: what the evidence says about the learner;
- strategy priority: where the next learning block has highest expected exam value.

A field may remain weak while another field receives the next block.

#### B5. Recovery semantics
Recovery must require more than improved raw accuracy. Use the existing Node-state path as the base:
`wrong -> repairing -> different-Q confirmation -> repaired -> spaced recheck -> stable`.

Define at least two levels:
- `provisional_recovery`: enough evidence to lower immediate repair priority;
- `durable_recovery`: spaced evidence supports stability.

#### B6. Anti-overconcentration rule
A field must not absorb unlimited blocks simply because it remains weak. After repeated 30-question blocks with poor marginal improvement, mark the field as a strategy-change candidate and preserve allocation for unassessed / low-coverage fields.

The hard cap will ultimately vary by field importance rather than using one universal number.

### Stage C — derive Exam Weight from the official-question dataset (original items 8 and 9)

Before adding external assumptions, inventory what the current closed Q1-Q2000 dataset can support directly.

Required outputs per field:
- official-question count;
- share of official questions;
- practical/general split when provenance supports it;
- year distribution when provenance supports it;
- recent 5y / 10y / available-long-horizon trends when the stored provenance supports those windows;
- stability/volatility of field appearance.

If the repository does not contain a complete 20-year provenance series, explicitly report the unsupported gap rather than inventing data. Only then decide whether outside historical data must be added.

The first Exam Weight version must be reproducible from source data and versioned.

### Stage D — field-specific targets (original items 10 and 11)

Keep raw Field Progress unchanged. Add separate strategy targets per field:
- minimum attack/evidence amount;
- target progress/readiness;
- weak-field additional-block ceiling;
- recovery threshold.

Important fields may demand higher targets and larger evidence budgets; lower-weight fields may be deprioritized after the minimum useful evidence is achieved.

Never inflate displayed progress to make a target look met. Represent `current` and `target` separately.

### Stage E — final strategy engine (original item 12)

Create a deterministic strategy score whose conceptual factors are:
- Exam Weight;
- current weakness;
- target deficit;
- unassessed/coverage deficit;
- time-to-exam adjustment;
- Safety override.

The engine answers one product question:
> 次の30問をどこに使えば、最も合格に近づくか。

The first implementation must run shadow-only against current Production history before it controls real selection.

### Stage F — promotion and documentation (original items 13 and 14)

Before Production promotion:
- compare old vs new recommendation on real history;
- verify no repeat/Safety regression;
- verify field overconcentration does not worsen;
- verify the new strategy improves allocation toward high-value deficits;
- keep a rollback path;
- document all thresholds and versions.

## Codex execution policy

Codex may be used for repository-wide inspection, pure-module implementation, tests, reports, branch/PR work, and large deterministic data analysis after the acceptance contract for that stage is fixed.

Before starting a Codex task, confirm the available usage is sufficient to finish the whole task (inspection -> implementation -> tests -> commit/push -> final report). Do not start a task that is likely to stop halfway because of usage limits.

Production DB writes, paid operations, and Production behavior changes remain separate approval/promotion decisions.

## Immediate next action

1. Finish Stage A (#342/#337 acceptance) without changing selector behavior.
2. In parallel, inspect current pure logic (`field_evidence`, `field_progress`, Node state, shadow recommendation) and design Stage B as a pure, shadow-only contract.
3. Only after Stage A closes, implement Stage B and its regression tests.
4. Then perform Stage C data analysis before fixing Exam Weight numbers.
