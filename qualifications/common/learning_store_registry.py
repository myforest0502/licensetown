"""Explicit lookup for qualification-scoped learner-history stores."""

from __future__ import annotations

from ..pt.config import PT
from ..pt.learning_store import PTLearningHistoryStore
from ..takken.config import TAKKEN


class LearningHistoryStoreNotConfigured(LookupError):
    """Raised when a known qualification has no learning-history store yet."""


_PT_STORE = PTLearningHistoryStore()
_STORES = {
    PT.qualification_id: _PT_STORE,
}
_KNOWN_QUALIFICATION_IDS = frozenset({PT.qualification_id, TAKKEN.qualification_id})


def get_learning_history_store(qualification_id: str):
    """Return the configured store without any implicit PT fallback."""
    qualification_id = str(qualification_id)
    if qualification_id not in _KNOWN_QUALIFICATION_IDS:
        raise KeyError(qualification_id)
    try:
        return _STORES[qualification_id]
    except KeyError as exc:
        raise LearningHistoryStoreNotConfigured(
            f"Learning history store is not configured for qualification: {qualification_id}"
        ) from exc
