import app as app_module
import goukaku_ui as ui_module
import supporter_report as report_module


class _ConnectionContext:
    def __init__(self, connection, events=None):
        self.connection = connection
        self.events = events if events is not None else []

    def __enter__(self):
        self.events.append("enter")
        return self.connection

    def __exit__(self, exc_type, exc, tb):
        self.events.append("exit")
        return False


def test_supporter_route_reuses_one_production_connection(monkeypatch):
    connection = object()
    events = []
    seen = {}

    monkeypatch.setattr(ui_module, "database_is_available", lambda: True)
    monkeypatch.setattr(
        ui_module,
        "get_db_connection",
        lambda: _ConnectionContext(connection, events),
    )

    def authorize(token, requested_learner_id, conn):
        seen["authorize"] = (token, requested_learner_id, conn)
        return "supporter", "learner"

    monkeypatch.setattr(
        ui_module,
        "_authorized_supporter_learner_with_connection",
        authorize,
    )

    def build_report(learner_id, *, _connection=None):
        seen["report"] = (learner_id, _connection)
        return {"parent_summary": {}}

    monkeypatch.setattr(ui_module, "build_supporter_report", build_report)

    def learner_name(learner_id, conn, default="学習者"):
        seen["name"] = (learner_id, conn, default)
        return "テスト学習者"

    monkeypatch.setattr(ui_module, "_user_name_with_connection", learner_name)
    monkeypatch.setattr(
        ui_module,
        "render_template",
        lambda *args, **kwargs: "ok",
    )

    response = app_module.app.test_client().get("/supporter?token=ok")

    assert response.status_code == 200
    assert events == ["enter", "exit"]
    assert seen["authorize"] == ("ok", None, connection)
    assert seen["report"] == ("learner", connection)
    assert seen["name"] == ("learner", connection, "学習者")


def test_supporter_report_uses_caller_owned_connection_without_opening_another(monkeypatch):
    connection = object()
    seen = {}

    monkeypatch.setattr(report_module, "database_is_available", lambda: True)
    monkeypatch.setattr(
        report_module,
        "get_db_connection",
        lambda: (_ for _ in ()).throw(
            AssertionError("caller-owned connection must be reused")
        ),
    )

    def learning_data(learner_id, conn):
        seen["learning_connection"] = conn
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
        lambda learner_id, _connection=None: {
            "has_learning": False,
            "fields": [],
            "answered_count": 0,
        },
    )
    monkeypatch.setattr(
        report_module,
        "get_latest_activity_day_summary",
        lambda learner_id, _connection=None: {"has_activity": False},
    )

    result = report_module.build_supporter_report(
        "learner",
        _connection=connection,
    )

    assert seen["learning_connection"] is connection
    assert result["parent_summary"]["current_position"]["answered_count"] == 0
    assert not hasattr(report_module, "_attempts_with_connection")
