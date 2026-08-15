import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Any
from zoneinfo import ZoneInfo

import psycopg


DATABASE_URL = os.getenv("DATABASE_URL")

_known_user_ids: set[str] = set()
_local_learning_events: dict[str, dict[str, Any]] = {}
_local_learning_seconds: dict[str, float] = {}

logger = logging.getLogger(__name__)


def database_is_available() -> bool:
    """DATABASE_URLが設定されているか確認する。"""
    return bool(DATABASE_URL)


def get_db_connection():
    """Neon PostgreSQLへの接続を作る。"""
    if not DATABASE_URL:
        raise RuntimeError(
            "DATABASE_URLが設定されていません。"
            "RenderのEnvironmentを確認してください。"
        )

    return psycopg.connect(DATABASE_URL)


def init_database() -> None:
    """ユーザー名とモードを保存するテーブルを作る。"""
    if not database_is_available():
        logger.warning(
            "DATABASE_URLがないため、ローカルの一時保存を使用します。"
        )
        return

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id TEXT PRIMARY KEY,
                    name TEXT,
                    mode TEXT,
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS learning_events (
                    event_key TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    mode TEXT NOT NULL,
                    answered_count INTEGER NOT NULL,
                    correct_count INTEGER NOT NULL,
                    answered_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )
            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS learning_events_user_date_idx
                ON learning_events (user_id, answered_at)
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS learning_time_totals (
                    user_id TEXT PRIMARY KEY,
                    total_seconds DOUBLE PRECISION NOT NULL DEFAULT 0
                )
                """
            )

    logger.info("Neonデータベースの準備が完了しました。")


class PersistentUserStore:
    """
    今までの辞書と同じ書き方を保ちながら、
    名前またはモードをNeonへ保存するクラス。
    """

    ALLOWED_COLUMNS = {"name", "mode"}

    def __init__(self, column_name: str):
        if column_name not in self.ALLOWED_COLUMNS:
            raise ValueError(
                f"保存できない項目です: {column_name}"
            )

        self.column_name = column_name
        self._local_store: dict[str, Any] = {}

    def get(self, user_id: str, default: Any = None) -> Any:
        """保存されている値を取得する。"""
        if not database_is_available():
            return self._local_store.get(user_id, default)

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    SELECT {self.column_name}
                    FROM user_profiles
                    WHERE user_id = %s
                    """,
                    (user_id,),
                )
                row = cur.fetchone()

        if row is None or row[0] is None:
            return default

        return row[0]

    def __contains__(self, user_id: str) -> bool:
        """「user_id in 保存箱」を使えるようにする。"""
        return self.get(user_id) is not None

    def __getitem__(self, user_id: str) -> Any:
        """「保存箱[user_id]」で値を取得する。"""
        value = self.get(user_id)

        if value is None:
            raise KeyError(user_id)

        return value

    def __setitem__(self, user_id: str, value: Any) -> None:
        """「保存箱[user_id] = 値」でNeonへ保存する。"""
        _known_user_ids.add(user_id)
        if not database_is_available():
            self._local_store[user_id] = value
            return

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    INSERT INTO user_profiles (
                        user_id,
                        {self.column_name},
                        updated_at
                    )
                    VALUES (%s, %s, NOW())
                    ON CONFLICT (user_id)
                    DO UPDATE SET
                        {self.column_name}
                            = EXCLUDED.{self.column_name},
                        updated_at = NOW()
                    """,
                    (user_id, value),
                )

    def pop(self, user_id: str, default: Any = None) -> Any:
        """保存値を削除し、削除前の値を返す。"""
        old_value = self.get(user_id, default)

        if not database_is_available():
            return self._local_store.pop(user_id, default)

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    UPDATE user_profiles
                    SET
                        {self.column_name} = NULL,
                        updated_at = NOW()
                    WHERE user_id = %s
                    """,
                    (user_id,),
                )

        return old_value


init_database()

user_names = PersistentUserStore("name")
user_modes = PersistentUserStore("mode")


def user_profile_exists(user_id: str) -> bool:
    """名前が未登録でも、過去に作られた利用者行があるか確認する。"""
    if not database_is_available():
        return user_id in _known_user_ids

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM user_profiles WHERE user_id = %s",
                (user_id,),
            )
            return cur.fetchone() is not None


