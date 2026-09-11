"""Shared qualification metadata contract only."""

from dataclasses import dataclass


@dataclass(frozen=True)
class QualificationConfig:
    """Stable qualification identity and its learner-facing name."""

    qualification_id: str
    display_name: str
