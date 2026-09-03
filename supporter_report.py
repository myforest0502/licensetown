"""Build supporter-facing learning data without developer diagnostics.

``parent_summary`` is the stable vNext parent contract.  Legacy top-level keys are
kept temporarily so the existing supporter UI can be migrated without changing
its data semantics in the same step.  #100 will measure the old calls before any
performance simplification.
"""

from __future__ import annotations

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
    get_question_attempts,
    get_unique_answered_question_count,
)
from field_evidence import build_field_evidence
from field_progress import build_field_progress
from learning_analysis import build_learning_guidance
from pass_readiness import build_pass_readiness
from supporter_performance import measure


_POSITION_TEXT = {
    "insufficient_evidence": "まだ判断材料を集めている段階です。",
    "building_coverage": "学習範囲を広げている段階です。",
    "repair_required": "理解を修正している項目があります。",
    "retention_confirmation_needed": "覚え直した内容の定着を確認している段階です。",
    "safety_attention_required": "優先して見直したい重要項目があります。",
    "approaching_readiness": "合格に必要な準備の証拠がそろいつつあります。",
    "readiness_supported": "LT上では幅広い準備の証拠が確認できています。",
}

_TRAJECTORY = {
    "insufficient_evidence": ("判定保留", "学習データが増えてから見通しを判断します。"),
    "building_coverage": ("学習継続", "まずは未確認の範囲を広げる段階です。"),
    "repair_required": ("要注意", "現在は弱点修復を優先する段階です。"),
    "retention_confirmation_needed": ("確認中", "修復した内容が時間をおいても保てるか確認中です。"),
    "safety_attention_required": ("要注意", "重要項目の見直しを優先する必要があります。"),
    "approaching_readiness": ("順調", "幅広い学習証拠がそろいつつあります。"),
    "readiness_supported": ("順調", "幅広い準備と定着の証拠がそろっています。"),
}


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
        return {"status": "要注意", "reason": "直近7日で問題学習の記録がありません。"}
    if days >= 3 or answers >= 30:
        return {
            "status": "継続中",
            "reason": f"直近7日で{days}日・{answers}問の学習記録があります。",
        }
    return {
        "status": "ペース確認",
        "reason": f"直近7日は{days}日・{answers}問です。無理なく続けられるペースか見守ります。",
    }


def _parent_summary(summary: dict, activity: dict, fields: list[dict], latest: dict, attempts: list[dict]) -> dict:
    with measure("parent_summary.evidence"):
        evidence = build_field_evidence(attempts)
        progress = build_field_progress(evidence)
    with measure("parent_summary.readiness"):
        readiness = build_pass_readiness(attempts, field_evidence=evidence, progress=progress)
    readiness_status = readiness["status"]
    coverage = float(readiness["components"]["coverage"].get("node_coverage") or 0.0)
    trajectory_status, trajectory_reason = _TRAJECTORY.get(
        readiness_status,
        ("判定保留", "判断材料を確認しています。"),
    )
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
        "current_position": {
            "status": readiness_status,
            "text": _POSITION_TEXT.get(readiness_status, "現在地を確認しています。"),
            "confirmed_scope_percent": int(round(coverage * 100)),
        },
        "trajectory": {
            "status": trajectory_status,
            "reason": trajectory_reason,
            "pass_probability": None,
            "pass_guarantee": False,
        },
    }


def _shared_dashboard_learning_data(learner_user_id: str, conn) -> dict:
    """Build the existing dashboard aggregate on a caller-owned DB connection."""
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


def build_supporter_report(learner_user_id: str) -> dict:
    """Return parent-facing data only; never consultation text or dev diagnostics."""
    with measure("build_supporter_report.total"):
        if database_is_available():
            with get_db_connection() as conn:
                with measure("db.dashboard_learning_data"):
                    learning_data = _shared_dashboard_learning_data(learner_user_id, conn)
                summary = learning_data["summary"]
                activity = learning_data["activity"]
                all_fields = learning_data["fields"]
                learned_fields = [item for item in all_fields if item["learned"]]
                with measure("python.learning_guidance"):
                    guidance = build_learning_guidance(summary["total_answers"], all_fields)
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
            with measure("python.learning_guidance"):
                guidance = build_learning_guidance(summary["total_answers"], all_fields)
            with measure("db.latest_learning_day_summary"):
                latest = _format_latest(get_latest_learning_day_summary(learner_user_id))
            with measure("db.latest_activity_day_summary"):
                latest_activity = _format_latest_activity(
                    get_latest_activity_day_summary(learner_user_id)
                )
        with measure("db.question_attempts"):
            attempts = get_question_attempts(learner_user_id)
        with measure("python.parent_summary"):
            parent_summary = _parent_summary(summary, activity, learned_fields, latest, attempts)

        return {
            # vNext stable contract
            "parent_summary": parent_summary,
            # temporary compatibility contract for the current supporter template/tests
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