from datetime import date
import os

from flask import Blueprint, abort, render_template, request, url_for
from itsdangerous import BadSignature, URLSafeSerializer, URLSafeTimedSerializer

from database import (
    get_field_learning_summary,
    get_learning_activity,
    get_learning_summary,
    get_supported_learner_ids,
    user_names,
)
from learning_analysis import build_learning_guidance
from supporter_report import build_supporter_report


goukaku_ui = Blueprint("goukaku_ui", __name__)

EXAM_DATE = date(2027, 2, 20)
TODAY_GOAL = 30
SUPPORTER_TOKEN_MAX_AGE_SECONDS = 30 * 24 * 60 * 60


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
        "correct_answers": 0,
        "study_minutes": 0,
        "last_7_days_accuracy": 0,
        "average_accuracy": 0,
        "field_stats": [],
        "weak_fields": [],
        "weak_analysis_message": "まずは100問を目標に基礎を固めましょう。",
        "recommended_study": [],
        "today_goal": TODAY_GOAL,
        "today_progress": 0,
        "streak_days": 0,
        "next_reward_answers": 100,
        "reward_progress": 0,
        "gensan_comment": "今日はまだ来てねぇな。5問だけやるか？＾＾",
    }
    if user_id:
        dashboard.update(get_learning_summary(user_id))
        dashboard.update(get_learning_activity(user_id))
        fields = get_field_learning_summary(user_id)
        dashboard["field_stats"] = [item for item in fields if item["learned"]]
        dashboard.update(build_learning_guidance(dashboard["total_answers"], fields))
        remainder = dashboard["total_answers"] % 100
        dashboard["next_reward_answers"] = 100 - remainder if remainder else 100
        dashboard["reward_progress"] = remainder
        if dashboard["today_progress"] >= dashboard["today_goal"]:
            dashboard["gensan_comment"] = "今日は頑張ったな。胸張っていいぞ＾＾"
        elif dashboard["today_progress"]:
            dashboard["gensan_comment"] = "ちゃんと続いてるじゃねぇか＾＾"
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
