"""Compatibility layer for the canonical licensetown package."""

from licensetown import (
    DEFAULT_QUALIFICATION_ID,
    QUALIFICATIONS,
    PT,
    TAKKEN,
    QualificationConfig,
    get_default_qualification,
    get_qualification,
)

__all__ = [
    "QualificationConfig", "PT", "TAKKEN", "QUALIFICATIONS",
    "DEFAULT_QUALIFICATION_ID", "get_qualification", "get_default_qualification",
]
