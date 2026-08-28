import logging
import math
import os
import json
import copy
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from typing import Any
from zoneinfo import ZoneInfo

import psycopg
from question_bank import CATEGORY_NAMES, QuestionBankError, get_category_small


DATABASE_URL = os.getenv("DATABASE_URL")

_known_user_ids: set[str] = set()
_local_learning_events: dict[str, dict[str, Any]] = {}
_local_question_attempts: list[dict[str, Any]] = []
_local_user_node_states: dict[tuple[str, str], dict[str, Any]] = {}
_local_learning_seconds: dict[str, float] = {}
_local_learning_time_events: list[dict[str, Any]] = []
_local_supporter_links: dict[tuple[str, str], bool] = {}
_local_initial_assessment_completed: set[str] = set()

logger = logging.getLogger(__name__)

STANDARD_STUDY_MINUTES = 500 * 60
STANDARD_TOTAL_ANSWERS = 3000
STANDARD_UNIQUE_QUESTIONS = 1000
NODE_LEARNING_SCHEMA_VERSION = "2026_08_node_learning_state_v1"


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


@contextmanager
def _connection_or_existing(connection=None):
    """同一処理内で渡されたDB接続を再利用し、単独呼び出しでは従来どおり接続する。"""
    if connection is not None:
        yield connection
        return
    with get_db_connection() as created_connection:
        yield created_connection


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
                    initial_assessment_completed BOOLEAN NOT NULL DEFAULT FALSE,
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )
            cur.execute(
                """
                ALTER TABLE user_profiles
                ADD COLUMN IF NOT EXISTS initial_assessment_completed BOOLEAN NOT NULL DEFAULT FALSE
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
                    answered_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    question_results JSONB
                )
                """
            )
            cur.execute(
                """
                ALTER TABLE learning_events
                ADD COLUMN IF NOT EXISTS question_results JSONB
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
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS learning_time_events (
                    id BIGSERIAL PRIMARY KEY,
                    event_key TEXT,
                    user_id TEXT NOT NULL,
                    elapsed_seconds DOUBLE PRECISION NOT NULL,
                    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )
            cur.execute(
                """
                ALTER TABLE learning_time_events
                ADD COLUMN IF NOT EXISTS event_key TEXT
                """
            )
            cur.execute(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS learning_time_events_event_key_idx
                ON learning_time_events (event_key) WHERE event_key IS NOT NULL
                """
            )
            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS learning_time_events_user_date_idx
                ON learning_time_events (user_id, recorded_at)
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS supporter_links (
                    id BIGSERIAL PRIMARY KEY,
                    supporter_user_id TEXT NOT NULL,
                    learner_user_id TEXT NOT NULL,
                    is_active BOOLEAN NOT NULL DEFAULT TRUE,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    UNIQUE (supporter_user_id, learner_user_id),
                    CHECK (supporter_user_id <> learner_user_id)
                )
                """
            )
            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS supporter_links_supporter_active_idx
                ON supporter_links (supporter_user_id, is_active)
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version TEXT PRIMARY KEY,
                    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS question_attempts (
                    id BIGSERIAL PRIMARY KEY,
                    event_key TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    question_id TEXT NOT NULL,
                    knowledge_node_id TEXT NOT NULL,
                    mode TEXT NOT NULL,
                    selected_answers JSONB NOT NULL,
                    is_correct BOOLEAN NOT NULL,
                    confidence SMALLINT,
                    answered_at TIMESTAMPTZ NOT NULL,
                    attempt_position SMALLINT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    UNIQUE (event_key, attempt_position),
                    CHECK (question_id ~ '^Q[1-9][0-9]{0,3}$'),
                    CHECK (knowledge_node_id ~ '^KN[0-9]{4}$'),
                    CHECK (confidence IS NULL OR confidence BETWEEN 1 AND 3),
                    CHECK (attempt_position >= 1)
                )
                """
            )
            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS question_attempts_user_date_idx
                ON question_attempts (user_id, answered_at DESC)
                """
            )
            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS question_attempts_user_question_date_idx
                ON question_attempts (user_id, question_id, answered_at DESC)
                """
            )
            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS question_attempts_user_node_date_idx
                ON question_attempts (user_id, knowledge_node_id, answered_at DESC)
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS user_node_state (
                    user_id TEXT NOT NULL,
                    knowledge_node_id TEXT NOT NULL,
                    state TEXT NOT NULL DEFAULT 'unseen',
                    attempt_count INTEGER NOT NULL DEFAULT 0,
                    correct_count INTEGER NOT NULL DEFAULT 0,
                    incorrect_count INTEGER NOT NULL DEFAULT 0,
                    confident_wrong_count INTEGER NOT NULL DEFAULT 0,
                    consecutive_correct INTEGER NOT NULL DEFAULT 0,
                    repair_confirmation_count INTEGER NOT NULL DEFAULT 0,
                    first_seen_at TIMESTAMPTZ,
                    last_seen_at TIMESTAMPTZ,
                    last_correct_at TIMESTAMPTZ,
                    last_incorrect_at TIMESTAMPTZ,
                    last_question_id TEXT,
                    next_review_at TIMESTAMPTZ,
                    last_error_type TEXT,
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    PRIMARY KEY (user_id, knowledge_node_id),
                    CHECK (knowledge_node_id ~ '^KN[0-9]{4}$'),
                    CHECK (state IN (
                        'unseen', 'checking', 'repairing', 'repaired',
                        'stable', 'recheck_due'
                    )),
                    CHECK (attempt_count >= 0),
                    CHECK (correct_count >= 0),
                    CHECK (incorrect_count >= 0),
                    CHECK (confident_wrong_count >= 0),
                    CHECK (consecutive_correct >= 0),
                    CHECK (repair_confirmation_count >= 0),
                    CHECK (
                        last_question_id IS NULL OR
                        last_question_id ~ '^Q[1-9][0-9]{0,3}$'
                    ),
                    CHECK (
                        last_error_type IS NULL OR
                        last_error_type IN (
                            'knowledge_gap',
                            'misconception',
                            'calculation_method',
                            'reading_overthinking',
                            'uncertain_recall',
                            'application_failure'
                        )
                    )
                )
                """
            )
            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS user_node_state_user_state_idx
                ON user_node_state (user_id, state)
                """
            )
            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS user_node_state_user_review_idx
                ON user_node_state (user_id, next_review_at)
                """
            )
            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS user_node_state_user_last_seen_idx
                ON user_node_state (user_id, last_seen_at DESC)
                """
            )
            cur.execute(
                """
                INSERT INTO schema_migrations (version)
                VALUES (%s)
                ON CONFLICT (version) DO NOTHING
                """,
                (NODE_LEARNING_SCHEMA_VERSION,),
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


def is_initial_assessment_completed(user_id: str) -> bool:
    """明示済み、または既存学習履歴がある利用者を現在地チェック済みとする。"""
    if not database_is_available():
        if user_id in _local_initial_assessment_completed:
            return True
        return any(
            event["user_id"] == user_id and int(event.get("answered_count", 0)) > 0
            for event in _local_learning_events.values()
        )
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    COALESCE(initial_assessment_completed, FALSE)
                    OR EXISTS (
                        SELECT 1 FROM learning_events
                        WHERE learning_events.user_id = user_profiles.user_id
                          AND answered_count > 0
                    )
                FROM user_profiles WHERE user_id = %s
                """,
                (user_id,),
            )
            row = cur.fetchone()
            if row:
                return bool(row[0])
            cur.execute(
                "SELECT 1 FROM learning_events WHERE user_id = %s AND answered_count > 0 LIMIT 1",
                (user_id,),
            )
            return cur.fetchone() is not None


def mark_initial_assessment_completed(user_id: str) -> None:
    """現在地チェック完了を後方互換なプロフィール列へ保存する。"""
    _known_user_ids.add(user_id)
    if not database_is_available():
        _local_initial_assessment_completed.add(user_id)
        return
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO user_profiles (user_id, initial_assessment_completed, updated_at)
                VALUES (%s, TRUE, NOW())
                ON CONFLICT (user_id) DO UPDATE SET
                    initial_assessment_completed = TRUE,
                    updated_at = NOW()
                """,
                (user_id,),
            )


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
        _local_learning_time_events[:] = [
            event for event in _local_learning_time_events if event["user_id"] != user_id
        ]
        _local_question_attempts[:] = [
            attempt for attempt in _local_question_attempts
            if attempt["user_id"] != user_id
        ]
        for state_key in [
            key for key in _local_user_node_states if key[0] == user_id
        ]:
            _local_user_node_states.pop(state_key, None)
        globals().get("_local_initial_assessment_completed", set()).discard(user_id)
        _known_user_ids.discard(user_id)
        return

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM question_attempts WHERE user_id = %s", (user_id,))
            cur.execute("DELETE FROM user_node_state WHERE user_id = %s", (user_id,))
            cur.execute("DELETE FROM learning_events WHERE user_id = %s", (user_id,))
            cur.execute("DELETE FROM learning_time_totals WHERE user_id = %s", (user_id,))
            cur.execute("DELETE FROM learning_time_events WHERE user_id = %s", (user_id,))
            cur.execute(
                "DELETE FROM user_profiles WHERE user_id = %s",
                (user_id,),
            )

    _known_user_ids.discard(user_id)


