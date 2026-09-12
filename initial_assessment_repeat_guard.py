"""Production composition guard for initial-assessment short-term repeats.

The legacy initial-assessment branch already supports exclusions in
``learning_engine.build_initial_assessment`` but does not pass learner history
from ``app.start_quiz``.  This hook keeps ``app.py`` stable while making the
same short-term evidence floor used by the other learner-facing paths apply to
initial assessment as well.
"""

from __future__ import annotations

from contextvars import ContextVar
from functools import wraps

from short_term_repeat_guard import blocked_short_term_evidence_ids


_INITIAL_ASSESSMENT_BLOCKED: ContextVar[frozenset[str] | None] = ContextVar(
    "lt_initial_assessment_blocked",
    default=None,
)


def install_initial_assessment_repeat_guard(legacy_module) -> None:
    """Make legacy initial assessment honor the learner's short-term guard."""
    if getattr(legacy_module, "_initial_assessment_repeat_guard_installed", False):
        return

    original_start_quiz = legacy_module.start_quiz
    original_build_initial_assessment = legacy_module.build_initial_assessment

    @wraps(original_build_initial_assessment)
    def guarded_build_initial_assessment(question_count=30, *args, **kwargs):
        contextual_blocked = _INITIAL_ASSESSMENT_BLOCKED.get()
        if contextual_blocked is None:
            return original_build_initial_assessment(question_count, *args, **kwargs)

        explicit = {str(value) for value in (kwargs.pop("exclude_ids", ()) or ())}
        explicit.update(contextual_blocked)
        return original_build_initial_assessment(
            question_count,
            *args,
            exclude_ids=explicit,
            **kwargs,
        )

    @wraps(original_start_quiz)
    def guarded_start_quiz(user_id, session_kind=None, question_count=None, exclude_ids=None):
        if session_kind != "initial_assessment":
            return original_start_quiz(
                user_id,
                session_kind=session_kind,
                question_count=question_count,
                exclude_ids=exclude_ids,
            )

        attempts = legacy_module.get_question_attempts(user_id)
        blocked = blocked_short_term_evidence_ids(attempts)
        blocked.update(str(value) for value in (exclude_ids or ()))
        token = _INITIAL_ASSESSMENT_BLOCKED.set(frozenset(blocked))
        try:
            return original_start_quiz(
                user_id,
                session_kind=session_kind,
                question_count=question_count,
                exclude_ids=exclude_ids,
            )
        finally:
            _INITIAL_ASSESSMENT_BLOCKED.reset(token)

    legacy_module.build_initial_assessment = guarded_build_initial_assessment
    legacy_module.start_quiz = guarded_start_quiz
    legacy_module._initial_assessment_repeat_guard_installed = True
