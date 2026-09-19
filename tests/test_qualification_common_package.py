"""Coverage for the canonical common/PT/Takken package split."""

from licensetown.common.base import QualificationConfig
from licensetown.common.bank_provider import QuestionBankProvider
from licensetown.common.provider_registry import (
    QuestionBankProviderNotConfigured,
    get_question_bank_provider,
)
from licensetown.pt.config import PT
from licensetown.takken.config import TAKKEN


def test_qualification_configs_use_common_config_contract():
    assert isinstance(PT, QualificationConfig)
    assert isinstance(TAKKEN, QualificationConfig)
    assert PT.qualification_id == "pt"
    assert TAKKEN.qualification_id == "takken"


def test_common_registry_keeps_pt_only_provider_behavior():
    assert get_question_bank_provider("pt").qualification_id == "pt"


def test_takken_provider_remains_fail_closed():
    try:
        get_question_bank_provider("takken")
    except QuestionBankProviderNotConfigured:
        pass
    else:
        raise AssertionError("Takken provider must remain unconfigured")