def get_question_history(user_id: str) -> list[dict[str, Any]]:
    """適応出題用に、保存済み問題別結果だけを時系列で返す。"""
    history = []
    for question_results, answered_at in _get_question_result_rows(user_id):
        if isinstance(question_results, str):
            try:
                question_results = json.loads(question_results)
            except json.JSONDecodeError:
                continue
        if not isinstance(question_results, list):
            continue
        for result in question_results:
            if isinstance(result, dict) and result.get("question_id"):
                history.append({**result, "timestamp": answered_at})
    return history


def get_question_attempts(user_id: str) -> list[dict[str, Any]]:
    """保存済みの1問単位回答履歴を内部利用向けに返す。"""
    if not database_is_available():
        return copy.deepcopy([
            attempt for attempt in _local_question_attempts
            if attempt["user_id"] == user_id
        ])
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT event_key, user_id, question_id, knowledge_node_id,
                       mode, selected_answers, is_correct, confidence,
                       answered_at, attempt_position
                FROM question_attempts
                WHERE user_id = %s
                ORDER BY answered_at, event_key, attempt_position
                """,
                (user_id,),
            )
            columns = (
                "event_key", "user_id", "question_id", "knowledge_node_id",
                "mode", "selected_answers", "is_correct", "confidence",
                "answered_at", "attempt_position",
            )
            return [dict(zip(columns, row)) for row in cur.fetchall()]


def get_user_node_states(user_id: str) -> list[dict[str, Any]]:
    """Node別の基本集計を内部利用向けに返す。"""
    if not database_is_available():
        return [
            dict(state)
            for (stored_user_id, _node_id), state
            in _local_user_node_states.items()
            if stored_user_id == user_id
        ]
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT user_id, knowledge_node_id, state, attempt_count,
                       correct_count, incorrect_count, confident_wrong_count,
                       consecutive_correct, repair_confirmation_count,
                       first_seen_at, last_seen_at, last_correct_at,
                       last_incorrect_at, last_question_id, next_review_at,
                       last_error_type, updated_at
                FROM user_node_state
                WHERE user_id = %s
                ORDER BY knowledge_node_id
                """,
                (user_id,),
            )
            columns = (
                "user_id", "knowledge_node_id", "state", "attempt_count",
                "correct_count", "incorrect_count", "confident_wrong_count",
                "consecutive_correct", "repair_confirmation_count",
                "first_seen_at", "last_seen_at", "last_correct_at",
                "last_incorrect_at", "last_question_id", "next_review_at",
                "last_error_type", "updated_at",
            )
            return [dict(zip(columns, row)) for row in cur.fetchall()]


