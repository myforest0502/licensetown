from datetime import date
import os

from flask import Blueprint, abort, render_template, request, url_for
from itsdangerous import BadSignature, URLSafeSerializer, URLSafeTimedSerializer

from database import (
    calculate_overall_progress,
    get_dashboard_learning_data,
    get_field_learning_summary,
    get_learning_activity,
    get_question_attempts,
    get_weekly_question_history,
    get_supported_learner_ids,
    user_names,
)
from learning_analysis import build_gensan_comment, build_learning_guidance
from supporter_report import build_supporter_report
from pilot_diagnostics import build_pilot_diagnostics
from field_progress_presentation import build_field_progress_presentation


goukaku_ui = Blueprint("goukaku_ui", __name__)

EXAM_DATE = date(2027, 2, 20)
TODAY_GOAL = 30
SUPPORTER_TOKEN_MAX_AGE_SECONDS = 30 * 24 * 60 * 60


def field_progress_ui_enabled():
    return os.getenv("ENABLE_FIELD_PROGRESS_UI", "").strip().lower() in {
        "1", "true", "yes", "on",
    }


def create_dashboard_token(user_id):
    serializer = URLSafeSerializer(
        os.getenv("CHANNEL_SECRET", "local-dashboard-secret"),
        salt="goukaku-dashboard",
    )
    return serializer.dumps({"user_id": user_id})


def dashboard_user_id(token):
    if not token:
        return None
    serializer = URLSafeSerializer(
        os.getenv("CHANNEL_SECRET", "local-dashboard-secret"),
        salt="goukaku-dashboard",
    )
    try:
        return serializer.loads(token).get("user_id")
    except (BadSignature, AttributeError):
        return None


def create_supporter_token(supporter_user_id):
    serializer = URLSafeTimedSerializer(
        os.getenv("CHANNEL_SECRET", "local-dashboard-secret"),
        salt="supporter-dashboard",
    )
    return serializer.dumps({"supporter_user_id": supporter_user_id})


def supporter_user_id(token):
    if not token:
        return None
    serializer = URLSafeTimedSerializer(
        os.getenv("CHANNEL_SECRET", "local-dashboard-secret"),
        salt="supporter-dashboard",
    )
    try:
        return serializer.loads(
            token,
            max_age=SUPPORTER_TOKEN_MAX_AGE_SECONDS,
        ).get("supporter_user_id")
    except (BadSignature, AttributeError):
        return None


def authorized_supporter_learner(token, requested_learner_id=None):
    """署名済みsupporterとactiveなリンクの両方から閲覧対象を確定する。"""
    supporter_id = supporter_user_id(token)
    if not supporter_id:
        abort(403)
    learner_ids = get_supported_learner_ids(supporter_id)
    if not learner_ids:
        abort(403)
    if requested_learner_id:
        if requested_learner_id not in learner_ids:
            abort(403)
        return supporter_id, requested_learner_id
    return supporter_id, learner_ids[0]


def build_dashboard(user_id=None):
    today = date.today()
    dashboard = {
        "current_date": today,
        "exam_date": EXAM_DATE,
        "days_until_exam": max((EXAM_DATE - today).days, 0),
        "exam_is_tentative": True,
        "overall_progress": 0,
        "total_answers": 0,
        "unique_answered_questions": 0,
        "correct_answers": 0,
        "study_minutes": 0,
        "last_7_days_accuracy": 0,
        "average_accuracy": 0,
        "field_stats": [],
        "field_progress_ui_enabled": False,
        "field_progress_fields": [],
        "weak_fields": [],
        "weak_analysis_message": "まずは100問を目標に基礎を固めましょう。",
        "recommended_study": [],
        "recommendation_reason": None,
        "today_goal": TODAY_GOAL,
        "today_progress": 0,
        "streak_days": 0,
        "next_reward_answers": 100,
        "reward_progress": 0,
        "gensan_comment": "今日はまだ来てねぇな。5問だけやるか？＾＾",
    }
    if user_id:
        learning_data = get_dashboard_learning_data(user_id)
        dashboard.update(learning_data["summary"])
        dashboard.update(learning_data["activity"])
        dashboard["unique_answered_questions"] = learning_data["unique_question_count"]
        dashboard["overall_progress"] = calculate_overall_progress(
            dashboard["study_minutes"],
            dashboard["total_answers"],
            dashboard["unique_answered_questions"],
        )
        fields = learning_data["fields"]
        dashboard["field_stats"] = [item for item in fields if item["learned"]]
        if field_progress_ui_enabled():
            dashboard["field_progress_ui_enabled"] = True
            dashboard["field_progress_fields"] = build_field_progress_presentation(
                get_question_attempts(user_id), legacy_fields=fields
            )
        dashboard.update(build_learning_guidance(dashboard["total_answers"], fields))
        remainder = dashboard["total_answers"] % 100
        dashboard["next_reward_answers"] = 100 - remainder if remainder else 100
        dashboard["reward_progress"] = remainder
        dashboard["gensan_comment"] = build_gensan_comment(
            dashboard["total_answers"],
            fields,
            dashboard["weak_fields"],
            dashboard["recommended_study"],
            dashboard["streak_days"],
            dashboard["today_progress"],
        )
    return dashboard


