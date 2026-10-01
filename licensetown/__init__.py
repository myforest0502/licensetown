"""LicenseTown application-domain package.

Canonical qualification ownership lives in exactly three subpackages:
common, pt, and takken. Repository/runtime plumbing stays outside this package.
"""

from .common.base import QualificationConfig
from .common.learning_store_registry import register_learning_history_store
from .common.provider_registry import register_question_bank_provider
from .pt.config import PT
from .takken.config import TAKKEN

QUALIFICATIONS = (PT, TAKKEN)
DEFAULT_QUALIFICATION_ID = PT.qualification_id

# The package root declares known IDs without importing concrete adapters. Each
# qualification adapter registers itself when loaded, avoiding startup cycles.
register_question_bank_provider(PT.qualification_id)
register_question_bank_provider(TAKKEN.qualification_id)
register_learning_history_store(PT.qualification_id)
register_learning_history_store(TAKKEN.qualification_id)

def get_qualification(qualification_id: str) -> QualificationConfig:
    for qualification in QUALIFICATIONS:
        if qualification.qualification_id == qualification_id:
            return qualification
    raise KeyError(qualification_id)

def get_default_qualification() -> QualificationConfig:
    return get_qualification(DEFAULT_QUALIFICATION_ID)
