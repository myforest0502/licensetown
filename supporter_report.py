"""見守り画面に必要な学習データだけを組み立てる。"""

from __future__ import annotations

from datetime import timezone
from zoneinfo import ZoneInfo

from database import get_dashboard_learning_data, get_latest_learning_day_summary
from learning_analysis import build_learning_guidance


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


def build_supporter_report(learner_user_id: str) -> dict:
    """相談データを参照せず、学習履歴だけからレポートを作る。"""
    learning_data = get_dashboard_learning_data(learner_user_id)
    summary = learning_data["summary"]
    activity = learning_data["activity"]
    fields = learning_data["fields"]
    guidance = build_learning_guidance(summary["total_answers"], fields)
    latest = get_latest_learning_day_summary(learner_user_id)
    if latest["has_learning"]:
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
    learned_fields = [item for item in fields if item["learned"]]
    return {
        "latest": latest,
        "latest_studied": latest["has_learning"],
        "latest_fields": latest["fields"],
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
