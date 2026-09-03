"""Build the small, parent-facing supporter data contract.

Pace comes from recent activity only. Ability/current position comes from the
formal question-attempt evidence path. Developer diagnostics never enter this
contract.
"""

from __future__ import annotations

from datetime import timezone
from zoneinfo import ZoneInfo

from database import (
    get_dashboard_learning_data,
    get_latest_learning_day_summary,
    get_question_attempts,
)
from field_evidence import build_field_evidence
from field_progress import build_field_progress
from pass_readiness import build_pass_readiness


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


def _pace(activity: dict) -> dict:
    days = int(activity.get("weekly_learning_days") or 0)
    answers = int(activity.get("weekly_answers") or 0)
    if answers == 0:
        return {
            "status": "要注意",
            "reason": "直近7日で問題学習の記録がありません。",
        }
    if days >= 3 or answers >= 30:
        return {
            "status": "継続中",
            "reason": f"直近7日で{days}日・{answers}問の学習記録があります。",
        }
    return {
        "status": "ペース確認",
        "reason": f"直近7日は{days}日・{answers}問です。無理なく続けられるペースか見守ります。",
    }


def build_supporter_report(learner_user_id: str) -> dict:
    """Return only facts needed by the normal parent/supporter screen."""
    learning_data = get_dashboard_learning_data(learner_user_id)
    summary = learning_data["summary"]
    activity = learning_data["activity"]
    fields = [item for item in learning_data["fields"] if item["learned"]]
    latest = _format_latest(get_latest_learning_day_summary(learner_user_id))

    attempts = get_question_attempts(learner_user_id)
    evidence = build_field_evidence(attempts)
    progress = build_field_progress(evidence)
    readiness = build_pass_readiness(
        attempts,
        field_evidence=evidence,
        progress=progress,
    )
    readiness_status = readiness["status"]
    coverage = float(
        readiness["components"]["coverage"].get("node_coverage") or 0.0
    )
    trajectory_status, trajectory_reason = _TRAJECTORY[readiness_status]

    cumulative_fields = [
        {
            "name": item["name"],
            "answered_count": int(item.get("answered_count") or 0),
        }
        for item in fields
    ]
    latest_fields = [
        {
            "name": item["name"],
            "answered_count": int(item.get("answered_count") or 0),
        }
        for item in latest.get("fields", [])
    ]

    return {
        "latest_day": {
            "has_learning": bool(latest.get("has_learning")),
            "date_label": latest.get("date_label", ""),
            "answered_at_label": latest.get("answered_at_label", ""),
            "answered_count": int(latest.get("answered_count") or 0),
            "study_minutes": int(latest.get("study_minutes") or 0),
            "fields": latest_fields,
        },
        "cumulative": {
            "answered_count": int(summary.get("total_answers") or 0),
            "study_minutes": int(summary.get("study_minutes") or 0),
            "fields": cumulative_fields,
        },
        "recent_7d": {
            "learning_days": int(activity.get("weekly_learning_days") or 0),
            "answered_count": int(activity.get("weekly_answers") or 0),
            "study_minutes": int(activity.get("weekly_study_minutes") or 0),
        },
        "pace": _pace(activity),
        "current_position": {
            "status": readiness_status,
            "text": _POSITION_TEXT[readiness_status],
            "confirmed_scope_percent": int(round(coverage * 100)),
        },
        "trajectory": {
            "status": trajectory_status,
            "reason": trajectory_reason,
            "pass_probability": None,
            "pass_guarantee": False,
        },
    }