@goukaku_ui.route("/goukaku-no-michi")
def home():
    token = request.args.get("token")
    user_id = dashboard_user_id(token)
    return render_template(
        "goukaku/home.html",
        dashboard=build_dashboard(user_id),
        dashboard_token=token,
        dashboard_title="合格への道",
        read_only=False,
        subjects_url=url_for("goukaku_ui.subjects", token=token),
        line_official_account_id=os.getenv("LINE_OFFICIAL_ACCOUNT_ID", "").strip(),
        liff_id=os.getenv("LIFF_ID", "").strip(),
    )


@goukaku_ui.route("/goukaku-no-michi/subjects")
def subjects():
    token = request.args.get("token")
    user_id = dashboard_user_id(token)
    subjects = get_field_learning_summary(user_id) if user_id else get_field_learning_summary("")
    activity = get_learning_activity(user_id) if user_id else get_learning_activity("")
    recent_fields = [item for item in subjects if item["recent_7d_answered_count"]]
    top_recent_field = max(
        recent_fields, key=lambda item: item["recent_7d_answered_count"], default=None
    )
    return render_template(
        "goukaku/subjects.html",
        subjects=subjects,
        activity=activity,
        top_recent_field=top_recent_field,
        dashboard_token=token,
        read_only=False,
        return_url=url_for("goukaku_ui.home", token=token),
    )


@goukaku_ui.route("/goukaku-no-michi/footprints")
def footprints():
    user_name = request.args.get("name", "あなた").strip()[:30] or "あなた"
    events = [
        ("8月12日", "トータル100問達成！"),
        ("8月15日", "初めて相談モードを利用"),
        ("8月17日", "初めて熱血モードにチャレンジ！"),
        ("8月24日", "調子が出ない中でも3問クリア"),
        ("9月3日", "初めて30問完走！"),
    ]
    return render_template("goukaku/footprints.html", user_name=user_name, events=events)


@goukaku_ui.route("/goukaku-no-michi/learning")
def learning():
    field_name = request.args.get("field", "おすすめ分野").strip()[:30] or "おすすめ分野"
    question_count = request.args.get("count", "10").strip()[:3]
    if not question_count.isdigit():
        question_count = "10"
    return render_template("goukaku/learning.html", field_name=field_name, question_count=question_count)


@goukaku_ui.route("/supporter")
def supporter_dashboard():
    token = request.args.get("token")
    _, learner_id = authorized_supporter_learner(
        token,
        request.args.get("learner_user_id"),
    )
    report = build_supporter_report(learner_id)
    learner_name = user_names.get(learner_id, "学習者") or "学習者"
    return render_template(
        "goukaku/supporter.html",
        learner_name=learner_name,
        learner_id=learner_id,
        supporter_token=token,
        report=report,
    )


@goukaku_ui.route("/supporter/weekly-question-history")
def supporter_weekly_question_history():
    token = request.args.get("token")
    _, learner_id = authorized_supporter_learner(token, request.args.get("learner_user_id"))
    learner_name = user_names.get(learner_id, "学習者") or "学習者"
    return render_template("goukaku/supporter_weekly_questions.html", learner_name=learner_name,
                           learner_id=learner_id, supporter_token=token,
                           weekly=get_weekly_question_history(learner_id))


@goukaku_ui.route("/supporter/pilot-diagnostics")
def supporter_pilot_diagnostics():
    token = request.args.get("token")
    _, learner_id = authorized_supporter_learner(token, request.args.get("learner_user_id"))
    period = request.args.get("period", "7")
    if period not in {"7", "30", "all"}:
        period = "7"
    return render_template("goukaku/supporter_pilot_diagnostics.html",
                           diagnostics=build_pilot_diagnostics(learner_id, period),
                           learner_id=learner_id, supporter_token=token)


@goukaku_ui.route("/supporter/goukaku-no-michi")
def supporter_goukaku_home():
    token = request.args.get("token")
    _, learner_id = authorized_supporter_learner(
        token,
        request.args.get("learner_user_id"),
    )
    learner_name = user_names.get(learner_id, "学習者") or "学習者"
    return render_template(
        "goukaku/home.html",
        dashboard=build_dashboard(learner_id),
        dashboard_token=None,
        dashboard_title=f"{learner_name}さんの合格への道",
        learner_name=learner_name,
        read_only=True,
        subjects_url=url_for(
            "goukaku_ui.supporter_goukaku_subjects",
            token=token,
            learner_user_id=learner_id,
        ),
        supporter_return_url=url_for(
            "goukaku_ui.supporter_dashboard",
            token=token,
            learner_user_id=learner_id,
        ),
        line_official_account_id="",
        liff_id="",
    )


@goukaku_ui.route("/supporter/goukaku-no-michi/subjects")
def supporter_goukaku_subjects():
    token = request.args.get("token")
    _, learner_id = authorized_supporter_learner(
        token,
        request.args.get("learner_user_id"),
    )
    subjects = get_field_learning_summary(learner_id)
    activity = get_learning_activity(learner_id)
    recent_fields = [item for item in subjects if item["recent_7d_answered_count"]]
    top_recent_field = max(
        recent_fields, key=lambda item: item["recent_7d_answered_count"], default=None
    )
    return render_template(
        "goukaku/subjects.html",
        subjects=subjects,
        activity=activity,
        top_recent_field=top_recent_field,
        dashboard_token=None,
        read_only=True,
        return_url=url_for(
            "goukaku_ui.supporter_goukaku_home",
            token=token,
            learner_user_id=learner_id,
        ),
    )