def _result_attempts(question_results):
    """Node ID付きの新規回答だけを1問単位保存対象にする。"""
    if not isinstance(question_results, list):
        return []
    if not question_results:
        return []
    has_node_ids = [bool(result.get("knowledge_node_id")) for result in question_results]
    if any(has_node_ids) and not all(has_node_ids):
        raise ValueError("question_results contains a missing knowledge_node_id")
    if not any(has_node_ids):
        return []
    return list(enumerate(question_results, start=1))


def _update_local_node_state(user_id, result, timestamp):
    node_id = result["knowledge_node_id"]
    state_key = (user_id, node_id)
    is_correct = bool(result.get("is_correct"))
    confidence = result.get("confidence")
    state = _local_user_node_states.get(state_key)
    if state is None:
        state = {
            "user_id": user_id,
            "knowledge_node_id": node_id,
            "state": "checking" if is_correct else "repairing",
            "attempt_count": 0,
            "correct_count": 0,
            "incorrect_count": 0,
            "confident_wrong_count": 0,
            "consecutive_correct": 0,
            "repair_confirmation_count": 0,
            "first_seen_at": timestamp,
            "last_seen_at": None,
            "last_correct_at": None,
            "last_incorrect_at": None,
            "last_question_id": None,
            "next_review_at": None,
            "last_error_type": None,
            "updated_at": timestamp,
        }
        _local_user_node_states[state_key] = state
    state["attempt_count"] += 1
    state["last_seen_at"] = timestamp
    state["last_question_id"] = result["question_id"]
    state["updated_at"] = timestamp
    if is_correct:
        state["correct_count"] += 1
        state["consecutive_correct"] += 1
        state["last_correct_at"] = timestamp
    else:
        state["incorrect_count"] += 1
        state["consecutive_correct"] = 0
        state["last_incorrect_at"] = timestamp
        state["state"] = "repairing"
        if confidence == 1:
            state["confident_wrong_count"] += 1


