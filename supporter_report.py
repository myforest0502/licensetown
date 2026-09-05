"""Build the parent-facing learning report.

The parent page intentionally uses only lightweight learning aggregates. Developer
and learner diagnostics live elsewhere under /internal or the learner dashboard.
"""

from __future__ import annotations

from contextlib import nullcontext
from datetime import timezone
from zoneinfo import ZoneInfo

from database import (
    _get_question_result_rows,
    database_is_available,
    get_dashboard_learning_data,
    get_db_connection,
    get_field_learning_summary,
    get_latest_activity_day_summary,
    get_latest_learning_day_summary,
    get_learning_activity,
    get_learning_summary,
    get_unique_answered_question_count,
)
from learning_analysis import build_learning_guidance
from supporter_performance import measure


def _supporter_comment(latest: dict, streak_days: int) -> str:
    if not latest["has_learning"]:
        return "学習記録はこれからです。急がせず、始められるタイミングを穏やかに見守ってあげてください＾＾"
    label = latest["date_label"]
    if latest["answered_count"] >= 30:
        return f"{label}はしっかり取り組めています。結果より、続けていることを見守ってあげてください＾＾"
    if latest["answered_count"] > 0:
        if streak_days >= 2:
            return f"{label}まで継続できています。口を出さず、見守るだけでも良さそうです。"
        return f"{label}に取り組めています。無理に追い込まず、この歩みを見守ってあげてください。"
    return "焦らず、次に取り組めるタイミングを見守ってあげてください。"


def _format_latest(latest: dict) -> dict:
    latest = dict(latest)
    if latest.get("has_learning"):
        answered_at = latest["last_answered_at"]
        if answered_at.tzinfo is None:
            answered_at = answered_at.replace(tzinfo=timezone.utc)
        answered_at = answered_at.astimezone(ZoneInfo("Asia/Tokyo"))
        latest["date_label"] = f"{answered_at.month}/{answered_at.day}"
        latest["answered_at_label"] = (
            f"{answered_at.month}/{answered_at.day} "
            f"{answered_at.hour:02}:{answered_at.minute:02}"
        )
    else:
        latest["date_label"] = ""
        latest["answered_at_label"] = ""
    return latest


def _format_latest_activity(latest_activity: dict) -> dict:
    latest_activity = dict(latest_activity)
    if latest_activity.get("has_activity"):
        _, month, day = latest_activity["date"].split("-")
        latest_activity["date_label"] = f"{int(month)}/{int(day)}"
    else:
        latest_activity["date_label"] = ""
    return latest_activity


def _pace(activity: dict) -> dict:
    days = int(activity.get("weekly_learning_days") or 0)
    answers = int(activity.get("weekly_answers") or 0)
    if answers == 0:
        return {"status": "様子見", "reason": "直近7日で問題学習の記録がありません。"}
    if days >= 3 or answers >= 30:
        return {
            "status": "継続中",
            "reason": f"直近7日で{days}日・{answers}問の学習記録があります。",
        }
    return {
        "status": "ペース確認",
        "reason": f"直近7日は{days}日・{answers}問です。無理なく続けられるペースか見守ります。",
    }


def _current_position(summary: dict, fields: list[dict]) -> dict:
    answers = int(summary.get("total_answers") or 0)
    accuracy = int(round(float(summary.get("average_accuracy") or 0)))
    field_count = len(fields)
    if answers == 0:
        text = "まだ学習記録がありません。"
        status = "これから"
    elif answers < 30:
        text = "まずは学習データを集めている段階です。"
        status = "学習開始"
    elif field_count < 3:
        text = "取り組む分野を少しずつ広げている段階です。"
        status = "範囲拡大中"
    elif accuracy >= 70:
        text = "複数分野で学習を進め、正答も安定してきています。"
        status = "学習継続"
    elif accuracy >= 50:
        text = "学習範囲を広げながら、正答を安定させている段階です。"
        status = "確認中"
    else:
        text = "学習は進んでいます。正答が安定しない分野を見直している段階です。"
        status = "見直し中"
    return {
        "status": status,
        "text": text,
        "answered_count": answers,
        "field_count": field_count,
        "average_accuracy": accuracy,
    }


def _trajectory(summary: dict, activity: dict, fields: list[dict]) -> dict:
    answers = int(summary.get("total_answers") or 0)
    accuracy = int(round(float(summary.get("average_accuracy") or 0)))
    weekly = int(activity.get("weekly_answers") or 0)
    if answers < 30:
        status = "判定保留"
        reason = "学習データが増えてから、進み方を見ていきます。"
    elif weekly == 0:
        status = "様子見"
        reason = "直近7日の問題学習がないため、まず再開できるかを見守ります。"
    elif len(fields) >= 3 and accuracy >= 70:
        status = "順調"
        reason = "学習を続けながら、複数分野で正答を積み上げています。"
    else:
        status = "継続中"
        reason = "学習は進んでいます。範囲と正答の安定をこれから確認していきます。"
    return {
        "status": status,
        "reason": reason,
        "pass_probability": None,
        "pass_guarantee": False,
    }


