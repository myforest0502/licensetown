# LicenseTown JSON / Neon architecture — 2026-09-03

Status: design baseline. No Production DB write or learner-facing behavior change.

## Decision

Use a hybrid architecture.

1. **Canonical Question Bank stays in version-controlled JSON and is loaded into memory at app startup.**
2. **Neon stores dynamic learner data, audit history, supporter relationships, and derived learner state.**
3. Do **not** make Production question delivery depend on a Question Bank SQL lookup at this stage.
4. If future analytics or authoring needs require SQL access to question content, add a read-only/mirrored catalog later; the JSON files remain the source of truth until an explicit migration is approved.

This decision prioritizes the current product goal: fast and reliable 5-question delivery, reproducible content review, rollback safety, and minimal runtime dependency.

## Why the Question Bank should remain JSON for now

The current loader already builds indexed in-memory dictionaries from the formal stores and enforces exact Q-ID parity across questions, answers, explanations, and tags. Runtime access is therefore local and deterministic after startup.

Moving canonical question content into Neon now would add:

- network/database dependency to normal study;
- migration and synchronization failure modes;
- more difficult content diff/review and rollback;
- a second source-of-truth problem while Repair Supply is still adding questions rapidly.

The Question Bank is small enough for process-memory loading. Even after the planned Q1661-Q1737 expansion, it remains appropriate for this architecture.

## Canonical static stores

Keep the existing separated stores:

- `data/question_bank/questions.json`
- `data/question_bank/answers.json`
- `data/question_bank/explanations.json`
- `data/question_bank/question_tags.json`
- `data/question_bank/knowledge_nodes.json`

Q number remains the immutable question ID. Knowledge Node ID remains the immutable concept ID.

Required cross-file invariant:

- every formal Q ID exists exactly once in questions / answers / explanations / tags;
- all referenced Knowledge Nodes exist;
- accepted answer contracts remain explicit;
- historical Q IDs are never reused or renumbered;
- deletion of a previously released Q should be exceptional and documented, not used as a normal cleanup mechanism.

## Question JSON contract

Minimum stable question record:

- `id`
- `management_code`
- `category_large`
- `category_small`
- `source` (`O` / `P` repository convention)
- `title`
- `question_text`
- `choices`
- `exam`

Answer record:

- `id`
- `display_answer`
- `accepted_answer_sets`
- `answer_basis`

Explanation record:

- `id`
- `explanation`
- `choice_explanations`

Tag record keeps the existing learning-engine metadata, including at minimum:

- `id`
- `knowledge_node`
- `task`
- `primary_ability`
- `secondary_ability` when applicable
- `level`
- `safety`
- `prerequisite_nodes`
- `tag_version`
- `tag_status`
- `source` (`original` / `past_exam` tag convention)

Future metadata should be added here rather than embedded into Q numbers. Candidate fields include disease, assessment, intervention, clinical reasoning, difficulty, exam-domain classification, weakness-analysis tags, search tags, review priority, and AI-item-generation tags.

## Runtime access rule

Normal study must use the loaded canonical Question Bank and **must not call OpenAI or Neon to retrieve question text, answer, or explanation per question**.

Neon may be consulted for learner-specific selection inputs such as prior attempts, node state, review timing, and audit metadata. Once the selector chooses a Q ID, the question content itself comes from the in-memory canonical store.

## Neon responsibility boundaries

Current Production schema already separates these responsibilities:

- `user_profiles`: learner identity/profile state used by the app;
- `learning_events`: batch/session-level persisted learning events and `question_results` JSONB audit payload;
- `question_attempts`: normalized one-question attempt history;
- `user_node_state`: derived per-user Knowledge Node learning state;
- `learning_time_events` / `learning_time_totals`: learning-time history and total;
- `supporter_links`: supporter-to-learner relationship;
- `schema_migrations`: applied DB schema versions.

This is the correct direction: **event history is evidence; node state is derived state.** Do not replace attempt history with only the latest state.

## Source-of-truth hierarchy

For content:

