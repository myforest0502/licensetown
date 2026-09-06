# LicenseTown

理学療法士国家試験受験生向けのAI伴走型学習プラットフォーム。

> やれば出来る子を、やったから出来た子へ。

LicenseTownは、問題演習・正式な学習履歴・Knowledge Node・弱点修復・保持確認・次の学習判断を組み合わせ、国家試験合格までの学習を支えることを目的としています。

## Current snapshot

As of 2026-09-06:

- Question Bank: **Q1-Q1737 / 1737 questions**
- source mix: **original 643 / past_exam 1094**
- Question Bank validator: PASS
- Question Bank is formal JSON and loaded deterministically from `data/question_bank/`
- LINE Bot study flow: operational
- learner study routes: end-to-end reliability audit completed
- Recent Question Cooldown v0.2: on main
- Phase 10 exact-Q adaptive selection: operationally closed
- learner dashboard / 「合格への道」: real-data navigation, progress, weekly facts, weakness/coverage guidance implemented
- Phase 11 learning-strategy judgment: **HOLD / Shadow-only**
- Phase 11 retrospective replay, Promotion Evidence Bundle, internal gate dashboard: implemented read-only
- Phase 11 J4 natural retention outcome audit and J5 intent-vs-exact-Q alignment audit: implemented read-only
- answer-submit performance issue #199: natural before/after evidence recorded and closed

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

Transforms approved formal evidence into understandable guidance in 「合格への道」. Phase 12 does not redefine mastery or replace Phase 10/11 responsibilities.

## Formal Knowledge Node states

- `unseen`
- `checking`
- `repairing`
- `repaired`
- `recheck_due`
- `stable`

Formal repair confirmation requires a **STRONG different-question** answer that is correct with confidence 1. Same-Q success or weak different-Q success alone does not move `repairing -> repaired`.

Unknown means encountered but not evaluably answered: it may keep a Node unresolved/repairing, but it does not independently become confirmed weakness evidence.

## Question Bank data

Formal data lives under `data/question_bank/`. Q number is the immutable question ID.

Core files include:

- `questions.json`
- `answers.json`
- `explanations.json`
- `question_tags.json`
- `question_tags.schema.json`
- `knowledge_nodes.json`
- `knowledge_node_canonical_map.json`
- `knowledge_node_relations.json`
- `bank_manifest.json`

`question_bank.py` loads the saved bank and validates closed-world consistency instead of generating ordinary study questions at request time.

## Phase 11 current evidence

Natural Production use on 2026-09-06 supplied a 200-answer study day and meaningful repair evidence. The important current conclusions are:

- generic same-day repeat accuracy is not treated as repair proof;
- STRONG different-question repair is being exercised naturally;
- natural retention review is not yet available in Production history;
- the first currently forecast J4 window begins around **2026-09-09 JST**, subject to intervening learner evidence;
- no timestamps or synthetic learner attempts are created to force that gate;
- J4 clears only after a natural STRONG different-question retention review produces a decisive formal outcome (`stable` or `repairing`);
- J5 independently checks whether persisted Phase10 exact-Q execution is compatible with a saved `recheck_due` intent;
- automatic learner-facing Phase11 promotion remains impossible; manual review is required.

See `docs/phase11-open-gates-20260906.md` and GitHub issue #90 for the current natural-retention evidence gate.

## Key diagnostics

Internal read-only diagnostics include:

- Phase 11 Shadow judgment
- symmetric Baseline-vs-Shadow evidence comparison
- retrospective historical Shadow replay
- adaptive_daily saved-selection audit
- repairing-Node repairability
- strong repair-supply priority
- repeat structure audit
- same-day session-load facts
- natural repair effectiveness
- retention horizon
- retention STRONG-supply and cooldown preflight
- natural retention outcomes
- J5 intent-selection alignment
- conservative Promotion Gate Status
- `PHASE11_PROMOTION_EVIDENCE_V1` export

## Current core boundary

Work that can be completed without manufacturing future learner behavior is implemented and test-covered. The remaining Phase11 promotion evidence is natural-use evidence, primarily the spaced J4/J5 case expected when repaired Nodes actually become due.

Question Bank JSON formalization, real-data learner navigation/dashboard, route reliability, and the measured answer-submit optimization are not current missing core migrations.

## Safety / development principles

- normal study uses saved Question Bank data rather than generating every question with AI;
- consultation text is not formal learning evidence;
- selector score is not a mastery score;
- Question Bank distribution is not learner weakness;
- Production learning events are never fabricated merely to satisfy QA gates;
- structural `different_question_strong` status does not by itself prove an alternate question is educationally discriminative;
- Phase11 remains Shadow-only until natural evidence justifies a separately reviewed learner-facing pilot;
- major changes preserve a recovery point and pass focused tests, full pytest and the Question Bank validator.
