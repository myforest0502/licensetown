"""Standalone qualification definitions, not wired into existing PT execution.

The default describes the legacy PT compatibility contract only. It does not
select a bank or infer the qualification of stored sessions or database rows.
"""

from .base import QualificationConfig
from .pt.config import PT
from .takken.config import TAKKEN

QUALIFICATIONS = (PT, TAKKEN)
DEFAULT_QUALIFICATION_ID = PT.qualification_id


def get_qualification(qualification_id: str) -> QualificationConfig:
    """Return known metadata; unknown IDs never silently fall back to PT."""
    for qualification in QUALIFICATIONS:
        if qualification.qualification_id == qualification_id:
            return qualification
    raise KeyError(qualification_id)


def get_default_qualification() -> QualificationConfig:
    """Return PT metadata without changing the existing application default."""
    return get_qualification(DEFAULT_QUALIFICATION_ID)
