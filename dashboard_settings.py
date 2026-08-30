"""Dashboard settings with safe defaults and explicit Japan-time boundaries."""

from datetime import date, datetime
import os
from zoneinfo import ZoneInfo


TOKYO = ZoneInfo("Asia/Tokyo")
SYSTEM_DEFAULT_EXAM_DATE = date(2027, 2, 20)
SYSTEM_DEFAULT_DAILY_QUESTION_GOAL = 30
REWARD_INTERVAL = 100


def tokyo_today(now=None):
    current = now or datetime.now(TOKYO)
    if current.tzinfo is None:
        current = current.replace(tzinfo=TOKYO)
    return current.astimezone(TOKYO).date()


def get_effective_exam_date(user_id=None):
    """Return configured exam date; an explicit blank/invalid value means unset."""
    del user_id
    if "DEFAULT_EXAM_DATE" not in os.environ:
        return SYSTEM_DEFAULT_EXAM_DATE
    raw = os.getenv("DEFAULT_EXAM_DATE", "").strip()
    if not raw:
        return None
    try:
        return date.fromisoformat(raw)
    except ValueError:
        return None


def get_daily_question_goal(user_id=None):
    """Return the motivational daily goal, independent of Adaptive 30 selection."""
    del user_id
    raw = os.getenv("DEFAULT_DAILY_QUESTION_GOAL", str(SYSTEM_DEFAULT_DAILY_QUESTION_GOAL))
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return SYSTEM_DEFAULT_DAILY_QUESTION_GOAL
    return value if value > 0 else SYSTEM_DEFAULT_DAILY_QUESTION_GOAL


def get_reward_progress(total_answers):
    answered = max(int(total_answers or 0), 0)
    progress = answered % REWARD_INTERVAL
    return {
        "reward_interval": REWARD_INTERVAL,
        "next_reward_answers": REWARD_INTERVAL - progress if progress else REWARD_INTERVAL,
        "reward_progress": progress,
    }