def record_learning_batch(
    user_id: str,
    event_key: str,
    mode: str,
    answered_count: int,
    correct_count: int,
    answered_at: datetime | None = None,
    question_results: list[dict[str, Any]] | None = None,
) -> bool:
    """確定済みの回答バッチを重複なしで保存する。"""
    timestamp = answered_at or datetime.now(timezone.utc)
    attempts = _result_attempts(question_results)
    if not database_is_available():
        if event_key in _local_learning_events:
            return False
        attempts_before = len(_local_question_attempts)
        states_before = copy.deepcopy(_local_user_node_states)
        try:
            _local_learning_events[event_key] = {
                "user_id": user_id,
                "mode": mode,
                "answered_count": answered_count,
                "correct_count": correct_count,
                "answered_at": timestamp,
                "question_results": (
                    json.loads(json.dumps(question_results, ensure_ascii=False))
                    if question_results is not None else None
                ),
            }
            for attempt_position, result in attempts:
                _local_question_attempts.append({
                    "event_key": event_key,
                    "user_id": user_id,
                    "question_id": result["question_id"],
                    "knowledge_node_id": result["knowledge_node_id"],
                    "mode": mode,
                    "selected_answers": copy.deepcopy(
                        result.get("selected_answers", [])
                    ),
                    "is_correct": bool(result.get("is_correct")),
                    "confidence": result.get("confidence"),
                    "answered_at": timestamp,
                    "attempt_position": attempt_position,
                })
                _update_local_node_state(user_id, result, timestamp)
        except Exception:
            _local_learning_events.pop(event_key, None)
            del _local_question_attempts[attempts_before:]
            _local_user_node_states.clear()
            _local_user_node_states.update(states_before)
            raise
        return True

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO learning_events (
                    event_key, user_id, mode, answered_count, correct_count,
                    answered_at, question_results
                ) VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb)
                ON CONFLICT (event_key) DO NOTHING
                """,
                (
                    event_key, user_id, mode, answered_count, correct_count, timestamp,
                    json.dumps(question_results, ensure_ascii=False)
                    if question_results is not None else None,
                ),
            )
            if cur.rowcount != 1:
                return False
            for attempt_position, result in attempts:
                cur.execute(
                    """
                    INSERT INTO question_attempts (
                        event_key, user_id, question_id, knowledge_node_id,
                        mode, selected_answers, is_correct, confidence,
                        answered_at, attempt_position
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s::jsonb, %s, %s, %s, %s
                    )
                    """,
                    (
                        event_key, user_id, result["question_id"],
                        result["knowledge_node_id"], mode,
                        json.dumps(result.get("selected_answers", []), ensure_ascii=False),
                        bool(result.get("is_correct")), result.get("confidence"),
                        timestamp, attempt_position,
                    ),
                )
                is_correct = bool(result.get("is_correct"))
                confident_wrong = int(
                    not is_correct and result.get("confidence") == 1
                )
                cur.execute(
                    """
                    INSERT INTO user_node_state (
                        user_id, knowledge_node_id, state, attempt_count,
                        correct_count, incorrect_count, confident_wrong_count,
                        consecutive_correct, first_seen_at, last_seen_at,
                        last_correct_at, last_incorrect_at, last_question_id,
                        updated_at
                    ) VALUES (
                        %s, %s, %s, 1, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, NOW()
                    )
                    ON CONFLICT (user_id, knowledge_node_id) DO UPDATE SET
                        state = CASE
                            WHEN EXCLUDED.incorrect_count = 1 THEN 'repairing'
                            ELSE user_node_state.state
                        END,
                        attempt_count = user_node_state.attempt_count + 1,
                        correct_count = user_node_state.correct_count + EXCLUDED.correct_count,
                        incorrect_count = user_node_state.incorrect_count + EXCLUDED.incorrect_count,
                        confident_wrong_count = user_node_state.confident_wrong_count + EXCLUDED.confident_wrong_count,
                        consecutive_correct = CASE
                            WHEN EXCLUDED.incorrect_count = 1 THEN 0
                            ELSE user_node_state.consecutive_correct + 1
                        END,
                        last_seen_at = EXCLUDED.last_seen_at,
                        last_correct_at = COALESCE(
                            EXCLUDED.last_correct_at,
                            user_node_state.last_correct_at
                        ),
                        last_incorrect_at = COALESCE(
                            EXCLUDED.last_incorrect_at,
                            user_node_state.last_incorrect_at
                        ),
                        last_question_id = EXCLUDED.last_question_id,
                        updated_at = NOW()
                    """,
                    (
                        user_id, result["knowledge_node_id"],
                        "checking" if is_correct else "repairing",
                        int(is_correct), int(not is_correct), confident_wrong,
                        int(is_correct), timestamp, timestamp,
                        timestamp if is_correct else None,
                        timestamp if not is_correct else None,
                        result["question_id"],
                    ),
                )
            return True


def add_learning_time(
    user_id: str,
    elapsed_seconds: float,
    recorded_at: datetime | None = None,
    event_key: str | None = None,
) -> bool:
    """終了または保存までの学習時間を累積する。"""
    seconds = max(float(elapsed_seconds), 0.0)
    timestamp = recorded_at or datetime.now(timezone.utc)
    interval_key = event_key or f"{user_id}:{timestamp.isoformat()}:{seconds}"
    if not database_is_available():
        if any(
            event.get("event_key") == interval_key
            for event in _local_learning_time_events
        ):
            return False
        _local_learning_seconds[user_id] = _local_learning_seconds.get(user_id, 0.0) + seconds
        _local_learning_time_events.append({
            "event_key": interval_key,
            "user_id": user_id,
            "elapsed_seconds": seconds,
            "recorded_at": timestamp,
        })
        return True
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO learning_time_events (
                    event_key, user_id, elapsed_seconds, recorded_at
                ) VALUES (%s, %s, %s, %s)
                ON CONFLICT (event_key) WHERE event_key IS NOT NULL DO NOTHING
                RETURNING event_key
                """,
                (interval_key, user_id, seconds, timestamp),
            )
            if cur.fetchone() is None:
                return False
            cur.execute(
                """
                INSERT INTO learning_time_totals (user_id, total_seconds)
                VALUES (%s, %s)
                ON CONFLICT (user_id) DO UPDATE SET
                    total_seconds = learning_time_totals.total_seconds + EXCLUDED.total_seconds
                """,
                (user_id, seconds),
            )
            return True


