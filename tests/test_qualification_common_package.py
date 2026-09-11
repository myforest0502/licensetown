"""Compatibility coverage for the common/PT/Takken package split."""

from qualifications.base import QualificationConfig as LegacyQualificationConfig
from qualifications.bank_provider import QuestionBankProvider as LegacyQuestionBankProvider
from qualifications.common.base import QualificationConfig
from qualifications.common.bank_provider import QuestionBankProvider
from qualifications.common.provider_registry import (
    QuestionBankProviderNotConfigured,
    get_question_bank_provider,
)
from qualifications.provider_registry import (
    QuestionBankProviderNotConfigured as LegacyProviderNotConfigured,
    get_question_bank_provider as legacy_get_question_bank_provider,
)
from qualifications.pt.config import PT
from qualifications.takken.config import TAKKEN


def test_common_contracts_preserve_legacy_import_identity():
    assert LegacyQualificationConfig is QualificationConfig
    assert LegacyQuestionBankProvider is QuestionBankProvider
    assert LegacyProviderNotConfigured is QuestionBankProviderNotConfigured
    assert legacy_get_question_bank_provider is get_question_bank_provider


def test_qualification_configs_use_common_config_contract():
    assert isinstance(PT, QualificationConfig)
    assert isinstance(TAKKEN, QualificationConfig)
    assert PT.qualification_id == "pt"
    assert TAKKEN.qualification_id == "takken"


def test_common_registry_keeps_pt_only_provider_behavior():
    assert get_question_bank_provider("pt").qualification_id == "pt"
