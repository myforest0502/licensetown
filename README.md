# LicenseTown

理学療法士国家試験受験生向けのAI伴走型学習プラットフォーム。

> やれば出来る子を、やったから出来た子へ。

LicenseTownは、学習者の努力量だけに頼らず、問題演習・正式な学習履歴・Knowledge Node・弱点修復・保持確認・次の学習判断を組み合わせて、国家試験合格までの学習を支えることを目的としています。

## Current snapshot

As of 2026-09-02:

- Question Bank: Q1-Q1605 / 1605 questions
- validator: PASS
- canonical Knowledge Nodes: 1509
- singleton Nodes: 1422
- multi-question Nodes: 87
- LINE Bot study flow: operational
- Recent Question Cooldown v0.2: on main
- adaptive selection audit: on main
- Phase 10 exact-Q adaptive selection: operationally closed
- Phase 11 learning-strategy judgment: diagnostics-only Shadow on main
- Phase 12 「合格への道」 guidance preview: implemented behind feature flag

The learner-facing baseline recommendation remains authoritative until the Phase 11 promotion gate is satisfied.

## Architecture boundary

### Phase 10 — exact question selection

Owns:

- exact Q selection
- Safety selection behavior
- repair evidence preference
- Knowledge Node diversity
- Recent Question Cooldown
- adaptive selection audit metadata

### Phase 11 — learning intent and scope

Deterministic, read-only Shadow judgment.

J1→J7 order:

1. Critical Safety repair
2. confident-wrong cluster
3. repeated-wrong cluster
4. recheck_due
5. insufficient coverage
6. uncertain-correct stabilization
7. maintenance

Phase 11 does not select exact Q IDs and does not mutate formal Node state.

### Phase 12 — learner-facing presentation

Transforms approved formal evidence and Phase 11 output into understandable guidance in 「合格への道」.

Phase 12 does not redefine mastery and does not replace Phase 10/11 responsibilities.

## Formal Knowledge Node states

- `unseen`
- `checking`
- `repairing`
- `repaired`
- `recheck_due`
- `stable`

Formal repair confirmation requires a strong different-Q answer that is correct with confidence 1. Same-Q success or weak different-Q success alone does not move `repairing -> repaired`.

## Question Bank data

Formal data lives under:

`data/question_bank/`

Core files include:

- `questions.json`
- `answers.json`
- `explanations.json`
- `question_tags.json`
- `knowledge_nodes.json`
- `question_tags_audit.txt`

Q number is the immutable question ID.

## Key diagnostics

Supporter diagnostics are read-only and are used to validate behavior before promotion.

Current diagnostic areas include:

- Phase 11 Shadow judgment
- symmetric Baseline-vs-Shadow evidence comparison
- adaptive_daily saved-selection audit
- repairing-Node repairability
- strong repair-supply priority
- repeat structure audit

A retrospective historical Shadow replay is designed next so persisted daily Baseline recommendation plans can be compared with reconstructed historical Shadow judgments without fabricating Production activity.

## Important docs

For the **current operational state**, read this first:

- `docs/phase11-open-gates-20260902.md`

Then use the design/history documents as needed:

- `docs/phase10-long-term-optimization.md`
- `docs/phase10-real-use-qa.md`
- `docs/phase11-index.md`
- `docs/phase11-v01-decision-table.md`
- `docs/phase11-promotion-evidence-matrix.md`
- `docs/phase11-retrospective-shadow-audit-v01.md`
- `docs/strong-repair-pilot-content-audit-v01.md`
- `docs/phase12-goukaku-visualization-v01.md`

## Current implementation work

Two small safety/evidence fixes are implemented as draft PRs but are intentionally not merged until executable tests can run:

- PR #9 — exclude unknown attempts from field repeated-weakness evidence
- PR #10 — fail closed for cross-Node formal repair confirmation

Current diagnostics/policy issues are tracked in GitHub. The open-gates document above is the canonical short status summary.

## Current promotion rule

Phase 11 must not replace learner-facing guidance based on one favorable screenshot, one disagreement, or one newly repaired Node.

Promotion requires evidence that it does not introduce:

- Critical Safety misses
- repeated overreaction to one ordinary wrong
- sparse-coverage failure
- recheck_due starvation
- conflict with Phase 10 exact selection
- true unexplained recent adaptive repetition

Baseline-vs-Shadow disagreements are reviewed symmetrically: either side may have stronger formal evidence.

Unknown attempts may count as learning/exposure activity but must not become confirmed weakness evidence or lower the Phase 11 J2 final accuracy tie-break; evaluable-only tie-break semantics are specified in Issue #11.

## Safety / development principles

- normal study should use saved Question Bank data rather than generate every question with AI
- consultation text is not formal learning evidence
- selector score is not a mastery score
- Question Bank distribution is not learner weakness
- Production learning events must not be fabricated merely to satisfy QA gates
- structural `different_question_strong` status does not by itself prove that an alternate question is educationally discriminative
- large changes should preserve a known recovery point and pass focused tests, full pytest, and the Question Bank validator

## Recovery checkpoint

A fixed recovery branch exists for the Q1605 + Phase11 diagnostics milestone:

`checkpoint/q1605-phase11-diagnostics-20260902`

This checkpoint predates later documentation-only cleanup commits and is intended as a stable code/data recovery point.
