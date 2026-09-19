"""Reuse adaptive-session attempt history for prerequisite backtrack checks.

The prerequisite pilot originally re-read all question attempts from Neon after
persisting every 5-answer batch. Adaptive daily selection already reads that
history when the session starts. This module captures that already-authoritative
snapshot, appends only successfully persisted batches in session order, and
lets the prerequisite pilot reuse it.

If a safe cache is not available, behavior falls back to the legacy DB read.
The selector, prerequisite diagnosis, Safety, repair, and cooldown rules are
not changed here.
"""

from __future__ import annotations

from datetime import datetime, timezone
from threading import Lock
from typing import Any


_SESSION_CACHE_KEY = "_prerequisite_attempt_cache"
_PENDING: dict[str, list[dict[str, Any]]] = {}
_PENDING_LOCK = Lock()


def _copy_attempts(attempts) -> list[dict[str, Any]]:
    return [dict(item) for item in attempts]


def _pilot_enabled(legacy, user_id: str, session: dict | None = None) -> bool:
    if not legacy.is_prerequisite_backtrack_pilot_enabled(
        legacy.ENABLE_PREREQUISITE_BACKTRACK,
        user_id,
        legacy.PREREQUISITE_BACKTRACK_PILOT_USER_IDS,
    ):
        return False
    if session is None:
        return True
    return (
        session.get("mode", "study") == "study"
        and session.get("session_kind") != "initial_assessment"
    )


def _selector_user_id(attempts: list[dict[str, Any]]) -> str | None:
    user_ids = {
        str(item.get("user_id"))
        for item in attempts
        if item.get("user_id")
    }
    if len(user_ids) != 1:
        return None
    return next(iter(user_ids))


def _current_batch_attempts(legacy, user_id: str, session: dict) -> list[dict[str, Any]]:
    current_set = int(session["current_set"])
    questions_per_set = int(session["questions_per_set"])
    start_number = ((current_set - 1) * questions_per_set) + 1
    event_key = f'{session["session_id"]}:{current_set}'
    answered_at = datetime.now(timezone.utc)
    attempts: list[dict[str, Any]] = []

    for attempt_position, question in enumerate(session["questions"], start=1):
        answer_data = session["all_answers"][start_number + attempt_position - 1]
        question_id = str(question.get("id"))
        confidence = answer_data.get("confidence")
        attempts.append({
            "event_key": event_key,
            "user_id": user_id,
            "question_id": question_id,
            "knowledge_node_id": legacy.get_question_tag(question_id).get("knowledge_node_id"),
            "is_correct": legacy.is_answer_correct(question, answer_data.get("answer")),
            "confidence": int(confidence) if str(confidence) in {"1", "2", "3"} else None,
            "answer_status": answer_data.get("answer_status", "answered"),
            "answered_at": answered_at,
            "attempt_position": attempt_position,
        })
    return attempts


def _queue_from_cache(legacy, user_id: str, session: dict):
    if (
        not _pilot_enabled(legacy, user_id, session)
        or session.get("current_set", 1) >= session.get("total_sets", 1)
        or session.get("prerequisite_backtrack_set") == session.get("current_set")
        or session.get("pending_prerequisite_backtrack")
    ):
        return None

    attempts = session.get(_SESSION_CACHE_KEY)
    if not isinstance(attempts, list) or not attempts:
        return legacy._lt_original_queue_prerequisite_backtrack_for_next_set(user_id, session)

    event_key = f'{session["session_id"]}:{session["current_set"]}'
    current_attempts = [item for item in attempts if item.get("event_key") == event_key]
    if not current_attempts:
        # Never trade correctness for speed: an incomplete cache uses the old path.
        return legacy._lt_original_queue_prerequisite_backtrack_for_next_set(user_id, session)

    current_end = session["current_set"] * session["questions_per_set"]
    excluded = {
        str(question.get("id"))
        for question in session.get("all_questions", ())[:current_end]
    }
    excluded.update(session.get("prerequisite_backtrack_used_ids", ()))
    candidate = legacy.build_pending_backtrack_candidate(
        current_attempts,
        attempts,
        legacy.get_reviewed_node_relations(),
        excluded_question_ids=excluded,
    )
    if candidate:
        session["pending_prerequisite_backtrack"] = candidate
    return candidate


def install_prerequisite_attempt_cache(legacy) -> None:
    """Patch the legacy module once, preserving DB fallback semantics."""
    if getattr(legacy, "_lt_prerequisite_attempt_cache_installed", False):
        return

    original_build = legacy.build_node_adaptive_session
    original_start = legacy.start_quiz
    original_record = legacy.record_confirmed_learning_batch
    original_queue = legacy.queue_prerequisite_backtrack_for_next_set

    # Kept on the legacy module so the cached queue can explicitly fall back.
    legacy._lt_original_queue_prerequisite_backtrack_for_next_set = original_queue

    def build_node_adaptive_session(attempts, *args, **kwargs):
        attempt_list = _copy_attempts(attempts)
        result = original_build(attempt_list, *args, **kwargs)
        user_id = _selector_user_id(attempt_list)
        if user_id and _pilot_enabled(legacy, user_id):
            with _PENDING_LOCK:
                _PENDING[user_id] = attempt_list
        return result

    def start_quiz(user_id, *args, **kwargs):
        # Prevent a pending snapshot from an unrelated web selector call from
        # being attached if this start does not perform adaptive selection.
        with _PENDING_LOCK:
            _PENDING.pop(user_id, None)
        result = original_start(user_id, *args, **kwargs)
        session = legacy.study_sessions.get(user_id)
        if session and session.get("session_kind") == "adaptive_daily" and _pilot_enabled(
            legacy, user_id, session
        ):
            with _PENDING_LOCK:
                cached = _PENDING.pop(user_id, None)
            if cached is not None:
                session[_SESSION_CACHE_KEY] = cached
        return result

    def record_confirmed_learning_batch(user_id, session):
        inserted = original_record(user_id, session)
        if inserted and _pilot_enabled(legacy, user_id, session):
            cached = session.get(_SESSION_CACHE_KEY)
            if isinstance(cached, list):
                cached.extend(_current_batch_attempts(legacy, user_id, session))
        return inserted

    def queue_prerequisite_backtrack_for_next_set(user_id, session):
        return _queue_from_cache(legacy, user_id, session)

    legacy.build_node_adaptive_session = build_node_adaptive_session
    legacy.start_quiz = start_quiz
    legacy.record_confirmed_learning_batch = record_confirmed_learning_batch
    legacy.queue_prerequisite_backtrack_for_next_set = queue_prerequisite_backtrack_for_next_set
    legacy._lt_prerequisite_attempt_cache_installed = True
