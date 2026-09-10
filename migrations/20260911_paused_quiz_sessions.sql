CREATE TABLE IF NOT EXISTS paused_quiz_sessions (
    user_id TEXT PRIMARY KEY REFERENCES user_profiles(user_id) ON DELETE CASCADE,
    session_payload JSONB NOT NULL,
    paused_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS paused_quiz_sessions_paused_at_idx
ON paused_quiz_sessions (paused_at);
