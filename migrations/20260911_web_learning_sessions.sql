CREATE TABLE IF NOT EXISTS web_learning_sessions (
    session_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES user_profiles(user_id) ON DELETE CASCADE,
    session_payload JSONB NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS web_learning_sessions_user_updated_idx
ON web_learning_sessions (user_id, updated_at DESC);
