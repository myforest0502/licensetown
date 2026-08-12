from datetime import date

from flask import Blueprint, render_template, request


goukaku_ui = Blueprint("goukaku_ui", __name__)

# Ver.1 presentation data. Keep it in one place so database-backed values can
# replace it without changing the templates.
EXAM_DATE = date(2027, 2, 23)
TODAY_GOAL = 30

SUBJECTS = [
    {"name": "教育学", "score": 72, "answers": 126, "minutes": 184},
    {"name": "心理学", "score": 68, "answers": 118, "minutes": 171},
    {"name": "解剖学", "score": 78, "answers": 154, "minutes": 223},
    {"name": "生理学", "score": 75, "answers": 148, "minutes": 210},
    {"name": "基礎運動学", "score": 70, "answers": 112, "minutes": 156},
    {"name": "人間発達学", "score": 74, "answers": 93, "minutes": 137},
    {"name": "病理学", "score": 65, "answers": 88, "minutes": 126},
    {"name": "医学概論", "score": 60, "answers": 76, "minutes": 109},
    {"name": "内科学", "score": 62, "answers": 320, "minutes": 462},
    {"name": "神経医学", "score": 82, "answers": 284, "minutes": 415},
    {"name": "運動器", "score": 58, "answers": 210, "minutes": 306},
    {"name": "精神医学", "score": 48, "answers": 85, "minutes": 121},
    {"name": "小児学", "score": 76, "answers": 137, "minutes": 198},
    {"name": "臨床心理学", "score": 66, "answers": 92, "minutes": 133},
    {"name": "臨床運動学", "score": 70, "answers": 105, "minutes": 152},
    {"name": "動作分析学", "score": 68, "answers": 101, "minutes": 148},
    {"name": "理学療法評価各論", "score": 74, "answers": 173, "minutes": 251},
    {"name": "理学療法治療各論", "score": 68, "answers": 166, "minutes": 242},
]

HOME_SUBJECT_NAMES = {"神経医学", "運動器", "内科学", "小児学", "精神医学", "理学療法評価各論"}
WEEKLY = [("月", 60), ("火", 75), ("水", 67), ("木", 70), ("金", 80), ("土", 65), ("日", 71)]


def build_dashboard():
    today = date.today()
    return {
        "current_date": today,
        "exam_date": EXAM_DATE,
        "days_until_exam": max((EXAM_DATE - today).days, 0),
        "exam_is_tentative": True,
        "overall_progress": 68,
        "total_answers": 1842,
        "correct_answers": 1256,
        "study_minutes": 2538,
        "last_7_days_accuracy": 72,
        "average_accuracy": 68,
        "field_stats": [item for item in SUBJECTS if item["name"] in HOME_SUBJECT_NAMES],
        "weak_fields": sorted((item for item in SUBJECTS if item["answers"] >= 10), key=lambda item: item["score"])[:3],
        "recommended_study": [("精神医学", 10), ("運動器", 10), ("内科学", 10)],
        "today_goal": TODAY_GOAL,
        "today_progress": 18,
    }


@goukaku_ui.route("/goukaku-no-michi")
def home():
    return render_template("goukaku/home.html", dashboard=build_dashboard())


@goukaku_ui.route("/goukaku-no-michi/subjects")
def subjects():
    return render_template("goukaku/subjects.html", subjects=SUBJECTS, weekly=WEEKLY)


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
