"""Compatibility alias for PT Phase11 active-repair candidate rules.

Retain legacy imports and function-global identity without changing authority.
"""
import sys

from qualifications.pt import phase11_active_repair_rules as _implementation

sys.modules[__name__] = _implementation
