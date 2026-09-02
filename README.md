# LicenseTown

理学療法士国家試験受験生向けのAI伴走型学習プラットフォーム。

> やれば出来る子を、やったから出来た子へ。

LicenseTownは、問題演習・正式な学習履歴・Knowledge Node・弱点修復・保持確認・次の学習判断を組み合わせ、国家試験合格までの学習を支えることを目的としています。

## Current snapshot

As of 2026-09-02:

- Question Bank: **Q1-Q1610 / 1610 questions**
- Question Bank validator: PASS
- canonical Knowledge Nodes: 1509
- singleton Nodes: 1422
- multi-question Nodes: 87
- LINE Bot study flow: operational
- Recent Question Cooldown v0.2: on main
- adaptive selection audit: on main
- Phase 10 exact-Q adaptive selection: operationally closed
- Phase 11 learning-strategy judgment: diagnostics-only Shadow on main
- Phase 11 retrospective current-policy replay: implemented, read-only
- Phase 11 Promotion Evidence Bundle: implemented, Supporter-only
- Phase 11 Production Review v0.1: **HOLD / Shadow-only**
- Repair Supply Phase2 batch1: **Q1606-Q1610 merged after manual medical/content review**
- Phase 12 「合格への道」 guidance preview: implemented behind feature flag

The learner-facing Baseline recommendation remains authoritative until the Phase 11 promotion gate is satisfied.

## Architecture boundary

### Phase 10 — exact question selection

Owns exact Q selection, Safety behavior, repair evidence preference, Knowledge Node diversity, Recent Question Cooldown and adaptive selection audit metadata.

### Phase 11 — learning intent and scope

Deterministic read-only Shadow judgment. J1→J7:

1. Critical Safety repair
2. confident-wrong cluster
3. repeated-wrong cluster
4. recheck_due
5. insufficient coverage
6. uncertain-correct stabilization
7. maintenance

Phase 11 does not select exact Q IDs and does not mutate formal Node state.

### Phase 12 — learner-facing presentation

Transforms approved formal evidence and Phase 11 output into understandable guidance in 「合格への道」. Phase 12 does not redefine mastery or replace Phase 10/11 responsibilities.

## Formal Knowledge Node states

- `unseen`
- `checking`
- `repairing`
- `repaired`
- `recheck_due`
- `stable`

Formal repair confirmation requires a **strong different-Q** answer that is correct with confidence 1. Same-Q success or weak different-Q success alone does not move `repairing -> repaired`.

Unknown means encountered but not evaluably answered: it may keep a Node unresolved/repairing, but it does not independently become confirmed weakness evidence.

## Question Bank data

Formal data lives under `data/question_bank/`.

Core files:

- `questions.json`
- `answers.json`
- `explanations.json`
- `question_tags.json`
- `knowledge_nodes.json`
- `question_tags_audit.txt`

Q number is the immutable question ID.

## Phase 11 current evidence

Initial Production review showed:

- current Shadow target had stronger formal evidence than Baseline;
- no Phase11 Critical Safety miss in eligible replay snapshots;
- no J2/J3 formal-trigger mismatch;
- no explainable-metadata recent-repeat red flag in the corrected repeat diagnostic;
- recheck_due/stable natural-use evidence is still insufficient for promotion;
- repair-confirmation supply was a major bottleneck.

Repair Supply Phase2 therefore adds independent STRONG alternate questions without changing Phase11 ranking or Phase10 selection weights. Batch1 Q1606-Q1610 targets the five highest Priority A Safety-moderate repairing Nodes identified from Production evidence.

Formal STRONG status is necessary evidence plumbing, not proof of educational effectiveness. Real `repairing -> repaired -> recheck_due -> stable` behavior must still be observed.

## Key diagnostics

Supporter diagnostics are read-only and include:

- Phase 11 Shadow judgment
- symmetric Baseline-vs-Shadow evidence comparison
- retrospective historical Shadow replay
- adaptive_daily saved-selection audit
- repairing-Node repairability
- strong repair-supply priority
- repeat structure audit
- one-click `PHASE11_PROMOTION_EVIDENCE_V1` export

## Important docs

Start here for current Phase11 status:

- `docs/phase11-open-gates-20260902.md`
- `docs/phase11-production-evidence-review-20260902-v01.md`
- `docs/phase11-promotion-review-runbook.md`
- `docs/phase11-promotion-evidence-matrix.md`
- `docs/phase11-index.md`

Repair Supply Phase2:

- `docs/repair-supply-phase2-principles-v01.md`
- `docs/repair-supply-phase2-first-batch-v01.md`
- `docs/repair-supply-phase2-batch1-item-design-v02.md`
- `docs/repair-supply-phase2-batch1-medical-review-v01.md`

Other references:

- `docs/phase10-long-term-optimization.md`
- `docs/phase10-real-use-qa.md`
- `docs/phase12-goukaku-visualization-v01.md`

## Promotion rule

Phase 11 must not replace learner-facing guidance because of one favorable screenshot, one disagreement or one newly repaired Node.

Promotion requires evidence of:

- no Critical Safety miss;
- no systematic single-wrong takeover;
- trustworthy repeat diagnostics;
- correct sparse-coverage and unknown handling;
- correct recheck_due behavior;
- no conflict with Phase 10 exact selection;
- symmetric disagreement review, including Current wins when they occur;
- prospective natural-use evidence that is clearly no worse than Baseline.

## Safety / development principles

- normal study uses saved Question Bank data rather than generating every question with AI;
- consultation text is not formal learning evidence;
- selector score is not a mastery score;
- Question Bank distribution is not learner weakness;
- Production learning events are never fabricated merely to satisfy QA gates;
- structural `different_question_strong` status does not by itself prove an alternate question is educationally discriminative;
- major changes preserve a recovery point and pass focused tests, full pytest and the Question Bank validator.

## Recovery checkpoints

- `checkpoint/q1605-phase11-diagnostics-20260902`
- `checkpoint/repair-supply-phase2-ready-20260902`

The latter is the pre-Q1606 Repair Supply Phase2 implementation checkpoint.
