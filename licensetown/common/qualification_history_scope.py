"""Production composition hook for qualification-scoped learner history.

The legacy app imports history functions directly from ``database``. During the
multi-qualification transition we rebind only those module-local names to the
explicit PT learning-history store, keeping the existing call sites unchanged.
"""

from __future__ import annotations

from qualifications.common.learning_store_registry import get_learning_history_store


_HISTORY_NAMES = (
    "get_question_attempts",
    "get_question_history",
    "is_initial_assessment_completed",
    "mark_initial_assessment_completed",
)


def install_pt_learning_history_scope(legacy_module) -> None:
    """Bind the existing PT learner runtime to explicitly PT-scoped history."""
    if getattr(legacy_module, "_pt_learning_history_scope_installed", False):
        return

    store = get_learning_history_store("pt")
    for name in _HISTORY_NAMES:
        if not hasattr(legacy_module, name):
            raise AttributeError(f"legacy learner runtime missing history hook: {name}")
        setattr(legacy_module, name, getattr(store, name))

    legacy_module._pt_learning_history_store = store
    legacy_module._pt_learning_history_scope_installed = True
