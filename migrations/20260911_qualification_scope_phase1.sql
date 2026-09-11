-- Phase 1 only: additive/backfill qualification scope for existing PT data.
--
-- IMPORTANT:
-- This migration is intentionally NOT wired into database.py/init_database().
-- Merging this file does not apply it to Production. Apply only after explicit
-- approval, a restore point, and pre/post row-count checks.
--
-- Existing runtime may continue omitting qualification_id; DEFAULT 'pt' keeps
-- current PT behavior until explicit qualification-aware reads/writes are wired.
-- This phase deliberately does NOT change existing primary/unique keys that the
-- legacy runtime depends on. Takken runtime must remain disabled until later key
-- and runtime cutover phases are complete.

ALTER TABLE question_attempts
    ADD COLUMN IF NOT EXISTS qualification_id TEXT NOT NULL DEFAULT 'pt';

ALTER TABLE learning_events
    ADD COLUMN IF NOT EXISTS qualification_id TEXT NOT NULL DEFAULT 'pt';

ALTER TABLE user_node_state
    ADD COLUMN IF NOT EXISTS qualification_id TEXT NOT NULL DEFAULT 'pt';

ALTER TABLE learning_time_events
    ADD COLUMN IF NOT EXISTS qualification_id TEXT NOT NULL DEFAULT 'pt';

ALTER TABLE paused_quiz_sessions
    ADD COLUMN IF NOT EXISTS qualification_id TEXT NOT NULL DEFAULT 'pt';

ALTER TABLE web_learning_sessions
    ADD COLUMN IF NOT EXISTS qualification_id TEXT NOT NULL DEFAULT 'pt';

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'question_attempts_qualification_id_check'
    ) THEN
        ALTER TABLE question_attempts
            ADD CONSTRAINT question_attempts_qualification_id_check
            CHECK (qualification_id ~ '^[a-z][a-z0-9_]*$');
    END IF;
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'learning_events_qualification_id_check'
    ) THEN
        ALTER TABLE learning_events
            ADD CONSTRAINT learning_events_qualification_id_check
            CHECK (qualification_id ~ '^[a-z][a-z0-9_]*$');
    END IF;
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'user_node_state_qualification_id_check'
    ) THEN
        ALTER TABLE user_node_state
            ADD CONSTRAINT user_node_state_qualification_id_check
            CHECK (qualification_id ~ '^[a-z][a-z0-9_]*$');
    END IF;
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'learning_time_events_qualification_id_check'
    ) THEN
        ALTER TABLE learning_time_events
            ADD CONSTRAINT learning_time_events_qualification_id_check
            CHECK (qualification_id ~ '^[a-z][a-z0-9_]*$');
    END IF;
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'paused_quiz_sessions_qualification_id_check'
    ) THEN
        ALTER TABLE paused_quiz_sessions
            ADD CONSTRAINT paused_quiz_sessions_qualification_id_check
            CHECK (qualification_id ~ '^[a-z][a-z0-9_]*$');
    END IF;
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'web_learning_sessions_qualification_id_check'
    ) THEN
        ALTER TABLE web_learning_sessions
            ADD CONSTRAINT web_learning_sessions_qualification_id_check
            CHECK (qualification_id ~ '^[a-z][a-z0-9_]*$');
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS question_attempts_qualification_user_date_idx
    ON question_attempts (qualification_id, user_id, answered_at DESC);
CREATE INDEX IF NOT EXISTS question_attempts_qualification_user_question_date_idx
    ON question_attempts (qualification_id, user_id, question_id, answered_at DESC);
CREATE INDEX IF NOT EXISTS learning_events_qualification_user_date_idx
    ON learning_events (qualification_id, user_id, answered_at);
CREATE INDEX IF NOT EXISTS user_node_state_qualification_user_state_idx
    ON user_node_state (qualification_id, user_id, state);
CREATE INDEX IF NOT EXISTS learning_time_events_qualification_user_date_idx
    ON learning_time_events (qualification_id, user_id, recorded_at);
CREATE INDEX IF NOT EXISTS paused_quiz_sessions_qualification_user_idx
    ON paused_quiz_sessions (qualification_id, user_id);
CREATE INDEX IF NOT EXISTS web_learning_sessions_qualification_user_updated_idx
    ON web_learning_sessions (qualification_id, user_id, updated_at DESC);

-- Initial-assessment state must be per qualification. Keep the legacy profile
-- boolean untouched while introducing a qualification-scoped authority.
CREATE TABLE IF NOT EXISTS qualification_user_state (
    user_id TEXT NOT NULL REFERENCES user_profiles(user_id) ON DELETE CASCADE,
    qualification_id TEXT NOT NULL,
    initial_assessment_completed BOOLEAN NOT NULL DEFAULT FALSE,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_id, qualification_id),
    CHECK (qualification_id ~ '^[a-z][a-z0-9_]*$')
);

INSERT INTO qualification_user_state (
    user_id, qualification_id, initial_assessment_completed, updated_at
)
SELECT user_id, 'pt', initial_assessment_completed, updated_at
FROM user_profiles
ON CONFLICT (user_id, qualification_id) DO UPDATE SET
    initial_assessment_completed = EXCLUDED.initial_assessment_completed,
    updated_at = EXCLUDED.updated_at;

-- Learning-time totals currently use user_id as their primary key. Introduce a
-- parallel qualification-scoped table rather than breaking the legacy key.
CREATE TABLE IF NOT EXISTS qualification_learning_time_totals (
    user_id TEXT NOT NULL,
    qualification_id TEXT NOT NULL,
    total_seconds DOUBLE PRECISION NOT NULL DEFAULT 0,
    PRIMARY KEY (user_id, qualification_id),
    CHECK (qualification_id ~ '^[a-z][a-z0-9_]*$')
);

INSERT INTO qualification_learning_time_totals (
    user_id, qualification_id, total_seconds
)
SELECT user_id, 'pt', total_seconds
FROM learning_time_totals
ON CONFLICT (user_id, qualification_id) DO UPDATE SET
    total_seconds = EXCLUDED.total_seconds;
