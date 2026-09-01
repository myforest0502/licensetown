# Unknown Storage Contract v0.1

Date: 2026-09-02
Status: current Production storage fact; no migration proposed.

## Formal write representation

A LicenseTown 0-answer / unknown quiz result is represented in saved question result data as:

- `selected_answers=[]`
- `confidence=null`
- `answer_status='unknown'`
- `is_correct=false`

## question_attempts persistence

The current Production `question_attempts` table does **not** persist a dedicated `answer_status` column.

It stores:

- event_key
- user_id
- question_id
- knowledge_node_id
- mode
- selected_answers
- is_correct
- confidence
- answered_at
- attempt_position

`get_question_attempts()` reconstructs the runtime status as:

```python
answer_status = 'unknown' if not selected_answers else 'answered'
```

The local fallback uses the same default reconstruction.

## Consequence

The approved evaluable definition in `docs/unknown-evidence-semantics-v01.md` does **not** require a DB migration.

For attempts loaded through the formal helper, downstream code can use:

```python
attempt.get('answer_status') != 'unknown'
```

because the helper reconstructs the status consistently.

For lower-level code that reads `question_attempts` directly, use the same storage contract rather than inventing another unknown rule.

## Historical replay

Retrospective Phase11 replay must verify unknown consistency across both sources when history coverage is checked:

- learning_events.question_results saved status/selected answers
- question_attempts selected_answers / confidence / is_correct

At minimum, an unknown formal result should correspond to an attempt with empty selected answers and no confidence under the current storage convention.

Do not require a nonexistent `question_attempts.answer_status` database column.

## Legacy compatibility

Old question_attempt rows may not have an explicit semantic version. Therefore the replay coverage gate should fail closed if saved event result and reconstructed attempt meaning disagree.

Do not mutate old rows just to normalize them for replay.

## Important semantic warning

Because unknown is physically stored with `is_correct=false`, any low-level consumer that filters only on:

```python
is_correct is False
```

will include unknown unless it explicitly excludes reconstructed unknown status.

This is the root pattern behind several current audit issues. New evidence code should prefer the formal loaded-attempt contract instead of raw `is_correct` alone when the question is about **confirmed wrong evidence**.