def _summary_values(total_answers, total_correct, recent_answers, recent_correct, today_answers, total_seconds):
    return {
        "total_answers": int(total_answers),
        "correct_answers": int(total_correct),
        "average_accuracy": round((total_correct / total_answers) * 100) if total_answers else 0,
        "last_7_days_accuracy": round((recent_correct / recent_answers) * 100) if recent_answers else 0,
        "today_progress": int(today_answers),
        "study_minutes": int(float(total_seconds) // 60),
    }


def calculate_overall_progress(
    study_minutes,
    total_answers,
    unique_question_count,
) -> int:
    """LT内の学習時間と問題演習量から標準学習量への進捗を返す。"""
    def nonnegative_number(value) -> float:
        try:
            return max(float(value), 0.0)
        except (TypeError, ValueError):
            return 0.0

    time_progress = min(
        nonnegative_number(study_minutes) / STANDARD_STUDY_MINUTES,
        1.0,
    )
    answer_progress = min(
        nonnegative_number(total_answers) / STANDARD_TOTAL_ANSWERS,
        1.0,
    )
    unique_progress = min(
        nonnegative_number(unique_question_count) / STANDARD_UNIQUE_QUESTIONS,
        1.0,
    )
    question_progress = min(answer_progress, unique_progress)
    return min(round(math.sqrt(time_progress * question_progress) * 100), 100)


def _get_question_result_rows(user_id: str, _connection=None):
    if not database_is_available():
        return [
            (event.get("question_results"), event["answered_at"])
            for event in _local_learning_events.values()
            if event["user_id"] == user_id and event.get("question_results") is not None
        ]
    with _connection_or_existing(_connection) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT question_results, answered_at
                FROM learning_events
                WHERE user_id = %s AND question_results IS NOT NULL
                ORDER BY answered_at
                """,
                (user_id,),
            )
            return cur.fetchall()


def get_unique_answered_question_count(
    user_id: str,
    _connection=None,
    _question_result_rows=None,
) -> int:
    """回答確定済みquestion_resultsから、重複を除いた正式Q番号数を返す。"""
    rows = (
        _question_result_rows
        if _question_result_rows is not None
        else _get_question_result_rows(user_id, _connection)
    )

    question_ids = set()
    for question_results, _answered_at in rows:
        if isinstance(question_results, str):
            try:
                question_results = json.loads(question_results)
            except json.JSONDecodeError:
                logger.warning("Invalid question_results JSON for user %s", user_id)
                continue
        if not isinstance(question_results, list):
            continue
        for result in question_results:
            if not isinstance(result, dict):
                continue
            question_id = str(result.get("question_id", "")).upper().strip()
            try:
                get_category_small(question_id)
            except QuestionBankError:
                logger.warning("Question result has an unknown question_id: %r", question_id)
                continue
            question_ids.add(question_id)
    return len(question_ids)


def get_learning_summary(
    user_id: str,
    now: datetime | None = None,
    _connection=None,
) -> dict[str, int]:
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

    with _connection_or_existing(_connection) as conn:
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


def _as_utc(timestamp: datetime) -> datetime:
    if timestamp.tzinfo is None:
        return timestamp.replace(tzinfo=timezone.utc)
    return timestamp.astimezone(timezone.utc)


def calculate_learning_streak(active_dates, today) -> int:
    """日本時間の学習日集合から、現在継続中の連続日数を返す。

    今日が未学習でも昨日が学習日なら、昨日までの記録は継続中とする。
    """
    learned_dates = set(active_dates)
    if today in learned_dates:
        cursor = today
    elif today - timedelta(days=1) in learned_dates:
        cursor = today - timedelta(days=1)
    else:
        return 0

    streak_days = 0
    while cursor in learned_dates:
        streak_days += 1
        cursor -= timedelta(days=1)
    return streak_days


def get_field_learning_summary(
    user_id: str,
    now: datetime | None = None,
    _connection=None,
    _question_result_rows=None,
) -> list[dict[str, Any]]:
    """question_resultsを正式Q番号と18分野に結合し、全期間と直近7日を集計する。"""
    current = _as_utc(now or datetime.now(timezone.utc))
    seven_days_ago = current - timedelta(days=7)
    today = current.astimezone(ZoneInfo("Asia/Tokyo")).date()
    summaries = {
        number: {
            "category_small": number,
            "name": name,
            "answered_count": 0,
            "correct_count": 0,
            "accuracy": None,
            "recent_7d_answered_count": 0,
            "recent_7d_correct_count": 0,
            "recent_7d_accuracy": None,
            "today_answered_count": 0,
            "today_correct_count": 0,
            "today_accuracy": None,
            "learned": False,
        }
        for number, name in CATEGORY_NAMES.items()
    }

    rows = (
        _question_result_rows
        if _question_result_rows is not None
        else _get_question_result_rows(user_id, _connection)
    )

    for question_results, answered_at in rows:
        if isinstance(question_results, str):
            try:
                question_results = json.loads(question_results)
            except json.JSONDecodeError:
                logger.warning("Invalid question_results JSON for user %s", user_id)
                continue
        if not isinstance(question_results, list):
            continue
        is_recent = _as_utc(answered_at) >= seven_days_ago
        is_today = _as_utc(answered_at).astimezone(ZoneInfo("Asia/Tokyo")).date() == today
        for result in question_results:
            if not isinstance(result, dict):
                continue
            try:
                category_small = get_category_small(result.get("question_id"))
            except QuestionBankError:
                logger.warning(
                    "Question result has an unknown question_id: %r",
                    result.get("question_id"),
                )
                continue
            summary = summaries[category_small]
            summary["answered_count"] += 1
            if result.get("is_correct") is True:
                summary["correct_count"] += 1
            if is_recent:
                summary["recent_7d_answered_count"] += 1
                if result.get("is_correct") is True:
                    summary["recent_7d_correct_count"] += 1
            if is_today:
                summary["today_answered_count"] += 1
                if result.get("is_correct") is True:
                    summary["today_correct_count"] += 1

    for summary in summaries.values():
        answered = summary["answered_count"]
        recent_answered = summary["recent_7d_answered_count"]
        summary["learned"] = answered > 0
        summary["accuracy"] = (
            round(summary["correct_count"] / answered * 100) if answered else None
        )
        summary["recent_7d_accuracy"] = (
            round(summary["recent_7d_correct_count"] / recent_answered * 100)
            if recent_answered else None
        )
        today_answered = summary["today_answered_count"]
        summary["today_accuracy"] = (
            round(summary["today_correct_count"] / today_answered * 100)
            if today_answered else None
        )
    return list(summaries.values())


def get_learning_activity(
    user_id: str,
    now: datetime | None = None,
    _connection=None,
) -> dict[str, Any]:
    """直近7日の回答数・学習時間と連続学習日数を実履歴から返す。"""
    current = _as_utc(now or datetime.now(timezone.utc))
    jst = ZoneInfo("Asia/Tokyo")
    today = current.astimezone(jst).date()
    dates = [today - timedelta(days=offset) for offset in range(6, -1, -1)]
    answers_by_date = {day: 0 for day in dates}
    seconds_by_date = {day: 0.0 for day in dates}

    if not database_is_available():
        learning_rows = [
            (event["answered_count"], event["correct_count"], event["answered_at"])
            for event in _local_learning_events.values()
            if event["user_id"] == user_id
        ]
        time_rows = [
            (event["elapsed_seconds"], event["recorded_at"])
            for event in _local_learning_time_events
            if event["user_id"] == user_id
        ]
    else:
        with _connection_or_existing(_connection) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT answered_count, correct_count, answered_at FROM learning_events WHERE user_id = %s",
                    (user_id,),
                )
                learning_rows = cur.fetchall()
                cur.execute(
                    "SELECT elapsed_seconds, recorded_at FROM learning_time_events WHERE user_id = %s",
                    (user_id,),
                )
                time_rows = cur.fetchall()

    active_dates = set()
    correct_by_date = {day: 0 for day in dates}
    for answered_count, correct_count, answered_at in learning_rows:
        day = _as_utc(answered_at).astimezone(jst).date()
        if int(answered_count) > 0:
            active_dates.add(day)
        if day in answers_by_date:
            answers_by_date[day] += int(answered_count)
            correct_by_date[day] += int(correct_count)
    for elapsed_seconds, recorded_at in time_rows:
        day = _as_utc(recorded_at).astimezone(jst).date()
        if day in seconds_by_date:
            seconds_by_date[day] += float(elapsed_seconds)

    streak_days = calculate_learning_streak(active_dates, today)

    daily = [
        {
            "date": day.isoformat(),
            "label": f"{day.month}/{day.day}",
            "answered_count": answers_by_date[day],
            "correct_count": correct_by_date[day],
            "accuracy": (
                round(correct_by_date[day] / answers_by_date[day] * 100)
                if answers_by_date[day] else 0
            ),
            "study_minutes": round(seconds_by_date[day] / 60),
        }
        for day in dates
    ]
    weekly_minutes = round(sum(seconds_by_date.values()) / 60)
    weekly_answers = sum(answers_by_date.values())
    weekly_correct = sum(correct_by_date.values())
    return {
        "daily": daily,
        "streak_days": streak_days,
        "weekly_study_minutes": weekly_minutes,
        "average_daily_study_minutes": round(weekly_minutes / 7),
        "weekly_learning_days": sum(1 for value in answers_by_date.values() if value > 0),
        "weekly_answers": weekly_answers,
        "weekly_correct": weekly_correct,
        "weekly_accuracy": (
            round(weekly_correct / weekly_answers * 100) if weekly_answers else 0
        ),
    }


def get_dashboard_learning_data(user_id: str) -> dict[str, Any]:
    """dashboard用の集計を、1DB接続と1回のquestion_results取得で組み立てる。"""
    if not database_is_available():
        question_rows = _get_question_result_rows(user_id)
        return {
            "summary": get_learning_summary(user_id),
            "activity": get_learning_activity(user_id),
            "fields": get_field_learning_summary(
                user_id, _question_result_rows=question_rows
            ),
            "unique_question_count": get_unique_answered_question_count(
                user_id, _question_result_rows=question_rows
            ),
        }

    with get_db_connection() as conn:
        question_rows = _get_question_result_rows(user_id, conn)
        return {
            "summary": get_learning_summary(user_id, _connection=conn),
            "activity": get_learning_activity(user_id, _connection=conn),
            "fields": get_field_learning_summary(
                user_id,
                _connection=conn,
                _question_result_rows=question_rows,
            ),
            "unique_question_count": get_unique_answered_question_count(
                user_id,
                _connection=conn,
                _question_result_rows=question_rows,
            ),
        }


def set_supporter_link(supporter_user_id: str, learner_user_id: str) -> bool:
    """管理者設定用。同一組み合わせは1行に保ち、再登録時は有効化する。"""
    if not supporter_user_id or not learner_user_id or supporter_user_id == learner_user_id:
        raise ValueError("supporter and learner must be different non-empty users")
    key = (supporter_user_id, learner_user_id)
    if not database_is_available():
        was_active = _local_supporter_links.get(key) is True
        _local_supporter_links[key] = True
        return not was_active
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO supporter_links (
                    supporter_user_id, learner_user_id, is_active
                ) VALUES (%s, %s, TRUE)
                ON CONFLICT (supporter_user_id, learner_user_id)
                DO UPDATE SET is_active = TRUE, updated_at = NOW()
                RETURNING is_active
                """,
                (supporter_user_id, learner_user_id),
            )
            return cur.fetchone() is not None


def deactivate_supporter_link(supporter_user_id: str, learner_user_id: str) -> bool:
    """見守り関係を削除せず無効化する。"""
    key = (supporter_user_id, learner_user_id)
    if not database_is_available():
        if _local_supporter_links.get(key) is not True:
            return False
        _local_supporter_links[key] = False
        return True
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE supporter_links SET is_active = FALSE, updated_at = NOW()
                WHERE supporter_user_id = %s AND learner_user_id = %s AND is_active = TRUE
                """,
                (supporter_user_id, learner_user_id),
            )
            return cur.rowcount == 1


def get_supported_learner_ids(supporter_user_id: str) -> list[str]:
    """有効なリンク先だけを返す。"""
    if not database_is_available():
        return sorted(
            learner_id
            for (supporter_id, learner_id), active in _local_supporter_links.items()
            if supporter_id == supporter_user_id and active
        )
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT learner_user_id FROM supporter_links
                WHERE supporter_user_id = %s AND is_active = TRUE
                ORDER BY created_at, id
                """,
                (supporter_user_id,),
            )
            return [row[0] for row in cur.fetchall()]
