# Takken Phase E Readiness v0.1

Date: 2026-09-14

## Purpose

Define the minimum safe boundary for starting LicenseTown's second qualification without copying PT-specific assumptions into Takken or weakening the already-stable PT Production path.

This is a readiness audit only. It does not activate Takken, create Takken questions, invent a Takken taxonomy, change Production storage, alter selectors, or promote any shadow strategy.

## Current conclusion

The multi-qualification storage/runtime boundary is sufficiently mature to begin **isolated dormant Takken work**, but the current learning/selection stack is not yet qualification-neutral end to end.

The primary blocker is not the database boundary. It is the absence of authoritative Takken domain data plus several PT Question Bank dependencies embedded in selection/evidence modules.

Therefore Phase E should begin with a dormant Takken data/provider vertical slice, not with runtime activation and not with a bulk PT-to-common refactor.

## Already ready as shared infrastructure

### Qualification identity and fail-closed registries

`qualifications/common/provider_registry.py` and `learning_store_registry.py` know both `pt` and `takken`, but only PT is configured. Takken raises an explicit not-configured error and unknown qualification IDs raise `KeyError`. There is no implicit fallback to PT.

This is the correct safety posture for Phase E and should be preserved.

### Small Question Bank read contract

`QuestionBankProvider` currently defines only the shared reads needed for stable question data:

- `qualification_id`
- `question_ids()`
- `get_question()`
- `get_question_tag()`
- `get_quiz_question()`

This is a useful minimum contract and should not be expanded merely to make every PT helper look common.

### Qualification-scoped durable state

The current PT Production path already proves the storage shape can carry qualification identity through learning history, answer writes, durable LINE/Web sessions, learning time, and dashboard reads. Takken can later implement the same common store contract without sharing PT rows or rewriting raw question IDs.

## Reusable algorithms vs PT-bound data

### Mostly reusable algorithm: Knowledge Node state transition

`knowledge_node_state_transition.py` is intentionally pure and has no persistence/selection side effects. Its states and retention clock are expressed in terms of attempts, canonical Nodes, repair evidence, and time rather than PT field names.

However it is **not yet independently qualification-neutral in execution**, because the repair/equivalence helpers it calls currently resolve against PT-backed master data. Treat the state-machine concept as reusable while keeping its current PT composition intact until qualification-specific evidence dependencies are injectable or separately namespaced.

### PT-bound: repair evidence master

`knowledge_node_repair_evidence.py` directly imports PT `question_bank.get_question_tag` and loads `data/question_bank/strong_different_question_pairs.json` from the current PT bank directory.

A Takken repair path must not reuse that PT master. The first Takken slice therefore needs its own reviewed question metadata/evidence source before repair confirmation can be enabled.

Do not solve this by moving the current PT file to `common/` unchanged.

### PT-bound: question equivalence

`question_equivalence.py` loads reviewed equivalence groups and canonical evidence Nodes from the current PT `data/question_bank` directory at import time.

The abstraction idea is reusable, but the data is qualification-specific. Takken needs its own equivalence dataset (possibly empty initially if there are no provenance duplicates) and a qualification-explicit resolver before the same algorithm can safely serve both domains.

### PT-bound: canonical Knowledge Node master

`knowledge_node_canonical.py` validates aliases against the current PT Knowledge Node master, merge candidates, and review files under `data/question_bank`.

Canonicalization as a concept is common; the alias/master dataset is qualification-specific. Takken must have its own Node namespace/master and cannot silently pass through PT canonical data.

## Current selector seams

### `learning_engine.py`

The module uses `PTQuestionBankProvider` for core bank reads, but it also contains PT-specific learner interpretation labels (`KNOW`, `MEASURE`, `INTERPRET`, `PREDICT`, `PRESCRIBE`, `DECIDE`) and its initial/daily assessment logic assumes the current PT tag schema.

This module should not be declared globally common merely because its bank reads use a provider. For the first Takken slice, either provide a separate Takken learning-engine adapter or extract only a proven generic selection primitive after an actual Takken tag contract exists.

### `adaptive_question_selector.py`

Core bank reads use `PTQuestionBankProvider`, but field membership still comes directly from legacy PT `question_bank.get_category_small`. Coverage also assumes integer `category_small` field IDs.

This is the clearest Phase E architecture seam: a Takken adaptive selector cannot safely reuse the current selector until its field/taxonomy lookup is qualification-explicit.

Do **not** immediately add PT's `get_category_small()` to the global Question Bank provider contract. First define the authoritative Takken taxonomy/data contract, then choose the smallest shared abstraction that both qualifications actually need (for example a separate taxonomy provider or a provider capability with qualification-owned field IDs).

## Explicitly PT-specific strategy layer

The current field/strategy stack should stay PT-specific unless a later Takken implementation demonstrates a genuinely identical contract.

Examples:

- `field_evidence.py` imports PT `CATEGORY_NAMES`, PT category lookup, PT Question Bank tags, and documents an 18-field bundle.
- `exam_weight_shadow.py` hard-codes PT's 18 fields and Q1-Q2000 source counts/provenance limitations.
- `field_learning_target_shadow.py` explicitly describes itself as PT field budgets/targets and requires exactly fields 1-18.

