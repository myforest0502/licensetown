-- Phase 2a: add qualification-aware uniqueness alongside legacy conflict keys.
--
-- This migration is intentionally additive. It does NOT drop or replace any
-- existing primary/unique constraint, so current PT runtime conflict targets
-- remain valid. A later code cutover can start using these qualified targets;
-- only after that may a separate migration remove legacy global uniqueness.

ALTER TABLE learning_events
    ADD CONSTRAINT learning_events_qualification_event_key_key
    UNIQUE (qualification_id, event_key);

ALTER TABLE question_attempts
    ADD CONSTRAINT question_attempts_qualification_event_position_key
    UNIQUE (qualification_id, event_key, attempt_position);

ALTER TABLE user_node_state
    ADD CONSTRAINT user_node_state_qualification_user_node_key
    UNIQUE (qualification_id, user_id, knowledge_node_id);

CREATE UNIQUE INDEX learning_time_events_qualification_event_key_idx
    ON learning_time_events (qualification_id, event_key)
    WHERE event_key IS NOT NULL;

ALTER TABLE paused_quiz_sessions
    ADD CONSTRAINT paused_quiz_sessions_qualification_user_key
    UNIQUE (qualification_id, user_id);

ALTER TABLE web_learning_sessions
    ADD CONSTRAINT web_learning_sessions_qualification_session_key
    UNIQUE (qualification_id, session_id);
