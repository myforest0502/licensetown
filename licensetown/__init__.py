"""LicenseTown application-domain package.

Canonical qualification ownership lives in exactly three subpackages:
common, pt, and takken. Repository/runtime plumbing stays outside this package.
"""

from .common.base import QualificationConfig
from .pt.config import PT
from .takken.config import TAKKEN

QUALIFICATIONS = (PT, TAKKEN)
DEFAULT_QUALIFICATION_ID = PT.qualification_id

def get_qualification(qualification_id: str) -> QualificationConfig:
    for qualification in QUALIFICATIONS:
        if qualification.qualification_id == qualification_id:
            return qualification
    raise KeyError(qualification_id)

def get_default_qualification() -> QualificationConfig:
    return get_qualification(DEFAULT_QUALIFICATION_ID)
