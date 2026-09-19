"""Compatibility alias for licensetown.pt.readiness_service."""

import sys
from licensetown.pt import readiness_service as _implementation
sys.modules[__name__] = _implementation