These are domain policies, not evidence that the common layer is incomplete. Takken should receive its own field model, exam weighting, and strategy policy using common state/evidence concepts where appropriate.

## What Phase E must not do

- Do not activate a Takken learner route or Production feature flag before a real Takken bank/provider/store path exists.
- Do not invent Takken categories, Knowledge Nodes, answer semantics, exam weights, or historical trends from PT structures.
- Do not make Takken fall back to the PT Question Bank, PT history, PT taxonomy, PT canonical Node master, or PT repair/equivalence files.
- Do not bulk-move root PT modules to `qualifications/common/` for directory cleanliness.
- Do not widen the shared provider/store interfaces until a concrete Takken requirement proves the need.
- Do not change Production DB/schema merely to prepare dormant Takken code; current qualification-aware keys already provide the isolation axis needed for the first offline slice.
- Do not treat PT Stage C/D/E/F strategy work as a ready-made Takken strategy.

## Minimal safe Phase E sequence

### E1 — authoritative Takken domain contract (no runtime)

Before writing a production Takken bank, define only facts that have an actual source:

- qualification ID (`takken`, already fixed)
- stable Takken question ID policy
- question record shape required by the common provider contract
- answer representation/grading semantics
- tag fields actually needed by the first learning slice
- Takken field/taxonomy identifiers and labels
- Knowledge Node identity rules
- provenance/source rules

If a value is not yet supported by real Takken source material, leave it unspecified rather than copying the PT value.

### E2 — dormant Takken Question Bank provider

Implement a Takken provider behind the existing common registry using a small, validated, non-Production dataset or authoritative first batch.

Acceptance:

- PT provider parity tests remain unchanged and green.
- `get_question_bank_provider("takken")` returns only Takken data.
- unknown qualifications still fail closed.
- Takken `Q1` and PT `Q1` can coexist because qualification identity is a separate axis.
- importing the Takken provider has no DB/network/write side effects.

### E3 — qualification-owned taxonomy boundary

Only after E2 proves the real Takken field model, remove the current selector's direct dependency on PT `get_category_small` using the smallest justified abstraction.

Acceptance:

- PT adaptive outputs remain behaviorally identical under PT inputs.
- Takken taxonomy lookup cannot access PT field IDs/names.
- category shortages/coverage logic cannot cross qualifications.

### E4 — Takken evidence namespace

Add Takken-owned canonical Node/equivalence/repair metadata only as required by real data.

Start conservatively. If no reviewed equivalence or strong repair pairs exist, use no such evidence rather than manufacturing it.

Acceptance:

- PT evidence masters stay byte/behavior compatible.
- Takken evidence never reads PT master files.
- same raw IDs across qualifications remain isolated.

### E5 — dormant Takken learning-history/store writer

Implement Takken store/writer against the already qualification-aware durable schema, still with no learner-facing route.

Acceptance:

- every Takken write carries `qualification_id='takken'`.
- PT reads cannot see Takken attempts/events/state and vice versa.
- session resume rejects a qualification mismatch.
- reset of one qualification cannot delete the other qualification's state.

### E6 — offline learning slice before runtime activation

Run a small offline flow:

`Takken provider -> question -> answer fact -> Takken attempt/history -> Node/evidence derivation -> next-question candidate`

Only the algorithms proven qualification-neutral should be reused. Domain-specific interpretation/strategy stays under Takken.

### E7 — isolated runtime gate/pilot (later decision)

Only after the dormant slice is validated should a separate explicit Takken route/gate be considered. This is a future promotion decision, not authorized by this readiness audit.

## Readiness matrix

| Area | Current state | Phase E judgment |
|---|---|---|
| Qualification identity | PT + Takken known | Ready |
| Provider registry | PT configured, Takken fail-closed | Ready |
| Learning-store registry | PT configured, Takken fail-closed | Ready |
| Durable DB qualification axis | Active for PT | Ready for dormant Takken use after store/writer implementation |
| Core Question Bank provider contract | Small/read-only | Ready for first Takken provider |
| Taxonomy/category lookup | PT direct dependency remains | Gap before shared adaptive selector |
| Knowledge Node state-machine concept | Pure state logic | Reusable concept, current evidence composition still PT-bound |
| Canonical Node master | PT data-bound | Takken-owned master required |
| Question equivalence | PT data-bound | Takken-owned resolver/data required only when evidence exists |
| Repair confirmation | PT tag/pair data-bound | Takken-owned evidence required |
| 18-field evidence/progress | PT-specific | Keep PT-specific |
| Exam Weight | PT-specific | Takken must define its own model |
| Learning strategy | PT-specific/shadow/pilot | Do not copy |
| Takken runtime | Not configured | Correctly blocked |

## Immediate next task

The next code task should **not** be a generic refactor. It should begin only when an authoritative Takken question/tag/taxonomy contract or first validated dataset is available.

Until then, the safe repository state is:

1. keep PT Production unchanged,
2. keep Takken fail-closed,
3. preserve the current common interfaces,
4. use this document as the Phase E boundary so future work starts from the first real Takken data contract rather than rediscovering or over-generalizing PT code.
