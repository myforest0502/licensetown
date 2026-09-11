"""Metadata only: no runtime, storage, or question-bank integration."""

from dataclasses import dataclass


@dataclass(frozen=True)
class QualificationConfig:
    """Stable qualification identity and its learner-facing name."""

    qualification_id: str
    display_name: str
