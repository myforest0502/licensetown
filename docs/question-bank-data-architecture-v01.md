# Question Bank data architecture v0.1

Date: 2026-09-03

## Purpose

Define the next safe data architecture for LicenseTown after the Repair Supply expansion, without changing learner-facing behavior, Production DB data, or the current selector.

## Current verified state

- The formal Question Bank is runtime-loaded from four canonical JSON stores: `questions.json`, `answers.json`, `explanations.json`, and `question_tags.json`.
- `question_bank.py` fails closed if IDs do not match exactly across the four stores or if the expected Q-range is incomplete.
- The JSON schema currently encodes the exact bank size/range, so every intentional Question Bank expansion requires a coordinated schema/count update.
- Neon already stores learner/runtime state separately in `user_profiles`, `learning_events`, `question_attempts`, `user_node_state`, learning-time tables, and supporter linkage.
- `question_attempts.question_id` already accepts four-digit Q IDs, and `knowledge_node_id` accepts the current `KNdddd` format.

## Architectural decision

For the next phase, keep **Question Bank content and learner state as separate concerns**.

### Canonical content

The four JSON stores remain the authoritative source for:

- immutable Q ID
- stem and choices
- accepted answer set(s)
- answer basis
- explanation and per-choice explanation
- category/source metadata
- Knowledge Node ID and text
- task / primary ability / secondary ability
- level / safety / prerequisites / tag version / tag status

Knowledge Node registry/canonical mapping files remain authoritative for Node structure and repair relationships.

### Learner/runtime state

Neon remains authoritative for:

- user/profile state
- learning events
- per-question attempts
- confidence
- Node learning state
- review timing
- supporter relationships
- learning time

Do not duplicate changing learner state into Question Bank JSON.

## Why not switch runtime Question Bank reads to Neon yet

The current JSON path already has strong fail-closed validation and is fast because it is loaded at process start. Moving learner-facing reads to Neon before the Repair Supply expansion is finished would combine two independent changes:

1. content expansion / metadata stabilization
2. persistence/runtime-source migration

That would make regressions harder to isolate. The safer sequence is to freeze the expanded bank first, then build and verify a DB mirror before changing the runtime source.

## Target migration sequence

### Stage 1 — finish and freeze the expanded canonical JSON bank

- Complete B12A–B12D.
- Final expected range after the current audit: Q1–Q1737, subject to the implementation audit remaining unchanged.
- Run full validator and cross-file parity checks.
- Re-run category/tag audit after the final batch.
- Freeze a Git tag/Release before any Question Bank persistence migration.

### Stage 2 — remove hard-coded range fragility without weakening validation

The current schema and loader encode an exact upper bound. Replace duplicated hard-coded Q-range expressions with one explicit bank-version/count contract, while preserving fail-closed behavior.

Required invariants:

- Q IDs are contiguous from Q1 through the declared maximum.
- no duplicate IDs
- exact ID parity among questions/answers/explanations/tags
- accepted answer keys exist in choices
- every tag references a valid Knowledge Node
- every Node/canonical reference resolves
- historical Q IDs are never renumbered or reused

Do not make the loader permissive simply to avoid updating counts.

### Stage 3 — add a read-only Question Bank DB mirror

Create normalized or semi-normalized mirror tables only after the JSON bank is frozen. Suggested minimal model:

- `question_bank_questions`
  - `question_id` PK
  - `management_code`
  - `category_large`
  - `category_small`
  - `source`
  - `title`
  - `question_text`
  - `choices JSONB`
  - `exam JSONB`
  - `content_hash`
  - `bank_version`

- `question_bank_answers`
  - `question_id` PK/FK
  - `display_answer`
  - `accepted_answer_sets JSONB`
  - `answer_basis`
  - `content_hash`

- `question_bank_explanations`
  - `question_id` PK/FK
  - `explanation`
  - `choice_explanations JSONB`
  - `content_hash`

- `question_bank_tags`
  - `question_id` PK/FK
  - `knowledge_node_id`
  - `knowledge_node`
  - `theme`
  - `task`
  - `primary_ability`
  - `secondary_ability`
  - `level`
  - `safety`
  - `prerequisite_nodes JSONB`
  - `tag_version`
  - `tag_status`
  - `source`
  - `content_hash`

- optional `question_bank_versions`
  - `bank_version` PK
  - `question_count`
  - `max_question_id`
  - `source_commit_sha`
  - `created_at`

At this stage **JSON remains the runtime source**. The DB mirror is for parity validation and future migration only.

### Stage 4 — deterministic JSON → DB import

Importer requirements:

- one transaction per bank version
- idempotent for the same version/content
- reject any overwrite where the same immutable Q ID has different historical content unless an explicit reviewed correction workflow is used
- compute deterministic hashes for each content component
- fail on missing/duplicate/mismatched IDs before DB write
- no learner tables touched
- dry-run mode required

### Stage 5 — parity gate

Before any runtime DB read:

- 100% Q ID parity JSON vs DB
- 100% answer parity
- 100% explanation parity
- 100% tag parity
- identical random/adaptive candidate sets for fixed fixtures
- identical scoring outcomes for all accepted-answer fixtures
- identical category and Knowledge Node resolution

Run this in CI and locally. Production writes remain prohibited during the proof stage.

### Stage 6 — optional runtime source switch

Only after parity is proven should a feature-gated DB reader be considered.

Safe rollout order:

1. shadow-read DB and compare with JSON while returning JSON results
2. record mismatches only
3. achieve zero mismatch across normal flows
4. enable DB reads in non-production/test environment
5. production switch only with a one-step fallback to JSON

There is no need to switch if JSON startup reads remain materially faster and simpler. DB migration should solve a real operational need, not be done for architecture aesthetics.

## Learner-history compatibility

`question_attempts` and `user_node_state` should continue referencing immutable textual IDs (`Qdddd`, `KNdddd`). The planned Q1737 range fits the current four-digit `question_id` constraint. No learner-history rewrite is needed merely because new questions are appended.

Never renumber historical Q IDs. New content is append-only except for explicitly reviewed corrections.

## Recommended correction policy

Because Q ID is the immutable learning-history key:

- typo/non-semantic correction: same Q ID, reviewed change, audit note
- answer/medical meaning correction: same Q ID only with explicit correction record and regression coverage
- materially new learning demand: new Q ID
- deleted/invalid question: retire from selection but do not reuse the Q ID

A future correction ledger may record `question_id`, old hash, new hash, reason, reviewer, date, and commit SHA.

## Completion criteria for the data-architecture phase

1. B12A–D complete and final bank validator passes.
2. Expanded bank receives a frozen Git tag/Release.
3. One authoritative bank-version/count contract replaces scattered manual range edits without weakening exactness.
4. JSON→DB mirror schema and dry-run importer are implemented with zero learner-table writes.
5. Full JSON↔DB parity test passes.
6. Runtime remains on JSON until an explicit later decision.

## Non-goals

This architecture work must not alter:

- Phase10 selector behavior
- Phase11 judgment weights
- Recent Question Cooldown behavior
- Node-state transition rules
- current learner recommendations
- Production learner data

The objective is to make the Question Bank safer to grow and eventually mirror/migrate, while preserving the currently validated learning engine.