1. repository canonical JSON;
2. deployed in-memory Question Bank;
3. any future DB catalog is a derived mirror only unless a later migration explicitly changes this contract.

For learner evidence:

1. `question_attempts` and persisted learning events are durable history;
2. `user_node_state` is rebuildable derived state;
3. dashboards, recommendations, and Phase11 judgments are derived views/decisions and must remain reproducible from persisted evidence plus versioned logic where practical.

## `learning_events.question_results` policy

Keep JSONB for event-specific/audit metadata that does not justify a dedicated relational column yet, including adaptive selection audit fields.

Do not use this JSONB payload as the sole durable source for core one-question facts already represented in `question_attempts`.

Selection metadata such as `selection_reason`, `selection_group`, `selection_score`, `repair_evidence_quality`, `recent_question_repeat`, and `recent_cooldown_bypassed` should remain audit metadata and must not silently become Knowledge Node state inputs unless a separate design explicitly approves that change.

## `question_attempts` policy

Treat this table as the normalized durable attempt ledger.

Stable identity and ordering:

- `event_key` identifies the parent learning event;
- `attempt_position` identifies order within that event;
- unique `(event_key, attempt_position)` prevents duplicate insertion;
- `question_id` and `knowledge_node_id` preserve the content/concept observed at answer time.

Do not rewrite historical rows when tags or canonical mappings later change. If future analysis needs “current canonical node” and “node at attempt time,” add explicit semantics rather than mutating history.

## `user_node_state` policy

This is a cache/materialized learner state, not raw evidence.

Allowed states remain:

- unseen
- checking
- repairing
- repaired
- recheck_due
- stable

State transitions must be reproducible from defined evidence rules. A rebuild/backfill path should continue to exist so corruption or rule upgrades do not require loss of attempt history.

## Database migration policy

Do not perform a large Question Bank SQL migration merely because the project has reached JSON maturity.

DB migrations should be driven by a concrete learner-data or performance requirement.

For every future schema migration:

1. define the data owner/source-of-truth;
2. define backward compatibility;
3. test on a temporary Neon branch first;
4. test existing Production-shaped data;
5. include rollback/rebuild strategy;
6. do not mutate Production until explicit approval when migration execution is required.

## Near-term DB work after Repair Supply

Priority order:

1. finish Q1661-Q1737 Repair Supply and re-run full Question Bank audit;
2. verify current indexes/queries using real Production-shaped workload before adding indexes;
3. formalize dashboard derived metrics from `question_attempts` + `user_node_state` rather than adding demo-value tables;
4. formalize learner “伴走カルテ” as a separate durable domain only after its fields and update rules are defined;
5. add schema only when a feature requires durable data that cannot be safely derived from existing evidence.

## Performance baseline

Current database size is tiny; premature normalization or indexing should be avoided. The main normal-study content path should remain local-memory JSON lookup. Database optimization should focus on learner-history queries only after measuring actual slow paths.

Required latency measurements remain:

- study mode -> 5 questions displayed;
- answer -> scoring;
- consult -> AI response.

Measure Render/app time, Neon query time, and OpenAI time separately.

## Acceptance criteria for this architecture

The design is successful if:

- normal question presentation works when Question Bank JSON is valid, without per-question DB/OpenAI retrieval;
- a Neon outage does not create an alternate AI-generated question path;
- learner writes fail safely rather than corrupting canonical content;
- Question Bank changes remain reviewable in Git and validator-enforced;
- learner history remains durable and reconstructable;
- node state can be rebuilt from evidence;
- future dashboard and Phase11 decisions can be audited from saved evidence;
- no duplicate canonical source of truth is introduced.

## Non-goals

This document does not:

- migrate Production data;
- alter current tables;
- change Phase10/Phase11 ranking or selector behavior;
- change learner-facing UI;
- add a SQL Question Bank;
- change Repair Supply implementation.

## Next implementation design

After Repair Supply is finished, the next DB-oriented implementation should be **dashboard real-data derivation**, not Question Bank SQL migration. It should define total reach, field reach, weakness TOP3, field advice inputs, and recommended-question inputs from the existing canonical Question Bank plus persisted learner evidence.