def reset_user_profile(user_id: str) -> None:
    """指定ユーザーのプロフィール行を削除し、完全な初回状態へ戻す。"""
    if not database_is_available():
        user_names._local_store.pop(user_id, None)
        user_modes._local_store.pop(user_id, None)
        for event_key in [
            key for key, event in _local_learning_events.items()
            if event["user_id"] == user_id
        ]:
            _local_learning_events.pop(event_key, None)
        _local_learning_seconds.pop(user_id, None)
        _known_user_ids.discard(user_id)
        return

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM learning_events WHERE user_id = %s", (user_id,))
            cur.execute("DELETE FROM learning_time_totals WHERE user_id = %s", (user_id,))
            cur.execute(
                "DELETE FROM user_profiles WHERE user_id = %s",
                (user_id,),
            )

    _known_user_ids.discard(user_id)


def record_learning_batch(
    user_id: str,
    event_key: str,
    mode: str,
    answered_count: int,
    correct_count: int,
    answered_at: datetime | None = None,
) -> bool:
    """確定済みの回答バッチを重複なしで保存する。"""
    timestamp = answered_at or datetime.now(timezone.utc)
    if not database_is_available():
        if event_key in _local_learning_events:
            return False
        _local_learning_events[event_key] = {
            "user_id": user_id,
            "mode": mode,
            "answered_count": answered_count,
            "correct_count": correct_count,
            "answered_at": timestamp,
        }
        return True

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO learning_events (
                    event_key, user_id, mode, answered_count, correct_count, answered_at
                ) VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (event_key) DO NOTHING
                """,
                (event_key, user_id, mode, answered_count, correct_count, timestamp),
            )
            return cur.rowcount == 1


def add_learning_time(user_id: str, elapsed_seconds: float) -> None:
    """終了または保存までの学習時間を累積する。"""
    seconds = max(float(elapsed_seconds), 0.0)
    if not database_is_available():
        _local_learning_seconds[user_id] = _local_learning_seconds.get(user_id, 0.0) + seconds
        return
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO learning_time_totals (user_id, total_seconds)
                VALUES (%s, %s)
                ON CONFLICT (user_id) DO UPDATE SET
                    total_seconds = learning_time_totals.total_seconds + EXCLUDED.total_seconds
                """,
                (user_id, seconds),
            )


def _summary_values(total_answers, total_correct, recent_answers, recent_correct, today_answers, total_seconds):
    return {
        "total_answers": int(total_answers),
        "correct_answers": int(total_correct),
        "average_accuracy": round((total_correct / total_answers) * 100) if total_answers else 0,
        "last_7_days_accuracy": round((recent_correct / recent_answers) * 100) if recent_answers else 0,
        "today_progress": int(today_answers),
        "study_minutes": int(float(total_seconds) // 60),
    }


def get_learning_summary(user_id: str, now: datetime | None = None) -> dict[str, int]:
    """合格への道の基本成績を学習履歴から集計する。"""
    current = now or datetime.now(timezone.utc)
    today = current.astimezone(ZoneInfo("Asia/Tokyo")).date()
    seven_days_ago = current - timedelta(days=7)
    if not database_is_available():
        events = [event for event in _local_learning_events.values() if event["user_id"] == user_id]
        recent = [event for event in events if event["answered_at"] >= seven_days_ago]
        today_events = [
            event for event in events
            if event["answered_at"].astimezone(ZoneInfo("Asia/Tokyo")).date() == today
        ]
        return _summary_values(
            sum(event["answered_count"] for event in events),
            sum(event["correct_count"] for event in events),
            sum(event["answered_count"] for event in recent),
            sum(event["correct_count"] for event in recent),
            sum(event["answered_count"] for event in today_events),
            _local_learning_seconds.get(user_id, 0.0),
        )

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    COALESCE(SUM(answered_count), 0),
                    COALESCE(SUM(correct_count), 0),
                    COALESCE(SUM(answered_count) FILTER (WHERE answered_at >= %s), 0),
                    COALESCE(SUM(correct_count) FILTER (WHERE answered_at >= %s), 0),
                    COALESCE(SUM(answered_count) FILTER (
                        WHERE (answered_at AT TIME ZONE 'Asia/Tokyo')::date = %s
                    ), 0)
                FROM learning_events WHERE user_id = %s
                """,
                (seven_days_ago, seven_days_ago, today, user_id),
            )
            values = cur.fetchone()
            cur.execute(
                "SELECT COALESCE(total_seconds, 0) FROM learning_time_totals WHERE user_id = %s",
                (user_id,),
            )
            row = cur.fetchone()
    return _summary_values(*values, row[0] if row else 0)
