import supporter_report as report_module


class _ConnectionContext:
    def __init__(self, connection):
        self.connection = connection

    def __enter__(self):
        return self.connection

    def __exit__(self, exc_type, exc, tb):
        return False


def test_production_supporter_report_reuses_existing_connection_without_attempt_diagnostics(monkeypatch):
    connection = object()
    seen = {}

    monkeypatch.setattr(report_module, "database_is_available", lambda: True)
    monkeypatch.setattr(
        report_module,
        "get_db_connection",
        lambda: _ConnectionContext(connection),
    )

    def learning_data(learner_user_id, conn):
        seen["learner_user_id"] = learner_user_id
        seen["connection"] = conn
        return {
            "summary": {"total_answers": 0, "study_minutes": 0, "average_accuracy": 0},
            "activity": {
                "weekly_learning_days": 0,
                "weekly_answers": 0,
                "weekly_study_minutes": 0,
                "weekly_accuracy": 0,
                "streak_days": 0,
            },
            "fields": [],
            "unique_question_count": 0,
        }

    monkeypatch.setattr(report_module, "_shared_dashboard_learning_data", learning_data)
    monkeypatch.setattr(
        report_module,
        "build_learning_guidance",
        lambda total_answers, fields: {
            "weak_fields": [],
            "weak_analysis_message": "",
            "recommended_study": [],
        },
    )
    monkeypatch.setattr(
        report_module,
        "get_latest_learning_day_summary",
        lambda learner_user_id, _connection=None: {
            "has_learning": False,
            "fields": [],
            "answered_count": 0,
        },
    )
    monkeypatch.setattr(
        report_module,
        "get_latest_activity_day_summary",
        lambda learner_user_id, _connection=None: {"has_activity": False},
    )

    result = report_module.build_supporter_report("learner-user")

    assert seen["learner_user_id"] == "learner-user"
    assert seen["connection"] is connection
    assert result["parent_summary"]["current_position"]["answered_count"] == 0
    assert not hasattr(report_module, "_attempts_with_connection")
