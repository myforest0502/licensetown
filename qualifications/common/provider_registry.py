"""Qualification-scoped Question Bank lookup with explicit PT registration.

This registry is a composition exception inside common: it imports concrete
qualification metadata and the PT adapter. The provider protocol itself remains
independent. Do not treat importing this registry as a side-effect-free contract
import; PT registration loads the legacy bank.

The registry is intentionally explicit: PT is available today, while a known
qualification without a provider must fail instead of silently falling back to
PT. Runtime qualification selection is not implemented here.
"""

from __future__ import annotations

from ..pt.config import PT
from ..pt.provider import PTQuestionBankProvider
from ..takken.config import TAKKEN


class QuestionBankProviderNotConfigured(LookupError):
    """Raised when a known qualification has no Question Bank provider yet."""


_PT_PROVIDER = PTQuestionBankProvider()
_PROVIDERS = {
    PT.qualification_id: _PT_PROVIDER,
}
_KNOWN_QUALIFICATION_IDS = frozenset({PT.qualification_id, TAKKEN.qualification_id})


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
