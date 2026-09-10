"""Durable storage for active/completed Web recommendation study sessions.

The learner-facing Web recommendation flow historically kept every session in
process memory. A normal Render restart therefore turned an in-progress
learning URL into a 404 even though the learner's already-confirmed attempts
were safely stored. This production composition layer persists the small Web
session snapshot and restores it lazily after a process restart.
"""

from __future__ import annotations

import copy
import json
import logging
import threading
from functools import wraps
from typing import Any


logger = logging.getLogger(__name__)
_TABLE = "web_learning_sessions"
_RETENTION_DAYS = 7
_local_snapshots: dict[str, dict[str, Any]] = {}
_local_lock = threading.RLock()


def _snapshot(session: dict[str, Any]) -> dict[str, Any]:
    return json.loads(json.dumps(session, ensure_ascii=False))


def _restore(payload: Any) -> dict[str, Any] | None:
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except json.JSONDecodeError:
            return None
    if not isinstance(payload, dict):
        return None
    required = {"user_id", "dashboard_token", "question_count", "questions", "current_index"}
    if not required.issubset(payload):
        return None
    return copy.deepcopy(payload)


class WebLearningSessionStore:
    def __init__(self, database_module):
        self.database = database_module

    def save(self, session_id: str, session: dict[str, Any]) -> bool:
        payload = _snapshot(session)
        if not self.database.database_is_available():
            with _local_lock:
                _local_snapshots[session_id] = payload
            return True
        try:
            with self.database.get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        f"DELETE FROM {_TABLE} WHERE updated_at < NOW() - INTERVAL '{_RETENTION_DAYS} days'"
                    )
                    cur.execute(
                        f"""
                        INSERT INTO {_TABLE} (session_id, user_id, session_payload, updated_at)
                        VALUES (%s, %s, %s::jsonb, NOW())
                        ON CONFLICT (session_id) DO UPDATE
                        SET user_id = EXCLUDED.user_id,
                            session_payload = EXCLUDED.session_payload,
                            updated_at = EXCLUDED.updated_at
                        """,
                        (session_id, str(session.get("user_id", "")), json.dumps(payload, ensure_ascii=False)),
                    )
            return True
        except Exception:
            logger.exception("web_learning_session save_failed session_id=%s", session_id)
            return False

    def load(self, session_id: str) -> dict[str, Any] | None:
        if not self.database.database_is_available():
            with _local_lock:
                return _restore(_local_snapshots.get(session_id))
        try:
            with self.database.get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        f"""
                        SELECT session_payload FROM {_TABLE}
                        WHERE session_id = %s
                          AND updated_at >= NOW() - INTERVAL '{_RETENTION_DAYS} days'
                        """,
                        (session_id,),
                    )
                    row = cur.fetchone()
            return _restore(row[0]) if row else None
        except Exception:
            logger.exception("web_learning_session load_failed session_id=%s", session_id)
            return None

    def load_all_recent(self) -> dict[str, dict[str, Any]]:
        if not self.database.database_is_available():
            with _local_lock:
                return {
                    session_id: restored
                    for session_id, payload in _local_snapshots.items()
                    if (restored := _restore(payload)) is not None
                }
        try:
            with self.database.get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        f"""
                        SELECT session_id, session_payload FROM {_TABLE}
                        WHERE updated_at >= NOW() - INTERVAL '{_RETENTION_DAYS} days'
                        ORDER BY updated_at
                        """
                    )
                    rows = cur.fetchall()
            restored = {}
            for session_id, payload in rows:
                session = _restore(payload)
                if session is not None:
                    restored[str(session_id)] = session
            return restored
        except Exception:
            logger.exception("web_learning_session load_all_failed")
            return {}

    def delete(self, session_id: str) -> bool:
        if not self.database.database_is_available():
            with _local_lock:
                _local_snapshots.pop(session_id, None)
            return True
        try:
            with self.database.get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(f"DELETE FROM {_TABLE} WHERE session_id = %s", (session_id,))
            return True
        except Exception:
            logger.exception("web_learning_session delete_failed session_id=%s", session_id)
            return False


class DurableWebLearningSessions(dict):
    def __init__(self, initial: dict[str, Any], store: WebLearningSessionStore):
        super().__init__()
        self.store = store
        self._lock = threading.RLock()
        for session_id, session in store.load_all_recent().items():
            dict.__setitem__(self, session_id, session)
        for session_id, session in initial.items():
            dict.__setitem__(self, session_id, session)

    def _restore_if_needed(self, session_id: str) -> None:
        with self._lock:
            if dict.__contains__(self, session_id):
                return
            session = self.store.load(session_id)
            if session is not None:
                dict.__setitem__(self, session_id, session)
                logger.info("web_learning_session restored session_id=%s", session_id)

    def get(self, session_id, default=None):
        self._restore_if_needed(session_id)
        return dict.get(self, session_id, default)

    def __getitem__(self, session_id):
        self._restore_if_needed(session_id)
        return dict.__getitem__(self, session_id)

    def __contains__(self, session_id):
        self._restore_if_needed(session_id)
        return dict.__contains__(self, session_id)

    def __setitem__(self, session_id, session):
        dict.__setitem__(self, session_id, session)
        if not self.store.save(str(session_id), session):
            logger.error("web_learning_session initial_persistence_not_confirmed session_id=%s", session_id)

    def persist(self, session_id: str) -> bool:
        session = dict.get(self, session_id)
        if session is None:
            return False
        return self.store.save(session_id, session)

    def pop(self, session_id, *args):
        self.store.delete(str(session_id))
        return dict.pop(self, session_id, *args)


def install_durable_web_learning_sessions(legacy_module, database_module) -> None:
    """Compose restart-safe Web recommendation sessions onto the Flask app."""
    if getattr(legacy_module, "_durable_web_learning_sessions_installed", False):
        return

    store = WebLearningSessionStore(database_module)
    existing = getattr(legacy_module, "web_recommendation_sessions", {})
    if not isinstance(existing, dict):
        raise TypeError("legacy web_recommendation_sessions must be a dict")
    durable = DurableWebLearningSessions(existing, store)
    legacy_module.web_recommendation_sessions = durable

    endpoint = "answer_web_recommendation"
    original_answer = legacy_module.app.view_functions.get(endpoint)
    if original_answer is None:
        raise RuntimeError("answer_web_recommendation endpoint not found")

    @wraps(original_answer)
    def durable_answer(session_id, *args, **kwargs):
        response = original_answer(session_id, *args, **kwargs)
        session = durable.get(session_id)
        if session is not None and not durable.persist(session_id):
            logger.error("web_learning_session answer_persistence_not_confirmed session_id=%s", session_id)
        return response

    legacy_module.answer_web_recommendation = durable_answer
    legacy_module.app.view_functions[endpoint] = durable_answer
    legacy_module._durable_web_learning_session_store = store
    legacy_module._durable_web_learning_sessions_installed = True
