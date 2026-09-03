"""Audit legacy learning history before a future Knowledge Node backfill.

This command is intentionally read-only in ⑤-C1.  Running it without
arguments performs a dry-run.  ``--apply`` is reserved but rejected until a
separately reviewed implementation is provided.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Iterable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import database
from question_bank import get_question_tag, question_ids


FORMAL_QUESTION_IDS = frozenset(question_ids())


LEARNING_EVENT_COLUMNS = (
    "event_key", "user_id", "mode", "answered_count", "correct_count",
    "answered_at", "question_results",
)
ATTEMPT_COLUMNS = (
    "event_key", "user_id", "question_id", "knowledge_node_id", "mode",
    "selected_answers", "is_correct", "confidence", "answered_at",
    "attempt_position",
)
STOP_COUNTERS = (
    "missing_question_id",
    "out_of_range_question_id",
    "unresolved_knowledge_node_id",
    "missing_is_correct",
    "invalid_confidence",
    "json_decode_errors",
    "answered_count_mismatches",
    "correct_count_mismatches",
    "existing_conflicts",
)


class BackfillSafetyError(RuntimeError):
    """Raised before commit when an apply safety condition is not satisfied."""


def _new_report() -> dict[str, Any]:
    return {
        "run_mode": "dry-run",
        "total_learning_events": 0,
        "events_with_question_results": 0,
        "events_without_question_results": 0,
        "total_attempt_candidates": 0,
        "missing_question_id": 0,
        "out_of_range_question_id": 0,
        "resolved_knowledge_node_id": 0,
        "unresolved_knowledge_node_id": 0,
        "missing_selected_answers": 0,
        "missing_is_correct": 0,
        "confidence_1": 0,
        "confidence_2": 0,
        "confidence_3": 0,
        "confidence_null": 0,
        "invalid_confidence": 0,
        "existing_matched": 0,
        "new_attempt_candidates": 0,
        "existing_conflicts": 0,
        "inserted": 0,
        "skipped": 0,
        "answered_count_mismatches": 0,
        "correct_count_mismatches": 0,
        "json_decode_errors": 0,
        "affected_users": 0,
        "rebuilt_state_rows": 0,
        "apply_eligible": False,
        "errors": 0,
        "warnings": 0,
    }


def _decode_json(value: Any) -> tuple[Any, bool]:
    if not isinstance(value, str):
        return value, True
    try:
        return json.loads(value), True
    except (TypeError, json.JSONDecodeError):
        return None, False


def _question_number(question_id: Any) -> int | None:
    if not isinstance(question_id, str):
        return None
    match = re.fullmatch(r"Q([1-9][0-9]*)", question_id.strip().upper())
    if not match:
        return None
    number = int(match.group(1))
    return number if f"Q{number}" in FORMAL_QUESTION_IDS else None


def _normalise_json_value(value: Any) -> Any:
    decoded, valid = _decode_json(value)
    return decoded if valid else value


def _normalise_timestamp(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def _attempt_signature(attempt: dict[str, Any]) -> tuple[Any, ...]:
    return (
        attempt.get("event_key"),
        attempt.get("user_id"),
        attempt.get("question_id"),
        attempt.get("knowledge_node_id"),
        attempt.get("mode"),
        _normalise_json_value(attempt.get("selected_answers")),
        attempt.get("is_correct"),
        attempt.get("confidence"),
        _normalise_timestamp(attempt.get("answered_at")),
        attempt.get("attempt_position"),
    )


def _resolve_node_id(
    question_id: str,
    tag_resolver: Callable[[str], dict[str, Any]],
) -> str | None:
    try:
        tag = tag_resolver(question_id)
    except Exception:
        return None
    node_id = tag.get("knowledge_node_id") if isinstance(tag, dict) else None
    return node_id if isinstance(node_id, str) and node_id else None


def audit_learning_history(
    learning_events: Iterable[dict[str, Any]],
    existing_attempts: Iterable[dict[str, Any]],
    tag_resolver: Callable[[str], dict[str, Any]] = get_question_tag,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Return a complete read-only audit and valid future insert candidates."""
    report = _new_report()
    events = list(learning_events)
    existing_by_key = {
        (item.get("event_key"), item.get("attempt_position")): item
        for item in existing_attempts
    }
    candidates: list[dict[str, Any]] = []
    users: set[str] = set()

    report["total_learning_events"] = len(events)
    for event in events:
        raw_results = event.get("question_results")
        if raw_results is None:
            report["events_without_question_results"] += 1
            continue
        report["events_with_question_results"] += 1
        results, valid_json = _decode_json(raw_results)
        if not valid_json or not isinstance(results, list):
            report["json_decode_errors"] += 1
            continue

        report["total_attempt_candidates"] += len(results)
        if event.get("answered_count") != len(results):
            report["answered_count_mismatches"] += 1

        actual_correct = sum(
            item.get("is_correct") is True
            for item in results
            if isinstance(item, dict)
        )
        if event.get("correct_count") != actual_correct:
            report["correct_count_mismatches"] += 1

        user_id = event.get("user_id")
        if isinstance(user_id, str) and user_id:
            users.add(user_id)

        for position, result in enumerate(results, start=1):
            if not isinstance(result, dict):
                report["missing_question_id"] += 1
                report["missing_is_correct"] += 1
                report["confidence_null"] += 1
                report["missing_selected_answers"] += 1
                continue

            question_id = result.get("question_id")
            if not question_id:
                report["missing_question_id"] += 1
                valid_question = False
            else:
                valid_question = _question_number(question_id) is not None
                if not valid_question:
                    report["out_of_range_question_id"] += 1

            if "selected_answers" not in result or result.get("selected_answers") is None:
                report["missing_selected_answers"] += 1
            if "is_correct" not in result or result.get("is_correct") is None:
                report["missing_is_correct"] += 1

            confidence = result.get("confidence")
            if confidence is None:
                report["confidence_null"] += 1
            elif type(confidence) is int and confidence in (1, 2, 3):
                report[f"confidence_{confidence}"] += 1
            else:
                report["invalid_confidence"] += 1

            node_id = None
            if question_id and valid_question:
                canonical_id = f"Q{_question_number(question_id)}"
                node_id = _resolve_node_id(canonical_id, tag_resolver)
                if node_id:
                    report["resolved_knowledge_node_id"] += 1
                else:
                    report["unresolved_knowledge_node_id"] += 1

            can_compare = (
                bool(question_id)
                and valid_question
                and bool(node_id)
                and "is_correct" in result
                and result.get("is_correct") is not None
                and (confidence is None or (type(confidence) is int and confidence in (1, 2, 3)))
            )
            if not can_compare:
                continue

            candidate = {
                "event_key": event.get("event_key"),
                "user_id": user_id,
                "question_id": f"Q{_question_number(question_id)}",
                "knowledge_node_id": node_id,
                "mode": event.get("mode"),
                "selected_answers": result.get("selected_answers"),
                "is_correct": result.get("is_correct"),
                "confidence": confidence,
                "answered_at": event.get("answered_at"),
                "attempt_position": position,
            }
            existing = existing_by_key.get((event.get("event_key"), position))
            if existing is None:
                report["new_attempt_candidates"] += 1
                candidates.append(candidate)
            elif _attempt_signature(existing) == _attempt_signature(candidate):
                report["existing_matched"] += 1
            else:
                report["existing_conflicts"] += 1

    report["affected_users"] = len(users)
    report["skipped"] = report["existing_matched"]
    report["rebuilt_state_rows"] = len(
        rebuild_user_node_states([*existing_by_key.values(), *candidates])
    )
    report["errors"] = sum(report[name] for name in STOP_COUNTERS)
    report["warnings"] = report["missing_selected_answers"]
    report["apply_eligible"] = report["errors"] == 0
    return report, candidates


