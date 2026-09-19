"""Compatibility alias for licensetown.pt.phase11_active_safety."""

import sys
from licensetown.pt import phase11_active_safety as _implementation
sys.modules[__name__] = _implementation
