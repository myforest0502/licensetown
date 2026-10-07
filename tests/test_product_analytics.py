import product_analytics as analytics


class FakeClient:
    def __init__(self, fail=False):
        self.fail = fail
        self.calls = []

    def capture(self, **kwargs):
        if self.fail:
            raise RuntimeError("analytics unavailable")
        self.calls.append(kwargs)
        return "event-id"

    def flush(self):
        return None


def test_pseudonymous_distinct_id_is_stable_and_does_not_expose_source(monkeypatch):
    monkeypatch.setenv("POSTHOG_PSEUDONYM_SALT", "test-only-salt")
    raw = "external-user-123"
    first = analytics.distinct_id_for_user(raw)
    second = analytics.distinct_id_for_user(raw)
    other = analytics.distinct_id_for_user("external-user-456")
    assert first == second
    assert first != other
    assert first.startswith("lt_")
    assert raw not in first


def test_safe_properties_allowlist_drops_sensitive_or_free_text(monkeypatch):
    monkeypatch.setenv("LICENSETOWN_ANALYTICS_ENV", "test")
    safe = analytics._safe_properties({
        "question_id": "Q123",
        "mode": "study",
        "is_correct": True,
        "email": "should-not-leave-app@example.com",
        "question": "full question body",
        "explanation": "full explanation",
        "token": "secret",
    })
    assert safe == {
        "analytics_environment": "test",
        "question_id": "Q123",
        "mode": "study",
        "is_correct": True,
    }


def test_learning_variant_distinguishes_product_modes():
    assert analytics.learning_variant({
        "mode": "study", "session_kind": "adaptive_daily"
    }) == "normal_lt"
    assert analytics.learning_variant({
        "mode": "study", "session_kind": "adaptive_daily", "floor_up_target_field": 9
    }) == "bottom_up_lt"
    assert analytics.learning_variant({
        "mode": "study", "session_kind": "manual", "category_small": 2
    }) == "field_study"
    assert analytics.learning_variant({
        "mode": "nekketsu", "session_kind": "manual", "category_small": 2
    }) == "nekketsu"
    assert analytics.learning_variant({
        "mode": "study", "session_kind": "dashboard_recommendation"
    }) == "dashboard_recommendation"


def test_capture_uses_only_pseudonymous_id_and_safe_properties(monkeypatch):
    monkeypatch.setenv("POSTHOG_PROJECT_API_KEY", "phc_test")
    monkeypatch.setenv("POSTHOG_PSEUDONYM_SALT", "test-only-salt")
    monkeypatch.setenv("LICENSETOWN_ANALYTICS_ENV", "test")
    fake = FakeClient()
    monkeypatch.setattr(analytics, "_client", fake)

    assert analytics.capture(
        "raw-external-id",
        "answer_submitted",
        {
            "question_id": "Q1",
            "is_correct": False,
            "confidence": 2,
            "question": "must not be sent",
            "selected_answers": "A",
        },
    )

    call = fake.calls[0]
    assert call["event"] == "answer_submitted"
    assert call["distinct_id"].startswith("lt_")
    assert "raw-external-id" not in call["distinct_id"]
    assert call["properties"]["question_id"] == "Q1"
    assert "question" not in call["properties"]
    assert "selected_answers" not in call["properties"]


def test_analytics_failure_never_blocks_application(monkeypatch):
    monkeypatch.setenv("POSTHOG_PROJECT_API_KEY", "phc_test")
    monkeypatch.setenv("POSTHOG_PSEUDONYM_SALT", "test-only-salt")
    monkeypatch.setattr(analytics, "_client", FakeClient(fail=True))
    assert analytics.capture("user", "session_started", {"mode": "study"}) is False
