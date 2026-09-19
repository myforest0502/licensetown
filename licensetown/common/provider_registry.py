"""Explicit qualification-scoped Question Bank lookup."""

from __future__ import annotations
from ..pt.config import PT
from ..pt.provider import PTQuestionBankProvider
from ..takken.config import TAKKEN

class QuestionBankProviderNotConfigured(LookupError):
    pass

_PT_PROVIDER = PTQuestionBankProvider()
_PROVIDERS = {PT.qualification_id: _PT_PROVIDER}
_KNOWN_QUALIFICATION_IDS = frozenset({PT.qualification_id, TAKKEN.qualification_id})

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
