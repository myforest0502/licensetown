"""Compatibility alias for licensetown.pt.phase11_active_repair_rules."""

import sys
from licensetown.pt import phase11_active_repair_rules as _implementation
sys.modules[__name__] = _implementation
