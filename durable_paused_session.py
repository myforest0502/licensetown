"""Durable storage for paused LINE quiz sessions.

The legacy learner flow intentionally keeps active sessions in memory.  A
paused session, however, is a user-visible promise ("源さんに預ける") and must
survive a normal Render process restart.  This production composition layer
persists only paused snapshots; active sessions remain in memory.
"""

from __future__ import annotations

import copy
import json
import logging
import threading
from datetime import datetime
from typing import Any


logger = logging.getLogger(__name__)
_TABLE = "paused_quiz_sessions"
_local_snapshots: dict[str, dict[str, Any]] = {}
_local_lock = threading.RLock()


def _json_default(value: Any):
    if isinstance(value, set):
        return sorted(value)
    if isinstance(value, datetime):
        return value.isoformat()
    raise TypeError(f"Unsupported paused-session value: {type(value).__name__}")


def _serializable_snapshot(session: dict[str, Any]) -> dict[str, Any]:
    """Return a detached JSON-compatible snapshot."""
    return json.loads(json.dumps(session, ensure_ascii=False, default=_json_default))


def _restore_snapshot(payload: Any) -> dict[str, Any] | None:
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except json.JSONDecodeError:
            return None
    if not isinstance(payload, dict) or payload.get("status") != "paused":
        return None
    restored = copy.deepcopy(payload)
    answers = restored.get("all_answers")
    if isinstance(answers, dict):
        converted = {}
        for key, value in answers.items():
            try:
                converted[int(key)] = value
            except (TypeError, ValueError):
                converted[key] = value
        restored["all_answers"] = converted
    return restored


class PausedSessionStore:
    def __init__(self, database_module):
        self.database = database_module

    def save(self, user_id: str, session: dict[str, Any]) -> bool:
        snapshot = _serializable_snapshot(session)
        if not self.database.database_is_available():
            with _local_lock:
                _local_snapshots[user_id] = snapshot
            return True
        try:
            with self.database.get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        f"""
                        INSERT INTO {_TABLE} (user_id, session_payload, paused_at)
                        VALUES (%s, %s::jsonb, NOW())
                        ON CONFLICT (user_id) DO UPDATE
                        SET session_payload = EXCLUDED.session_payload,
                            paused_at = EXCLUDED.paused_at
                        """,
                        (user_id, json.dumps(snapshot, ensure_ascii=False)),
                    )
            return True
        except Exception:
            logger.exception("paused_session_store save_failed user_id=%s", user_id)
            return False

    def load(self, user_id: str) -> dict[str, Any] | None:
        if not self.database.database_is_available():
            with _local_lock:
                return _restore_snapshot(_local_snapshots.get(user_id))
        try:
            with self.database.get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        f"SELECT session_payload FROM {_TABLE} WHERE user_id = %s",
                        (user_id,),
                    )
                    row = cur.fetchone()
            return _restore_snapshot(row[0]) if row else None
        except Exception:
            logger.exception("paused_session_store load_failed user_id=%s", user_id)
            return None

    def delete(self, user_id: str) -> bool:
        if not self.database.database_is_available():
            with _local_lock:
                _local_snapshots.pop(user_id, None)
            return True
        try:
            with self.database.get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(f"DELETE FROM {_TABLE} WHERE user_id = %s", (user_id,))
            return True
        except Exception:
            logger.exception("paused_session_store delete_failed user_id=%s", user_id)
            return False


class DurableStudySessions(dict):
    """Legacy-compatible dict that lazily restores only paused sessions."""

    def __init__(self, initial: dict[str, Any], store: PausedSessionStore):
        super().__init__(initial)
        self.store = store
        self._lock = threading.RLock()

    def _restore_if_needed(self, user_id):
        with self._lock:
            if dict.__contains__(self, user_id):
                return
            snapshot = self.store.load(user_id)
            if snapshot is not None:
                dict.__setitem__(self, user_id, snapshot)
                logger.info("paused_session_store restored user_id=%s", user_id)

    def get(self, user_id, default=None):
        self._restore_if_needed(user_id)
        return dict.get(self, user_id, default)

    def __getitem__(self, user_id):
        self._restore_if_needed(user_id)
        return dict.__getitem__(self, user_id)

    def __contains__(self, user_id):
        self._restore_if_needed(user_id)
        return dict.__contains__(self, user_id)

    def __setitem__(self, user_id, session):
        # Creating/replacing a live session explicitly abandons any old paused
        # snapshot.  Restoration bypasses this method via dict.__setitem__.
        self.store.delete(user_id)
        dict.__setitem__(self, user_id, session)

    def pop(self, user_id, *args):
        self.store.delete(user_id)
        return dict.pop(self, user_id, *args)


def install_durable_paused_sessions(legacy_module, database_module) -> None:
    """Compose durable pause/resume behavior onto the legacy learner flow."""
    if getattr(legacy_module, "_durable_paused_sessions_installed", False):
        return

    store = PausedSessionStore(database_module)
    existing_sessions = getattr(legacy_module, "study_sessions", {})
    if not isinstance(existing_sessions, dict):
        raise TypeError("legacy study_sessions must be a dict")
    durable_sessions = DurableStudySessions(existing_sessions, store)
    legacy_module.study_sessions = durable_sessions

    original_pause = legacy_module.pause_quiz_session
    original_resume = legacy_module.resume_quiz_session

    def durable_pause(user_id):
        paused = original_pause(user_id)
        if not paused:
            return paused
        session = durable_sessions.get(user_id)
        if not session or session.get("status") != "paused":
            return paused
        if not store.save(user_id, session):
            logger.error("paused_session_store persistence_not_confirmed user_id=%s", user_id)
        return paused

    def durable_resume(user_id):
        session = original_resume(user_id)
        if session is not None:
            store.delete(user_id)
        return session

    legacy_module.pause_quiz_session = durable_pause
    legacy_module.resume_quiz_session = durable_resume
    legacy_module._durable_paused_session_store = store
    legacy_module._durable_paused_sessions_installed = True
