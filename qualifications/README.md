# Qualification ownership and compatibility

Baseline: main `722afce9ac00e09889822bc09079f2f256b29fad` (2026-09-19).
See `docs/QUALIFICATION_THREE_LAYER_AUDIT_V01.md` for the full retained-module
inventory. That document describes the earlier audit; the relocation below
supersedes only its exam-weight location decision.

| Class | Home / examples | Boundary |
|---|---|---|
| A: shared contracts | common/base.py, bank_provider.py, learning_store.py | Identity and interfaces only; no PT taxonomy or automatic default |
| B: PT | pt/config.py, provider.py, learning_store.py, learning_writer.py, exam_weight_shadow.py | PT identity, bank adapter, qualified persistence, 18-field frequency/provenance policy |
| C: dormant Takken | takken/config.py and package marker | Metadata only; no question bank, taxonomy, session or provider implementation |
| D: retained composition | common/*_registry.py, root runtime and loaders | Concrete PT wiring and compatibility; not domain-neutral merely because a file is under common |

## Dependency rules

Concrete qualifications depend on common contracts. Package initializers stay
metadata-only. The existing registries are explicit composition exceptions:
provider registry imports the PT bank adapter; store registry imports the PT
store and legacy database. Do not eagerly re-export these from package markers.
A future qualification must register a reviewed implementation explicitly.
Known but unconfigured Takken raises the existing NotConfigured exceptions;
unknown identifiers raise KeyError. Neither may silently select PT.

## Minimal physical separation in this change

`exam_weight_shadow.py` now aliases `qualifications.pt.exam_weight_shadow`.
The PT implementation is byte-identical to the baseline, with no relative file
access or bank/database initialization. Both import paths share the same module
object, constants, function globals and monkeypatches, in either import order.
The canonical module name and source-file introspection now point to the PT path;
no repository consumer depends on their previous values. Existing callers retain
their imports. Stage D/E retains exactly the same weights and authority limits.

## Deliberately retained locations

- app.py / wsgi.py / Procfile / requirements.txt: startup and installation order.
- learning_engine.py / adaptive_question_selector.py / strategy modules:
  PT rules, Safety, repeat/cooldown and runtime composition remain mixed.
- question_bank.py / data/question_bank / KN/equivalence/repair modules:
  fixed data paths and import-time loading; Q1-Q2000 stays immutable.
- database.py / qualification_*_scope.py / session modules: SQL scope, legacy
  fallback and captured-function installation order; no schema work here.
- dashboard, LINE, templates/static and preview assets: current routes and paths.
- tests: existing flat layout retained because fixtures/deselections use paths;
  new compatibility coverage is named test_pt_exam_weight_compatibility.py.
- docs/scripts/reports/staging/migrations: existing links, imports and provenance.

Shared sessions, user state, DB access and selector implementations are only
future candidates; moving them here would not make their current PT semantics
qualification-neutral. No second persistence truth is introduced:
question_attempts -> derived KN state -> field/strategy/readiness -> selector/UI.
Stage E remains the existing PT pilot (field/strategy only); selector owns Q IDs.
Phase11 remains HOLD / Shadow-only.

## Next step

Review this single relocation and its regression evidence before any further
move. A separate Takken slice needs authoritative bank/answer/explanation data,
reviewed taxonomy/KN and qualification-specific learning semantics. Until then,
do not activate Takken or copy PT rules into it. No bulk module/test relocation.

## Stage 2: one PT rule module (2026-09-19)

Baseline main: `3e3a31842f3bc5e883f8893e450a9e1d26d19cc3` (merged #369).
`phase11_active_repair_rules.py` now lives in `qualifications/pt/` with a legacy
module alias. Its PT J2/J3 thresholds and ordering are unchanged. This makes the
existing PT repair policy ownership explicit without importing it from common.
The implementation has only typing imports and pure functions: no data paths,
DB/Bank/app initialization, environment lookup, mutable cache or persistent state.
Both import orders preserve public/private function identity and patched globals.
Source/module introspection identifies the PT path, as for the prior relocation.
`phase11_formal_judgment.py` keeps its legacy import; Phase11 stays HOLD/Shadow-only.
No Stage E authority module, selector, Q/KN data, session or UI file is moved.

Candidates deliberately retained:
- field_evaluation_shadow / field_progress / field_learning_target_shadow /
  learning_strategy_context_shadow: Stage E policy/input paths; excluded here.
- knowledge_node_canonical / knowledge_node_relations: file-relative data paths
  and import-time data loading; not low-risk relocation candidates.
- dashboard_settings: mixes PT exam defaults with shared time/reward helpers.
- question_order_quality: five-question answer-pattern control, not demonstrably
  PT-exclusive; no speculative common extraction.
- learner_readiness_presentation: shared-looking copy mixed with readiness and
  PT repair/Safety contracts; retain the learner-facing boundary.

The next step is review of this single relocation, not automatic further moves
or Phase11 promotion. Existing Takken fail-closed behavior remains unchanged.
