"""Qualification-independent learner-history store registry."""

from __future__ import annotations

class LearningHistoryStoreNotConfigured(LookupError):
    pass

_STORES = {}
_KNOWN_QUALIFICATION_IDS = set()


def register_learning_history_store(qualification_id: str, store=None) -> None:
    """Register a known qualification and its optional concrete store."""
    qualification_id = str(qualification_id)
    _KNOWN_QUALIFICATION_IDS.add(qualification_id)
    if store is not None:
        _STORES[qualification_id] = store

def get_learning_history_store(qualification_id: str):
    qualification_id = str(qualification_id)
    if qualification_id not in _KNOWN_QUALIFICATION_IDS:
        raise KeyError(qualification_id)
    try:
        return _STORES[qualification_id]
    except KeyError as exc:
        raise LearningHistoryStoreNotConfigured(
            f"Learning history store is not configured for qualification: {qualification_id}"
        ) from exc
