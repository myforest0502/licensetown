"""Qualification-scoped Question Bank provider lookup.

The registry is intentionally explicit: PT is available today, while a known
qualification without a provider must fail instead of silently falling back to
PT. Runtime qualification selection is not implemented here.
"""

from __future__ import annotations

from .pt.provider import PTQuestionBankProvider


class QuestionBankProviderNotConfigured(LookupError):
    """Raised when a known qualification has no Question Bank provider yet."""


_PT_PROVIDER = PTQuestionBankProvider()
_PROVIDERS = {
    _PT_PROVIDER.qualification_id: _PT_PROVIDER,
}
_KNOWN_QUALIFICATION_IDS = frozenset({"pt", "takken"})


def get_question_bank_provider(qualification_id: str):
    """Return the configured provider without any implicit PT fallback."""
    qualification_id = str(qualification_id)
    if qualification_id not in _KNOWN_QUALIFICATION_IDS:
        raise KeyError(qualification_id)
    try:
        return _PROVIDERS[qualification_id]
    except KeyError as exc:
        raise QuestionBankProviderNotConfigured(
            f"Question Bank provider is not configured for qualification: {qualification_id}"
        ) from exc
