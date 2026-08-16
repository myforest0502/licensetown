"""見守り画面に必要な学習データだけを組み立てる。"""

from __future__ import annotations

from database import get_field_learning_summary, get_learning_activity, get_learning_summary
from learning_analysis import build_learning_guidance


def _supporter_comment(today_answers: int, streak_days: int) -> str:
    if today_answers >= 30:
        return "今日はしっかり取り組めています。結果より、続けていることを褒めてあげてください＾＾"
    if today_answers > 0:
        if streak_days >= 2:
            return "継続できています。今日は口を出さず、見守るだけでも良さそうです。"
        return "今日は少し取り組めています。無理に追い込まず、このまま続けてもらいましょう。"
    return "今日はまだ学習がありません。少しだけ声を掛けてもいいかもしれません。でも怒っちゃダメですよｗ"


def build_supporter_report(learner_user_id: str) -> dict:
    """相談データを参照せず、学習履歴だけからレポートを作る。"""
    summary = get_learning_summary(learner_user_id)
    activity = get_learning_activity(learner_user_id)
    fields = get_field_learning_summary(learner_user_id)
    guidance = build_learning_guidance(summary["total_answers"], fields)
    today = activity["daily"][-1]
    today_fields = [
        {
            "name": item["name"],
            "answered_count": item["today_answered_count"],
            "accuracy": item["today_accuracy"],
        }
        for item in fields if item["today_answered_count"]
    ]
    learned_fields = [item for item in fields if item["learned"]]
    return {
        "today": today,
        "today_studied": today["answered_count"] > 0,
        "today_fields": today_fields,
        "weekly_learning_days": activity["weekly_learning_days"],
        "weekly_answers": activity["weekly_answers"],
        "weekly_study_minutes": activity["weekly_study_minutes"],
        "weekly_accuracy": activity["weekly_accuracy"],
        "streak_days": activity["streak_days"],
        "fields": learned_fields,
        "weak_fields": guidance["weak_fields"],
        "weak_analysis_message": guidance["weak_analysis_message"],
        "recommended_study": guidance["recommended_study"],
        "comment": _supporter_comment(today["answered_count"], activity["streak_days"]),
    }
