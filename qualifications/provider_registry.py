"""Compatibility imports for shared qualification provider lookup."""

from .common.provider_registry import (
    QuestionBankProviderNotConfigured,
    get_question_bank_provider,
)

__all__ = [
    "QuestionBankProviderNotConfigured",
    "get_question_bank_provider",
]