def _parent_summary(summary: dict, activity: dict, fields: list[dict], latest: dict) -> dict:
    return {
        "latest_day": {
            "has_learning": bool(latest.get("has_learning")),
            "date_label": latest.get("date_label", ""),
            "answered_at_label": latest.get("answered_at_label", ""),
            "answered_count": int(latest.get("answered_count") or 0),
            "study_minutes": int(latest.get("study_minutes") or 0),
            "fields": [
                {"name": item["name"], "answered_count": int(item.get("answered_count") or 0)}
                for item in latest.get("fields", [])
            ],
        },
        "cumulative": {
            "answered_count": int(summary.get("total_answers") or 0),
            "study_minutes": int(summary.get("study_minutes") or 0),
            "fields": [
                {"name": item["name"], "answered_count": int(item.get("answered_count") or 0)}
                for item in fields
            ],
        },
        "recent_7d": {
            "learning_days": int(activity.get("weekly_learning_days") or 0),
            "answered_count": int(activity.get("weekly_answers") or 0),
            "study_minutes": int(activity.get("weekly_study_minutes") or 0),
        },
        "pace": _pace(activity),
        "current_position": _current_position(summary, fields),
        "trajectory": _trajectory(summary, activity, fields),
    }


def _shared_dashboard_learning_data(learner_user_id: str, conn) -> dict:
    question_rows = _get_question_result_rows(learner_user_id, conn)
    return {
        "summary": get_learning_summary(learner_user_id, _connection=conn),
        "activity": get_learning_activity(learner_user_id, _connection=conn),
        "fields": get_field_learning_summary(
            learner_user_id,
            _connection=conn,
            _question_result_rows=question_rows,
        ),
        "unique_question_count": get_unique_answered_question_count(
            learner_user_id,
            _connection=conn,
            _question_result_rows=question_rows,
        ),
    }


def build_supporter_report(learner_user_id: str, *, _connection=None) -> dict:
    """Return parent-facing aggregates without loading per-question diagnostics."""
    with measure("build_supporter_report.total"):
        if database_is_available():
            connection_context = (
                nullcontext(_connection)
                if _connection is not None
                else get_db_connection()
            )
            with connection_context as conn:
                with measure("db.dashboard_learning_data"):
                    learning_data = _shared_dashboard_learning_data(learner_user_id, conn)
                summary = learning_data["summary"]
                activity = learning_data["activity"]
                all_fields = learning_data["fields"]
                learned_fields = [item for item in all_fields if item["learned"]]
                with measure("db.latest_learning_day_summary"):
                    latest = _format_latest(
                        get_latest_learning_day_summary(learner_user_id, _connection=conn)
                    )
                with measure("db.latest_activity_day_summary"):
                    latest_activity = _format_latest_activity(
                        get_latest_activity_day_summary(learner_user_id, _connection=conn)
                    )
        else:
            with measure("db.dashboard_learning_data"):
                learning_data = get_dashboard_learning_data(learner_user_id)
            summary = learning_data["summary"]
            activity = learning_data["activity"]
            all_fields = learning_data["fields"]
            learned_fields = [item for item in all_fields if item["learned"]]
            with measure("db.latest_learning_day_summary"):
                latest = _format_latest(get_latest_learning_day_summary(learner_user_id))
            with measure("db.latest_activity_day_summary"):
                latest_activity = _format_latest_activity(
                    get_latest_activity_day_summary(learner_user_id)
                )

        with measure("python.learning_guidance"):
            guidance = build_learning_guidance(summary["total_answers"], all_fields)
        with measure("python.parent_summary"):
            parent_summary = _parent_summary(summary, activity, learned_fields, latest)

        return {
            "parent_summary": parent_summary,
            "latest": latest,
            "latest_studied": latest["has_learning"],
            "latest_fields": latest["fields"],
            "latest_activity": latest_activity,
            "weekly_learning_days": activity["weekly_learning_days"],
            "weekly_answers": activity["weekly_answers"],
            "weekly_study_minutes": activity["weekly_study_minutes"],
            "weekly_accuracy": activity["weekly_accuracy"],
            "streak_days": activity["streak_days"],
            "fields": learned_fields,
            "weak_fields": guidance["weak_fields"],
            "weak_analysis_message": guidance["weak_analysis_message"],
            "recommended_study": guidance["recommended_study"],
            "comment": _supporter_comment(latest, activity["streak_days"]),
        }
