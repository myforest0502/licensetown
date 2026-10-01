"""Qualification-independent Question Bank provider registry."""

from __future__ import annotations

class QuestionBankProviderNotConfigured(LookupError):
    pass

_PROVIDERS = {}
_KNOWN_QUALIFICATION_IDS = set()


def register_question_bank_provider(qualification_id: str, provider=None) -> None:
    """Register a known qualification and its optional concrete provider."""
    qualification_id = str(qualification_id)
    _KNOWN_QUALIFICATION_IDS.add(qualification_id)
    if provider is not None:
        _PROVIDERS[qualification_id] = provider

def get_question_bank_provider(qualification_id: str):
    qualification_id = str(qualification_id)
    if qualification_id not in _KNOWN_QUALIFICATION_IDS:
        raise KeyError(qualification_id)
    try:
        return _PROVIDERS[qualification_id]
    except KeyError as exc:
        raise QuestionBankProviderNotConfigured(
            f"Question Bank provider is not configured for qualification: {qualification_id}"
        ) from exc
