"""Production composition for PT-scoped learning-time totals.

The legacy recorder remains authoritative for today's PT runtime and already
writes ``learning_time_events`` rows that default to ``qualification_id='pt'``.
This hook mirrors only successful, deduplicated PT time additions into the new
qualification-scoped totals table so later dashboard/reset cutovers have a
separate PT authority without breaking the legacy total.
"""

from __future__ import annotations

import logging


logger = logging.getLogger(__name__)
_QUALIFICATION_ID = "pt"


def install_pt_learning_time_scope(legacy_module, database_module) -> None:
    """Mirror successful legacy PT time additions into scoped PT totals."""
    if getattr(legacy_module, "_pt_learning_time_scope_installed", False):
        return

    original_add_learning_time = legacy_module.add_learning_time

    def qualified_add_learning_time(
        user_id,
        elapsed_seconds,
        recorded_at=None,
        event_key=None,
    ):
        result = original_add_learning_time(
            user_id,
            elapsed_seconds,
            recorded_at=recorded_at,
            event_key=event_key,
        )
        if not result or not database_module.database_is_available():
            return result

        seconds = max(float(elapsed_seconds), 0.0)
        try:
            with database_module.get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO qualification_learning_time_totals (
                            user_id, qualification_id, total_seconds
                        ) VALUES (%s, %s, %s)
                        ON CONFLICT (user_id, qualification_id) DO UPDATE SET
                            total_seconds =
                                qualification_learning_time_totals.total_seconds
                                + EXCLUDED.total_seconds
                        """,
                        (user_id, _QUALIFICATION_ID, seconds),
                    )
        except Exception:
            # The learner's already-recorded PT event/time must not be rolled
            # back by a transitional mirror failure. It can be reconciled from
            # qualification-tagged learning_time_events.
            logger.exception(
                "pt_learning_time_scope mirror_failed user_id=%s event_key=%s",
                user_id,
                event_key,
            )
        return result

    legacy_module.add_learning_time = qualified_add_learning_time
    legacy_module._pt_learning_time_scope_original = original_add_learning_time
    legacy_module._pt_learning_time_scope_installed = True
