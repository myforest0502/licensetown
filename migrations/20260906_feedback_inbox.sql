CREATE TABLE IF NOT EXISTS feedback_inbox (
    id BIGSERIAL PRIMARY KEY,
    public_id TEXT NOT NULL UNIQUE,
    tracking_token TEXT NOT NULL UNIQUE,
    source TEXT NOT NULL DEFAULT 'web',
    name TEXT,
    email TEXT,
    category TEXT NOT NULL,
    message TEXT NOT NULL,
    page_path TEXT,
    line_user_id TEXT,
    status TEXT NOT NULL DEFAULT 'received',
    operator_reply TEXT,
    email_delivery_status TEXT NOT NULL DEFAULT 'not_requested',
    email_sent_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    replied_at TIMESTAMPTZ,
    CONSTRAINT feedback_inbox_category_check
        CHECK (category IN ('bug', 'request', 'usage', 'other')),
    CONSTRAINT feedback_inbox_status_check
        CHECK (status IN ('received', 'reviewing', 'planned', 'responded', 'closed')),
    CONSTRAINT feedback_inbox_email_delivery_check
        CHECK (email_delivery_status IN ('not_requested', 'pending', 'sent', 'failed'))
);

CREATE INDEX IF NOT EXISTS feedback_inbox_status_created_idx
    ON feedback_inbox (status, created_at DESC);

CREATE INDEX IF NOT EXISTS feedback_inbox_created_idx
    ON feedback_inbox (created_at DESC);