def _sort_attempt(attempt: dict[str, Any]) -> tuple[str, str, int]:
    timestamp = _normalise_timestamp(attempt.get("answered_at"))
    return (
        "" if timestamp is None else str(timestamp),
        str(attempt.get("event_key") or ""),
        int(attempt.get("attempt_position") or 0),
    )


def rebuild_user_node_states(
    attempts: Iterable[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Pure ⑤-C2 helper: rebuild basic state from the complete attempt stream."""
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for attempt in attempts:
        user_id = attempt.get("user_id")
        node_id = attempt.get("knowledge_node_id")
        if not user_id or not node_id:
            continue
        grouped.setdefault((user_id, node_id), []).append(dict(attempt))

    states: list[dict[str, Any]] = []
    for (user_id, node_id), node_attempts in sorted(grouped.items()):
        ordered = sorted(node_attempts, key=_sort_attempt)
        correct_count = sum(item.get("is_correct") is True for item in ordered)
        incorrect_count = len(ordered) - correct_count
        confident_wrong_count = sum(
            item.get("is_correct") is False and item.get("confidence") == 1
            for item in ordered
        )
        consecutive_correct = 0
        for item in reversed(ordered):
            if item.get("is_correct") is not True:
                break
            consecutive_correct += 1
        correct_times = [
            item.get("answered_at") for item in ordered
            if item.get("is_correct") is True
        ]
        incorrect_times = [
            item.get("answered_at") for item in ordered
            if item.get("is_correct") is False
        ]
        last = ordered[-1]
        states.append({
            "user_id": user_id,
            "knowledge_node_id": node_id,
            "state": "repairing" if last.get("is_correct") is False else "checking",
            "attempt_count": len(ordered),
            "correct_count": correct_count,
            "incorrect_count": incorrect_count,
            "confident_wrong_count": confident_wrong_count,
            "consecutive_correct": consecutive_correct,
            "repair_confirmation_count": 0,
            "first_seen_at": ordered[0].get("answered_at"),
            "last_seen_at": last.get("answered_at"),
            "last_correct_at": correct_times[-1] if correct_times else None,
            "last_incorrect_at": incorrect_times[-1] if incorrect_times else None,
            "last_question_id": last.get("question_id"),
            "next_review_at": None,
            "last_error_type": None,
        })
    return states


def load_read_only_snapshot(connection) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Read the two source datasets.  This function deliberately issues SELECT only."""
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT event_key, user_id, mode, answered_count, correct_count,
                   answered_at, question_results
            FROM learning_events
            ORDER BY answered_at, event_key
            """
        )
        events = [dict(zip(LEARNING_EVENT_COLUMNS, row)) for row in cursor.fetchall()]
        cursor.execute(
            """
            SELECT event_key, user_id, question_id, knowledge_node_id, mode,
                   selected_answers, is_correct, confidence, answered_at,
                   attempt_position
            FROM question_attempts
            ORDER BY answered_at, event_key, attempt_position
            """
        )
        attempts = [dict(zip(ATTEMPT_COLUMNS, row)) for row in cursor.fetchall()]
    return events, attempts


def run_dry_run(connection=None) -> dict[str, Any]:
    if connection is None:
        if not database.database_is_available():
            raise RuntimeError("DATABASE_URL is required for the audit command")
        with database.get_db_connection() as created_connection:
            events, attempts = load_read_only_snapshot(created_connection)
    else:
        events, attempts = load_read_only_snapshot(connection)
    report, _candidates = audit_learning_history(events, attempts)
    return report


def required_confirmation(report: dict[str, Any]) -> str:
    """Return the human confirmation token for the current re-audit."""
    return f"BACKFILL_{report['new_attempt_candidates']}_ATTEMPTS"


def _insert_attempt(cursor, candidate: dict[str, Any]) -> bool:
    cursor.execute(
        """
        INSERT INTO question_attempts (
            event_key, user_id, question_id, knowledge_node_id, mode,
            selected_answers, is_correct, confidence, answered_at,
            attempt_position
        ) VALUES (
            %s, %s, %s, %s, %s, %s::jsonb, %s, %s, %s, %s
        )
        ON CONFLICT (event_key, attempt_position) DO NOTHING
        RETURNING id
        """,
        (
            candidate["event_key"], candidate["user_id"],
            candidate["question_id"], candidate["knowledge_node_id"],
            candidate["mode"],
            json.dumps(candidate.get("selected_answers"), ensure_ascii=False),
            candidate["is_correct"], candidate.get("confidence"),
            candidate["answered_at"], candidate["attempt_position"],
        ),
    )
    return cursor.fetchone() is not None


def _replace_user_node_states(
    cursor,
    affected_users: set[str],
    states: list[dict[str, Any]],
) -> None:
    """Replace only affected users' derived state inside the apply transaction."""
    if not affected_users:
        return
    cursor.execute(
        "DELETE FROM user_node_state WHERE user_id = ANY(%s)",
        (sorted(affected_users),),
    )
    for state in states:
        cursor.execute(
            """
            INSERT INTO user_node_state (
                user_id, knowledge_node_id, state, attempt_count,
                correct_count, incorrect_count, confident_wrong_count,
                consecutive_correct, repair_confirmation_count,
                first_seen_at, last_seen_at, last_correct_at,
                last_incorrect_at, last_question_id, next_review_at,
                last_error_type, updated_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, 0,
                %s, %s, %s, %s, %s, NULL, NULL, NOW()
            )
            """,
            (
                state["user_id"], state["knowledge_node_id"], state["state"],
                state["attempt_count"], state["correct_count"],
                state["incorrect_count"], state["confident_wrong_count"],
                state["consecutive_correct"], state["first_seen_at"],
                state["last_seen_at"], state["last_correct_at"],
                state["last_incorrect_at"], state["last_question_id"],
            ),
        )


def _count_states(cursor, affected_users: set[str]) -> int:
    if not affected_users:
        return 0
    cursor.execute(
        "SELECT COUNT(*) FROM user_node_state WHERE user_id = ANY(%s)",
        (sorted(affected_users),),
    )
    row = cursor.fetchone()
    return int(row[0]) if row else 0


def apply_backfill(
    connection,
    confirm: str,
    tag_resolver: Callable[[str], dict[str, Any]] = get_question_tag,
) -> dict[str, Any]:
    """Apply missing attempts and rebuild state; caller owns the transaction."""
    before_events, before_attempts = load_read_only_snapshot(connection)
    audit, candidates = audit_learning_history(
        before_events, before_attempts, tag_resolver
    )
    if not audit["apply_eligible"]:
        raise BackfillSafetyError("re-audit is not apply eligible; no writes allowed")
    expected_confirm = required_confirmation(audit)
    if confirm != expected_confirm:
        raise BackfillSafetyError(
            f"confirmation mismatch; expected {expected_confirm}"
        )

    inserted = 0
    with connection.cursor() as cursor:
        for candidate in candidates:
            inserted += int(_insert_attempt(cursor, candidate))

    after_events, after_attempts = load_read_only_snapshot(connection)
    post_audit, remaining = audit_learning_history(
        after_events, after_attempts, tag_resolver
    )
    if len(after_events) != len(before_events):
        raise BackfillSafetyError("learning_events count changed during apply")
    if (
        not post_audit["apply_eligible"]
        or remaining
        or post_audit["existing_conflicts"]
    ):
        raise BackfillSafetyError("post-insert attempt verification failed")

    source_event_keys = {event.get("event_key") for event in before_events}
    affected_users = {
        attempt["user_id"]
        for attempt in after_attempts
        if attempt.get("event_key") in source_event_keys and attempt.get("user_id")
    }
    affected_attempts = [
        attempt for attempt in after_attempts
        if attempt.get("user_id") in affected_users
    ]
    rebuilt_states = rebuild_user_node_states(affected_attempts)
    with connection.cursor() as cursor:
        _replace_user_node_states(cursor, affected_users, rebuilt_states)
        rebuilt_count = _count_states(cursor, affected_users)
    if rebuilt_count != len(rebuilt_states):
        raise BackfillSafetyError("user_node_state row verification failed")

    final_events, final_attempts = load_read_only_snapshot(connection)
    final_audit, final_remaining = audit_learning_history(
        final_events, final_attempts, tag_resolver
    )
    if (
        len(final_events) != len(before_events)
        or not final_audit["apply_eligible"]
        or final_remaining
        or final_audit["existing_conflicts"]
        or final_audit["existing_matched"] != audit["total_attempt_candidates"]
    ):
        raise BackfillSafetyError("post-write verification failed")

    result = dict(final_audit)
    result.update({
        "run_mode": "apply",
        "inserted": inserted,
        "skipped": final_audit["existing_matched"] - inserted,
        "conflicts": final_audit["existing_conflicts"],
        "question_attempts_total": len(final_attempts),
        "rebuilt_state_rows": rebuilt_count,
        "learning_events_before": len(before_events),
        "learning_events_after": len(final_events),
        "learning_events_unchanged": len(before_events) == len(final_events),
    })
    return result


def run_apply(confirm: str, connection=None) -> dict[str, Any]:
    """Run one atomic apply.  Connection context commits or rolls back."""
    if connection is None:
        if not database.database_is_available():
            raise RuntimeError("DATABASE_URL is required for the apply command")
        with database.get_db_connection() as created_connection:
            return apply_backfill(created_connection, confirm)
    with connection:
        return apply_backfill(connection, confirm)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="apply missing attempts after a fresh safety audit",
    )
    parser.add_argument(
        "--confirm",
        help="required apply token, for example BACKFILL_335_ATTEMPTS",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.apply and not args.confirm:
        print("ERROR: --apply requires --confirm; no database writes were made.")
        return 2
    try:
        report = run_apply(args.confirm) if args.apply else run_dry_run()
    except BackfillSafetyError as exc:
        print(f"ERROR: {exc}; transaction rolled back.")
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report["apply_eligible"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
