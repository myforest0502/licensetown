from datetime import datetime, timezone

import pytest

import feedback_store


def test_validate_feedback_allows_nickname_and_optional_email():
    values = feedback_store.validate_feedback(
        name="げん好き",
        email="",
        category="request",
        message="ここをもう少し分かりやすくしてほしいです。",
    )
    assert values["name"] == "げん好き"
    assert values["email"] is None
    assert values["category"] == "request"


def test_validate_feedback_rejects_bad_email():
    with pytest.raises(feedback_store.FeedbackValidationError):
        feedback_store.validate_feedback(
            name="test",
            email="not-an-email",
            category="bug",
            message="動きません",
        )


def test_validate_feedback_requires_category_and_message():
    with pytest.raises(feedback_store.FeedbackValidationError):
        feedback_store.validate_feedback(name="", email="", category="", message="text")
    with pytest.raises(feedback_store.FeedbackValidationError):
        feedback_store.validate_feedback(name="", email="", category="other", message="")


def test_get_public_status_does_not_return_private_fields(monkeypatch):
    class Cursor:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def execute(self, sql, params):
            assert "name" not in sql.lower()
            assert "email" not in sql.lower()
            assert "message" not in sql.lower()

        def fetchone(self):
            now = datetime.now(timezone.utc)
            return ("LT-20260906-ABCDEF12", "bug", "received", None, now, now, None)

    class Connection:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def cursor(self):
            return Cursor()

    monkeypatch.setattr(feedback_store, "database_is_available", lambda: True)
    monkeypatch.setattr(feedback_store, "get_db_connection", lambda: Connection())

    item = feedback_store.get_feedback_for_public_status("private-token")
    assert item["public_id"] == "LT-20260906-ABCDEF12"
    assert "email" not in item
    assert "name" not in item
    assert "message" not in item
