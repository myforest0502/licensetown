CREATE TABLE trial100_attempts (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    test_date DATE NOT NULL,
    source_version TEXT NOT NULL,
    total_questions INTEGER NOT NULL,
    correct_count INTEGER NOT NULL,
    completion_status TEXT NOT NULL DEFAULT 'completed',
    duration_minutes INTEGER,
    supportive BOOLEAN NOT NULL DEFAULT FALSE,
    field_breakdown JSONB,
    review_summary JSONB,
    recorded_by TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, test_date, source_version),
    CHECK (length(btrim(user_id)) > 0),
    CHECK (length(btrim(source_version)) > 0),
    CHECK (total_questions > 0),
    CHECK (correct_count BETWEEN 0 AND total_questions),
    CHECK (completion_status IN ('completed', 'incomplete')),
    CHECK (duration_minutes IS NULL OR duration_minutes > 0)
);

CREATE INDEX trial100_attempts_user_date_idx
ON trial100_attempts (user_id, test_date DESC);
