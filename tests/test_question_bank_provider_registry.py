"""Regression coverage for explicit qualification-scoped provider lookup."""

import pytest

from qualifications.provider_registry import (
    QuestionBankProviderNotConfigured,
    get_question_bank_provider,
)
from qualifications.pt.provider import PTQuestionBankProvider


def test_pt_provider_is_available_and_stable():
    first = get_question_bank_provider("pt")
    second = get_question_bank_provider("pt")
    assert isinstance(first, PTQuestionBankProvider)
    assert first is second
    assert first.qualification_id == "pt"


def test_takken_does_not_silently_fall_back_to_pt():
    with pytest.raises(
        QuestionBankProviderNotConfigured,
        match="not configured for qualification: takken",
    ):
        get_question_bank_provider("takken")


def test_unknown_qualification_fails_closed():
    with pytest.raises(KeyError):
        get_question_bank_provider("unknown")


def test_lookup_does_not_normalize_or_infer_ids():
    for value in ("PT", " pt ", ""):
        with pytest.raises(KeyError):
            get_question_bank_provider(value)
